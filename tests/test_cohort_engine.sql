-- ============================================================
-- Cohort Engine v1 Regression Tests
-- ============================================================
-- Purpose:
--   Protect known cohort-engine behavior before backend/API
--   development begins.
--
-- Run against the research_cohort database.
-- ============================================================

-- Test 1: Adult diabetes cohort
-- Expected result: 6,620 patients

DO $$
DECLARE
    actual_count BIGINT;
    expected_count CONSTANT BIGINT := 6620;
BEGIN
    SELECT COUNT(*)
    INTO actual_count
    FROM cohort_membership
    WHERE cohort_definition_id = 1;

    IF actual_count <> expected_count THEN
        RAISE EXCEPTION
            'FAIL: Adult diabetes cohort expected % members but found %',
            expected_count,
            actual_count;
    END IF;

    RAISE NOTICE
        'PASS: Adult diabetes cohort contains % members',
        actual_count;
END
$$;
-- Test 2: Cohort membership contains no duplicate patients
-- within the same cohort definition.

DO $$
DECLARE
    duplicate_count BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO duplicate_count
    FROM (
        SELECT
            cohort_definition_id,
            patient_id
        FROM cohort_membership
        GROUP BY cohort_definition_id, patient_id
        HAVING COUNT(*) > 1
    ) duplicates;

    IF duplicate_count <> 0 THEN
        RAISE EXCEPTION
            'FAIL: Found % duplicate cohort membership records',
            duplicate_count;
    END IF;

    RAISE NOTICE
        'PASS: Cohort membership contains no duplicate patients';
END
$$;
-- Test 3: Every cohort member references an existing patient.

DO $$
DECLARE
    orphan_count BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO orphan_count
    FROM cohort_membership cm
    LEFT JOIN patients p
        ON p.patient_id = cm.patient_id
    WHERE p.patient_id IS NULL;

    IF orphan_count <> 0 THEN
        RAISE EXCEPTION
            'FAIL: Found % cohort members without a valid patient',
            orphan_count;
    END IF;

    RAISE NOTICE
        'PASS: All cohort members reference valid patients';
END
$$;
-- Test 4: Every stored cohort criterion is supported
-- by the criterion whitelist.

DO $$
DECLARE
    unsupported_count BIGINT;
BEGIN
    SELECT COUNT(*)
    INTO unsupported_count
    FROM cohort_criteria cc
    LEFT JOIN cohort_criterion_whitelist w
        ON w.domain = cc.domain
       AND w.field_name = cc.field_name
       AND w.operator = cc.operator
    WHERE w.criterion_whitelist_id IS NULL;

    IF unsupported_count <> 0 THEN
        RAISE EXCEPTION
            'FAIL: Found % unsupported stored cohort criteria',
            unsupported_count;
    END IF;

    RAISE NOTICE
        'PASS: All stored cohort criteria are supported by the whitelist';
END
$$;