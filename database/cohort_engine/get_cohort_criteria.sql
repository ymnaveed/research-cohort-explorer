-- ============================================================
-- Research Cohort Explorer
-- Cohort Engine: Retrieve Structured Cohort Criteria
-- ============================================================

SELECT
    cd.cohort_definition_id,
    cd.cohort_name,
    cd.study_start_date,
    cd.study_end_date,
    cc.criterion_order,
    cc.criterion_type,
    cc.domain,
    cc.field_name,
    cc.operator,
    cc.value_text
FROM cohort_definitions cd
JOIN cohort_criteria cc
    ON cc.cohort_definition_id = cd.cohort_definition_id
WHERE cd.cohort_definition_id = :'cohort_id'
ORDER BY cc.criterion_order;
