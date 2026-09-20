-- ============================================================
-- Research Cohort Explorer
-- Cohort Engine: Evaluate Cohort
-- ============================================================

WITH criterion_1 AS (
    SELECT value_text AS diagnosis_code
    FROM cohort_criteria
    WHERE cohort_definition_id = :'cohort_id'
      AND criterion_order = 1
      AND criterion_type = 'inclusion'
      AND domain = 'diagnosis'
      AND field_name = 'diagnosis_code'
      AND operator = '='
),
criterion_2 AS (
    SELECT value_text::INTEGER AS minimum_age
    FROM cohort_criteria
    WHERE cohort_definition_id = :'cohort_id'
      AND criterion_order = 2
      AND criterion_type = 'inclusion'
      AND domain = 'demographics'
      AND field_name = 'age_at_study_end'
      AND operator = '>='
),
criterion_3 AS (
    SELECT value_text::DATE AS minimum_recorded_date
    FROM cohort_criteria
    WHERE cohort_definition_id = :'cohort_id'
      AND criterion_order = 3
      AND criterion_type = 'inclusion'
      AND domain = 'diagnosis'
      AND field_name = 'recorded_date'
      AND operator = '>='
),
criterion_4 AS (
    SELECT value_text::DATE AS maximum_recorded_date
    FROM cohort_criteria
    WHERE cohort_definition_id = :'cohort_id'
      AND criterion_order = 4
      AND criterion_type = 'inclusion'
      AND domain = 'diagnosis'
      AND field_name = 'recorded_date'
      AND operator = '<='
)
SELECT COUNT(DISTINCT d.patient_id) AS final_cohort_count
FROM vw_diagnoses d
JOIN vw_patient_demographics p
    ON p.patient_id = d.patient_id
CROSS JOIN criterion_1 c1
CROSS JOIN criterion_2 c2
CROSS JOIN criterion_3 c3
CROSS JOIN criterion_4 c4
WHERE d.diagnosis_code = c1.diagnosis_code
  AND p.age_at_study_end >= c2.minimum_age
  AND d.recorded_date >= c3.minimum_recorded_date
  AND d.recorded_date <= c4.maximum_recorded_date;
