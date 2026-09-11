/**
 * OIML R-76 Pure JavaScript Metrological Calculation Engine
 * Conforms strictly to OIML R-76-1:2006 (E)
 */

const CLASS_I = "I";
const CLASS_II = "II";
const CLASS_III = "III";
const CLASS_IIII = "IIII";

const CLASS_NAMES = {
    [CLASS_I]: "Class I (Special Accuracy)",
    [CLASS_II]: "Class II (High Accuracy)",
    [CLASS_III]: "Class III (Medium Accuracy)",
    [CLASS_IIII]: "Class IIII (Ordinary Accuracy)",
};

function getR76ClassRequirements(accClass) {
    const reqs = {
        [CLASS_I]: {
            name: CLASS_NAMES[CLASS_I],
            min_e_g: 0.001,
            min_n: 50000,
            max_n: null,
            min_capacity_factor: 100,
            mpe_steps: [
                { max_e: 50000, mpe_e: 0.5 },
                { max_e: 200000, mpe_e: 1.0 },
                { max_e: Infinity, mpe_e: 1.5 },
            ],
        },
        [CLASS_II]: {
            name: CLASS_NAMES[CLASS_II],
            min_e_g: 0.001,
            min_n: 100,
            max_n: 100000,
            min_capacity_factor: 20,
            mpe_steps: [
                { max_e: 5000, mpe_e: 0.5 },
                { max_e: 20000, mpe_e: 1.0 },
                { max_e: 100000, mpe_e: 1.5 },
            ],
        },
        [CLASS_III]: {
            name: CLASS_NAMES[CLASS_III],
            min_e_g: 0.1,
            min_n: 100,
            max_n: 10000,
            min_capacity_factor: 20,
            mpe_steps: [
                { max_e: 500, mpe_e: 0.5 },
                { max_e: 2000, mpe_e: 1.0 },
                { max_e: 10000, mpe_e: 1.5 },
            ],
        },
        [CLASS_IIII]: {
            name: CLASS_NAMES[CLASS_IIII],
            min_e_g: 5.0,
            min_n: 100,
            max_n: 1000,
            min_capacity_factor: 10,
            mpe_steps: [
                { max_e: 50, mpe_e: 0.5 },
                { max_e: 200, mpe_e: 1.0 },
                { max_e: 1000, mpe_e: 1.5 },
            ],
        },
    };
    return reqs[accClass] || reqs[CLASS_III];
}

function calculateScaleDivisions(maxCap, e) {
    if (e <= 0) return 0;
    return Math.round(maxCap / e);
}

function calculateMinCapacity(accClass, e) {
    if (accClass === CLASS_I) return 100.0 * e;
    if (accClass === CLASS_II) return (e < 0.1 ? 20.0 : 50.0) * e;
    if (accClass === CLASS_III) return 20.0 * e;
    if (accClass === CLASS_IIII) return 10.0 * e;
    return 20.0 * e;
}

function validateInstrumentParameters(accClass, maxCap, minCap, e, d) {
    const errors = [];
    const warnings = [];

    if (maxCap <= 0) errors.push("Maximum capacity (Max) must be greater than 0.");
    if (e <= 0) errors.push("Verification interval (e) must be greater than 0.");
    if (d <= 0) errors.push("Actual interval (d) must be greater than 0.");
    if (d > e) warnings.push(`Actual interval d (${d}) > verification interval e (${e}).`);

    if (errors.length > 0) {
        return { is_valid: false, errors, warnings, n: 0, required_min: 0 };
    }

    const n = calculateScaleDivisions(maxCap, e);
    const reqs = getR76ClassRequirements(accClass);
    const required_min = calculateMinCapacity(accClass, e);

    if (n < reqs.min_n) {
        errors.push(`Scale divisions n = ${n.toLocaleString()} is below minimum allowed (${reqs.min_n.toLocaleString()}) for ${reqs.name}.`);
    }
    if (reqs.max_n !== null && n > reqs.max_n) {
        errors.push(`Scale divisions n = ${n.toLocaleString()} exceeds maximum allowed (${reqs.max_n.toLocaleString()}) for ${reqs.name}.`);
    }
    if (minCap < (required_min - 1e-9)) {
        warnings.push(`Stated Min capacity (${minCap}) is below OIML R-76 minimum (${required_min}).`);
    }

    return {
        is_valid: errors.length === 0,
        n: n,
        required_min: Number(required_min.toFixed(6)),
        errors,
        warnings,
    };
}

function calculateMPE(load, accClass, e, isInService = false) {
    if (e <= 0 || load < 0) return 0.0;
    const m_in_e = load / e;
    const reqs = getR76ClassRequirements(accClass);
    let factor = 0.5;

    for (const step of reqs.mpe_steps) {
        if (m_in_e <= step.max_e) {
            factor = step.mpe_e;
            break;
        }
    }

    let mpe = factor * e;
    if (isInService) mpe *= 2.0;
    return Number(mpe.toFixed(8));
}

