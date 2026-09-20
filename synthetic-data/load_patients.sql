-- ============================================================
-- Research Cohort Explorer
-- Load Synthetic Patients
-- ============================================================

\echo 'Loading synthetic patients...'

BEGIN;

\copy patients (
    research_id,
    date_of_birth,
    sex,
    race,
    ethnicity,
    zip3
)
FROM 'synthetic-data/output/patients.csv'
WITH (
    FORMAT csv,
    HEADER true
);

COMMIT;

\echo 'Synthetic patient load complete.'