# ============================================================
# Research Cohort Explorer
# Synthetic Procedure Generator
# ============================================================

import csv
import random
from collections import Counter
from datetime import datetime, date, timedelta
from pathlib import Path

from config import (
    SEED,
    STUDY_START_DATE,
    STUDY_END_DATE,
)


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

OUTPUT_DIR = Path(__file__).resolve().parent / "output"

PATIENTS_FILE = OUTPUT_DIR / "patients.csv"
ENCOUNTERS_FILE = OUTPUT_DIR / "encounters.csv"
OUTPUT_FILE = OUTPUT_DIR / "procedures.csv"

STUDY_START = date.fromisoformat(STUDY_START_DATE)
STUDY_END = date.fromisoformat(STUDY_END_DATE)

RANDOM_SEED = SEED


# Synthetic procedure distribution.
#
# These are modeling assumptions for the synthetic dataset and
# do not represent a real healthcare population.
PROCEDURE_DISTRIBUTION = {
    "ECG": 0.30,
    "CHEST_XRAY": 0.25,
    "ECHO": 0.18,
    "CT_CHEST": 0.17,
    "COLONOSCOPY": 0.10,
}


# Probability that a generated procedure is linked to an
# existing encounter.
ENCOUNTER_LINK_PROBABILITY = 0.85


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def parse_timestamp(value):
    return datetime.fromisoformat(value)


def random_date(start_date, end_date):
    """Return a random date between two dates, inclusive."""
    if start_date > end_date:
        return start_date

    delta = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, delta))


def weighted_choice(distribution):
    values = list(distribution.keys())
    weights = list(distribution.values())
    return random.choices(values, weights=weights, k=1)[0]


def generate_procedure_datetime(procedure_day):
    """Generate a synthetic timestamp during the selected day."""
    hour = random.randint(7, 18)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    return datetime(
        procedure_day.year,
        procedure_day.month,
        procedure_day.day,
        hour,
        minute,
        second,
    )


# ------------------------------------------------------------
# Load patients
# ------------------------------------------------------------

print("Generating synthetic procedures...")
print(f"Random seed: {RANDOM_SEED}")

random.seed(RANDOM_SEED)

patients = {}

