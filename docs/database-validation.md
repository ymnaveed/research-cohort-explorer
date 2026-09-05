# Database Validation Report

## Research Cohort Explorer

**Project:** Research Cohort Explorer  
**Database:** PostgreSQL 16  
**Database Name:** research_cohort  
**Database User:** research_admin  
**Environment:** Docker Compose  
**Data Type:** Synthetic data only  
**Validation Status:** PASSED  
**Validation Scope:** Production database and synthetic-data generation pipeline

---

# 1. Purpose

This document records the database validation activities performed for the Research Cohort Explorer project.

The purpose of the validation was to confirm that the synthetic clinical datasets loaded into PostgreSQL are structurally valid, internally consistent, temporally valid, and suitable for downstream cohort-building, analytics, research-informatics, and application development.

The project uses synthetic data only. No real patient data, medical records, or personally identifiable health information are used.

The validation covered:

- Primary-key uniqueness
- Research identifier integrity
- Foreign-key relationships
- Patient and encounter relationships
- Encounter-linked clinical records
- Reference-code validation
- Temporal integrity
- Patient date-of-birth constraints
- Encounter date consistency
- Laboratory result validity
- Medication date validity
- Clinical note validity
- Procedure date validity
- Staging-table validation
- Production-table validation
- Synthetic data quality
- Database infrastructure observations

---

# 2. Database Environment

The PostgreSQL database is running inside Docker using PostgreSQL 16.

The database is defined in:

docker-compose.yml

The database configuration is:

Database:
research_cohort

User:
research_admin

PostgreSQL version:
16

Container:
research-cohort-postgres

Port:
5432

The database is initialized through SQL scripts mounted into the PostgreSQL initialization directory.

The initialization structure includes:

- database/init.sql
- database/schema/001_extensions.sql
- database/schema/002_reference_tables.sql
- database/schema/003_core_tables.sql
- database/seed/reference_data.sql

---

# 3. Production Schema

The production database contains the following primary clinical tables:

1. patients
2. encounters
3. diagnoses
4. lab_results
5. medication_orders
6. clinical_notes
7. procedures

The database also contains reference tables:

1. diagnosis_codes
2. encounter_types
3. facilities
4. lab_tests
5. medication_codes
6. note_types
7. procedure_codes
8. providers

The production database also contains staging tables used during synthetic-data loading and validation.

---

# 4. Production Dataset Summary

The final production database contains the following validated record counts.

| Dataset | Records |
|---|---:|
| patients | 100,000 |
| encounters | 1,151,313 |
| diagnoses | 56,531 |
| lab_results | 1,408,495 |
| medication_orders | 114,123 |
| clinical_notes | 1,401,000 |
| procedures | 211,638 |
| **Total** | **4,463,110** |

The total number of records across the seven primary clinical datasets is:

4,463,110

All datasets were generated using the project random seed:

20260827

The patient dataset contains 100,000 synthetic patients.

---

# 5. Patient Dataset Validation

## 5.1 Patient identifiers

The patient dataset was validated for:

- Required research identifiers
- Unique research identifiers
- Patient coverage
- Valid date-of-birth values
- Valid sex values
- Valid ZIP3 values

Results:

- Patient rows: 100,000
- Unique research IDs: 100,000
- First research ID: P-000001
- Last research ID: P-100000
- Missing research IDs: 0
- Missing date of birth: 0
- Missing sex: 0
- Missing ZIP3: 0

The patient dataset passed validation.

---

# 6. Encounter Dataset Validation

The encounter dataset contains:

1,151,313

records.

Validation included:

- Unique encounter identifiers
- Valid patient references
- Valid encounter types
- Valid encounter dates
- Patient/encounter date consistency
- Study-period boundaries

Results:

- Encounter rows: 1,151,313
- Unique encounter IDs: 1,151,313
- Unique patients represented: 100,000
- Missing patient references: 0
- Missing encounter type: 0
- Missing encounter date: 0

Encounter date range:

Start:
2015-01-01

End:
2025-12-31

Encounter types:

| Encounter Type | Records |
|---|---:|
| TELEHEALTH | 173,264 |
| INPATIENT | 92,099 |
| OFFICE | 632,265 |
| URGENT_CARE | 138,476 |
| ED | 115,209 |

The encounter dataset passed validation.

---

# 7. Encounter-to-Patient Temporal Integrity

A database trigger was implemented to prevent encounters from occurring before a patient's date of birth.

