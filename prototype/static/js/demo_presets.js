/**
 * Pre-configured Metrological Demo Presets for NAWI Verification (OIML R-76)
 * Ideal for live demonstration during SIH / College evaluation.
 */

const DEMO_PRESETS = {
    retail_class3: {
        name: "Class III Retail Scale (15 kg / 5 g)",
        certificate_no: "CERT-2026-RET-0192",
        test_date: new Date().toISOString().split("T")[0],
        inspector_name: "Er. R. Sharma (Senior Metrologist)",
        customer_name: "Fresh Mart Hypermarket Ltd",
        location: "Central Inspection Bay #2, Mumbai",
        is_in_service: false,
        use_turning_point: true,
        instrument: {
            manufacturer: "Mettler Toledo / Avery",
            model: "bRite Standard Retail NAWI",
            serial_no: "BR-2026-88341",
            accuracy_class: "III",
            max_capacity: 15.0,
            min_capacity: 0.1,
            e: 0.005,
            d: 0.005,
            unit: "kg",
            tare_max: 5.0,
            device_type: "Electronic Counter-Top Scale"
        },
        environment: {
            temp_c: 22.0,
            humidity_pct: 52.0,
            pressure_hpa: 1012.5
        },
        standards: {
            standards_id: "OIML Class M1 Standard Weights (1g - 20kg)",
            standards_cert: "NABL-CAL-2026-00912"
        },
        zero_test: {
            indication: 0.0,
            delta_l: 0.0025
        },
        tare_test: {
            tare_load: 2.0,
            tare_indication: 2.0,
            delta_l_tare: 0.0025,
            net_test_load: 5.0,
            net_indication: 5.0,
            delta_l_net: 0.0025
        },
        eccentricity_test: {
            test_load: 5.0,
            points: [
                { position_id: 1, position_name: "Center (1)", indication: 5.000, delta_l: 0.0025 },
                { position_id: 2, position_name: "Front-Left (2)", indication: 5.000, delta_l: 0.0020 },
                { position_id: 3, position_name: "Back-Left (3)", indication: 5.000, delta_l: 0.0030 },
                { position_id: 4, position_name: "Back-Right (4)", indication: 5.000, delta_l: 0.0025 },
                { position_id: 5, position_name: "Front-Right (5)", indication: 5.000, delta_l: 0.0025 }
            ]
        },
        repeatability_test: {
            series: [
                { load: 7.5, readings: [7.500, 7.500, 7.505] },
                { load: 15.0, readings: [15.000, 15.005, 15.000] }
            ]
        },
        weighing_test: {
            rows: [
                { load: 0.1, i_inc: 0.100, delta_l_inc: 0.0025, i_dec: 0.100, delta_l_dec: 0.0025 },
                { load: 2.5, i_inc: 2.500, delta_l_inc: 0.0025, i_dec: 2.500, delta_l_dec: 0.0025 },
                { load: 5.0, i_inc: 5.000, delta_l_inc: 0.0025, i_dec: 5.000, delta_l_dec: 0.0025 },
                { load: 10.0, i_inc: 10.000, delta_l_inc: 0.0025, i_dec: 10.000, delta_l_dec: 0.0025 },
                { load: 15.0, i_inc: 15.000, delta_l_inc: 0.0025, i_dec: 15.000, delta_l_dec: 0.0025 }
            ]
        }
    },
    lab_balance_class2: {
        name: "Class II Analytical Balance (220 g / 0.001 g)",
        certificate_no: "CERT-2026-LAB-0431",
        test_date: new Date().toISOString().split("T")[0],
        inspector_name: "Dr. Ananya Sen (Principal Metrologist)",
        customer_name: "Advanced Pharma Analytics R&D",
        location: "Cleanroom Lab Alpha, Bengaluru",
        is_in_service: false,
        use_turning_point: true,
        instrument: {
            manufacturer: "Sartorius / Shimadzu",
            model: "Secura 225D High Precision Balance",
            serial_no: "SEC-992014-K",
            accuracy_class: "II",
            max_capacity: 220.0,
            min_capacity: 0.02,
            e: 0.001,
            d: 0.0001,
            unit: "g",
            tare_max: 220.0,
            device_type: "Precision Laboratory Balance"
        },
        environment: {
            temp_c: 20.2,
            humidity_pct: 45.0,
            pressure_hpa: 1013.0
        },
        standards: {
            standards_id: "OIML Class E2 Reference Weights Set (1mg - 500g)",
            standards_cert: "NPLI-CAL-2026-1188"
        },
        zero_test: {
            indication: 0.0,
            delta_l: 0.0005
        },
        tare_test: {
            tare_load: 50.0,
            tare_indication: 50.0,
            delta_l_tare: 0.0005,
            net_test_load: 100.0,
            net_indication: 100.0,
            delta_l_net: 0.0005
        },
        eccentricity_test: {
            test_load: 70.0,
            points: [
                { position_id: 1, position_name: "Center (1)", indication: 70.000, delta_l: 0.0005 },
                { position_id: 2, position_name: "Front-Left (2)", indication: 70.000, delta_l: 0.0004 },
                { position_id: 3, position_name: "Back-Left (3)", indication: 70.000, delta_l: 0.0006 },
                { position_id: 4, position_name: "Back-Right (4)", indication: 70.000, delta_l: 0.0005 },
                { position_id: 5, position_name: "Front-Right (5)", indication: 70.000, delta_l: 0.0005 }
            ]
        },
        repeatability_test: {
            series: [
                { load: 100.0, readings: [100.000, 100.001, 100.000, 100.000] },
                { load: 200.0, readings: [200.000, 200.001, 200.001, 200.000] }
            ]
        },
        weighing_test: {
            rows: [
                { load: 0.02, i_inc: 0.020, delta_l_inc: 0.0005, i_dec: 0.020, delta_l_dec: 0.0005 },
                { load: 5.0, i_inc: 5.000, delta_l_inc: 0.0005, i_dec: 5.000, delta_l_dec: 0.0005 },
                { load: 20.0, i_inc: 20.000, delta_l_inc: 0.0005, i_dec: 20.000, delta_l_dec: 0.0005 },
                { load: 100.0, i_inc: 100.000, delta_l_inc: 0.0005, i_dec: 100.000, delta_l_dec: 0.0005 },
                { load: 220.0, i_inc: 220.000, delta_l_inc: 0.0005, i_dec: 220.000, delta_l_dec: 0.0005 }
            ]
        }
    },
    industrial_class3: {
        name: "Class III Industrial Platform Scale (60 kg / 20 g)",
        certificate_no: "CERT-2026-IND-7719",
        test_date: new Date().toISOString().split("T")[0],
        inspector_name: "K. Patel (Legal Metrology Officer)",
        customer_name: "National Cargo & Freight Hub",
        location: "Warehouse Terminal 4, Gujarat",
        is_in_service: false,
        use_turning_point: true,
        instrument: {
            manufacturer: "Essae / Sansui",
            model: "DS-215 Heavy Industrial Floor NAWI",
            serial_no: "IND-60K-004481",
            accuracy_class: "III",
            max_capacity: 60.0,
            min_capacity: 0.4,
            e: 0.02,
            d: 0.02,
            unit: "kg",
            tare_max: 20.0,
            device_type: "Industrial Floor/Platform Scale"
        },
        environment: {
            temp_c: 24.5,
            humidity_pct: 58.0,
            pressure_hpa: 1009.0
        },
        standards: {
            standards_id: "OIML Class M1 Cast Iron Weights (5kg, 10kg, 20kg)",
            standards_cert: "W&M-IND-2026-9011"
        },
        zero_test: {
            indication: 0.0,
            delta_l: 0.010
        },
        tare_test: {
            tare_load: 10.0,
            tare_indication: 10.0,
            delta_l_tare: 0.010,
            net_test_load: 20.0,
            net_indication: 20.0,
            delta_l_net: 0.010
        },
        eccentricity_test: {
            test_load: 20.0,
            points: [
                { position_id: 1, position_name: "Center (1)", indication: 20.00, delta_l: 0.010 },
                { position_id: 2, position_name: "Front-Left (2)", indication: 20.00, delta_l: 0.008 },
                { position_id: 3, position_name: "Back-Left (3)", indication: 20.00, delta_l: 0.012 },
                { position_id: 4, position_name: "Back-Right (4)", indication: 20.00, delta_l: 0.010 },
                { position_id: 5, position_name: "Front-Right (5)", indication: 20.00, delta_l: 0.010 }
            ]
        },
        repeatability_test: {
            series: [
                { load: 30.0, readings: [30.00, 30.02, 30.00] },
                { load: 60.0, readings: [60.00, 60.02, 60.00] }
            ]
        },
        weighing_test: {
            rows: [
                { load: 0.4, i_inc: 0.40, delta_l_inc: 0.010, i_dec: 0.40, delta_l_dec: 0.010 },
                { load: 10.0, i_inc: 10.00, delta_l_inc: 0.010, i_dec: 10.00, delta_l_dec: 0.010 },
                { load: 20.0, i_inc: 20.00, delta_l_inc: 0.010, i_dec: 20.00, delta_l_dec: 0.010 },
                { load: 40.0, i_inc: 40.00, delta_l_inc: 0.010, i_dec: 40.00, delta_l_dec: 0.010 },
                { load: 60.0, i_inc: 60.00, delta_l_inc: 0.010, i_dec: 60.00, delta_l_dec: 0.010 }
            ]
        }
    },
    failing_scale: {
        name: "Out-of-Tolerance / Failing Scale (Demo)",
        certificate_no: "REJECT-2026-FAIL-0012",
        test_date: new Date().toISOString().split("T")[0],
        inspector_name: "Er. R. Sharma (Metrology Inspector)",
        customer_name: "Quality Audit Demo Agency",
        location: "Fault Testing Workbench",
        is_in_service: false,
        use_turning_point: true,
        instrument: {
            manufacturer: "Unbranded Mechanical-Electronic Hybrid",
            model: "Old 30K Industrial",
            serial_no: "DEFECT-9092-X",
            accuracy_class: "III",
            max_capacity: 30.0,
            min_capacity: 0.2,
            e: 0.01,
            d: 0.01,
            unit: "kg",
            tare_max: 10.0,
            device_type: "Worn Platform Scale"
        },
        environment: {
            temp_c: 28.0,
            humidity_pct: 70.0,
            pressure_hpa: 1010.0
        },
        standards: {
            standards_id: "OIML Class M1 Standard Weights",
            standards_cert: "NABL-CAL-2026-00912"
        },
        zero_test: {
            indication: 0.0,
            delta_l: 0.005
        },
        tare_test: {
            tare_load: 5.0,
            tare_indication: 5.0,
            delta_l_tare: 0.005,
            net_test_load: 10.0,
            net_indication: 10.0,
            delta_l_net: 0.005
        },
        eccentricity_test: {
            test_load: 10.0,
            points: [
                { position_id: 1, position_name: "Center (1)", indication: 10.00, delta_l: 0.005 },
                { position_id: 2, position_name: "Front-Left (2 - Corner Binding)", indication: 10.04, delta_l: 0.005 },
                { position_id: 3, position_name: "Back-Left (3)", indication: 10.00, delta_l: 0.005 },
                { position_id: 4, position_name: "Back-Right (4)", indication: 10.00, delta_l: 0.005 },
                { position_id: 5, position_name: "Front-Right (5)", indication: 10.00, delta_l: 0.005 }
            ]
        },
        repeatability_test: {
            series: [
                { load: 15.0, readings: [15.00, 15.01, 15.00] },
                { load: 30.0, readings: [30.00, 30.03, 29.98] }
            ]
        },
        weighing_test: {
            rows: [
                { load: 0.2, i_inc: 0.20, delta_l_inc: 0.005, i_dec: 0.20, delta_l_dec: 0.005 },
                { load: 5.0, i_inc: 5.00, delta_l_inc: 0.005, i_dec: 5.00, delta_l_dec: 0.005 },
                { load: 10.0, i_inc: 10.00, delta_l_inc: 0.005, i_dec: 10.00, delta_l_dec: 0.005 },
                { load: 20.0, i_inc: 20.02, delta_l_inc: 0.005, i_dec: 20.02, delta_l_dec: 0.005 },
                { load: 30.0, i_inc: 30.04, delta_l_inc: 0.005, i_dec: 30.05, delta_l_dec: 0.005 }
            ]
        }
    }
};