with PATIENTS_FILE.open("r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        research_id = row["research_id"]

        dob = date.fromisoformat(row["date_of_birth"])

        patients[research_id] = {
            "date_of_birth": dob,
        }

print(f"Patients loaded: {len(patients)}")


# ------------------------------------------------------------
# Load encounters
# ------------------------------------------------------------

encounters_by_patient = {}

with ENCOUNTERS_FILE.open("r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        research_id = row["research_id"]

        encounter_date = parse_timestamp(row["encounter_date"])

        encounter = {
            "encounter_id": int(row["encounter_id"]),
            "encounter_date": encounter_date,
        }

        encounters_by_patient.setdefault(research_id, []).append(encounter)

print(f"Patients with encounters: {len(encounters_by_patient)}")


# ------------------------------------------------------------
# Generate procedures
# ------------------------------------------------------------

rows = []

procedure_id = 1

for research_id, patient in patients.items():

    patient_dob = patient["date_of_birth"]

    # Valid study period for this patient.
    valid_start = max(STUDY_START, patient_dob)
    valid_end = STUDY_END

    if valid_start > valid_end:
        continue

    patient_encounters = encounters_by_patient.get(
        research_id,
        []
    )

    encounter_count = len(patient_encounters)

    # Patients with more healthcare activity receive more
    # procedures. Keep the distribution bounded.
    if encounter_count <= 4:
        procedure_count = random.randint(0, 1)
    elif encounter_count <= 8:
        procedure_count = random.randint(0, 2)
    elif encounter_count <= 14:
        procedure_count = random.randint(1, 3)
    else:
        procedure_count = random.randint(2, 5)

    for _ in range(procedure_count):

        procedure_code = weighted_choice(
            PROCEDURE_DISTRIBUTION
        )

        encounter_id = None

        # Link to an existing encounter when possible.
        if (
            patient_encounters
            and random.random() < ENCOUNTER_LINK_PROBABILITY
        ):

            encounter = random.choice(patient_encounters)

            encounter_day = encounter["encounter_date"].date()

            # Linked procedure uses the same calendar date
            # as the encounter.
            procedure_day = encounter_day

            procedure_datetime = generate_procedure_datetime(
                procedure_day
            )

            encounter_id = encounter["encounter_id"]

        else:

            procedure_day = random_date(
                valid_start,
                valid_end,
            )

            procedure_datetime = generate_procedure_datetime(
                procedure_day
            )

        rows.append(
            {
                "procedure_id": procedure_id,
                "research_id": research_id,
                "encounter_id": encounter_id,
                "procedure_code": procedure_code,
                "procedure_date": procedure_datetime.isoformat(
                    sep=" "
                ),
            }
        )

        procedure_id += 1


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

print()
print("Validation")

duplicate_ids = len(rows) - len(
    {row["procedure_id"] for row in rows}
)

missing_research_ids = sum(
    1
    for row in rows
    if not row["research_id"]
)

invalid_codes = sum(
    1
    for row in rows
    if row["procedure_code"] not in PROCEDURE_DISTRIBUTION
)

invalid_encounters = 0
patient_encounter_mismatches = 0

procedures_before_birth = 0
procedures_outside_study = 0

encounter_date_mismatches = 0

encounter_lookup = {}

for research_id, patient_encounters in encounters_by_patient.items():
    for encounter in patient_encounters:
        encounter_lookup[encounter["encounter_id"]] = (
            research_id,
            encounter["encounter_date"],
        )


for row in rows:

    research_id = row["research_id"]

    patient = patients.get(research_id)

    if patient is None:
        missing_research_ids += 1
        continue

    procedure_datetime = parse_timestamp(
        row["procedure_date"]
    )

    procedure_day = procedure_datetime.date()

    if (
        procedure_day < STUDY_START
        or procedure_day > STUDY_END
    ):
        procedures_outside_study += 1

    if procedure_day < patient["date_of_birth"]:
        procedures_before_birth += 1

    if row["encounter_id"] is not None:

        encounter_id = row["encounter_id"]

        encounter_info = encounter_lookup.get(
            encounter_id
        )

        if encounter_info is None:
            invalid_encounters += 1

        else:
            encounter_research_id, encounter_datetime = (
                encounter_info
            )

            if encounter_research_id != research_id:
                patient_encounter_mismatches += 1

            if (
                procedure_day
                != encounter_datetime.date()
            ):
                encounter_date_mismatches += 1


# ------------------------------------------------------------
# Validation output
# ------------------------------------------------------------

print(f"Rows: {len(rows)}")
print(f"Duplicate procedure_id: {duplicate_ids}")
print(f"Missing research_id: {missing_research_ids}")
print(f"Invalid procedure codes: {invalid_codes}")
print(f"Invalid encounter links: {invalid_encounters}")
print(
    f"Patient/encounter mismatches: "
    f"{patient_encounter_mismatches}"
)
print(
    f"Procedure before patient birth: "
    f"{procedures_before_birth}"
)
print(
    f"Procedures outside study period: "
    f"{procedures_outside_study}"
)
print(
    f"Linked procedure date mismatches: "
    f"{encounter_date_mismatches}"
)


# ------------------------------------------------------------
# Distribution summary
# ------------------------------------------------------------

procedure_counts = Counter(
    row["procedure_code"]
    for row in rows
)

linked_count = sum(
    1
    for row in rows
    if row["encounter_id"] is not None
)

unlinked_count = len(rows) - linked_count

print()
print("Procedure distribution")

for code in sorted(procedure_counts):
    print(f"{code}: {procedure_counts[code]}")

print()
print(f"Linked procedures: {linked_count}")
print(f"Unlinked procedures: {unlinked_count}")


# ------------------------------------------------------------
# Final validation gate
# ------------------------------------------------------------

validation_errors = (
    duplicate_ids
    + missing_research_ids
    + invalid_codes
    + invalid_encounters
    + patient_encounter_mismatches
    + procedures_before_birth
    + procedures_outside_study
    + encounter_date_mismatches
)

if validation_errors > 0:
    raise RuntimeError(
        f"Procedure validation failed with "
        f"{validation_errors} error(s)."
    )

print()
print("Validation passed.")


# ------------------------------------------------------------
# Write output
# ------------------------------------------------------------

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open(
    "w",
    newline="",
    encoding="utf-8",
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "procedure_id",
            "research_id",
            "encounter_id",
            "procedure_code",
            "procedure_date",
        ],
    )

    writer.writeheader()
    writer.writerows(rows)


print()
print("Generation complete.")
print(f"Output file: {OUTPUT_FILE}")
print(f"Procedures generated: {len(rows)}")