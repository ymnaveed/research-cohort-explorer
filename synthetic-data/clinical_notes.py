import csv
import random
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from config import SEED, STUDY_START_DATE, STUDY_END_DATE


# ============================================================
# Research Cohort Explorer
# Synthetic Clinical Notes Generator
# ============================================================
#
# Generates synthetic clinical notes using:
#   - Existing synthetic patients
#   - Existing synthetic encounters
#   - Existing synthetic diagnoses
#   - Existing synthetic medications
#
# Output:
#   synthetic-data/output/clinical_notes.csv
#
# IMPORTANT:
#   This generator creates synthetic text only.
#   No real patient information is used.
# ============================================================


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

PATIENTS_FILE = OUTPUT_DIR / "patients.csv"
ENCOUNTERS_FILE = OUTPUT_DIR / "encounters.csv"
DIAGNOSES_FILE = OUTPUT_DIR / "diagnoses.csv"
MEDICATIONS_FILE = OUTPUT_DIR / "medications.csv"
OUTPUT_FILE = OUTPUT_DIR / "clinical_notes.csv"


STUDY_START = date.fromisoformat(STUDY_START_DATE)
STUDY_END = date.fromisoformat(STUDY_END_DATE)


# ============================================================
# Reference descriptions
# ============================================================

DIAGNOSIS_DESCRIPTIONS = {
    "E11.9": "type 2 diabetes mellitus without complications",
    "E78.5": "hyperlipidemia",
    "I10": "essential hypertension",
    "I25.10": "atherosclerotic heart disease",
    "J45.909": "asthma",
    "N18.3": "chronic kidney disease, stage 3",
}

MEDICATION_DESCRIPTIONS = {
    "METFORMIN": "metformin",
    "LISINOPRIL": "lisinopril",
    "AMLODIPINE": "amlodipine",
    "ATORVASTATIN": "atorvastatin",
    "ALBUTEROL": "albuterol",
}


VALID_NOTE_TYPES = {
    "CONSULT",
    "DISCHARGE",
    "ED_NOTE",
    "NURSING",
    "PROGRESS",
}


# ============================================================
# Utility functions
# ============================================================

def load_csv(path):
    """Load a CSV file into a list of dictionaries."""

    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def parse_date(value):
    """Parse YYYY-MM-DD date values."""

    if not value:
        return None

    return date.fromisoformat(str(value)[:10])


def parse_datetime(value):
    """Parse common ISO/timestamp formats."""

    if not value:
        return None

    text = str(value).strip()

    # Handle trailing Z
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    dt = datetime.fromisoformat(text)

    # Convert timezone-aware values to naive values for CSV output.
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)

    return dt


def format_datetime(value):
    """Format datetime consistently for CSV output."""

    return value.strftime("%Y-%m-%d %H:%M:%S")


def clamp_datetime_to_patient(dt, patient):
    """Ensure a note timestamp is within the patient's valid lifetime."""

    dob = parse_date(patient["date_of_birth"])
    death_date = parse_date(patient.get("death_date"))

    if dt.date() < dob:
        dt = datetime.combine(dob, datetime.min.time())

    if death_date is not None and dt.date() > death_date:
        dt = datetime.combine(death_date, datetime.min.time())

    return dt


def choose_time_offset(max_minutes=120):
    """Return a small deterministic random time offset."""

    return timedelta(minutes=random.randint(0, max_minutes))


# ============================================================
# Clinical context helpers
# ============================================================

def get_patient_diagnoses(diagnoses_by_patient, research_id):
    """Return diagnosis descriptions for a patient."""

    diagnoses = diagnoses_by_patient.get(research_id, [])

    descriptions = []

    for diagnosis in diagnoses:
        code = diagnosis.get("diagnosis_code", "")
        description = DIAGNOSIS_DESCRIPTIONS.get(code)

        if description and description not in descriptions:
            descriptions.append(description)

    return descriptions


def get_patient_medications(medications_by_patient, research_id):
    """Return medication descriptions for a patient."""

    medications = medications_by_patient.get(research_id, [])

    descriptions = []

    for medication in medications:
        code = medication.get("medication_code", "")
        description = MEDICATION_DESCRIPTIONS.get(code)

        if description and description not in descriptions:
            descriptions.append(description)

    return descriptions


