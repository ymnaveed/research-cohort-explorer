-- ============================================================
-- Research Cohort Explorer
-- Analytical View: Clinical Notes
-- ============================================================

CREATE OR REPLACE VIEW vw_clinical_notes AS
SELECT
    n.note_id,
    n.patient_id,
    p.research_id,
    n.encounter_id,
    n.note_date,
    n.note_type_code,
    nt.description AS note_type_description,
    nt.category AS note_category,
    n.note_text
FROM clinical_notes n
JOIN patients p
    ON p.patient_id = n.patient_id
JOIN note_types nt
    ON nt.note_type_code = n.note_type_code;
