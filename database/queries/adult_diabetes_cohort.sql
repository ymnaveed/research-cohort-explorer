-- ============================================================
-- Research Cohort Explorer
-- Cohort: Adult patients with Type 2 diabetes
-- ============================================================

SELECT
    p.research_id,
    p.date_of_birth,
    p.sex,
    p.race,
    p.ethnicity,
    d.diagnosis_code,
    dc.description AS diagnosis_description,
    MIN(d.recorded_date) AS first_diabetes_recorded_date
FROM patients p
JOIN diagnoses d
    ON d.patient_id = p.patient_id
JOIN diagnosis_codes dc
    ON dc.diagnosis_code = d.diagnosis_code
WHERE d.diagnosis_code = 'E11.9'
  AND p.date_of_birth <= DATE '2025-12-31' - INTERVAL '18 years'
  AND d.recorded_date BETWEEN DATE '2015-01-01' AND DATE '2025-12-31'
GROUP BY
    p.research_id,
    p.date_of_birth,
    p.sex,
    p.race,
    p.ethnicity,
    d.diagnosis_code,
    dc.description
ORDER BY
    p.research_id;
