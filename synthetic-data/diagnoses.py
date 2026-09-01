import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

from config import SEED


random.seed(SEED)

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "output"
OUTPUT_FILE = INPUT_DIR / "diagnoses.csv"

PATIENTS_FILE = INPUT_DIR / "patients.csv"
ENCOUNTERS_FILE = INPUT_DIR / "encounters.csv"

STUDY_START_DATE = date(2015, 1, 1)
STUDY_END_DATE = date(2025, 12, 31)


# Diagnosis probabilities are approximate and intentionally synthetic.
# They are designed to create useful relationships for cohort analysis.
DIAGNOSIS_PROBABILITIES = {
    "E11.9": 0.08,   # Type 2 diabetes
    "I10": 0.20,     # Hypertension
    "E78.5": 0.18,   # Hyperlipidemia
    "N18.3": 0.03,   # CKD stage 3
    "J45.909": 0.08, # Asthma
    "I25.10": 0.02,  # ASCVD
}


def load_patients():
    patients = []

    with PATIENTS_FILE.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            patients.append(
                {
                    "research_id": row["research_id"],
                    "date_of_birth": date.fromisoformat(row["date_of_birth"]),
                }
            )

    return patients


def load_encounters():
    encounters = []

    with ENCOUNTERS_FILE.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            encounter_datetime = datetime.strptime(
                row["encounter_date"],
                "%Y-%m-%d %H:%M:%S"
            )

            encounters.append(
                {
                    "encounter_id": int(row["encounter_id"]),
                    "research_id": row["research_id"],
                    "encounter_date": encounter_datetime.date(),
                }
            )

    return encounters


def choose_diagnoses():
    selected = []

    for diagnosis_code, probability in DIAGNOSIS_PROBABILITIES.items():
        if random.random() < probability:
            selected.append(diagnosis_code)

    return selected


def random_date(start_date, end_date):
    if start_date > end_date:
        return start_date

    days = (end_date - start_date).days

    return start_date + timedelta(
        days=random.randint(0, days)
    )


def generate_diagnosis(patient, patient_encounters):
    diagnosis_codes = choose_diagnoses()
    records = []

    for diagnosis_code in diagnosis_codes:
        earliest_onset = max(
            STUDY_START_DATE,
            patient["date_of_birth"] + timedelta(days=5 * 365)
        )

        if earliest_onset > STUDY_END_DATE:
            continue

        onset_date = random_date(
            earliest_onset,
            STUDY_END_DATE
        )

        recorded_date = onset_date + timedelta(
            days=random.randint(0, 30)
        )

        if recorded_date > STUDY_END_DATE:
            recorded_date = STUDY_END_DATE

        eligible_encounters = [
            encounter
            for encounter in patient_encounters
            if onset_date
            <= encounter["encounter_date"]
            <= recorded_date
        ]

        encounter_id = None

        if eligible_encounters:
            encounter = random.choice(eligible_encounters)
            encounter_id = encounter["encounter_id"]

        diagnosis_type = (
            "PRIMARY"
            if random.random() < 0.70
            else "SECONDARY"
        )

        records.append({
            "research_id": patient["research_id"],
            "encounter_id": encounter_id,
            "diagnosis_code": diagnosis_code,
            "onset_date": onset_date.isoformat(),
            "recorded_date": recorded_date.isoformat(),
            "diagnosis_type": diagnosis_type,
        })

    return records


def validate_diagnoses(diagnoses, patients, encounters):
    patient_ids = {
        patient["research_id"]
        for patient in patients
    }

    encounter_ids = {
        encounter["encounter_id"]
        for encounter in encounters
    }

    assert len(diagnoses) > 0, "No diagnoses were generated."

    for diagnosis in diagnoses:

        assert diagnosis["research_id"] in patient_ids, (
            f"Unknown patient: {diagnosis['research_id']}"
        )

        if diagnosis["encounter_id"] is not None:
            assert diagnosis["encounter_id"] in encounter_ids, (
                f"Unknown encounter: {diagnosis['encounter_id']}"
            )

        onset_date = date.fromisoformat(diagnosis["onset_date"])
        recorded_date = date.fromisoformat(diagnosis["recorded_date"])

        assert STUDY_START_DATE <= onset_date <= STUDY_END_DATE
        assert STUDY_START_DATE <= recorded_date <= STUDY_END_DATE
        assert recorded_date >= onset_date

        assert diagnosis["diagnosis_code"] in DIAGNOSIS_PROBABILITIES

        assert diagnosis["diagnosis_type"] in {
            "PRIMARY",
            "SECONDARY",
        }

    print("Validation passed.")


def write_diagnoses(diagnoses):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "research_id",
        "encounter_id",
        "diagnosis_code",
        "onset_date",
        "recorded_date",
        "diagnosis_type",
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(diagnoses)


def main():
    print("Generating synthetic diagnoses...")
    print(f"Random seed: {SEED}")

    patients = load_patients()
    encounters = load_encounters()

    print(f"Patients loaded: {len(patients)}")
    print(f"Encounters loaded: {len(encounters)}")

    encounters_by_patient = {}

    for encounter in encounters:
        encounters_by_patient.setdefault(
            encounter["research_id"],
            []
        ).append(encounter)

    diagnoses = []

    for patient in patients:
        patient_encounters = encounters_by_patient.get(
            patient["research_id"],
            []
        )

        diagnoses.extend(
            generate_diagnosis(
                patient,
                patient_encounters
            )
        )

    validate_diagnoses(
        diagnoses,
        patients,
        encounters
    )

    write_diagnoses(diagnoses)

    print()
    print("Generation complete.")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Diagnoses generated: {len(diagnoses)}")


if __name__ == "__main__":
    main()