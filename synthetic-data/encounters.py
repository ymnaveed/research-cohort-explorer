# ============================================================
# Research Cohort Explorer
# Synthetic Encounter Generator
# ============================================================

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path


# ------------------------------------------------------------
# Load configuration
# ------------------------------------------------------------

CONFIG_PATH = Path(__file__).parent / "config.py"

config_namespace = {}
exec(CONFIG_PATH.read_text(), config_namespace)

SEED = config_namespace["SEED"]
ENCOUNTERS_PER_PATIENT_MIN = config_namespace[
    "ENCOUNTERS_PER_PATIENT_MIN"
]
ENCOUNTERS_PER_PATIENT_MAX = config_namespace[
    "ENCOUNTERS_PER_PATIENT_MAX"
]
ENCOUNTER_TYPE_DISTRIBUTION = config_namespace[
    "ENCOUNTER_TYPE_DISTRIBUTION"
]
ENCOUNTER_DURATION_HOURS = config_namespace[
    "ENCOUNTER_DURATION_HOURS"
]
STUDY_START_DATE = date.fromisoformat(
    config_namespace["STUDY_START_DATE"]
)
STUDY_END_DATE = date.fromisoformat(
    config_namespace["STUDY_END_DATE"]
)

OUTPUT_DIR = Path(__file__).parent / "output"
PATIENTS_FILE = OUTPUT_DIR / "patients.csv"
ENCOUNTERS_FILE = OUTPUT_DIR / "encounters.csv"


# ------------------------------------------------------------
# Random number generator
# ------------------------------------------------------------

rng = random.Random(SEED)


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def weighted_choice(distribution):
    """Choose one value using the supplied probability distribution."""
    values = list(distribution.keys())
    weights = list(distribution.values())

    return rng.choices(values, weights=weights, k=1)[0]


def random_date(start_date, end_date):
    """Generate a random date between two dates, inclusive."""
    if start_date > end_date:
        raise ValueError(
            f"Invalid date range: {start_date} > {end_date}"
        )

    days = (end_date - start_date).days

    return start_date + timedelta(
        days=rng.randint(0, days)
    )


def random_datetime(start_date, end_date):
    """Generate a random timestamp between two dates."""
    selected_date = random_date(start_date, end_date)

    hour = rng.randint(7, 19)
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)

    return datetime(
        selected_date.year,
        selected_date.month,
        selected_date.day,
        hour,
        minute,
        second,
    )


def generate_discharge_date(encounter_date, encounter_type):
    """Generate a discharge timestamp based on encounter type."""

    min_hours, max_hours = ENCOUNTER_DURATION_HOURS[
        encounter_type
    ]

    duration_hours = rng.uniform(
        min_hours,
        max_hours,
    )

    discharge_date = encounter_date + timedelta(
        hours=duration_hours
    )

    # Do not allow discharge beyond the synthetic study period.
    study_end_datetime = datetime.combine(
        STUDY_END_DATE,
        datetime.max.time(),
    )

    if discharge_date > study_end_datetime:
        discharge_date = study_end_datetime

    return discharge_date


# ------------------------------------------------------------
# Load patients
# ------------------------------------------------------------

def load_patients():
    """Load patients from the generated patient CSV."""

    if not PATIENTS_FILE.exists():
        raise FileNotFoundError(
            f"Patient file not found: {PATIENTS_FILE}"
        )

    patients = []

    with PATIENTS_FILE.open(
        newline="",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            patients.append(
                {
                    "research_id": row["research_id"],
                    "date_of_birth": date.fromisoformat(
                        row["date_of_birth"]
                    ),
                }
            )

    return patients


# ------------------------------------------------------------
# Generate encounters
# ------------------------------------------------------------

def generate_encounters(patients):
    """Generate synthetic encounters for each patient."""

    encounters = []

    encounter_id = 1

    for patient in patients:

        birth_date = patient["date_of_birth"]

        # A patient cannot have an encounter before birth.
        earliest_date = max(
            STUDY_START_DATE,
            birth_date,
        )

        # Patients born after the study period cannot
        # have any encounters.
        if earliest_date > STUDY_END_DATE:
            continue

        encounter_count = rng.randint(
            ENCOUNTERS_PER_PATIENT_MIN,
            ENCOUNTERS_PER_PATIENT_MAX,
        )

        for _ in range(encounter_count):

            encounter_type = weighted_choice(
                ENCOUNTER_TYPE_DISTRIBUTION
            )

            encounter_datetime = random_datetime(
                earliest_date,
                STUDY_END_DATE,
            )

            discharge_datetime = generate_discharge_date(
                encounter_datetime,
                encounter_type,
            )

            encounters.append(
                {
                    "encounter_id": encounter_id,
                    "research_id": patient["research_id"],
                    "encounter_date": encounter_datetime,
                    "encounter_type_code": encounter_type,
                    "discharge_date": discharge_datetime,
                }
            )

            encounter_id += 1

    return encounters


# ------------------------------------------------------------
# Validate generated encounters
# ------------------------------------------------------------

def validate_encounters(encounters, patients):
    """Validate encounter dates against patient DOB."""

    patient_lookup = {
        patient["research_id"]: patient
        for patient in patients
    }

    errors = []

    for encounter in encounters:

        patient = patient_lookup[
            encounter["research_id"]
        ]

        birth_date = patient["date_of_birth"]

        encounter_date = encounter[
            "encounter_date"
        ]

        discharge_date = encounter[
            "discharge_date"
        ]

        if encounter_date.date() < birth_date:
            errors.append(
                (
                    encounter["encounter_id"],
                    "Encounter occurs before patient birth.",
                )
            )

        if discharge_date < encounter_date:
            errors.append(
                (
                    encounter["encounter_id"],
                    "Discharge occurs before encounter.",
                )
            )

    return errors


# ------------------------------------------------------------
# Write CSV
# ------------------------------------------------------------

def write_encounters(encounters):
    """Write generated encounters to CSV."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with ENCOUNTERS_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        fieldnames = [
            "encounter_id",
            "research_id",
            "encounter_date",
            "encounter_type_code",
            "discharge_date",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for encounter in encounters:

            writer.writerow(
                {
                    "encounter_id":
                        encounter["encounter_id"],

                    "research_id":
                        encounter["research_id"],

                    "encounter_date":
                        encounter[
                            "encounter_date"
                        ].isoformat(
                            sep=" "
                        ),

                    "encounter_type_code":
                        encounter[
                            "encounter_type_code"
                        ],

                    "discharge_date":
                        encounter[
                            "discharge_date"
                        ].isoformat(
                            sep=" "
                        ),
                }
            )


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    print("Generating synthetic encounters...")
    print(f"Random seed: {SEED}")

    patients = load_patients()

    print(f"Patients loaded: {len(patients)}")

    encounters = generate_encounters(
        patients
    )

    print(
        f"Encounters generated: {len(encounters)}"
    )

    errors = validate_encounters(
        encounters,
        patients,
    )

    if errors:

        print()
        print(
            f"Validation failed: {len(errors)} errors"
        )

        for encounter_id, message in errors[:10]:
            print(
                f"Encounter {encounter_id}: {message}"
            )

        raise SystemExit(1)

    print("Validation passed.")

    write_encounters(encounters)

    print()
    print("Generation complete.")
    print(
        f"Output file: {ENCOUNTERS_FILE}"
    )
    print(
        f"Encounters generated: {len(encounters)}"
    )


if __name__ == "__main__":
    main()