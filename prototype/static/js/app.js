/**
 * NAWI Test Report Generation System (OIML R-76)
 * Client-side Controller & Dynamic Real-time Calculations
 */

let calcDebounceTimer = null;
let currentEvaluation = null;

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initPresets();
    initDynamicTables();
    attachLiveCalculationListeners();

    // Load default preset initially if form is empty
    const presetSelect = document.getElementById("demoPresetSelect");
    if (presetSelect && presetSelect.value) {
        loadPreset(presetSelect.value);
    } else {
        triggerLiveCalculation();
    }
});

/* ==========================================================================
   Tab Navigation
   ========================================================================== */
function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.getAttribute("data-tab");
            switchTab(target);
        });
    });

    // Step navigation buttons
    document.querySelectorAll(".btn-next-tab").forEach(btn => {
        btn.addEventListener("click", () => {
            const nextTab = btn.getAttribute("data-next");
            switchTab(nextTab);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });

    document.querySelectorAll(".btn-prev-tab").forEach(btn => {
        btn.addEventListener("click", () => {
            const prevTab = btn.getAttribute("data-prev");
            switchTab(prevTab);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });
}

function switchTab(tabId) {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));

    const targetBtn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    const targetPanel = document.getElementById(tabId);

    if (targetBtn) targetBtn.classList.add("active");
    if (targetPanel) targetPanel.classList.add("active");
}

/* ==========================================================================
   Presets Management
   ========================================================================== */
function initPresets() {
    const selector = document.getElementById("demoPresetSelect");
    if (!selector) return;

    selector.addEventListener("change", (e) => {
        const val = e.target.value;
        if (val && DEMO_PRESETS[val]) {
            loadPreset(val);
        }
    });

    const resetBtn = document.getElementById("btnResetForm");
    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            if (confirm("Reset all test inputs to blank?")) {
                document.getElementById("testForm").reset();
                triggerLiveCalculation();
            }
        });
    }
}

function loadPreset(presetKey) {
    const data = DEMO_PRESETS[presetKey];
    if (!data) return;

    // Instrument
    setVal("certNo", data.certificate_no || "");
    setVal("testDate", data.test_date || "");
    setVal("inspectorName", data.inspector_name || "");
    setVal("customerName", data.customer_name || "");
    setVal("location", data.location || "");
    setVal("isInService", data.is_in_service ? "1" : "0");
    setVal("useTurningPoint", data.use_turning_point ? "1" : "0");

    const inst = data.instrument || {};
    setVal("instManufacturer", inst.manufacturer || "");
    setVal("instModel", inst.model || "");
    setVal("instSerial", inst.serial_no || "");
    setVal("instAccuracyClass", inst.accuracy_class || "III");
    setVal("instMaxCapacity", inst.max_capacity || "");
    setVal("instMinCapacity", inst.min_capacity || "");
    setVal("instE", inst.e || "");
    setVal("instD", inst.d || "");
    setVal("instUnit", inst.unit || "kg");
    setVal("instTareMax", inst.tare_max || "");
    setVal("instDeviceType", inst.device_type || "");

    // Environment & Standards
    const env = data.environment || {};
    setVal("envTemp", env.temp_c || 20);
    setVal("envHumidity", env.humidity_pct || 50);
    setVal("envPressure", env.pressure_hpa || 1013.25);

    const std = data.standards || {};
    setVal("stdWeightsId", std.standards_id || "");
    setVal("stdWeightsCert", std.standards_cert || "");

    // Zero Test
    const z = data.zero_test || {};
    setVal("zeroIndication", z.indication !== undefined ? z.indication : 0);
    setVal("zeroDeltaL", z.delta_l !== undefined ? z.delta_l : "");

    // Tare Test
    const t = data.tare_test || {};
    setVal("tareLoad", t.tare_load || "");
    setVal("tareIndication", t.tare_indication || "");
    setVal("tareDeltaL", t.delta_l_tare !== undefined ? t.delta_l_tare : "");
    setVal("tareNetLoad", t.net_test_load || "");
    setVal("tareNetIndication", t.net_indication || "");
    setVal("tareNetDeltaL", t.delta_l_net !== undefined ? t.delta_l_net : "");

    // Eccentricity Test
    const ecc = data.eccentricity_test || {};
    setVal("eccTestLoad", ecc.test_load || "");
    const eccPoints = ecc.points || [];
    for (let i = 1; i <= 5; i++) {
        const pt = eccPoints.find(p => p.position_id === i) || {};
        setVal(`eccInd_${i}`, pt.indication !== undefined ? pt.indication : "");
        setVal(`eccDeltaL_${i}`, pt.delta_l !== undefined ? pt.delta_l : "");
    }

    // Repeatability Test
    renderRepeatabilityRows(data.repeatability_test ? data.repeatability_test.series : []);

    // Weighing Test
    renderWeighingRows(data.weighing_test ? data.weighing_test.rows : []);

    // Trigger instant recalculation
    triggerLiveCalculation();
}