def diagnosis_context(diagnoses):
    """Create a short synthetic diagnosis summary."""

    if not diagnoses:
        return "No chronic diagnosis was specifically documented in this synthetic note."

    selected = diagnoses[:3]

    if len(selected) == 1:
        return f"Relevant history includes {selected[0]}."

    if len(selected) == 2:
        return f"Relevant history includes {selected[0]} and {selected[1]}."

    return (
        f"Relevant history includes {selected[0]}, "
        f"{selected[1]}, and {selected[2]}."
    )


def medication_context(medications):
    """Create a short synthetic medication summary."""

    if not medications:
        return "No chronic medication was specifically documented."

    selected = medications[:3]

    if len(selected) == 1:
        return f"Medication history includes {selected[0]}."

    if len(selected) == 2:
        return f"Medication history includes {selected[0]} and {selected[1]}."

    return (
        f"Medication history includes {selected[0]}, "
        f"{selected[1]}, and {selected[2]}."
    )


# ============================================================
# Note text generators
# ============================================================

def generate_consult_note(patient, encounter, diagnoses, medications):
    """Generate a synthetic consultation note."""

    reason_options = [
        "routine follow-up",
        "evaluation of chronic conditions",
        "review of recent symptoms",
        "preventive care follow-up",
        "medication review",
        "ongoing disease management",
    ]

    assessment_options = [
        "Patient appears clinically stable during this synthetic encounter.",
        "Current findings are consistent with the patient's documented history.",
        "No acute complication is identified in the synthetic encounter data.",
        "Clinical status is appropriate for outpatient management.",
    ]

    plan_options = [
        "Continue current management and follow up as clinically indicated.",
        "Continue monitoring and reassess at the next scheduled visit.",
        "Review routine laboratory monitoring and continue follow-up.",
        "Maintain the current treatment plan with routine reassessment.",
    ]

    reason = random.choice(reason_options)
    assessment = random.choice(assessment_options)
    plan = random.choice(plan_options)

    return (
        f"Consultation note. Reason for visit: {reason}. "
        f"{diagnosis_context(diagnoses)} "
        f"{medication_context(medications)} "
        f"{assessment} "
        f"Plan: {plan}"
    )


def generate_progress_note(patient, encounter, diagnoses, medications):
    """Generate a synthetic progress note."""

    status_options = [
        "Patient is stable with no acute concerns documented.",
        "Patient reports no major interval change in the synthetic record.",
        "Clinical status remains stable based on available encounter information.",
        "Patient is being monitored without a new acute issue documented.",
    ]

    plan_options = [
        "Continue current treatment and routine monitoring.",
        "Continue established management and follow up as scheduled.",
        "Monitor symptoms and laboratory values as appropriate.",
        "Continue care plan with reassessment during follow-up.",
    ]

    status = random.choice(status_options)
    plan = random.choice(plan_options)

    return (
        f"Progress note. {status} "
        f"{diagnosis_context(diagnoses)} "
        f"{medication_context(medications)} "
        f"Plan: {plan}"
    )


def generate_ed_note(patient, encounter, diagnoses, medications):
    """Generate a synthetic emergency department note."""

    complaint_options = [
        "acute symptoms requiring evaluation",
        "new onset discomfort",
        "short-duration respiratory symptoms",
        "generalized symptoms",
        "evaluation of a reported change in condition",
        "non-specific acute complaint",
    ]

    disposition_options = [
        "Patient was assessed and discharged with routine follow-up instructions.",
        "Patient was evaluated and remained clinically stable during the synthetic encounter.",
        "Patient was discharged after evaluation with outpatient follow-up recommended.",
        "Patient remained under observation during the documented encounter.",
    ]

    complaint = random.choice(complaint_options)
    disposition = random.choice(disposition_options)

    return (
        f"Emergency department note. Chief concern: {complaint}. "
        f"{diagnosis_context(diagnoses)} "
        f"{medication_context(medications)} "
        f"Evaluation did not identify a specific acute complication in the synthetic data. "
        f"{disposition}"
    )


