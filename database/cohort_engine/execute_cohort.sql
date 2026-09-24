-- ============================================================
-- Research Cohort Explorer
-- Cohort Engine: Execute Cohort
-- ============================================================
-- Current supported semantics:
--   1. Inclusion criteria support demographics, diagnoses,
--      laboratory results, medication orders, procedures, and encounters
--   2. Inclusion criteria are combined with AND
--   3. Demographic inclusions are evaluated on the patient
--      anchor row
--   4. Diagnosis inclusions are evaluated on the same diagnosis
--      row inside a correlated EXISTS subquery
--   5. Laboratory inclusions are evaluated on the same laboratory
--      result row inside a correlated EXISTS subquery
--   6. Medication inclusions are evaluated on the same medication
--      order row inside a correlated EXISTS subquery
--   7. Procedure inclusions are evaluated on the same procedure
--      row inside a correlated EXISTS subquery
--   8. Encounter inclusions are evaluated on the same encounter
--      row inside a correlated EXISTS subquery
--   9. Diagnosis exclusions are supported
--  10. Each diagnosis exclusion is evaluated independently through
--      its own correlated NOT EXISTS subquery
--  11. Demographic, laboratory, medication, procedure, and encounter
--      exclusions are not currently supported
--  12. At least one supported inclusion criterion is required
--  13. Cohort membership is replaced inside a transaction
--  14. Successful execution is recorded in cohort_execution_log
-- ============================================================

WITH criterion_validation AS (
    SELECT
        cc.cohort_criterion_id,
        cc.cohort_definition_id,
        cc.criterion_order,
        cc.criterion_type,
        w.criterion_whitelist_id,
        w.source_view,
        w.source_alias,
        w.source_column,
        w.operator,
        w.value_type,
        cc.value_text,
        CASE
            WHEN w.criterion_whitelist_id IS NULL THEN FALSE
            WHEN cc.criterion_type NOT IN ('inclusion', 'exclusion') THEN FALSE
            WHEN cc.criterion_type = 'exclusion'
             AND w.source_view <> 'vw_diagnoses' THEN FALSE
            WHEN w.source_view NOT IN (
                'vw_patient_demographics',
                'vw_diagnoses',
                'vw_lab_results',
                'vw_medication_orders',
                'vw_procedures',
                'vw_encounters'
            ) THEN FALSE
            WHEN w.value_type = 'text' THEN TRUE
            WHEN w.value_type = 'integer' THEN
                pg_input_is_valid(
                    cc.value_text,
                    'integer'
                )
            WHEN w.value_type = 'numeric' THEN
                pg_input_is_valid(
                    cc.value_text,
                    'numeric'
                )
            WHEN w.value_type = 'date' THEN
                pg_input_is_valid(
                    cc.value_text,
                    'date'
                )
            ELSE FALSE
        END AS criterion_is_valid
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
        ) AS valid_criteria,
        COUNT(*) FILTER (
            WHERE criterion_type = 'inclusion'
              AND criterion_is_valid
        ) AS valid_inclusion_criteria
    FROM criterion_validation
),

generated_predicates AS (
    SELECT
        cv.criterion_order,
        cv.criterion_type,
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
      AND v.total_criteria = v.valid_criteria
      AND v.total_criteria > 0
      AND v.valid_inclusion_criteria > 0
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

laboratory_group AS (
    SELECT
        string_agg(
            sql_predicate,
            ' AND '
            ORDER BY criterion_order
        ) AS predicates
    FROM generated_predicates
    WHERE criterion_type = 'inclusion'
      AND source_view = 'vw_lab_results'
),

medication_group AS (
    SELECT
        string_agg(
            sql_predicate,
            ' AND '
            ORDER BY criterion_order
        ) AS predicates
    FROM generated_predicates
    WHERE criterion_type = 'inclusion'
      AND source_view = 'vw_medication_orders'
),

procedure_group AS (
    SELECT
        string_agg(
            sql_predicate,
            ' AND '
            ORDER BY criterion_order
        ) AS predicates
    FROM generated_predicates
    WHERE criterion_type = 'inclusion'
      AND source_view = 'vw_procedures'
),

encounter_group AS (
    SELECT
        string_agg(
            sql_predicate,
            ' AND '
            ORDER BY criterion_order
        ) AS predicates
    FROM generated_predicates
    WHERE criterion_type = 'inclusion'
      AND source_view = 'vw_encounters'
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
),

inclusion_clause AS (
    SELECT
        concat_ws(
            ' AND ',
            demographics_group.predicates,
            CASE
                WHEN diagnosis_group.predicates IS NOT NULL
                    THEN format(
                        'EXISTS (SELECT 1 FROM vw_diagnoses d WHERE d.patient_id = p.patient_id AND %s)',
                        diagnosis_group.predicates
                    )
            END,
            CASE
                WHEN laboratory_group.predicates IS NOT NULL
                    THEN format(
                        'EXISTS (SELECT 1 FROM vw_lab_results l WHERE l.patient_id = p.patient_id AND %s)',
                        laboratory_group.predicates
                    )
            END,
            CASE
                WHEN medication_group.predicates IS NOT NULL
                    THEN format(
                        'EXISTS (SELECT 1 FROM vw_medication_orders m WHERE m.patient_id = p.patient_id AND %s)',
                        medication_group.predicates
                    )
            END,
            CASE
                WHEN procedure_group.predicates IS NOT NULL
                    THEN format(
                        'EXISTS (SELECT 1 FROM vw_procedures pr WHERE pr.patient_id = p.patient_id AND %s)',
                        procedure_group.predicates
                    )
            END,
            CASE
                WHEN encounter_group.predicates IS NOT NULL
                    THEN format(
                        'EXISTS (SELECT 1 FROM vw_encounters e WHERE e.patient_id = p.patient_id AND %s)',
                        encounter_group.predicates
                    )
            END
        ) AS predicates
    FROM demographics_group
    CROSS JOIN diagnosis_group
    CROSS JOIN laboratory_group
    CROSS JOIN medication_group
    CROSS JOIN procedure_group
    CROSS JOIN encounter_group
)

SELECT
    format(
        'BEGIN; INSERT INTO cohort_execution_log (cohort_definition_id, cohort_version, status) SELECT cd.cohort_definition_id, cd.version, ''running'' FROM cohort_definitions cd WHERE cd.cohort_definition_id = %s; DELETE FROM cohort_membership WHERE cohort_definition_id = %s; INSERT INTO cohort_membership (cohort_definition_id, patient_id) SELECT %s, p.patient_id FROM vw_patient_demographics p WHERE %s%s; UPDATE cohort_execution_log SET completed_at = CURRENT_TIMESTAMP, status = ''succeeded'', member_count = (SELECT COUNT(*) FROM cohort_membership WHERE cohort_definition_id = %s) WHERE execution_id = currval(''cohort_execution_log_execution_id_seq''); SELECT COUNT(*) AS materialized_members FROM cohort_membership WHERE cohort_definition_id = %s; COMMIT;',
        :'cohort_id',
        :'cohort_id',
        :'cohort_id',
        inclusion_clause.predicates,
        COALESCE(
            diagnosis_exclusions.predicates,
            ''
        ),
        :'cohort_id',
        :'cohort_id'
    ) AS execution_sql
FROM inclusion_clause
CROSS JOIN diagnosis_exclusions
CROSS JOIN validated v
WHERE v.total_criteria > 0
  AND v.total_criteria = v.valid_criteria
  AND v.valid_inclusion_criteria > 0
  AND inclusion_clause.predicates <> '';