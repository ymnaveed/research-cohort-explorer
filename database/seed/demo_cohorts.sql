-- ============================================================
-- Research Cohort Explorer
-- Demo Cohort Library
-- ============================================================
--
-- Creates a reproducible set of six demonstration cohorts
-- covering every Cohort Engine v1 inclusion domain and
-- diagnosis exclusion logic.
--
-- This script is intended to be run AFTER the synthetic
-- clinical dataset has been loaded.
--
-- The script is idempotent for the cohort names below:
-- existing demo cohorts are reused rather than duplicated.
-- Demo cohort metadata is normalized to active status.
-- Criteria are replaced with the canonical definitions.
-- Cohort membership is rebuilt using execute_cohort().
-- ============================================================

BEGIN;


-- ============================================================
-- 1. Adult Type 2 Diabetes
-- ============================================================

INSERT INTO cohort_definitions (
    cohort_name,
    description,
    study_start_date,
    study_end_date,
    version,
    status
)
SELECT
    'Adult Type 2 Diabetes',
    'Adult patients with a Type 2 diabetes diagnosis during the study period.',
    DATE '2015-01-01',
    DATE '2025-12-31',
    1,
    'active'
WHERE NOT EXISTS (
    SELECT 1
    FROM cohort_definitions
    WHERE cohort_name = 'Adult Type 2 Diabetes'
);

DELETE FROM cohort_criteria
WHERE cohort_definition_id = (
    SELECT cohort_definition_id
    FROM cohort_definitions
    WHERE cohort_name = 'Adult Type 2 Diabetes'
    ORDER BY cohort_definition_id
    LIMIT 1
);

INSERT INTO cohort_criteria (
    cohort_definition_id,
    criterion_order,
    criterion_type,
    domain,
    field_name,
    operator,
    value_text
)
SELECT
    cohort_definition_id,
    1,
    'inclusion',
    'diagnosis',
    'diagnosis_code',
    '=',
    'E11.9'
FROM cohort_definitions
WHERE cohort_name = 'Adult Type 2 Diabetes'
ORDER BY cohort_definition_id
LIMIT 1;

INSERT INTO cohort_criteria (
    cohort_definition_id,
    criterion_order,
    criterion_type,
    domain,
    field_name,
    operator,
    value_text
)
SELECT
    cohort_definition_id,
    2,
    'inclusion',
    'demographics',
    'age_at_study_end',
    '>=',
    '18'
FROM cohort_definitions
WHERE cohort_name = 'Adult Type 2 Diabetes'
ORDER BY cohort_definition_id
LIMIT 1;

INSERT INTO cohort_criteria (
    cohort_definition_id,
    criterion_order,
    criterion_type,
    domain,
    field_name,
    operator,
    value_text
)
SELECT
    cohort_definition_id,
    3,
    'inclusion',
    'diagnosis',
    'recorded_date',
    '>=',
    '2015-01-01'
FROM cohort_definitions
WHERE cohort_name = 'Adult Type 2 Diabetes'
ORDER BY cohort_definition_id
LIMIT 1;

INSERT INTO cohort_criteria (
    cohort_definition_id,
    criterion_order,
    criterion_type,
    domain,
    field_name,
    operator,
    value_text
)
SELECT
    cohort_definition_id,
    4,
    'inclusion',
    'diagnosis',
    'recorded_date',
    '<=',
    '2025-12-31'
FROM cohort_definitions
WHERE cohort_name = 'Adult Type 2 Diabetes'
ORDER BY cohort_definition_id
LIMIT 1;


-- ============================================================
-- 2. Elevated HbA1c
-- ============================================================

INSERT INTO cohort_definitions (
    cohort_name,
    description,
    study_start_date,
    study_end_date,
    version,
    status
)
SELECT
    'Elevated HbA1c',
    'Patients with at least one Hemoglobin A1c result greater than or equal to 6.5%.',
    DATE '2015-01-01',
    DATE '2025-12-31',
    1,
    'active'
WHERE NOT EXISTS (
    SELECT 1
    FROM cohort_definitions
    WHERE cohort_name = 'Elevated HbA1c'
);

DELETE FROM cohort_criteria
WHERE cohort_definition_id = (
    SELECT cohort_definition_id
    FROM cohort_definitions
    WHERE cohort_name = 'Elevated HbA1c'
    ORDER BY cohort_definition_id
    LIMIT 1
);

INSERT INTO cohort_criteria (
    cohort_definition_id,
    criterion_order,
    criterion_type,
    domain,
    field_name,
    operator,
    value_text
)
SELECT
    cohort_definition_id,
    1,
    'inclusion',
    'laboratory',
    'test_code',
    '=',
    'HBA1C'