function calculateErrorTurningPoint(load, indication, deltaL, e, useTurningPoint = true) {
    if (useTurningPoint && deltaL !== null && deltaL !== undefined && deltaL !== "") {
        return Number((indication + (0.5 * e) - Number(deltaL) - load).toFixed(8));
    }
    return Number((indication - load).toFixed(8));
}

function evaluateZeroTest(zeroIndication, deltaLZero, e, useTurningPoint = true) {
    const e0 = calculateErrorTurningPoint(0.0, zeroIndication, deltaLZero, e, useTurningPoint);
    const maxAllowed = Number((0.25 * e).toFixed(6));
    const passed = Math.abs(e0) <= (maxAllowed + 1e-7);
    return {
        zero_indication: zeroIndication,
        delta_l_zero: deltaLZero,
        e0: Number(e0.toFixed(6)),
        max_allowed_error: maxAllowed,
        passed,
        status: passed ? "PASS" : "FAIL",
    };
}

function evaluateTareTest(tareLoad, tareIndication, deltaLTare, netLoad, netIndication, deltaLNet, accClass, e, isInService = false, useTurningPoint = true) {
    const eTare = calculateErrorTurningPoint(tareLoad, tareIndication, deltaLTare, e, useTurningPoint);
    const tareZeroPassed = Math.abs(eTare) <= (0.25 * e + 1e-7);

    const eNetRaw = calculateErrorTurningPoint(netLoad, netIndication, deltaLNet, e, useTurningPoint);
    const eNetCorr = Number((eNetRaw - eTare).toFixed(6));
    const mpeNet = calculateMPE(netLoad, accClass, e, isInService);
    const netPassed = Math.abs(eNetCorr) <= (mpeNet + 1e-7);
    const passed = tareZeroPassed && netPassed;

    return {
        tare_load: tareLoad,
        tare_indication: tareIndication,
        delta_l_tare: deltaLTare,
        e_tare: Number(eTare.toFixed(6)),
        tare_zero_passed: tareZeroPassed,
        net_test_load: netLoad,
        net_indication: netIndication,
        delta_l_net: deltaLNet,
        e_net_raw: Number(eNetRaw.toFixed(6)),
        e_net_corr: eNetCorr,
        mpe_net: mpeNet,
        net_passed: netPassed,
        passed,
        status: passed ? "PASS" : "FAIL",
    };
}

function evaluateRepeatabilityTest(series, accClass, e, isInService = false) {
    const evaluated = [];
    let allPassed = true;

    for (const item of series) {
        const load = Number(item.load || 0);
        const readings = (item.readings || []).map(Number).filter(x => !isNaN(x));

        if (readings.length < 3) {
            evaluated.push({
                load, readings, count: readings.length,
                i_max: 0, i_min: 0, delta: 0, mpe: 0,
                passed: false, status: "INCOMPLETE (< 3 runs)"
            });
            allPassed = false;
            continue;
        }

        const iMax = Math.max(...readings);
        const iMin = Math.min(...readings);
        const delta = Number((iMax - iMin).toFixed(6));
        const mpe = calculateMPE(load, accClass, e, isInService);
        const passed = delta <= (mpe + 1e-7);
        if (!passed) allPassed = false;

        evaluated.push({
            load, readings, count: readings.length,
            i_max: Number(iMax.toFixed(6)),
            i_min: Number(iMin.toFixed(6)),
            delta, mpe, passed,
            status: passed ? "PASS" : "FAIL"
        });
    }

    return {
        series: evaluated,
        passed: allPassed && evaluated.length > 0,
        status: (allPassed && evaluated.length > 0) ? "PASS" : "FAIL",
    };
}

function evaluateEccentricityTest(testLoad, points, accClass, e, zeroError = 0.0, isInService = false, useTurningPoint = true) {
    const mpe = calculateMPE(testLoad, accClass, e, isInService);
    const evaluated = [];
    let allPassed = true;
    const errorsList = [];

    for (const pt of points) {
        const indication = Number(pt.indication || 0);
        const rawErr = calculateErrorTurningPoint(testLoad, indication, pt.delta_l, e, useTurningPoint);
        const corrErr = Number((rawErr - zeroError).toFixed(6));
        const passed = Math.abs(corrErr) <= (mpe + 1e-7);
        if (!passed) allPassed = false;
        errorsList.push(corrErr);

        evaluated.push({
            position_id: pt.position_id,
            position_name: pt.position_name || `Position ${pt.position_id}`,
            indication,
            delta_l: pt.delta_l,
            raw_error: Number(rawErr.toFixed(6)),
            corrected_error: corrErr,
            mpe, passed,
            status: passed ? "PASS" : "FAIL"
        });
    }

    const maxDiff = errorsList.length > 0 ? Number((Math.max(...errorsList) - Math.min(...errorsList)).toFixed(6)) : 0;

    return {
        test_load: testLoad,
        mpe,
        zero_error_applied: zeroError,
        points: evaluated,
        max_error_diff: maxDiff,
        passed: allPassed && evaluated.length > 0,
        status: (allPassed && evaluated.length > 0) ? "PASS" : "FAIL",
    };
}