function setVal(elementId, val) {
    const el = document.getElementById(elementId);
    if (!el) return;
    if (el.type === "checkbox") {
        el.checked = Boolean(val);
    } else {
        el.value = val;
    }
}

function getVal(elementId, defaultVal = "") {
    const el = document.getElementById(elementId);
    if (!el) return defaultVal;
    if (el.type === "checkbox") return el.checked;
    return el.value;
}

/* ==========================================================================
   Dynamic Tables: Repeatability & Weighing
   ========================================================================== */
function initDynamicTables() {
    // Weighing rows add/remove
    const addWeighBtn = document.getElementById("btnAddWeighingRow");
    if (addWeighBtn) {
        addWeighBtn.addEventListener("click", () => {
            const tbody = document.getElementById("weighingTableBody");
            const rowCount = tbody.querySelectorAll("tr").length + 1;
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><input type="number" step="any" class="weigh-load" placeholder="Load"></td>
                <td><input type="number" step="any" class="weigh-i-inc" placeholder="I (Inc)"></td>
                <td><input type="number" step="any" class="weigh-dl-inc" placeholder="ΔL"></td>
                <td class="mono-val weigh-ec-inc">—</td>
                <td><input type="number" step="any" class="weigh-i-dec" placeholder="I (Dec)"></td>
                <td><input type="number" step="any" class="weigh-dl-dec" placeholder="ΔL"></td>
                <td class="mono-val weigh-ec-dec">—</td>
                <td class="mono-val weigh-hyst">—</td>
                <td class="mono-val weigh-mpe">—</td>
                <td class="weigh-status"><span class="badge badge-tech">—</span></td>
                <td><button type="button" class="table-action-btn btn-del-row" title="Remove">&times;</button></td>
            `;
            tbody.appendChild(tr);
            attachRowDelete(tr.querySelector(".btn-del-row"));
            triggerLiveCalculation();
        });
    }

    // Attach existing delete buttons
    document.querySelectorAll(".btn-del-row").forEach(btn => attachRowDelete(btn));

    // Repeatability series add
    const addRepBtn = document.getElementById("btnAddRepeatabilitySeries");
    if (addRepBtn) {
        addRepBtn.addEventListener("click", () => {
            const tbody = document.getElementById("repeatabilityTableBody");
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><input type="number" step="any" class="rep-load" placeholder="e.g. 7.5"></td>
                <td><input type="text" class="rep-readings" placeholder="Comma separated, e.g. 7.500, 7.502, 7.500"></td>
                <td class="mono-val rep-imax">—</td>
                <td class="mono-val rep-imin">—</td>
                <td class="mono-val rep-delta">—</td>
                <td class="mono-val rep-mpe">—</td>
                <td class="rep-status"><span class="badge badge-tech">—</span></td>
                <td><button type="button" class="table-action-btn btn-del-row" title="Remove">&times;</button></td>
            `;
            tbody.appendChild(tr);
            attachRowDelete(tr.querySelector(".btn-del-row"));
            triggerLiveCalculation();
        });
    }
}

function attachRowDelete(btn) {
    if (!btn) return;
    btn.addEventListener("click", (e) => {
        const tr = e.target.closest("tr");
        if (tr) {
            tr.remove();
            triggerLiveCalculation();
        }
    });
}

