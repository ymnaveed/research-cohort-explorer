-- ============================================================
-- Research Cohort Explorer
-- Cohort Engine: Execute Cohort
-- ============================================================
-- Current supported semantics:
--   1. Inclusion criteria only
--   2. All criteria combined with AND
--   3. Demographics evaluated on the patient anchor row
--   4. Diagnosis criteria evaluated on the same diagnosis row
--      inside a correlated EXISTS subquery
--   5. Only whitelist-supported criteria with valid typed values
--      are executable
--
-- This script generates a controlled execution statement.
-- It does not accept arbitrary SQL as an input.
-- ============================================================

WITH criterion_validation AS (
    SELECT
        cc.cohort_definition_id,
        cc.criterion_order,
        cc.criterion_type,
        w.criterion_whitelist_id,
        w.source_view,
        w.source_alias,
        w.source_column,
        w.operator,
        w.value_type,
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
        END AS criterion_is_valid,
        cc.value_text
    FROM cohort_criteria cc
    LEFT JOIN cohort_criterion_whitelist w
        ON w.domain = cc.domain
       AND w.field_name = cc.field_name
       AND w.operator = cc.operator
    WHERE cc.cohort_definition_id = :'cohort_id'
),
validated AS (
    SELECT
        COUNT(*) AS total_criteria,
        COUNT(*) FILTER (
            WHERE criterion_is_valid
        ) AS valid_criteria
    FROM criterion_validation
),
generated_predicates AS (
    SELECT
        cv.criterion_order,
        cv.source_view,
        CASE
            WHEN cv.value_type = 'text' THEN
                format(
                    '%I.%I %s %L',
                    cv.source_alias,
                    cv.source_column,
                    cv.operator,
                    cv.value_text
                )

            WHEN cv.value_type = 'integer' THEN
                format(
                    '%I.%I %s %L::INTEGER',
                    cv.source_alias,
                    cv.source_column,
                    cv.operator,
                    cv.value_text
                )

            WHEN cv.value_type = 'numeric' THEN
                format(
                    '%I.%I %s %L::NUMERIC',
                    cv.source_alias,
                    cv.source_column,
                    cv.operator,
                    cv.value_text
                )

            WHEN cv.value_type = 'date' THEN
                format(
                    '%I.%I %s %L::DATE',
                    cv.source_alias,
                    cv.source_column,
                    cv.operator,
                    cv.value_text
                )
        END AS sql_predicate
    FROM criterion_validation cv
    CROSS JOIN validated v
    WHERE cv.criterion_is_valid
      AND v.total_criteria > 0
      AND v.total_criteria = v.valid_criteria
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
        'BEGIN; INSERT INTO cohort_execution_log (cohort_definition_id, cohort_version, status) SELECT cd.cohort_definition_id, cd.version, ''running'' FROM cohort_definitions cd WHERE cd.cohort_definition_id = %s; DELETE FROM cohort_membership WHERE cohort_definition_id = %s; INSERT INTO cohort_membership (cohort_definition_id, patient_id) SELECT %s, p.patient_id FROM vw_patient_demographics p WHERE %s AND EXISTS (SELECT 1 FROM vw_diagnoses d WHERE d.patient_id = p.patient_id AND %s); UPDATE cohort_execution_log SET completed_at = CURRENT_TIMESTAMP, status = ''succeeded'', member_count = (SELECT COUNT(*) FROM cohort_membership WHERE cohort_definition_id = %s) WHERE execution_id = currval(''cohort_execution_log_execution_id_seq''); SELECT COUNT(*) AS materialized_members FROM cohort_membership WHERE cohort_definition_id = %s; COMMIT;',
        :'cohort_id',
        :'cohort_id',
        :'cohort_id',
        demographics_group.predicates,
        diagnosis_group.predicates,
        :'cohort_id',
        :'cohort_id'
    ) AS execution_sql
FROM demographics_group
CROSS JOIN diagnosis_group
CROSS JOIN validated v
WHERE v.total_criteria > 0
  AND v.total_criteria = v.valid_criteria
  AND demographics_group.predicates IS NOT NULL
  AND diagnosis_group.predicates IS NOT NULL;




