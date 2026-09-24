-- ============================================================
-- Research Cohort Explorer
-- Cohort Execution Function
-- ============================================================
-- Provides an API-callable interface to the validated cohort
-- engine.
--
-- Supported inclusion domains:
--   demographics
--   diagnosis
--   laboratory
--   medication
--   procedure
--   encounter
--
-- Supported exclusions:
--   diagnosis only
--
-- The function:
--   1. Confirms the cohort exists
--   2. Validates all stored criteria against the whitelist
--   3. Requires at least one valid inclusion criterion
--   4. Generates the cohort predicate from trusted metadata
--   5. Replaces materialized cohort membership
--   6. Records successful execution
--   7. Returns the resulting member count
-- ============================================================

CREATE OR REPLACE FUNCTION execute_cohort(
    p_cohort_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_cohort_version INTEGER;
    v_total_criteria BIGINT;
    v_valid_criteria BIGINT;
    v_valid_inclusion_criteria BIGINT;
    v_inclusion_clause TEXT;
    v_exclusion_clause TEXT;
    v_execution_id BIGINT;
    v_member_count BIGINT;
BEGIN
    -- --------------------------------------------------------
    -- Confirm that the requested cohort exists.
    -- --------------------------------------------------------
    SELECT version
    INTO v_cohort_version
    FROM cohort_definitions
    WHERE cohort_definition_id = p_cohort_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Cohort % not found', p_cohort_id;
    END IF;

    -- --------------------------------------------------------
    -- Validate all stored criteria.
    -- --------------------------------------------------------
    WITH criterion_validation AS (
        SELECT
            cc.cohort_criterion_id,
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

                WHEN cc.criterion_type NOT IN (
                    'inclusion',
                    'exclusion'
                ) THEN FALSE

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

        WHERE cc.cohort_definition_id = p_cohort_id
    )

    SELECT
        COUNT(*),
        COUNT(*) FILTER (
            WHERE criterion_is_valid
        ),
        COUNT(*) FILTER (
            WHERE criterion_type = 'inclusion'
              AND criterion_is_valid
        )
    INTO
        v_total_criteria,
        v_valid_criteria,
        v_valid_inclusion_criteria
    FROM criterion_validation;

    IF v_total_criteria = 0 THEN
        RAISE EXCEPTION
            'Cohort % has no criteria',
            p_cohort_id;
    END IF;

    IF v_total_criteria <> v_valid_criteria THEN
        RAISE EXCEPTION
            'Cohort % contains unsupported or invalid criteria',
            p_cohort_id;
    END IF;

    IF v_valid_inclusion_criteria = 0 THEN
        RAISE EXCEPTION
            'Cohort % has no valid inclusion criteria',
            p_cohort_id;
    END IF;

    -- --------------------------------------------------------
    -- Generate the validated inclusion and exclusion clauses.
    -- --------------------------------------------------------
    WITH criterion_validation AS (
        SELECT
            cc.cohort_criterion_id,
            cc.criterion_order,
            cc.criterion_type,
            w.source_view,
            w.source_alias,
            w.source_column,
            w.operator,
            w.value_type,
            cc.value_text

        FROM cohort_criteria cc

        JOIN cohort_criterion_whitelist w
            ON w.domain = cc.domain
           AND w.field_name = cc.field_name
           AND w.operator = cc.operator

        WHERE cc.cohort_definition_id = p_cohort_id
    ),

    generated_predicates AS (
        SELECT
            criterion_order,
            criterion_type,
            source_view,

            CASE
                WHEN value_type = 'text' THEN
                    format(
                        '%I.%I %s %L',
                        source_alias,
                        source_column,
                        operator,
                        value_text
                    )

                WHEN value_type = 'integer' THEN
                    format(
                        '%I.%I %s %L::INTEGER',
                        source_alias,
                        source_column,
                        operator,
                        value_text
                    )

                WHEN value_type = 'numeric' THEN
                    format(
                        '%I.%I %s %L::NUMERIC',
                        source_alias,
                        source_column,
                        operator,
                        value_text
                    )

                WHEN value_type = 'date' THEN
                    format(
                        '%I.%I %s %L::DATE',
                        source_alias,
                        source_column,
                        operator,
                        value_text
                    )
            END AS sql_predicate

        FROM criterion_validation
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
                    ' AND NOT EXISTS (
                        SELECT 1
                        FROM vw_diagnoses d
                        WHERE d.patient_id = p.patient_id
                          AND %s
                    )',
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
        concat_ws(
            ' AND ',

            demographics_group.predicates,

            CASE
                WHEN diagnosis_group.predicates IS NOT NULL
                THEN format(
                    'EXISTS (
                        SELECT 1
                        FROM vw_diagnoses d
                        WHERE d.patient_id = p.patient_id
                          AND %s
                    )',
                    diagnosis_group.predicates
                )
            END,

            CASE
                WHEN laboratory_group.predicates IS NOT NULL
                THEN format(
                    'EXISTS (
                        SELECT 1
                        FROM vw_lab_results l
                        WHERE l.patient_id = p.patient_id
                          AND %s
                    )',
                    laboratory_group.predicates
                )
            END,

            CASE
                WHEN medication_group.predicates IS NOT NULL
                THEN format(
                    'EXISTS (
                        SELECT 1
                        FROM vw_medication_orders m
                        WHERE m.patient_id = p.patient_id
                          AND %s
                    )',
                    medication_group.predicates
                )
            END,

            CASE
                WHEN procedure_group.predicates IS NOT NULL
                THEN format(
                    'EXISTS (
                        SELECT 1
                        FROM vw_procedures pr
                        WHERE pr.patient_id = p.patient_id
                          AND %s
                    )',
                    procedure_group.predicates
                )
            END,

            CASE
                WHEN encounter_group.predicates IS NOT NULL
                THEN format(
                    'EXISTS (
                        SELECT 1
                        FROM vw_encounters e
                        WHERE e.patient_id = p.patient_id
                          AND %s
                    )',
                    encounter_group.predicates
                )
            END
        ),

        COALESCE(
            diagnosis_exclusions.predicates,
            ''
        )

    INTO
        v_inclusion_clause,
        v_exclusion_clause

    FROM demographics_group
    CROSS JOIN diagnosis_group
    CROSS JOIN laboratory_group
    CROSS JOIN medication_group
    CROSS JOIN procedure_group
    CROSS JOIN encounter_group
    CROSS JOIN diagnosis_exclusions;

    IF v_inclusion_clause IS NULL
       OR v_inclusion_clause = '' THEN
        RAISE EXCEPTION
            'Cohort % produced no inclusion predicate',
            p_cohort_id;
    END IF;

    -- --------------------------------------------------------
    -- Start execution audit record.
    -- --------------------------------------------------------
    INSERT INTO cohort_execution_log (
        cohort_definition_id,
        cohort_version,
        status
    )
    VALUES (
        p_cohort_id,
        v_cohort_version,
        'running'
    )
    RETURNING execution_id
    INTO v_execution_id;

    -- --------------------------------------------------------
    -- Replace existing materialized membership.
    -- --------------------------------------------------------
    DELETE FROM cohort_membership
    WHERE cohort_definition_id = p_cohort_id;

    EXECUTE format(
        'INSERT INTO cohort_membership (
            cohort_definition_id,
            patient_id
        )
        SELECT
            %L,
            p.patient_id
        FROM vw_patient_demographics p
        WHERE %s%s',
        p_cohort_id,
        v_inclusion_clause,
        v_exclusion_clause
    );

    -- --------------------------------------------------------
    -- Count materialized members.
    -- --------------------------------------------------------
    SELECT COUNT(*)
    INTO v_member_count
    FROM cohort_membership
    WHERE cohort_definition_id = p_cohort_id;

    -- --------------------------------------------------------
    -- Complete execution audit record.
    -- --------------------------------------------------------
    UPDATE cohort_execution_log
    SET
        completed_at = CURRENT_TIMESTAMP,
        status = 'succeeded',
        member_count = v_member_count
    WHERE execution_id = v_execution_id;

    RETURN v_member_count;
END;
$$;