def generate_nursing_note(patient, encounter, diagnoses, medications):
    """Generate a synthetic nursing note."""

    observation_options = [
        "Patient resting comfortably at the time of documentation.",
        "Patient observed without acute distress.",
        "Routine nursing assessment completed.",
        "Patient's condition monitored according to the encounter plan.",
    ]

    care_options = [
        "Routine supportive care provided.",
        "Safety and comfort measures maintained.",
        "Monitoring continued according to the clinical plan.",
        "Patient education and routine care activities documented.",
    ]

    observation = random.choice(observation_options)
    care = random.choice(care_options)

    return (
        f"Nursing note. {observation} "
        f"{care} "
        f"{diagnosis_context(diagnoses)}"
    )


def generate_discharge_note(patient, encounter, diagnoses, medications):
    """Generate a synthetic discharge summary."""

    discharge_options = [
        "Patient discharged in stable condition.",
        "Patient completed the synthetic encounter and was discharged in stable condition.",
        "Discharge planning completed with routine follow-up recommended.",
        "Patient discharged after completion of the documented evaluation.",
    ]

    followup_options = [
        "Follow up with the appropriate outpatient provider.",
        "Continue routine clinical monitoring.",
        "Follow the established treatment plan and return for scheduled reassessment.",
        "Continue medications as documented and attend follow-up care.",
    ]

    discharge_statement = random.choice(discharge_options)
    followup = random.choice(followup_options)

    return (
        f"Discharge summary. {discharge_statement} "
        f"{diagnosis_context(diagnoses)} "
        f"{medication_context(medications)} "
        f"Follow-up plan: {followup}"
    )


def generate_note_text(
    note_type,
    patient,
    encounter,
    diagnoses,
    medications,
):
    """Dispatch note generation according to note type."""

    if note_type == "CONSULT":
        return generate_consult_note(
            patient,
            encounter,
            diagnoses,
            medications,
        )

    if note_type == "PROGRESS":
        return generate_progress_note(
            patient,
            encounter,
            diagnoses,
            medications,
        )

    if note_type == "ED_NOTE":
        return generate_ed_note(
            patient,
            encounter,
            diagnoses,
            medications,
        )

    if note_type == "NURSING":
        return generate_nursing_note(
            patient,
            encounter,
            diagnoses,
            medications,
        )

    if note_type == "DISCHARGE":
        return generate_discharge_note(
            patient,
            encounter,
            diagnoses,
            medications,
        )

    raise ValueError(f"Unsupported note type: {note_type}")


# ============================================================
# Note type selection
# ============================================================

def choose_note_types(encounter_type):
    """
    Determine how many and which note types to generate
    for a synthetic encounter.
    """

    if encounter_type == "ED":
        if random.random() < 0.20:
            return ["ED_NOTE", "NURSING"]

        return ["ED_NOTE"]

    if encounter_type == "INPATIENT":
        roll = random.random()

        if roll < 0.55:
            return ["PROGRESS", "NURSING"]

        if roll < 0.85:
            return ["PROGRESS", "NURSING", "DISCHARGE"]

        return ["PROGRESS"]

    if encounter_type in {
        "OFFICE",
        "TELEHEALTH",
        "URGENT_CARE",
    }:
        if random.random() < 0.12:
            return ["CONSULT", "PROGRESS"]

        return ["CONSULT"]

    return ["PROGRESS"]


# ============================================================
# Note date generation
# ============================================================

def generate_encounter_note_datetime(encounter):
    """
    Generate a note timestamp on the same calendar date
    as the associated encounter.
    """

    encounter_dt = parse_datetime(encounter["encounter_date"])

    note_dt = encounter_dt + choose_time_offset(120)

    # Keep note on the same calendar date as the encounter.
    if note_dt.date() != encounter_dt.date():
        note_dt = encounter_dt

    return note_dt


