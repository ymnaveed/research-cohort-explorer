import csv
import random
from datetime import date, timedelta
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

SEED = 20260827

STUDY_START_DATE = date(2015, 1, 1)
STUDY_END_DATE = date(2025, 12, 31)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

PATIENT_FILE = OUTPUT_DIR / "patients.csv"
ENCOUNTER_FILE = OUTPUT_DIR / "encounters.csv"
DIAGNOSIS_FILE = OUTPUT_DIR / "diagnoses.csv"
OUTPUT_FILE = OUTPUT_DIR / "medications.csv"


# ============================================================
# Medication reference
# ============================================================

MEDICATIONS = {
    "METFORMIN": {
        "doses": [
            "500 mg",
            "850 mg",
            "1000 mg",
        ],
        "routes": [
            "ORAL",
        ],
    },

    "LISINOPRIL": {
        "doses": [
            "5 mg",
            "10 mg",
            "20 mg",
            "40 mg",
        ],
        "routes": [
            "ORAL",
        ],
    },

    "AMLODIPINE": {
        "doses": [
            "5 mg",
            "10 mg",
        ],
        "routes": [
            "ORAL",
        ],
    },

    "ATORVASTATIN": {
        "doses": [
            "10 mg",
            "20 mg",
            "40 mg",
            "80 mg",
        ],
        "routes": [
            "ORAL",
        ],
    },

    "ALBUTEROL": {
        "doses": [
            "90 mcg",
            "180 mcg",
        ],
        "routes": [
            "INHALATION",
        ],
    },
}


# ============================================================
# Diagnosis -> medication mappings
# ============================================================

DISEASE_MEDICATIONS = {
    "E11.9": [
        "METFORMIN",
    ],

    "I10": [
        "LISINOPRIL",
        "AMLODIPINE",
    ],

    "E78.5": [
        "ATORVASTATIN",
    ],

    "I25.10": [
        "ATORVASTATIN",
    ],

    "J45.909": [
        "ALBUTEROL",
    ],

    "N18.3": [
        "LISINOPRIL",
    ],
}


# ============================================================
# Utility functions
# ============================================================

def choose_status(end_date):
    """
    Choose medication order status based on the medication end date.
    """

    if end_date == STUDY_END_DATE:
        return "ACTIVE"

    return random.choices(
        [
            "COMPLETED",
            "DISCONTINUED",
        ],
        weights=[
            0.65,
            0.35,
        ],
        k=1,
    )[0]


def choose_medications(diseases):
    """
    Select medications based on the patient's diagnoses.
    """

    medications = set()

    for disease in diseases:

        for medication in DISEASE_MEDICATIONS.get(
            disease,
            [],
        ):
            medications.add(medication)

    # Some patients without a diagnosis may still have
    # background medication use in the synthetic dataset.
    if not medications and random.random() < 0.04:

        medications.add(
            random.choice(
                list(MEDICATIONS.keys())
            )
        )

    return sorted(medications)


def generate_order_dates(patient_dob):
    """
    Generate medication start/end dates within the patient's
    valid lifetime and the study period.

    Invariant:
        patient DOB <= start_date <= end_date <= study end
    """

    earliest_start = max(
        STUDY_START_DATE,
        patient_dob,
    )

    available_days = (
        STUDY_END_DATE - earliest_start
    ).days

    start_date = earliest_start + timedelta(
        days=random.randint(
            0,
            available_days,
        )
    )

    duration_days = random.randint(
        30,
        730,
    )

    end_date = start_date + timedelta(
        days=duration_days
    )

    if end_date >= STUDY_END_DATE:
        end_date = STUDY_END_DATE

    return start_date, end_date


# ============================================================
# Medication generation
# ============================================================

