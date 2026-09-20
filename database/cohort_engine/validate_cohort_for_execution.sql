-- ============================================================
-- Research Cohort Explorer
-- Cohort Engine: Validate Cohort for Execution
-- ============================================================

WITH criterion_validation AS (
    SELECT
        cc.cohort_definition_id,
        cc.criterion_type,
        cc.cohort_criterion_id,
        w.criterion_whitelist_id,
        w.source_view,
        CASE
            WHEN w.criterion_whitelist_id IS NULL THEN FALSE
            WHEN cc.criterion_type <> 'inclusion' THEN FALSE
            WHEN w.source_view NOT IN (
                'vw_patient_demographics',
                'vw_diagnoses'
            ) THEN FALSE
            WHEN w.value_type = 'text' THEN TRUE
            WHEN w.value_type = 'integer' THEN
                pg_input_is_valid(cc.value_text, 'integer')
            WHEN w.value_type = 'numeric' THEN
                pg_input_is_valid(cc.value_text, 'numeric')
            WHEN w.value_type = 'date' THEN
                pg_input_is_valid(cc.value_text, 'date')
            ELSE FALSE
        END AS criterion_is_valid
    FROM cohort_criteria cc
    LEFT JOIN cohort_criterion_whitelist w
        ON w.domain = cc.domain
       AND w.field_name = cc.field_name
       AND w.operator = cc.operator
    WHERE cc.cohort_definition_id = :'cohort_id'
)
SELECT
    cohort_definition_id,
    COUNT(*) AS total_criteria,
    COUNT(*) FILTER (
        WHERE criterion_is_valid
    ) AS valid_criteria,
    COUNT(*) FILTER (
        WHERE NOT criterion_is_valid
    ) AS invalid_criteria,
    CASE
        WHEN COUNT(*) > 0
         AND COUNT(*) FILTER (WHERE criterion_is_valid) = COUNT(*)
            THEN 'ready'
        ELSE 'blocked'
    END AS execution_status
FROM criterion_validation
GROUP BY cohort_definition_id;