function renderWeighingRows(rows) {
    const tbody = document.getElementById("weighingTableBody");
    if (!tbody) return;
    tbody.innerHTML = "";

    (rows || []).forEach(r => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><input type="number" step="any" class="weigh-load" value="${r.load !== undefined ? r.load : ''}"></td>
            <td><input type="number" step="any" class="weigh-i-inc" value="${r.i_inc !== undefined ? r.i_inc : ''}"></td>
            <td><input type="number" step="any" class="weigh-dl-inc" value="${r.delta_l_inc !== undefined ? r.delta_l_inc : ''}"></td>
            <td class="mono-val weigh-ec-inc">—</td>
            <td><input type="number" step="any" class="weigh-i-dec" value="${r.i_dec !== undefined ? r.i_dec : ''}"></td>
            <td><input type="number" step="any" class="weigh-dl-dec" value="${r.delta_l_dec !== undefined ? r.delta_l_dec : ''}"></td>
            <td class="mono-val weigh-ec-dec">—</td>
            <td class="mono-val weigh-hyst">—</td>
            <td class="mono-val weigh-mpe">—</td>
            <td class="weigh-status"><span class="badge badge-tech">—</span></td>
            <td><button type="button" class="table-action-btn btn-del-row" title="Remove">&times;</button></td>
        `;
        tbody.appendChild(tr);
        attachRowDelete(tr.querySelector(".btn-del-row"));
    });
}

function renderRepeatabilityRows(series) {
    const tbody = document.getElementById("repeatabilityTableBody");
    if (!tbody) return;
    tbody.innerHTML = "";

    (series || []).forEach(s => {
        const readingsStr = (s.readings || []).join(", ");
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><input type="number" step="any" class="rep-load" value="${s.load !== undefined ? s.load : ''}"></td>
            <td><input type="text" class="rep-readings" value="${readingsStr}"></td>
            <td class="mono-val rep-imax">—</td>
            <td class="mono-val rep-imin">—</td>
            <td class="mono-val rep-delta">—</td>
            <td class="mono-val rep-mpe">—</td>
            <td class="rep-status"><span class="badge badge-tech">—</span></td>
            <td><button type="button" class="table-action-btn btn-del-row" title="Remove">&times;</button></td>
        `;
        tbody.appendChild(tr);
        attachRowDelete(tr.querySelector(".btn-del-row"));
    });
}

/* ==========================================================================
   Form Serialization
   ========================================================================== */
