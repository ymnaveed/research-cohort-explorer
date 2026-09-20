-- ============================================================
-- Research Cohort Explorer
-- Cohort Engine: Generate Complete Cohort SQL
-- ============================================================
-- Current supported semantics:
--   1. Inclusion criteria only
--   2. All criteria combined with AND
--   3. Demographics evaluated on the patient anchor row
--   4. Diagnosis criteria evaluated on the same diagnosis row
--      inside a correlated EXISTS subquery
--
-- This script generates SQL text only. It does not execute it.
-- ============================================================

WITH generated_predicates AS (
    SELECT
        cc.criterion_order,
        cc.criterion_type,
        w.source_view,
        w.source_alias,
        CASE
            WHEN w.value_type = 'text' THEN
                format(
                    '%I.%I %s %L',
                    w.source_alias,
                    w.source_column,
                    w.operator,
                    cc.value_text
                )

            WHEN w.value_type = 'integer' THEN
                format(
                    '%I.%I %s %L::INTEGER',
                    w.source_alias,
                    w.source_column,
                    w.operator,
                    cc.value_text
                )

            WHEN w.value_type = 'numeric' THEN
                format(
                    '%I.%I %s %L::NUMERIC',
                    w.source_alias,
                    w.source_column,
                    w.operator,
                    cc.value_text
                )

            WHEN w.value_type = 'date' THEN
                format(
                    '%I.%I %s %L::DATE',
                    w.source_alias,
                    w.source_column,
                    w.operator,
                    cc.value_text
                )
        END AS sql_predicate
    FROM cohort_criteria cc
    JOIN cohort_criterion_whitelist w
        ON w.domain = cc.domain
       AND w.field_name = cc.field_name
       AND w.operator = cc.operator
    WHERE cc.cohort_definition_id = :'cohort_id'
      AND cc.criterion_type = 'inclusion'
),
demographics_group AS (
    SELECT
        string_agg(
            sql_predicate,
            ' AND '
            ORDER BY criterion_order
        ) AS predicates
    FROM generated_predicates
    WHERE source_view = 'vw_patient_demographics'
),
diagnosis_group AS (
    SELECT
        string_agg(
            sql_predicate,
            ' AND '
            ORDER BY criterion_order
        ) AS predicates
    FROM generated_predicates
    WHERE source_view = 'vw_diagnoses'
)
SELECT
    format(
        'SELECT p.patient_id FROM vw_patient_demographics p WHERE %s AND EXISTS (SELECT 1 FROM vw_diagnoses d WHERE d.patient_id = p.patient_id AND %s);',
        demographics_group.predicates,
        diagnosis_group.predicates
    ) AS generated_sql
FROM demographics_group
CROSS JOIN diagnosis_group;
