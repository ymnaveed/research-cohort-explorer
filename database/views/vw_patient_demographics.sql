-- ============================================================
-- Research Cohort Explorer
-- Analytical View: Patients
-- ============================================================

CREATE OR REPLACE VIEW vw_patient_demographics AS
SELECT
    p.patient_id,
    p.research_id,
    p.date_of_birth,
    p.sex,
    p.race,
    p.ethnicity,
    p.zip3,
    p.death_date,
    EXTRACT(
        YEAR FROM AGE(DATE '2025-12-31', p.date_of_birth)
    )::INTEGER AS age_at_study_end
FROM patients p;