function serializeForm() {
    // Weighing rows
    const weighingRows = [];
    document.querySelectorAll("#weighingTableBody tr").forEach(tr => {
        const load = tr.querySelector(".weigh-load")?.value;
        const i_inc = tr.querySelector(".weigh-i-inc")?.value;
        const delta_l_inc = tr.querySelector(".weigh-dl-inc")?.value;
        const i_dec = tr.querySelector(".weigh-i-dec")?.value;
        const delta_l_dec = tr.querySelector(".weigh-dl-dec")?.value;

        if (load !== "" && load !== undefined) {
            weighingRows.push({
                load: parseFloat(load),
                i_inc: i_inc !== "" ? parseFloat(i_inc) : 0,
                delta_l_inc: delta_l_inc !== "" ? parseFloat(delta_l_inc) : null,
                i_dec: i_dec !== "" ? parseFloat(i_dec) : null,
                delta_l_dec: delta_l_dec !== "" ? parseFloat(delta_l_dec) : null,
            });
        }
    });

    // Repeatability series
    const repSeries = [];
    document.querySelectorAll("#repeatabilityTableBody tr").forEach(tr => {
        const load = tr.querySelector(".rep-load")?.value;
        const readingsStr = tr.querySelector(".rep-readings")?.value || "";
        const readings = readingsStr.split(",")
            .map(x => x.trim())
            .filter(x => x !== "")
            .map(x => parseFloat(x))
            .filter(x => !isNaN(x));

        if (load !== "" && load !== undefined) {
            repSeries.push({
                load: parseFloat(load),
                readings: readings,
            });
        }
    });

    // Eccentricity points
    const eccPoints = [];
    const posNames = {
        1: "Center (1)",
        2: "Front-Left (2)",
        3: "Back-Left (3)",
        4: "Back-Right (4)",
        5: "Front-Right (5)",
    };
    for (let i = 1; i <= 5; i++) {
        const ind = getVal(`eccInd_${i}`);
        const dl = getVal(`eccDeltaL_${i}`);
        if (ind !== "") {
            eccPoints.push({
                position_id: i,
                position_name: posNames[i] || `Position ${i}`,
                indication: parseFloat(ind),
                delta_l: dl !== "" ? parseFloat(dl) : null,
            });
        }
    }

    return {
        certificate_no: getVal("certNo"),
        test_date: getVal("testDate"),
        inspector_name: getVal("inspectorName"),
        customer_name: getVal("customerName"),
        location: getVal("location"),
        is_in_service: getVal("isInService") === "1" || getVal("isInService") === true,
        use_turning_point: getVal("useTurningPoint") === "1" || getVal("useTurningPoint") === true,
        instrument: {
            manufacturer: getVal("instManufacturer"),
            model: getVal("instModel"),
            serial_no: getVal("instSerial"),
            accuracy_class: getVal("instAccuracyClass") || "III",
            max_capacity: parseFloat(getVal("instMaxCapacity") || 0),
            min_capacity: parseFloat(getVal("instMinCapacity") || 0),
            e: parseFloat(getVal("instE") || 0),
            d: parseFloat(getVal("instD") || 0),
            unit: getVal("instUnit") || "kg",
            tare_max: parseFloat(getVal("instTareMax") || 0),
            device_type: getVal("instDeviceType") || "Standard Electronic Platform",
        },
        environment: {
            temp_c: parseFloat(getVal("envTemp") || 20),
            humidity_pct: parseFloat(getVal("envHumidity") || 50),
            pressure_hpa: parseFloat(getVal("envPressure") || 1013.25),
        },
        standards: {
            standards_id: getVal("stdWeightsId"),
            standards_cert: getVal("stdWeightsCert"),
        },
        zero_test: {
            indication: parseFloat(getVal("zeroIndication") || 0),
            delta_l: getVal("zeroDeltaL") !== "" ? parseFloat(getVal("zeroDeltaL")) : null,
        },
        tare_test: {
            tare_load: parseFloat(getVal("tareLoad") || 0),
            tare_indication: parseFloat(getVal("tareIndication") || 0),
            delta_l_tare: getVal("tareDeltaL") !== "" ? parseFloat(getVal("tareDeltaL")) : null,
            net_test_load: parseFloat(getVal("tareNetLoad") || 0),
            net_indication: parseFloat(getVal("tareNetIndication") || 0),
            delta_l_net: getVal("tareNetDeltaL") !== "" ? parseFloat(getVal("tareNetDeltaL")) : null,
        },
        eccentricity_test: {
            test_load: parseFloat(getVal("eccTestLoad") || 0),
            points: eccPoints,
        },
        repeatability_test: {
            series: repSeries,
        },
        weighing_test: {
            rows: weighingRows,
        },
    };
}

/* ==========================================================================
   Live Real-Time Calculations
   ========================================================================== */
function attachLiveCalculationListeners() {
    const form = document.getElementById("testForm");
    if (!form) return;

    form.addEventListener("input", () => triggerLiveCalculation());
    form.addEventListener("change", () => triggerLiveCalculation());

    const saveBtn = document.getElementById("btnSaveAndGeneratePDF");
    if (saveBtn) {
        saveBtn.addEventListener("click", () => handleSaveAndGeneratePDF());
    }
}

function triggerLiveCalculation() {
    if (calcDebounceTimer) clearTimeout(calcDebounceTimer);
    calcDebounceTimer = setTimeout(() => {
        performCalculation();
    }, 250);
}