The validation included a deliberately invalid test case.

A valid encounter was inserted for patient 1 on:

2020-06-15

An invalid encounter was then attempted for the same patient on:

1979-06-15

The database correctly rejected the invalid record with:

Encounter date 1979-06-15 10:30:00 cannot be before patient 1 date of birth 1980-01-01

A second validation attempted to update a patient's date of birth to a value that would conflict with an existing encounter.

The database correctly rejected the update with:

Patient 1 date range conflicts with one or more existing encounters

This confirms that patient/encounter temporal integrity is enforced at the database level.

---

# 8. Diagnosis Dataset Validation

The diagnosis dataset contains:

56,531

records.

The generated CSV contains:

- research_id
- encounter_id
- diagnosis_code
- onset_date
- recorded_date
- diagnosis_type

Validation results:

- Diagnosis rows: 56,531
- Unique patients represented: 45,239
- Missing research IDs: 0
- Missing diagnosis codes: 0
- Missing onset dates: 0
- Missing recorded dates: 0
- Primary diagnoses: 39,642
- Secondary diagnoses: 16,889
- Unlinked diagnoses: 53,893

Diagnosis onset dates range from:

2015-01-01

through:

2025-12-31

Linked diagnoses were validated against their corresponding encounters.

Patient/encounter mismatches:

0

No broken patient references were found.

No broken encounter references were found for diagnosis records containing an encounter_id.

The diagnosis dataset passed validation.

---

# 9. Laboratory Dataset Validation

The laboratory dataset contains:

1,408,495

records.

The laboratory CSV contains:

- lab_result_id
- research_id
- encounter_id
- test_code
- result_numeric
- result_text
- unit
- result_date

Laboratory test types:

| Test Code | Records |
|---|---:|
| BP_SYS | 234,414 |
| CREAT | 234,837 |
| GLUCOSE | 235,459 |
| HBA1C | 234,105 |
| HDL | 234,746 |
| LDL | 234,934 |

Linked laboratory results:

915,624

Unlinked laboratory results:

492,871

Unlinked laboratory records are intentional and represent laboratory measurements that are not associated with a specific encounter.

---

# 10. Laboratory Validation Results

The final laboratory validation produced the following results:

- Laboratory rows: 1,408,495
- Unique laboratory IDs: 1,408,495
- Unique patients: 100,000
- Missing patient references: 0
- Missing encounter references: 0
- Invalid test codes: 0
- Missing laboratory values: 0
- Invalid result values: 0
- Broken patient references: 0
- Broken encounter references: 0
- Patient/encounter mismatches: 0
- Laboratory results before patient birth: 0
- Laboratory results outside study period: 0
- Encounter/result timestamp mismatches: 0

Final laboratory date range:

Earliest:
2015-01-01 00:02:26

Latest:
2025-12-31 23:55:32

The laboratory dataset passed validation.

---

# 11. Laboratory Data Defect and Correction

During the initial laboratory validation, a temporal integrity defect was discovered.

The first generated laboratory dataset contained:

23,173

laboratory results that occurred before the corresponding patient's date of birth.

The issue was traced to the synthetic laboratory generator.

The original generation logic selected unlinked laboratory dates across the entire study period without considering the patient's date of birth.

This resulted in synthetic laboratory measurements occurring before some patients were born.

The generator was corrected so that unlinked laboratory measurements are generated no earlier than:

MAX(
    study start date,
    patient date of birth
)

The patient date of birth was also explicitly parsed as a datetime value before laboratory dates were generated.

The validation logic was expanded to check:

result_date >= patient.date_of_birth

The laboratory dataset was then regenerated.

The corrected generation produced:

1,408,495

laboratory results.

After correction:

Laboratory results before birth:

0

Laboratory results outside the study period:

0

The corrected laboratory dataset was loaded into a staging table and fully validated before production insertion.

This demonstrates the use of validation-driven development to identify and correct a synthetic-data generation defect.

---

# 12. Laboratory Staging Validation

A persistent staging table was created:

lab_results_stage

The staging table was populated from the corrected laboratory CSV.

Rows loaded:

1,408,495

Staging validation results:

| Validation | Result |
|---|---:|
| Rows | 1,408,495 |
| Unique lab IDs | 1,408,495 |
| Unique patients | 100,000 |
| Unlinked labs | 492,871 |
| Missing values | 0 |
| Missing patients | 0 |
| Missing encounters | 0 |
| Patient/encounter mismatches | 0 |
| Labs before birth | 0 |
| Labs outside study | 0 |

