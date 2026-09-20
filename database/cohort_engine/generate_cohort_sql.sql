-- ============================================================
-- Research Cohort Explorer
-- Cohort Engine: Generate Complete Cohort SQL
-- ============================================================
-- Current supported semantics:
--   1. Inclusion criteria support demographics and diagnoses
--   2. Inclusion criteria are combined with AND
--   3. Demographic inclusions are evaluated on the patient anchor row
--   4. Diagnosis inclusions are evaluated on the same diagnosis row
--      inside a correlated EXISTS subquery
--   5. Diagnosis exclusions are supported
--   6. Each diagnosis exclusion is evaluated independently through
--      its own correlated NOT EXISTS subquery
--   7. Demographic exclusions are not currently supported
--   8. SQL is generated only when every stored criterion is
--      supported and has a valid typed value
--
-- This script generates SQL text only. It does not execute it.
-- ============================================================

WITH validation AS (
    SELECT
        COUNT(*) AS total_criteria,
        COUNT(w.criterion_whitelist_id) AS supported_criteria,
        COUNT(*) FILTER (
            WHERE w.criterion_whitelist_id IS NOT NULL
              AND cc.criterion_type IN ('inclusion', 'exclusion')
              AND (
                    cc.criterion_type = 'inclusion'
                    OR (
                        cc.criterion_type = 'exclusion'
                        AND w.source_view = 'vw_diagnoses'
                    )
                  )
              AND w.source_view IN (
                    'vw_patient_demographics',
                    'vw_diagnoses'
                  )
              AND CASE
                    WHEN w.value_type = 'text' THEN TRUE
                    WHEN w.value_type = 'integer' THEN
                        pg_input_is_valid(cc.value_text, 'integer')
                    WHEN w.value_type = 'numeric' THEN
                        pg_input_is_valid(cc.value_text, 'numeric')
                    WHEN w.value_type = 'date' THEN
                        pg_input_is_valid(cc.value_text, 'date')
                    ELSE FALSE
                  END
        ) AS valid_value_criteria
    FROM cohort_criteria cc
    LEFT JOIN cohort_criterion_whitelist w
        ON w.domain = cc.domain
       AND w.field_name = cc.field_name
       AND w.operator = cc.operator
    WHERE cc.cohort_definition_id = :'cohort_id'
),
generated_predicates AS (
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
    CROSS JOIN validation v
    WHERE cc.cohort_definition_id = :'cohort_id'
      AND v.total_criteria = v.supported_criteria
      AND v.total_criteria = v.valid_value_criteria
      AND v.total_criteria > 0
),
demographics_group AS (
    SELECT
        string_agg(
            sql_predicate,
            ' AND '
            ORDER BY criterion_order
        ) AS predicates
    FROM generated_predicates
    WHERE criterion_type = 'inclusion'
      AND source_view = 'vw_patient_demographics'
),
diagnosis_group AS (
    SELECT
        string_agg(
            sql_predicate,
            ' AND '
            ORDER BY criterion_order
        ) AS predicates
    FROM generated_predicates
    WHERE criterion_type = 'inclusion'
      AND source_view = 'vw_diagnoses'
),
diagnosis_exclusions AS (
    SELECT
        string_agg(
            format(
                ' AND NOT EXISTS (SELECT 1 FROM vw_diagnoses d WHERE d.patient_id = p.patient_id AND %s)',
                sql_predicate
            ),
            ''
            ORDER BY criterion_order
        ) AS predicates
    FROM generated_predicates
    WHERE criterion_type = 'exclusion'
      AND source_view = 'vw_diagnoses'
)
SELECT
    format(
        'SELECT p.patient_id FROM vw_patient_demographics p WHERE %s AND EXISTS (SELECT 1 FROM vw_diagnoses d WHERE d.patient_id = p.patient_id AND %s)%s;',
        demographics_group.predicates,
        diagnosis_group.predicates,
        COALESCE(
            diagnosis_exclusions.predicates,
            ''
        )
    ) AS generated_sql
FROM demographics_group
CROSS JOIN diagnosis_group
CROSS JOIN diagnosis_exclusions
WHERE demographics_group.predicates IS NOT NULL
  AND diagnosis_group.predicates IS NOT NULL;