async function performCalculation() {
    const payload = serializeForm();
    try {
        const response = await fetch("/api/calculate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        if (!response.ok) throw new Error("Calculation API failed");

        const result = await response.json();
        currentEvaluation = result;
        updateUIWithEvaluation(result, payload);
    } catch (err) {
        console.error("Live calculation error:", err);
    }
}

function updateUIWithEvaluation(res, payload) {
    const unit = payload.instrument.unit || "kg";

    // 1. Overall Status Pill Bar
    const statusPill = document.getElementById("overallStatusBadge");
    if (statusPill) {
        statusPill.className = `status-badge ${res.overall_status.toLowerCase()}`;
        statusPill.textContent = res.overall_status;
    }

    // Mini pill dots
    updatePillDot("pillZero", res.zero_test?.passed);
    updatePillDot("pillTare", res.tare_test?.passed);
    updatePillDot("pillWeigh", res.weighing_test?.passed);
    updatePillDot("pillRep", res.repeatability_test?.passed);
    updatePillDot("pillEcc", res.eccentricity_test?.passed);

    // 2. Instrument Verification Limits
    const nDisplay = document.getElementById("displayDivisionsN");
    if (nDisplay) {
        nDisplay.textContent = `${res.parameters.n.toLocaleString()} divisions`;
    }
    const minReqDisplay = document.getElementById("displayMinRequired");
    if (minReqDisplay) {
        minReqDisplay.textContent = `${res.parameters.required_min} ${unit}`;
    }

    const paramWarnings = document.getElementById("paramValidationMsg");
    if (paramWarnings) {
        if (!res.parameters.is_valid) {
            paramWarnings.className = "alert alert-danger";
            paramWarnings.style.display = "block";
            paramWarnings.innerHTML = res.parameters.errors.join("<br>");
        } else if (res.parameters.warnings.length > 0) {
            paramWarnings.className = "alert alert-warning";
            paramWarnings.style.display = "block";
            paramWarnings.innerHTML = res.parameters.warnings.join("<br>");
        } else {
            paramWarnings.style.display = "none";
        }
    }

    // 3. Zero Test Feedback
    const zeroFeedback = document.getElementById("zeroTestFeedback");
    if (zeroFeedback && res.zero_test) {
        const z = res.zero_test;
        zeroFeedback.innerHTML = `
            Zero Error E₀: <strong>${z.e0} ${unit}</strong> | 
            Max Allowed (0.25e): <strong>± ${z.max_allowed_error} ${unit}</strong> | 
            Status: <span class="badge ${z.passed ? 'badge-sih' : 'badge-danger'}">${z.status}</span>
        `;
    }

    // 4. Tare Test Feedback
    const tareFeedback = document.getElementById("tareTestFeedback");
    if (tareFeedback && res.tare_test) {
        const t = res.tare_test;
        tareFeedback.innerHTML = `
            Tare Balance Error: <strong>${t.e_tare} ${unit}</strong> (${t.tare_zero_passed ? 'PASS' : 'FAIL'}) | 
            Net Corrected Error (Ec): <strong>${t.e_net_corr} ${unit}</strong> | 
            Net MPE: <strong>± ${t.mpe_net} ${unit}</strong> | 
            Status: <span class="badge ${t.passed ? 'badge-sih' : 'badge-danger'}">${t.status}</span>
        `;
    }

    // 5. Eccentricity Feedback & Table
    const eccFeedback = document.getElementById("eccFeedback");
    if (eccFeedback && res.eccentricity_test) {
        const ecc = res.eccentricity_test;
        eccFeedback.innerHTML = `
            Test Load MPE: <strong>± ${ecc.mpe} ${unit}</strong> | 
            Max Error Spread Across Corners: <strong>${ecc.max_error_diff} ${unit}</strong> | 
            Result: <span class="badge ${ecc.passed ? 'badge-sih' : 'badge-danger'}">${ecc.status}</span>
        `;
    }

    (res.eccentricity_test?.points || []).forEach(pt => {
        const row = document.querySelector(`.ecc-row-${pt.position_id}`);
        if (row) {
            row.querySelector(".ecc-raw-err").textContent = `${pt.raw_error} ${unit}`;
            row.querySelector(".ecc-corr-err").textContent = `${pt.corrected_error} ${unit}`;
            row.querySelector(".ecc-mpe").textContent = `± ${pt.mpe} ${unit}`;
            const badge = row.querySelector(".ecc-status");
            badge.innerHTML = `<span class="badge ${pt.passed ? 'badge-sih' : 'badge-danger'}">${pt.status}</span>`;
        }
    });

    // 6. Repeatability Feedback & Table
    const repFeedback = document.getElementById("repFeedback");
    if (repFeedback && res.repeatability_test) {
        const rep = res.repeatability_test;
        repFeedback.innerHTML = `
            Overall Repeatability: <span class="badge ${rep.passed ? 'badge-sih' : 'badge-danger'}">${rep.status}</span>
        `;
    }

    const repTrs = document.querySelectorAll("#repeatabilityTableBody tr");
    (res.repeatability_test?.series || []).forEach((s, idx) => {
        const tr = repTrs[idx];
        if (tr) {
            tr.querySelector(".rep-imax").textContent = `${s.i_max} ${unit}`;
            tr.querySelector(".rep-imin").textContent = `${s.i_min} ${unit}`;
            tr.querySelector(".rep-delta").textContent = `${s.delta} ${unit}`;
            tr.querySelector(".rep-mpe").textContent = `± ${s.mpe} ${unit}`;
            tr.querySelector(".rep-status").innerHTML = `<span class="badge ${s.passed ? 'badge-sih' : 'badge-danger'}">${s.status}</span>`;
        }
    });

    // 7. Weighing Feedback & Table
    const weighFeedback = document.getElementById("weighFeedback");
    if (weighFeedback && res.weighing_test) {
        const w = res.weighing_test;
        weighFeedback.innerHTML = `
            Points Tested: <strong>${w.row_count}</strong> (Min 5 required) | 
            Max Hysteresis: <strong>${w.max_hysteresis} ${unit}</strong> | 
            Result: <span class="badge ${w.passed ? 'badge-sih' : 'badge-danger'}">${w.status}</span>
        `;
    }

    const weighTrs = document.querySelectorAll("#weighingTableBody tr");
    (res.weighing_test?.rows || []).forEach((row, idx) => {
        const tr = weighTrs[idx];
        if (tr) {
            tr.querySelector(".weigh-ec-inc").textContent = `${row.e_inc_corr} ${unit}`;
            tr.querySelector(".weigh-ec-dec").textContent = row.e_dec_corr !== null ? `${row.e_dec_corr} ${unit}` : "—";
            tr.querySelector(".weigh-hyst").textContent = row.hysteresis !== null ? `${row.hysteresis} ${unit}` : "—";
            tr.querySelector(".weigh-mpe").textContent = `± ${row.mpe} ${unit}`;
            tr.querySelector(".weigh-status").innerHTML = `<span class="badge ${row.passed ? 'badge-sih' : 'badge-danger'}">${row.status}</span>`;
        }
    });

    // 8. Review Tab Summary Table
    const reviewTbody = document.getElementById("reviewSummaryBody");
    if (reviewTbody && res.summary) {
        reviewTbody.innerHTML = "";
        res.summary.forEach(item => {
            const tr = document.createElement("tr");
            const isPass = item.status === "PASS";
            tr.innerHTML = `
                <td><strong>${item.test}</strong></td>
                <td>Conforms to OIML R-76-1:2006 (E)</td>
                <td><span class="badge ${isPass ? 'badge-sih' : 'badge-danger'}">${item.status}</span></td>
            `;
            reviewTbody.appendChild(tr);
        });

        const certStatus = document.getElementById("reviewOverallCertBadge");
        if (certStatus) {
            certStatus.className = `cert-status-badge ${res.overall_status.toLowerCase()}`;
            certStatus.textContent = `FINAL VERDICT: ${res.overall_status}`;
        }
    }
}

function updatePillDot(elementId, passed) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.className = `pill-dot ${passed ? 'pass' : (passed === false ? 'fail' : 'neutral')}`;
}

/* ==========================================================================
   Save to SQLite & ReportLab PDF Generation
   ========================================================================== */
async function handleSaveAndGeneratePDF() {
    const saveBtn = document.getElementById("btnSaveAndGeneratePDF");
    const originalText = saveBtn.innerHTML;
    saveBtn.disabled = true;
    saveBtn.innerHTML = `<span>Compiling ReportLab PDF...</span>`;

    const payload = serializeForm();

    try {
        const response = await fetch("/api/reports", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) throw new Error("Failed to save report and compile PDF");

        const data = await response.json();
        
        // Show success alert card
        const resultCard = document.getElementById("generationSuccessCard");
        if (resultCard) {
            resultCard.style.display = "block";
            document.getElementById("savedReportId").textContent = data.report_id;
            document.getElementById("btnViewWebReport").href = data.report_url;
            document.getElementById("btnDownloadPDF").href = `${data.pdf_url}?download=1`;
            document.getElementById("btnPreviewPDF").href = data.pdf_url;
        }

        // Switch to Review Tab
        switchTab("tabReview");
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // Trigger PDF opening in background/new tab
        window.open(data.pdf_url, "_blank");

    } catch (err) {
        alert("Error saving test report or compiling PDF: " + err.message);
    } finally {
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;
    }
}
