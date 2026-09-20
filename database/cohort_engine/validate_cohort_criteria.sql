-- ============================================================
-- Research Cohort Explorer
-- Cohort Engine: Validate Cohort Criteria
-- ============================================================

SELECT
    cc.cohort_definition_id,
    COUNT(*) AS total_criteria,
    COUNT(w.criterion_whitelist_id) AS supported_criteria,
    COUNT(*) - COUNT(w.criterion_whitelist_id) AS unsupported_criteria,
    CASE
        WHEN COUNT(*) = COUNT(w.criterion_whitelist_id)
            THEN 'valid'
        ELSE 'invalid'
    END AS validation_status
FROM cohort_criteria cc
LEFT JOIN cohort_criterion_whitelist w
    ON w.domain = cc.domain
   AND w.field_name = cc.field_name
   AND w.operator = cc.operator
WHERE cc.cohort_definition_id = :'cohort_id'
GROUP BY cc.cohort_definition_id;
