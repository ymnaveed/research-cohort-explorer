-- ============================================================
-- Research Cohort Explorer
-- Analytical View: Medication Orders
-- ============================================================

CREATE OR REPLACE VIEW vw_medication_orders AS
SELECT
    m.medication_order_id,
    m.patient_id,
    p.research_id,
    m.encounter_id,
    m.medication_code,
    mc.medication_name,
    mc.medication_class,
    m.order_date,
    m.start_date,
    m.end_date,
    m.dose,
    m.route,
    m.status
FROM medication_orders m
JOIN patients p
    ON p.patient_id = m.patient_id
JOIN medication_codes mc
    ON mc.medication_code = m.medication_code;
