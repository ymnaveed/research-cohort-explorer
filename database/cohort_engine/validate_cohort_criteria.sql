-- ============================================================
-- Research Cohort Explorer
-- Cohort Engine: Validate Cohort Criteria
-- ============================================================

WITH criterion_validation AS (
    SELECT
        cc.cohort_definition_id,
        cc.cohort_criterion_id,
        w.criterion_whitelist_id,
        CASE
            WHEN w.criterion_whitelist_id IS NULL THEN FALSE
            WHEN w.value_type = 'text' THEN TRUE
            WHEN w.value_type = 'integer' THEN
                pg_input_is_valid(cc.value_text, 'integer')
            WHEN w.value_type = 'numeric' THEN
                pg_input_is_valid(cc.value_text, 'numeric')
            WHEN w.value_type = 'date' THEN
                pg_input_is_valid(cc.value_text, 'date')
            ELSE FALSE
        END AS value_is_valid
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
    COUNT(criterion_whitelist_id) AS supported_criteria,
    COUNT(*) - COUNT(criterion_whitelist_id) AS unsupported_criteria,
    COUNT(*) FILTER (
        WHERE criterion_whitelist_id IS NOT NULL
          AND value_is_valid
    ) AS valid_value_criteria,
    COUNT(*) FILTER (
        WHERE criterion_whitelist_id IS NOT NULL
          AND NOT value_is_valid
    ) AS invalid_value_criteria,
    CASE
        WHEN COUNT(*) > 0
         AND COUNT(*) = COUNT(criterion_whitelist_id)
         AND COUNT(*) FILTER (WHERE value_is_valid) = COUNT(*)
            THEN 'valid'
        ELSE 'invalid'
    END AS validation_status
FROM criterion_validation
GROUP BY cohort_definition_id;
