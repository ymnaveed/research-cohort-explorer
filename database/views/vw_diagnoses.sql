-- ============================================================
-- Research Cohort Explorer
-- Analytical View: Diagnoses
-- ============================================================

CREATE OR REPLACE VIEW vw_diagnoses AS
SELECT
    d.diagnosis_id,
    d.patient_id,
    p.research_id,
    d.encounter_id,
    d.diagnosis_code,
    dc.description AS diagnosis_description,
    dc.category AS diagnosis_category,
    d.onset_date,
    d.recorded_date,
    d.diagnosis_type
FROM diagnoses d
JOIN patients p
    ON p.patient_id = d.patient_id
JOIN diagnosis_codes dc
    ON dc.diagnosis_code = d.diagnosis_code;