def generate_unlinked_note_datetime(patient, encounter_dates):
    """
    Generate a patient-level note without an encounter_id.

    To maintain temporal consistency, choose a date from one
    of the patient's existing encounter dates.
    """

    if encounter_dates:
        base_date = random.choice(encounter_dates)

        note_dt = datetime.combine(
            base_date,
            datetime.min.time(),
        ) + choose_time_offset(12 * 60)

    else:
        dob = parse_date(patient["date_of_birth"])

        earliest = max(STUDY_START, dob)

        death_date = parse_date(patient.get("death_date"))

        latest = STUDY_END

        if death_date is not None:
            latest = min(latest, death_date)

        if earliest > latest:
            return datetime.combine(earliest, datetime.min.time())

        available_days = (latest - earliest).days

        note_date = earliest + timedelta(
            days=random.randint(0, available_days)
        )

        note_dt = datetime.combine(
            note_date,
            datetime.min.time(),
        ) + choose_time_offset(12 * 60)

    return clamp_datetime_to_patient(note_dt, patient)


# ============================================================
# Main generation
# ============================================================

def generate_clinical_notes():
    """Generate the complete synthetic clinical notes dataset."""

    print("Generating synthetic clinical notes...")
    print(f"Random seed: {SEED}")

    random.seed(SEED)

    # --------------------------------------------------------
    # Load source datasets
    # --------------------------------------------------------

    patients = load_csv(PATIENTS_FILE)
    encounters = load_csv(ENCOUNTERS_FILE)
    diagnoses = load_csv(DIAGNOSES_FILE)
    medications = load_csv(MEDICATIONS_FILE)

    print(f"Patients loaded: {len(patients)}")
    print(f"Encounters loaded: {len(encounters)}")
    print(f"Diagnoses loaded: {len(diagnoses)}")
    print(f"Medications loaded: {len(medications)}")

    # --------------------------------------------------------
    # Build lookup structures
    # --------------------------------------------------------

    patients_by_research_id = {
        row["research_id"]: row
        for row in patients
    }

    encounters_by_patient = defaultdict(list)

    for encounter in encounters:
        research_id = encounter["research_id"]

        if research_id in patients_by_research_id:
            encounters_by_patient[research_id].append(encounter)

    diagnoses_by_patient = defaultdict(list)

    for diagnosis in diagnoses:
        research_id = diagnosis["research_id"]

        if research_id in patients_by_research_id:
            diagnoses_by_patient[research_id].append(diagnosis)

    medications_by_patient = defaultdict(list)

    for medication in medications:
        research_id = medication["research_id"]

        if research_id in patients_by_research_id:
            medications_by_patient[research_id].append(medication)

    # --------------------------------------------------------
    # Generate notes
    # --------------------------------------------------------

    notes = []

    note_id = 1

    # Encounter-linked notes
    for encounter in encounters:
        research_id = encounter["research_id"]

        patient = patients_by_research_id.get(research_id)

        if patient is None:
            continue

        encounter_type = encounter["encounter_type_code"]

        note_types = choose_note_types(encounter_type)

        patient_diagnoses = get_patient_diagnoses(
            diagnoses_by_patient,
            research_id,
        )

        patient_medications = get_patient_medications(
            medications_by_patient,
            research_id,
        )

        for note_type in note_types:

            note_dt = generate_encounter_note_datetime(
                encounter
            )

            note_dt = clamp_datetime_to_patient(
                note_dt,
                patient,
            )

            note_text = generate_note_text(
                note_type,
                patient,
                encounter,
                patient_diagnoses,
                patient_medications,
            )

            notes.append(
                {
                    "note_id": note_id,
                    "research_id": research_id,
                    "encounter_id": encounter["encounter_id"],
                    "note_date": format_datetime(note_dt),
                    "note_type_code": note_type,
                    "note_text": note_text,
                }
            )

            note_id += 1

    # --------------------------------------------------------
    # Generate a smaller number of patient-level notes
    # without an encounter link.
    # --------------------------------------------------------

    patient_level_note_count = 0

    for patient in patients:

        # Approximately 8% of patients receive one
        # additional patient-level note.
        if random.random() >= 0.08:
            continue

        research_id = patient["research_id"]

        patient_encounters = encounters_by_patient.get(
            research_id,
            [],
        )

        encounter_dates = []

        for encounter in patient_encounters:
            encounter_dt = parse_datetime(
                encounter["encounter_date"]
            )

            if encounter_dt is not None:
                encounter_dates.append(
                    encounter_dt.date()
                )

        note_type = random.choice(
            [
                "CONSULT",
                "PROGRESS",
                "NURSING",
            ]
        )

        note_dt = generate_unlinked_note_datetime(
            patient,
            encounter_dates,
        )

        patient_diagnoses = get_patient_diagnoses(
            diagnoses_by_patient,
            research_id,
        )

        patient_medications = get_patient_medications(
            medications_by_patient,
            research_id,
        )

        note_text = generate_note_text(
            note_type,
            patient,
            {},
            patient_diagnoses,
            patient_medications,
        )

        notes.append(
            {
                "note_id": note_id,
                "research_id": research_id,
                "encounter_id": "",
                "note_date": format_datetime(note_dt),
                "note_type_code": note_type,
                "note_text": note_text,
            }
        )

        note_id += 1
        patient_level_note_count += 1

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    print()
    print("Validation")

    note_ids = [
        int(row["note_id"])
        for row in notes
    ]

    duplicate_note_ids = len(note_ids) - len(set(note_ids))

    missing_research_id = sum(
        1
        for row in notes
        if not row["research_id"]
        or row["research_id"] not in patients_by_research_id
    )

    invalid_note_types = sum(
        1
        for row in notes
        if row["note_type_code"] not in VALID_NOTE_TYPES
    )

    empty_note_text = sum(
        1
        for row in notes
        if not row["note_text"].strip()
    )

    invalid_encounter_links = 0
    patient_encounter_mismatch = 0
    note_before_birth = 0
    note_after_death = 0
    linked_note_date_mismatch = 0

    encounters_by_id = {
        row["encounter_id"]: row
        for row in encounters
    }

    for row in notes:

        patient = patients_by_research_id.get(
            row["research_id"]
        )

        note_dt = parse_datetime(row["note_date"])

        if patient is None:
            continue

        dob = parse_date(
            patient["date_of_birth"]
        )

        death_date = parse_date(
            patient.get("death_date")
        )

        if note_dt.date() < dob:
            note_before_birth += 1

        if (
            death_date is not None
            and note_dt.date() > death_date
        ):
            note_after_death += 1

        encounter_id = row["encounter_id"]

        if encounter_id:

            encounter = encounters_by_id.get(
                encounter_id
            )

            if encounter is None:
                invalid_encounter_links += 1
                continue

            if (
                encounter["research_id"]
                != row["research_id"]
            ):
                patient_encounter_mismatch += 1

            encounter_dt = parse_datetime(
                encounter["encounter_date"]
            )

            if (
                encounter_dt is None
                or note_dt.date()
                != encounter_dt.date()
            ):
                linked_note_date_mismatch += 1

    print(f"Rows: {len(notes)}")
    print(f"Duplicate note_id: {duplicate_note_ids}")
    print(f"Missing/invalid research_id: {missing_research_id}")
    print(f"Invalid note_type_code: {invalid_note_types}")
    print(f"Empty note_text: {empty_note_text}")
    print(f"Invalid encounter links: {invalid_encounter_links}")
    print(
        "Patient/encounter mismatch: "
        f"{patient_encounter_mismatch}"
    )
    print(
        "Note before patient birth: "
        f"{note_before_birth}"
    )
    print(
        "Note after patient death: "
        f"{note_after_death}"
    )
    print(
        "Linked note date mismatch: "
        f"{linked_note_date_mismatch}"
    )
    print(
        "Patient-level unlinked notes: "
        f"{patient_level_note_count}"
    )

    validation_failed = (
        duplicate_note_ids > 0
        or missing_research_id > 0
        or invalid_note_types > 0
        or empty_note_text > 0
        or invalid_encounter_links > 0
        or patient_encounter_mismatch > 0
        or note_before_birth > 0
        or note_after_death > 0
        or linked_note_date_mismatch > 0
    )

    if validation_failed:
        raise ValueError(
            "Clinical notes validation failed."
        )

    print("Validation passed.")

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "note_id",
        "research_id",
        "encounter_id",
        "note_date",
        "note_type_code",
        "note_text",
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(notes)

    print()
    print("Generation complete.")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Clinical notes generated: {len(notes)}")


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    generate_clinical_notes()