def generate_medication_orders(
    patients,
    encounters,
    diagnosis_by_patient,
):

    encounters_by_patient = {}

    for encounter in encounters:

        encounters_by_patient.setdefault(
            encounter["research_id"],
            [],
        ).append(encounter)

    results = []

    medication_order_id = 1

    for patient in patients:

        research_id = patient["research_id"]

        patient_dob = date.fromisoformat(
            patient["date_of_birth"]
        )

        diseases = diagnosis_by_patient.get(
            research_id,
            set(),
        )

        patient_encounters = encounters_by_patient.get(
            research_id,
            [],
        )

        medications = choose_medications(
            diseases
        )

        # Patients with more diagnoses are slightly more likely
        # to have multiple concurrent medications.
        if (
            len(diseases) >= 2
            and random.random() < 0.35
        ):

            additional_medication = random.choice(
                list(MEDICATIONS.keys())
            )

            medications = sorted(
                set(medications)
                | {additional_medication}
            )

        for medication_code in medications:

            order_count = random.choices(
                [
                    1,
                    2,
                    3,
                ],
                weights=[
                    0.65,
                    0.25,
                    0.10,
                ],
                k=1,
            )[0]

            for _ in range(order_count):

                # ------------------------------------------------
                # Generate medication dates constrained by DOB.
                # ------------------------------------------------

                start_date, end_date = (
                    generate_order_dates(
                        patient_dob
                    )
                )

                encounter_id = None

                # ------------------------------------------------
                # Optionally associate the medication order with
                # an encounter occurring during the medication
                # period.
                # ------------------------------------------------

                if (
                    patient_encounters
                    and random.random() < 0.60
                ):

                    eligible_encounters = [
    encounter
    for encounter
    in patient_encounters
    if (
        start_date
        <= date.fromisoformat(
            encounter["encounter_date"][:10]
        )
        <= end_date
    )
]

                    if eligible_encounters:

                        encounter = random.choice(
                            eligible_encounters
                        )

                        encounter_id = (
                            encounter["encounter_id"]
                        )

                medication = MEDICATIONS[
                    medication_code
                ]

                dose = random.choice(
                    medication["doses"]
                )

                route = random.choice(
                    medication["routes"]
                )

                status = choose_status(
                    end_date
                )

                # ------------------------------------------------
                # Order date occurs on or before medication start.
                # Never allow it to precede the patient's DOB.
                # ------------------------------------------------

                order_date = start_date - timedelta(
                    days=random.randint(
                        0,
                        7,
                    )
                )

                if order_date < patient_dob:
                    order_date = patient_dob

                if order_date < STUDY_START_DATE:
                    order_date = STUDY_START_DATE

                results.append(
                    {
                        "medication_order_id":
                            medication_order_id,

                        "research_id":
                            research_id,

                        "encounter_id":
                            encounter_id,

                        "medication_code":
                            medication_code,

                        "order_date":
                            order_date.isoformat(),

                        "start_date":
                            start_date.isoformat(),

                        "end_date":
                            end_date.isoformat(),

                        "dose":
                            dose,

                        "route":
                            route,

                        "status":
                            status,
                    }
                )

                medication_order_id += 1

    return results


# ============================================================
# CSV loading
# ============================================================