Only after the staging validation passed was the corrected data inserted into the production lab_results table.

---

# 13. Medication Dataset Validation

The medication dataset contains:

114,123

records.

The dataset contains medication orders associated with synthetic patients and, where applicable, encounters.

Validation results:

- Medication rows: 114,123
- Unique medication order IDs: 114,123
- Unique patients: 47,381
- Unlinked medication orders: 75,568
- Missing medication codes: 0
- Missing status values: 0
- Invalid medication dates: 0
- Invalid encounter links: 0
- Encounter-period violations: 0

Medication order dates were validated against:

- Patient date of birth
- Study start date
- Study end date
- Medication start date
- Medication end date

Final production temporal validation:

| Validation | Result |
|---|---:|
| Medications before birth | 0 |
| Orders before birth | 0 |
| Invalid end dates | 0 |
| Medications outside study | 0 |

Medication date range:

Earliest:
2015-01-01

Latest:
2025-12-31

The medication dataset passed validation.

---

# 14. Clinical Notes Dataset Validation

The clinical notes dataset contains:

1,401,000

records.

Validation results:

- Note rows: 1,401,000
- Unique note IDs: 1,401,000
- Unique patients: 100,000
- Unlinked notes: 7,989
- Missing note types: 0
- Empty note text: 0
- Invalid encounter links: 0
- Patient/encounter mismatches: 0
- Notes before patient birth: 0
- Notes after patient death: 0
- Linked note date mismatches: 0

Final note date range:

Earliest:
2015-01-01 01:04:00

Latest:
2025-12-31 21:48:10

The clinical notes dataset passed validation.

---

# 15. Procedure Dataset Validation

The procedure dataset contains:

211,638

records.

Procedure codes include:

| Procedure Code | Records |
|---|---:|
| CHEST_XRAY | 53,013 |
| COLONOSCOPY | 21,190 |
| CT_CHEST | 35,752 |
| ECG | 63,658 |
| ECHO | 38,025 |

Linked procedures:

180,225

Unlinked procedures:

31,413

Validation results:

- Procedure rows: 211,638
- Unique procedure IDs: 211,638
- Unique patients: 87,062
- Missing research IDs: 0
- Invalid procedure codes: 0
- Invalid encounter links: 0
- Patient/encounter mismatches: 0
- Procedures before patient birth: 0
- Procedures outside study period: 0
- Linked procedure date mismatches: 0

Final procedure date range:

Earliest:
2015-01-01 07:32:51

Latest:
2025-12-31 18:50:32

The procedure dataset passed validation.

---

# 16. Cross-Table Foreign-Key Validation

Each major clinical relationship was independently validated.

The following relationships were checked.

## 16.1 Encounters to Patients

Broken encounter-to-patient references:

0

---

## 16.2 Diagnoses to Patients

Broken diagnosis-to-patient references:

0

---

## 16.3 Diagnoses to Encounters

Broken diagnosis-to-encounter references:

0

Only diagnosis records containing an encounter_id were evaluated for this relationship.

---

## 16.4 Laboratory Results to Patients

Broken laboratory-to-patient references:

0

---

## 16.5 Laboratory Results to Encounters

Broken laboratory-to-encounter references:

0

Only laboratory results containing an encounter_id were evaluated for this relationship.

---

## 16.6 Medication Orders to Patients

Broken medication-to-patient references:

0

---

## 16.7 Medication Orders to Encounters

Broken medication-to-encounter references:

0

Only medication orders containing an encounter_id were evaluated for this relationship.

---

## 16.8 Clinical Notes to Patients

Broken clinical-note-to-patient references:

0

---

## 16.9 Clinical Notes to Encounters

Broken clinical-note-to-encounter references:

0

Only clinical notes containing an encounter_id were evaluated for this relationship.

---

## 16.10 Procedures to Patients

Broken procedure-to-patient references:

0

---

## 16.11 Procedures to Encounters

Broken procedure-to-encounter references:

0

---

# 17. Cross-Table Relationship Summary

| Relationship | Broken References |
|---|---:|
| encounters → patients | 0 |
| diagnoses → patients | 0 |
| diagnoses → encounters | 0 |
| lab_results → patients | 0 |
| lab_results → encounters | 0 |
| medication_orders → patients | 0 |
| medication_orders → encounters | 0 |
| clinical_notes → patients | 0 |
| clinical_notes → encounters | 0 |
| procedures → patients | 0 |
| procedures → encounters | 0 |