FROM cohort_definitions
WHERE cohort_name = 'Elevated HbA1c'
ORDER BY cohort_definition_id
LIMIT 1;

INSERT INTO cohort_criteria (
    cohort_definition_id,
    criterion_order,
    criterion_type,
    domain,
    field_name,
    operator,
    value_text
)
SELECT
    cohort_definition_id,
    2,
    'inclusion',
    'laboratory',
    'result_numeric',
    '>=',
    '6.5'
FROM cohort_definitions
WHERE cohort_name = 'Elevated HbA1c'
ORDER BY cohort_definition_id
LIMIT 1;


-- ============================================================
-- 3. Metformin Users
-- ============================================================

INSERT INTO cohort_definitions (
    cohort_name,
    description,
    study_start_date,
    study_end_date,
    version,
    status
)
SELECT
    'Metformin Users',
    'Patients with at least one Metformin medication order during the study period.',
    DATE '2015-01-01',
    DATE '2025-12-31',
    1,
    'active'
WHERE NOT EXISTS (
    SELECT 1
    FROM cohort_definitions
    WHERE cohort_name = 'Metformin Users'
);

DELETE FROM cohort_criteria
WHERE cohort_definition_id = (
    SELECT cohort_definition_id
    FROM cohort_definitions
    WHERE cohort_name = 'Metformin Users'
    ORDER BY cohort_definition_id
    LIMIT 1
);

INSERT INTO cohort_criteria (
    cohort_definition_id,
    criterion_order,
    criterion_type,
    domain,
    field_name,
    operator,
    value_text
)
SELECT
    cohort_definition_id,
    1,
    'inclusion',
    'medication',
    'medication_code',
    '=',
    'METFORMIN'
FROM cohort_definitions
WHERE cohort_name = 'Metformin Users'
ORDER BY cohort_definition_id
LIMIT 1;


-- ============================================================
-- 4. Echocardiogram Patients
-- ============================================================

INSERT INTO cohort_definitions (
    cohort_name,
    description,
    study_start_date,
    study_end_date,
    version,
    status
)
SELECT
    'Echocardiogram Patients',
    'Patients with at least one echocardiogram procedure during the study period.',
    DATE '2015-01-01',
    DATE '2025-12-31',
    1,
    'active'
WHERE NOT EXISTS (
    SELECT 1
    FROM cohort_definitions
    WHERE cohort_name = 'Echocardiogram Patients'
);

DELETE FROM cohort_criteria
WHERE cohort_definition_id = (
    SELECT cohort_definition_id
    FROM cohort_definitions
    WHERE cohort_name = 'Echocardiogram Patients'
    ORDER BY cohort_definition_id
    LIMIT 1
);

INSERT INTO cohort_criteria (
    cohort_definition_id,
    criterion_order,
    criterion_type,
    domain,
    field_name,
    operator,
    value_text
)
SELECT
    cohort_definition_id,
    1,
    'inclusion',
    'procedure',
    'procedure_code',
    '=',
    'ECHO'
FROM cohort_definitions
WHERE cohort_name = 'Echocardiogram Patients'
ORDER BY cohort_definition_id
LIMIT 1;


-- ============================================================
-- 5. Emergency Department Patients
-- ============================================================

INSERT INTO cohort_definitions (
    cohort_name,
    description,
    study_start_date,
    study_end_date,
    version,
    status
)
SELECT
    'Emergency Department Patients',
    'Patients with at least one Emergency Department encounter during the study period.',
    DATE '2015-01-01',
    DATE '2025-12-31',
    1,
    'active'
WHERE NOT EXISTS (
    SELECT 1
    FROM cohort_definitions
    WHERE cohort_name = 'Emergency Department Patients'
);

DELETE FROM cohort_criteria
WHERE cohort_definition_id = (
    SELECT cohort_definition_id
    FROM cohort_definitions
    WHERE cohort_name = 'Emergency Department Patients'
    ORDER BY cohort_definition_id
    LIMIT 1
);

INSERT INTO cohort_criteria (
    cohort_definition_id,
    criterion_order,
    criterion_type,
    domain,
    field_name,
    operator,
    value_text
)
SELECT
    cohort_definition_id,
    1,
    'inclusion',
    'encounter',
    'encounter_type_code',
    '=',
    'ED'
FROM cohort_definitions
WHERE cohort_name = 'Emergency Department Patients'
ORDER BY cohort_definition_id
LIMIT 1;


-- ============================================================
-- 6. Hypertension Without Type 2 Diabetes
-- ============================================================