def load_csv(path):
    """
    Load a CSV file into a list of dictionaries.
    """

    with open(
        path,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:

        return list(
            csv.DictReader(file)
        )


# ============================================================
# Diagnosis lookup
# ============================================================

def build_diagnosis_lookup(diagnoses):
    """
    Build:

        research_id -> set of diagnosis codes
    """

    diagnosis_by_patient = {}

    for row in diagnoses:

        research_id = row["research_id"]
        diagnosis_code = row["diagnosis_code"]

        diagnosis_by_patient.setdefault(
            research_id,
            set(),
        ).add(
            diagnosis_code
        )

    return diagnosis_by_patient


# ============================================================
# Validation
# ============================================================

def validate_results(
    results,
    patients,
    encounters,
):

    patient_by_research_id = {
        patient["research_id"]: patient
        for patient in patients
    }

    encounter_by_id = {
        int(encounter["encounter_id"]): encounter
        for encounter in encounters
    }

    duplicate_ids = (
        len(results)
        - len(
            {
                row["medication_order_id"]
                for row in results
            }
        )
    )

    missing_research_id = sum(
        1
        for row in results
        if (
            row["research_id"] not in
            patient_by_research_id
        )
    )

    invalid_medication_codes = sum(
        1
        for row in results
        if (
            row["medication_code"]
            not in MEDICATIONS
        )
    )

    invalid_medication_dates = 0

    invalid_statuses = 0

    invalid_encounter_links = 0

    encounter_outside_period = 0

    before_patient_birth = 0

    after_patient_death = 0

    order_before_birth = 0

    order_after_death = 0

    order_after_start = 0

    for row in results:

        order_date = date.fromisoformat(
            row["order_date"]
        )

        start_date = date.fromisoformat(
            row["start_date"]
        )

        end_date = date.fromisoformat(
            row["end_date"]
        )

        # --------------------------------------------------------
        # Medication date validation
        # --------------------------------------------------------

        if order_date > start_date:
            order_after_start += 1

        if end_date < start_date:
            invalid_medication_dates += 1

        if start_date < STUDY_START_DATE:
            invalid_medication_dates += 1

        if end_date > STUDY_END_DATE:
            invalid_medication_dates += 1

        # --------------------------------------------------------
        # Status validation
        # --------------------------------------------------------

        if row["status"] not in {
            "ACTIVE",
            "COMPLETED",
            "DISCONTINUED",
        }:
            invalid_statuses += 1

        # --------------------------------------------------------
        # Patient relationship validation
        # --------------------------------------------------------

        patient = patient_by_research_id.get(
            row["research_id"]
        )

        if patient is not None:

            patient_dob = date.fromisoformat(
                patient["date_of_birth"]
            )

            if start_date < patient_dob:
                before_patient_birth += 1

            if order_date < patient_dob:
                order_before_birth += 1

            death_date_text = patient.get(
                "death_date",
                "",
            )

            if death_date_text:

                death_date = date.fromisoformat(
                    death_date_text
                )

                if start_date > death_date:
                    after_patient_death += 1

                if order_date > death_date:
                    order_after_death += 1

        # --------------------------------------------------------
        # Encounter validation
        # --------------------------------------------------------

        encounter_id = row["encounter_id"]

        if encounter_id:

            try:
                encounter_id_int = int(
                    encounter_id
                )

                encounter = encounter_by_id.get(
                    encounter_id_int
                )

                if encounter is None:

                    invalid_encounter_links += 1

                else:

                    encounter_date = date.fromisoformat(
                        encounter[
                            "encounter_date"
                        ][:10]
                    )

                    if (
                        encounter_date < start_date
                        or encounter_date > end_date
                    ):
                        encounter_outside_period += 1

                    if (
                        encounter[
                            "research_id"
                        ]
                        != row["research_id"]
                    ):
                        invalid_encounter_links += 1

            except (
                ValueError,
                TypeError,
            ):

                invalid_encounter_links += 1

    print()
    print("Validation")
    print(
        f"Rows: {len(results)}"
    )
    print(
        f"Duplicate medication_order_id: {duplicate_ids}"
    )
    print(
        f"Missing research_id: {missing_research_id}"
    )
    print(
        f"Invalid medication_code: {invalid_medication_codes}"
    )
    print(
        f"Invalid medication dates: {invalid_medication_dates}"
    )
    print(
        f"Invalid status: {invalid_statuses}"
    )
    print(
        f"Invalid encounter links: {invalid_encounter_links}"
    )
    print(
        f"Encounter outside medication period: {encounter_outside_period}"
    )
    print(
        f"Medication start before patient birth: {before_patient_birth}"
    )
    print(
        f"Medication start after patient death: {after_patient_death}"
    )
    print(
        f"Order date before patient birth: {order_before_birth}"
    )
    print(
        f"Order date after patient death: {order_after_death}"
    )
    print(
        f"Order date after medication start: {order_after_start}"
    )

    assert duplicate_ids == 0
    assert missing_research_id == 0
    assert invalid_medication_codes == 0
    assert invalid_medication_dates == 0
    assert invalid_statuses == 0
    assert invalid_encounter_links == 0
    assert encounter_outside_period == 0
    assert before_patient_birth == 0
    assert after_patient_death == 0
    assert order_before_birth == 0
    assert order_after_death == 0
    assert order_after_start == 0

    print("Validation passed.")


# ============================================================
# CSV output
# ============================================================

def write_csv(results):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "medication_order_id",
        "research_id",
        "encounter_id",
        "medication_code",
        "order_date",
        "start_date",
        "end_date",
        "dose",
        "route",
        "status",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            results
        )


# ============================================================
# Main
# ============================================================

def main():

    random.seed(SEED)

    print(
        "Generating synthetic medication data..."
    )

    print(
        f"Random seed: {SEED}"
    )

    # --------------------------------------------------------
    # Load source data
    # --------------------------------------------------------

    patients = load_csv(
        PATIENT_FILE
    )

    encounters = load_csv(
        ENCOUNTER_FILE
    )

    diagnoses = load_csv(
        DIAGNOSIS_FILE
    )

    print(
        f"Patients loaded: {len(patients)}"
    )

    print(
        f"Encounters loaded: {len(encounters)}"
    )

    diagnosis_by_patient = (
        build_diagnosis_lookup(
            diagnoses
        )
    )

    print(
        f"Patients with diagnoses: "
        f"{len(diagnosis_by_patient)}"
    )

    # --------------------------------------------------------
    # Generate medication orders
    # --------------------------------------------------------

    results = generate_medication_orders(
        patients,
        encounters,
        diagnosis_by_patient,
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_results(
        results,
        patients,
        encounters,
    )

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    write_csv(
        results
    )

    print()
    print(
        "Generation complete."
    )

    print(
        f"Output file: {OUTPUT_FILE}"
    )

    print(
        f"Medication orders generated: "
        f"{len(results)}"
    )


if __name__ == "__main__":
    main()