-- ============================================================
-- Research Cohort Explorer
-- Analytical View: Encounters
-- ============================================================

CREATE OR REPLACE VIEW vw_encounters AS
SELECT
    e.encounter_id,
    e.patient_id,
    p.research_id,
    e.encounter_date,
    e.encounter_type_code,
    et.description AS encounter_type_description,
    et.category AS encounter_category,
    e.facility_id,
    f.facility_code,
    f.facility_name,
    f.facility_type,
    f.city AS facility_city,
    f.state AS facility_state,
    e.provider_id,
    pr.provider_code,
    pr.provider_type,
    pr.specialty AS provider_specialty,
    e.discharge_date
FROM encounters e
JOIN patients p
    ON p.patient_id = e.patient_id
JOIN encounter_types et
    ON et.encounter_type_code = e.encounter_type_code
LEFT JOIN facilities f
    ON f.facility_id = e.facility_id
LEFT JOIN providers pr
    ON pr.provider_id = e.provider_id;
