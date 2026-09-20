-- ============================================================
-- Research Cohort Explorer
-- Cohort Engine: Generate Criterion SQL
-- ============================================================

SELECT
    cc.criterion_order,
    cc.criterion_type,
    cc.domain,
    cc.field_name,
    cc.operator,
    cc.value_text,
    w.source_view,
    w.source_alias,
    w.source_column,
    w.value_type,
    CASE
        WHEN w.value_type = 'text' THEN
            format('%I.%I %s %L', w.source_alias, w.source_column, w.operator, cc.value_text)

        WHEN w.value_type = 'integer' THEN
            format('%I.%I %s %L::INTEGER', w.source_alias, w.source_column, w.operator, cc.value_text)

        WHEN w.value_type = 'numeric' THEN
            format('%I.%I %s %L::NUMERIC', w.source_alias, w.source_column, w.operator, cc.value_text)

        WHEN w.value_type = 'date' THEN
            format('%I.%I %s %L::DATE', w.source_alias, w.source_column, w.operator, cc.value_text)
    END AS sql_predicate
FROM cohort_criteria cc
JOIN cohort_criterion_whitelist w
    ON w.domain = cc.domain
   AND w.field_name = cc.field_name
   AND w.operator = cc.operator
WHERE cc.cohort_definition_id = :'cohort_id'
ORDER BY cc.criterion_order;
