-- ============================================================
-- Research Cohort Explorer
-- Analytical View: Laboratory Results
-- ============================================================

CREATE OR REPLACE VIEW vw_lab_results AS
SELECT
    l.lab_result_id,
    l.patient_id,
    p.research_id,
    l.encounter_id,
    l.test_code,
    lt.test_name,
    lt.default_unit,
    l.result_numeric,
    l.result_text,
    l.unit,
    l.result_date
FROM lab_results l
JOIN patients p
    ON p.patient_id = l.patient_id
JOIN lab_tests lt
    ON lt.test_code = l.test_code;