All independently tested relationships passed.

---

# 18. Intentional Unlinked Records

Several clinical datasets intentionally allow records without an encounter_id.

These records are not considered data-quality failures.

The reason is that real-world clinical data can contain records that are associated with a patient but are not directly tied to a specific encounter.

The validated unlinked-record counts are:

| Dataset | Unlinked Records |
|---|---:|
| diagnoses | 53,893 |
| lab_results | 492,871 |
| medication_orders | 75,568 |
| clinical_notes | 7,989 |
| procedures | 31,413 |

These records remain linked to a valid patient.

Therefore:

Unlinked encounter relationship does not mean unlinked patient relationship.

This distinction is intentional in the synthetic data model.

---

# 19. Temporal Integrity Summary

The synthetic clinical data covers the study period:

2015-01-01 through 2025-12-31

Temporal validation was performed for all major event-based datasets.

| Dataset | Before Birth | Outside Study | Status |
|---|---:|---:|---|
| encounters | 0 | 0 | PASS |
| diagnoses | 0 | 0 | PASS |
| lab_results | 0 | 0 | PASS |
| medication_orders | 0 | 0 | PASS |
| clinical_notes | 0 | 0 | PASS |
| procedures | 0 | 0 | PASS |

All event datasets passed temporal validation.

---

# 20. Reference-Code Validation

The synthetic clinical datasets use controlled reference values.

Reference tables include:

- diagnosis_codes
- encounter_types
- facilities
- lab_tests
- medication_codes
- note_types
- procedure_codes
- providers

Validation was performed to ensure generated records use valid reference codes.

Results:

- Invalid encounter types: 0
- Invalid diagnosis codes: 0
- Invalid laboratory test codes: 0
- Invalid medication codes: 0
- Invalid note types: 0
- Invalid procedure codes: 0

All reference-code validations passed.

---

# 21. Primary-Key Validation

Primary identifiers were checked for uniqueness during synthetic-data generation and loading.

Validated identifiers include:

- patient research_id
- encounter_id
- lab_result_id
- medication_order_id
- note_id
- procedure_id

Results:

| Identifier | Duplicate Count |
|---|---:|
| research_id | 0 |
| encounter_id | 0 |
| lab_result_id | 0 |
| medication_order_id | 0 |
| note_id | 0 |
| procedure_id | 0 |

The generated datasets contain no duplicate primary identifiers in the validated production records.

---

# 22. Production Data Summary

The final validated production database contains:

Patients:

100,000

Encounters:

1,151,313

Diagnoses:

56,531

Laboratory results:

1,408,495

Medication orders:

114,123

Clinical notes:

1,401,000

Procedures:

211,638

Total records:

4,463,110

All major datasets were successfully loaded into PostgreSQL.

---

# 23. Database Integrity Status

The following validation categories have passed:

[PASS] Patient identifiers

[PASS] Encounter identifiers

[PASS] Laboratory identifiers

[PASS] Medication identifiers

[PASS] Clinical note identifiers

[PASS] Procedure identifiers

[PASS] Patient references

[PASS] Encounter references

[PASS] Patient/encounter consistency

[PASS] Reference-code integrity

[PASS] Encounter temporal integrity

[PASS] Diagnosis temporal integrity

[PASS] Laboratory temporal integrity

[PASS] Medication temporal integrity

[PASS] Clinical note temporal integrity

[PASS] Procedure temporal integrity

[PASS] Laboratory value validation

[PASS] Medication date validation

[PASS] Clinical note text validation

[PASS] Procedure code validation

[PASS] Production loading validation

---

# 24. Database Trigger Validation

The database includes application-level and database-level protections against invalid patient/encounter temporal relationships.

The encounter validation trigger prevents an encounter from occurring before the patient's date of birth.

The patient validation trigger prevents changes to a patient's date-of-birth or death-date values when those changes would conflict with existing encounters.

Both behaviors were tested successfully.

This provides an additional layer of protection beyond synthetic-data generator validation.

---

# 25. Staging Strategy

The project uses staging tables during bulk data loading.

The general loading workflow is:

1. Generate synthetic CSV data.
2. Validate the CSV independently.
3. Load CSV into a staging table.
4. Validate staging data.
5. Resolve research identifiers to production patient IDs.
6. Insert validated data into production tables.
7. Validate production relationships.
8. Validate production temporal integrity.
9. Preserve staging tables temporarily for troubleshooting and reload operations.