function evaluateWeighingTest(rows, accClass, e, zeroError = 0.0, isInService = false, useTurningPoint = true) {
    const evaluated = [];
    let allPassed = true;
    let maxHysteresis = 0;

    for (const r of rows) {
        const load = Number(r.load || 0);
        const mpe = calculateMPE(load, accClass, e, isInService);

        const iInc = Number(r.i_inc || 0);
        const rawInc = calculateErrorTurningPoint(load, iInc, r.delta_l_inc, e, useTurningPoint);
        const corrInc = Number((rawInc - zeroError).toFixed(6));
        const passedInc = Math.abs(corrInc) <= (mpe + 1e-7);

        const hasDec = r.i_dec !== null && r.i_dec !== undefined && String(r.i_dec).trim() !== "";
        let rawDec = null;
        let corrDec = null;
        let passedDec = true;
        let hysteresis = null;

        if (hasDec) {
            const iDec = Number(r.i_dec);
            rawDec = calculateErrorTurningPoint(load, iDec, r.delta_l_dec, e, useTurningPoint);
            corrDec = Number((rawDec - zeroError).toFixed(6));
            passedDec = Math.abs(corrDec) <= (mpe + 1e-7);
            hysteresis = Number(Math.abs(corrDec - corrInc).toFixed(6));
            if (hysteresis > maxHysteresis) maxHysteresis = hysteresis;
        }

        const rowPassed = passedInc && passedDec;
        if (!rowPassed) allPassed = false;

        evaluated.push({
            load, mpe,
            i_inc: iInc,
            delta_l_inc: r.delta_l_inc,
            e_inc_raw: Number(rawInc.toFixed(6)),
            e_inc_corr: corrInc,
            passed_inc: passedInc,
            i_dec: hasDec ? Number(r.i_dec) : null,
            delta_l_dec: r.delta_l_dec,
            e_dec_raw: rawDec !== null ? Number(rawDec.toFixed(6)) : null,
            e_dec_corr: corrDec,
            passed_dec: passedDec,
            hysteresis,
            passed: rowPassed,
            status: rowPassed ? "PASS" : "FAIL"
        });
    }

    return {
        rows: evaluated,
        max_hysteresis: Number(maxHysteresis.toFixed(6)),
        zero_error_applied: zeroError,
        passed: allPassed && evaluated.length >= 5,
        row_count: evaluated.length,
        status: (allPassed && evaluated.length >= 5) ? "PASS" : (allPassed ? "INCOMPLETE (< 5 points)" : "FAIL"),
    };
}

function evaluateFullR76Report(payload) {
    const inst = payload.instrument || {};
    const accClass = inst.accuracy_class || CLASS_III;
    const maxCap = Number(inst.max_capacity || 0);
    const minCap = Number(inst.min_capacity || 0);
    const e = Number(inst.e || 0);
    const d = Number(inst.d || e);
    const isInService = Boolean(payload.is_in_service);
    const useTurningPoint = payload.use_turning_point !== false;

    const params = validateInstrumentParameters(accClass, maxCap, minCap, e, d);

    const zeroEval = evaluateZeroTest(
        Number(payload.zero_test?.indication || 0),
        payload.zero_test?.delta_l,
        e,
        useTurningPoint
    );

    const tareEval = evaluateTareTest(
        Number(payload.tare_test?.tare_load || 0),
        Number(payload.tare_test?.tare_indication || 0),
        payload.tare_test?.delta_l_tare,
        Number(payload.tare_test?.net_test_load || 0),
        Number(payload.tare_test?.net_indication || 0),
        payload.tare_test?.delta_l_net,
        accClass, e, isInService, useTurningPoint
    );

    const weighEval = evaluateWeighingTest(
        payload.weighing_test?.rows || [],
        accClass, e, zeroEval.e0, isInService, useTurningPoint
    );

    const repEval = evaluateRepeatabilityTest(
        payload.repeatability_test?.series || [],
        accClass, e, isInService
    );

    const eccEval = evaluateEccentricityTest(
        Number(payload.eccentricity_test?.test_load || 0),
        payload.eccentricity_test?.points || [],
        accClass, e, zeroEval.e0, isInService, useTurningPoint
    );

    const subtestsPass = zeroEval.passed && tareEval.passed && weighEval.passed && repEval.passed && eccEval.passed;
    const overallPass = params.is_valid && subtestsPass;

    return {
        overall_status: overallPass ? "PASS" : "FAIL",
        overall_passed: overallPass,
        is_in_service: isInService,
        use_turning_point: useTurningPoint,
        parameters: params,
        zero_test: zeroEval,
        tare_test: tareEval,
        weighing_test: weighEval,
        repeatability_test: repEval,
        eccentricity_test: eccEval,
        summary: [
            { test: "Instrument Metrological Limits (Table 3)", status: params.is_valid ? "PASS" : "FAIL" },
            { test: "Zero Setting Accuracy (A.4.2)", status: zeroEval.status },
            { test: "Tare Balancing & Net Weighing (A.4.6)", status: tareEval.status },
            { test: "Weighing Performance & Hysteresis (A.4.4)", status: weighEval.status },
            { test: "Repeatability (A.4.10)", status: repEval.status },
            { test: "Eccentricity (A.4.7)", status: eccEval.status },
        ]
    };
}
