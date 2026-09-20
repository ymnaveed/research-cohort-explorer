-- ============================================================
-- Research Cohort Explorer
-- Analytical View: Procedures
-- ============================================================

CREATE OR REPLACE VIEW vw_procedures AS
SELECT
    pr.procedure_id,
    pr.patient_id,
    p.research_id,
    pr.encounter_id,
    pr.procedure_code,
    pc.procedure_name,
    pc.category AS procedure_category,
    pr.procedure_date
FROM procedures pr
JOIN patients p
    ON p.patient_id = pr.patient_id
JOIN procedure_codes pc
    ON pc.procedure_code = pr.procedure_code;