This approach reduces the risk of corrupting production tables with invalid synthetic records.

---

# 26. Laboratory Staging and Reload Process

The laboratory layer demonstrated the value of the staging strategy.

The initial laboratory dataset contained 23,173 records occurring before patient birth.

The problem was detected in staging before the corrected production dataset was finalized.

The workflow was:

1. Detect temporal defect.
2. Trace defect to synthetic generator.
3. Correct patient DOB handling.
4. Correct random measurement-date generation.
5. Recompile the generator.
6. Regenerate the laboratory dataset.
7. Validate the regenerated CSV.
8. Truncate laboratory staging table.
9. Reload corrected CSV into staging.
10. Validate staging.
11. Truncate production lab_results.
12. Insert corrected staging data into production.
13. Validate production relationships.
14. Validate production temporal integrity.

Final laboratory validation:

0 records before patient birth.

This process is documented as an example of controlled data-quality remediation.

---

# 27. Infrastructure Validation

The PostgreSQL container is running successfully under Docker Compose.

Container:

research-cohort-postgres

PostgreSQL:

16

Port mapping:

5432:5432

The database remained available throughout the data-generation and loading workflow.

---

# 28. Docker Shared-Memory Observation

During an attempted large combined cross-table validation query, PostgreSQL returned:

ERROR: could not resize shared memory segment to 4194304 bytes: No space left on device

The issue was investigated.

The Docker container showed approximately:

64 MB

of shared memory available through /dev/shm.

Host disk space was not the limiting factor.

The host filesystem had substantial free space remaining.

The issue was therefore identified as a Docker/PostgreSQL shared-memory limitation associated with the large query execution rather than a database disk-space problem.

No production data was lost.

No production data was corrupted.

No database configuration changes were required.

The combined validation query was replaced with smaller independent relationship checks.

All individual relationship checks subsequently completed successfully with zero broken references.

This demonstrates that validation queries should be designed with resource constraints in mind when working with large synthetic datasets.

---

# 29. Validation Methodology

Validation was performed at multiple layers.

## Layer 1: Generator Validation

Each Python synthetic-data generator validates its own output before completion.

Examples include:

- Missing identifiers
- Duplicate identifiers
- Invalid reference codes
- Invalid dates
- Invalid relationships
- Missing values
- Out-of-range values

---

## Layer 2: CSV Validation

Generated CSV files were independently inspected for:

- Row count
- Identifier uniqueness
- Patient coverage
- Missing values
- Date ranges
- Relationship identifiers
- File size
- Header correctness

---

## Layer 3: Staging Validation

CSV data was loaded into staging tables.

Staging tables were checked for:

- Duplicate IDs
- Missing patient identifiers
- Missing encounter identifiers
- Invalid reference codes
- Invalid dates
- Patient/encounter mismatches
- Temporal violations

---

## Layer 4: Production Validation

After insertion into production tables, data was validated again.

Production validation included:

- Row counts
- Identifier uniqueness
- Foreign-key relationships
- Patient relationships
- Encounter relationships
- Temporal relationships
- Reference-code integrity

---

## Layer 5: Database Constraint Validation

Database constraints and triggers were tested directly.

This confirms that invalid relationships cannot simply be introduced through application-level logic.

---

# 30. Data Quality Principles Demonstrated

The current database implementation demonstrates several important data-engineering principles.

## 30.1 Validate before loading

Synthetic data is validated before being inserted into production tables.

## 30.2 Validate after loading

Production data is independently validated after insertion.

## 30.3 Maintain referential integrity

Clinical records are linked to valid synthetic patients and, where applicable, valid encounters.

## 30.4 Enforce temporal integrity

Clinical events cannot occur before patient birth.

## 30.5 Separate staging from production

Staging tables provide a controlled location for bulk-loading and validation.

## 30.6 Preserve intentional missing relationships

Records without encounter links are permitted when they are intentional.

## 30.7 Use database-level safeguards

Database triggers provide protection against invalid patient/encounter date relationships.

## 30.8 Investigate failures rather than ignoring them

The initial laboratory temporal defect was investigated, corrected, regenerated, and revalidated.

---

# 31. Current Production Status

The production synthetic clinical database is considered:

VALIDATED

The following conditions are satisfied:

- 100,000 synthetic patients loaded
- 1,151,313 encounters loaded
- 56,531 diagnoses loaded
- 1,408,495 laboratory results loaded
- 114,123 medication orders loaded
- 1,401,000 clinical notes loaded
- 211,638 procedures loaded
- 4,463,110 total clinical records
- No broken patient references
- No broken encounter references
- No patient/encounter mismatches
- No temporal records before patient birth
- No event records outside the study period
- No invalid reference codes
- No duplicate validated identifiers
- No missing required patient identifiers
- No missing required clinical values
- No invalid laboratory values
- No invalid medication dates
- No invalid clinical note records
- No invalid procedure records

---

# 32. Known Design Characteristics

The following characteristics are intentional and should not be interpreted as defects.

## 32.1 Unlinked clinical records

Some diagnoses, laboratory results, medication orders, clinical notes, and procedures do not have an encounter_id.

These records remain linked to a valid patient.

## 32.2 Synthetic distributions

Clinical event distributions are generated synthetically and are intended for software development, database engineering, analytics testing, and demonstration purposes.

They are not intended to represent actual clinical prevalence.

## 32.3 Synthetic clinical values

Laboratory values and clinical events are synthetic.

They must not be interpreted as real patient measurements.

## 32.4 Study period

The current synthetic clinical event study period is:

2015-01-01 through 2025-12-31

---

# 33. Development Baseline

The validated database now provides a stable baseline for development of the Research Cohort Explorer application.

The next application layers can use the validated data without requiring immediate regeneration of the existing clinical datasets.

The database is suitable for development of:

- Cohort construction
- SQL cohort queries
- Research population filtering
- Clinical phenotype logic
- Patient-level analytics
- Encounter analytics
- Laboratory trend analysis
- Medication analysis
- Diagnosis analysis
- Procedure analysis
- Clinical-note analysis
- Attrition analysis
- Data-quality dashboards
- Cohort summaries
- Research feasibility analysis
- Provenance tracking
- Audit logging

---

# 34. Recommended Next Development Phase

The next development phase should focus on the application and analytics layer.

Recommended sequence:

1. Create database views for common analytical entities.
2. Create cohort-definition tables.
3. Create cohort membership tables.
4. Implement cohort query logic.
5. Add SQL query generation.
6. Add cohort-size calculations.
7. Add cohort attrition analysis.
8. Add data-quality metrics.
9. Add provenance tracking.
10. Add audit logging.
11. Build FastAPI backend endpoints.
12. Build React/TypeScript frontend.
13. Add authentication and authorization.
14. Add testing.
15. Add performance benchmarking.
16. Add documentation for research workflows.

---

# 35. Validation Conclusion

The Research Cohort Explorer synthetic clinical database has completed the current database validation phase.

The final production dataset contains:

4,463,110

records across seven primary clinical datasets.

All major patient, encounter, diagnosis, laboratory, medication, clinical-note, and procedure datasets passed their respective validation checks.

All independently tested patient and encounter relationships returned zero broken references.

All temporal integrity checks returned zero records occurring before patient birth.

All clinical event datasets remained within the defined study period.

The laboratory generation defect involving 23,173 pre-birth laboratory results was identified, corrected at the generator level, regenerated, staged, and successfully reloaded into production.

The final laboratory production validation returned zero pre-birth results.

Database-level patient/encounter temporal safeguards were also tested successfully.

The database is therefore considered ready to serve as the validated synthetic-data foundation for the next phase of the Research Cohort Explorer project.

---

# 36. Final Validation Status

OVERALL STATUS:

PASS

DATABASE STATUS:

VALIDATED

DATA TYPE:

SYNTHETIC ONLY

PRODUCTION RECORDS:

4,463,110

PATIENTS:

100,000

BROKEN PATIENT REFERENCES:

0

BROKEN ENCOUNTER REFERENCES:

0

PATIENT/ENCOUNTER MISMATCHES:

0

PRE-BIRTH CLINICAL EVENTS:

0

OUT-OF-STUDY CLINICAL EVENTS:

0

INVALID REFERENCE CODES:

0

DUPLICATE VALIDATED IDENTIFIERS:

0

LABORATORY RESULTS BEFORE BIRTH:

0

DATABASE TEMPORAL TRIGGER TEST:

PASS

STAGING VALIDATION:

PASS

PRODUCTION VALIDATION:

PASS

OVERALL:

PASS

---

# End of Database Validation Report