INSERT INTO cohort_definitions (
    cohort_name,
    description,
    study_start_date,
    study_end_date,
    version,
    status
)
SELECT
    'Hypertension Without Type 2 Diabetes',
    'Patients with hypertension who do not have a Type 2 diabetes diagnosis.',
    DATE '2015-01-01',
    DATE '2025-12-31',
    1,
    'active'
WHERE NOT EXISTS (
    SELECT 1
    FROM cohort_definitions
    WHERE cohort_name = 'Hypertension Without Type 2 Diabetes'
);

DELETE FROM cohort_criteria
WHERE cohort_definition_id = (
    SELECT cohort_definition_id
    FROM cohort_definitions
    WHERE cohort_name = 'Hypertension Without Type 2 Diabetes'
    ORDER BY cohort_definition_id
    LIMIT 1
);

INSERT INTO cohort_criteria (
    cohort_definition_id,
    criterion_order,
    criterion_type,
    domain,
    field_name,
    operator,
    value_text
)
SELECT
    cohort_definition_id,
    1,
    'inclusion',
    'diagnosis',
    'diagnosis_code',
    '=',
    'I10'
FROM cohort_definitions
WHERE cohort_name = 'Hypertension Without Type 2 Diabetes'
ORDER BY cohort_definition_id
LIMIT 1;

INSERT INTO cohort_criteria (
    cohort_definition_id,
    criterion_order,
    criterion_type,
    domain,
    field_name,
    operator,
    value_text
)
SELECT
    cohort_definition_id,
    2,
    'exclusion',
    'diagnosis',
    'diagnosis_code',
    '=',
    'E11.9'
FROM cohort_definitions
WHERE cohort_name = 'Hypertension Without Type 2 Diabetes'
ORDER BY cohort_definition_id
LIMIT 1;


-- ============================================================
-- Normalize demo cohort status
-- ============================================================
--
-- INSERT ... WHERE NOT EXISTS preserves existing cohort rows.
-- Therefore, explicitly set the canonical demo cohorts to active
-- so rerunning this seed also normalizes existing installations.

UPDATE cohort_definitions
SET status = 'active'
WHERE cohort_name IN (
    'Adult Type 2 Diabetes',
    'Elevated HbA1c',
    'Metformin Users',
    'Echocardiogram Patients',
    'Emergency Department Patients',
    'Hypertension Without Type 2 Diabetes'
);


-- ============================================================
-- Execute all six demo cohorts
-- ============================================================

SELECT execute_cohort(
    (
        SELECT cohort_definition_id
        FROM cohort_definitions
        WHERE cohort_name = 'Adult Type 2 Diabetes'
        ORDER BY cohort_definition_id
        LIMIT 1
    )
);

SELECT execute_cohort(
    (
        SELECT cohort_definition_id
        FROM cohort_definitions
        WHERE cohort_name = 'Elevated HbA1c'
        ORDER BY cohort_definition_id
        LIMIT 1
    )
);

SELECT execute_cohort(
    (
        SELECT cohort_definition_id
        FROM cohort_definitions
        WHERE cohort_name = 'Metformin Users'
        ORDER BY cohort_definition_id
        LIMIT 1
    )
);

SELECT execute_cohort(
    (
        SELECT cohort_definition_id
        FROM cohort_definitions
        WHERE cohort_name = 'Echocardiogram Patients'
        ORDER BY cohort_definition_id
        LIMIT 1
    )
);

SELECT execute_cohort(
    (
        SELECT cohort_definition_id
        FROM cohort_definitions
        WHERE cohort_name = 'Emergency Department Patients'
        ORDER BY cohort_definition_id
        LIMIT 1
    )
);

SELECT execute_cohort(
    (
        SELECT cohort_definition_id
        FROM cohort_definitions
        WHERE cohort_name = 'Hypertension Without Type 2 Diabetes'
        ORDER BY cohort_definition_id
        LIMIT 1
    )
);


COMMIT;


-- ============================================================
-- Verification
-- ============================================================

SELECT
    cd.cohort_definition_id,
    cd.cohort_name,
    cd.status,
    cd.version,
    COUNT(cm.patient_id) AS member_count
FROM cohort_definitions cd
LEFT JOIN cohort_membership cm
    ON cm.cohort_definition_id = cd.cohort_definition_id
WHERE cd.cohort_name IN (
    'Adult Type 2 Diabetes',
    'Elevated HbA1c',
    'Metformin Users',
    'Echocardiogram Patients',
    'Emergency Department Patients',
    'Hypertension Without Type 2 Diabetes'
)
GROUP BY
    cd.cohort_definition_id,
    cd.cohort_name,
    cd.status,
    cd.version
ORDER BY
    cd.cohort_definition_id;