-- ============================================================
-- Synthetic Reference Data
-- ============================================================


-- ============================================================
-- Diagnosis Codes
-- ============================================================

INSERT INTO diagnosis_codes
    (diagnosis_code, description, category)
VALUES
    ('E11.9', 'Type 2 diabetes mellitus without complications', 'Endocrine'),
    ('I10', 'Essential hypertension', 'Cardiovascular'),
    ('E78.5', 'Hyperlipidemia, unspecified', 'Metabolic'),
    ('N18.3', 'Chronic kidney disease, stage 3', 'Renal'),
    ('J45.909', 'Asthma, unspecified', 'Respiratory'),
    ('I25.10', 'Atherosclerotic heart disease', 'Cardiovascular');


-- ============================================================
-- Laboratory Tests
-- ============================================================

INSERT INTO lab_tests
    (test_code, test_name, default_unit)
VALUES
    ('HBA1C', 'Hemoglobin A1c', '%'),
    ('GLUCOSE', 'Glucose', 'mg/dL'),
    ('CREAT', 'Creatinine', 'mg/dL'),
    ('LDL', 'LDL Cholesterol', 'mg/dL'),
    ('HDL', 'HDL Cholesterol', 'mg/dL'),
    ('BP_SYS', 'Systolic Blood Pressure', 'mmHg');


-- ============================================================
-- Medication Codes
-- ============================================================

INSERT INTO medication_codes
    (medication_code, medication_name, medication_class)
VALUES
    ('METFORMIN', 'Metformin', 'Antidiabetic'),
    ('LISINOPRIL', 'Lisinopril', 'ACE Inhibitor'),
    ('ATORVASTATIN', 'Atorvastatin', 'Statin'),
    ('AMLODIPINE', 'Amlodipine', 'Calcium Channel Blocker'),
    ('ALBUTEROL', 'Albuterol', 'Bronchodilator');


-- ============================================================
-- Procedure Codes
-- ============================================================

INSERT INTO procedure_codes
    (procedure_code, procedure_name, category)
VALUES
    ('ECG', 'Electrocardiogram', 'Cardiology'),
    ('ECHO', 'Echocardiogram', 'Cardiology'),
    ('CHEST_XRAY', 'Chest X-Ray', 'Radiology'),
    ('COLONOSCOPY', 'Colonoscopy', 'Gastroenterology'),
    ('CT_CHEST', 'CT Chest', 'Radiology');


-- ============================================================
-- Encounter Types
-- ============================================================

INSERT INTO encounter_types
    (encounter_type_code, description, category)
VALUES
    ('ED', 'Emergency Department', 'Acute Care'),
    ('OFFICE', 'Office Visit', 'Outpatient'),
    ('INPATIENT', 'Inpatient Admission', 'Inpatient'),
    ('TELEHEALTH', 'Telehealth Visit', 'Outpatient'),
    ('URGENT_CARE', 'Urgent Care Visit', 'Acute Care');


-- ============================================================
-- Facilities
-- ============================================================

INSERT INTO facilities
    (facility_code, facility_name, facility_type, city, state)
VALUES
    ('FAC-001', 'Northwoods Medical Center', 'Hospital', 'Marshfield', 'WI'),
    ('FAC-002', 'Northwoods Clinic East', 'Clinic', 'Marshfield', 'WI'),
    ('FAC-003', 'Northwoods Urgent Care', 'Urgent Care', 'Spencer', 'WI');


-- ============================================================
-- Providers
-- ============================================================

INSERT INTO providers
    (provider_code, provider_type, specialty)
VALUES
    ('PRV-001', 'Physician', 'Internal Medicine'),
    ('PRV-002', 'Physician', 'Cardiology'),
    ('PRV-003', 'Physician', 'Endocrinology'),
    ('PRV-004', 'Nurse Practitioner', 'Family Medicine'),
    ('PRV-005', 'Physician Assistant', 'Emergency Medicine');


-- ============================================================
-- Clinical Note Types
-- ============================================================

INSERT INTO note_types
    (note_type_code, description, category)
VALUES
    ('PROGRESS', 'Progress Note', 'Clinical'),
    ('CONSULT', 'Consultation Note', 'Clinical'),
    ('DISCHARGE', 'Discharge Summary', 'Clinical'),
    ('NURSING', 'Nursing Note', 'Clinical'),
    ('ED_NOTE', 'Emergency Department Note', 'Emergency');