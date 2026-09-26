import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";
const MEMBER_PAGE_SIZE = 50;

const CRITERION_OPTIONS = {
  demographics: {
    age_at_study_end: [">="],
  },
  diagnosis: {
    diagnosis_code: ["="],
    recorded_date: [">=", "<="],
  },
  encounter: {
    encounter_type_code: ["="],
  },
  laboratory: {
    result_numeric: [">=", "<="],
    test_code: ["="],
  },
  medication: {
    medication_code: ["="],
  },
  procedure: {
    procedure_code: ["="],
  },
};

function App() {
  const [cohorts, setCohorts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [cohortName, setCohortName] = useState("");
  const [cohortDescription, setCohortDescription] = useState("");
  const [cohortStartDate, setCohortStartDate] = useState("");
  const [cohortEndDate, setCohortEndDate] = useState("");
  const [cohortSaving, setCohortSaving] = useState(false);
  const [cohortSaveError, setCohortSaveError] = useState("");
  const [cohortSaveSuccess, setCohortSaveSuccess] = useState("");

  const [selectedCohort, setSelectedCohort] = useState(null);
  const [criteria, setCriteria] = useState([]);
  const [criteriaLoading, setCriteriaLoading] = useState(false);
  const [criteriaError, setCriteriaError] = useState("");

  const [executionLoading, setExecutionLoading] = useState(false);
  const [executionError, setExecutionError] = useState("");
  const [executionResult, setExecutionResult] = useState(null);

  const [criterionType, setCriterionType] = useState("inclusion");
  const [criterionDomain, setCriterionDomain] = useState("diagnosis");
  const [criterionField, setCriterionField] = useState("diagnosis_code");
  const [criterionOperator, setCriterionOperator] = useState("=");
  const [criterionValue, setCriterionValue] = useState("");
  const [criterionSaving, setCriterionSaving] = useState(false);
  const [criterionSaveError, setCriterionSaveError] = useState("");

  const [criterionDeletingId, setCriterionDeletingId] = useState(null);
  const [criterionDeleteError, setCriterionDeleteError] = useState("");

  const [members, setMembers] = useState([]);
  const [memberCount, setMemberCount] = useState(0);
  const [memberOffset, setMemberOffset] = useState(0);
  const [membersLoading, setMembersLoading] = useState(false);
  const [membersError, setMembersError] = useState("");

  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    async function checkApiHealth() {
      try {
        const response = await fetch(
          `${API_BASE_URL}/health/database`,
        );

        if (!response.ok) {
          throw new Error("API health check failed");
        }

        const data = await response.json();

        setApiStatus(
          data.status === "ok" ? "connected" : "unavailable",
        );
      } catch {
        setApiStatus("unavailable");
      }
    }

    async function loadCohorts() {
      try {
        const response = await fetch(`${API_BASE_URL}/cohorts`);

        if (!response.ok) {
          throw new Error(`API request failed: ${response.status}`);
        }

        const data = await response.json();
        setCohorts(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    checkApiHealth();
    loadCohorts();
  }, []);

  async function createCohort(event) {
    event.preventDefault();

    const trimmedName = cohortName.trim();
    const trimmedDescription = cohortDescription.trim();

    setCohortSaveError("");
    setCohortSaveSuccess("");

    if (!trimmedName) {
      setCohortSaveError("Cohort name is required.");
      return;
    }

    if (!cohortStartDate || !cohortEndDate) {
      setCohortSaveError("Study start and end dates are required.");
      return;
    }

    if (cohortEndDate < cohortStartDate) {
      setCohortSaveError(
        "Study end date cannot be before study start date.",
      );
      return;
    }

    const newCohort = {
      cohort_name: trimmedName,
      description: trimmedDescription || null,
      study_start_date: cohortStartDate,
      study_end_date: cohortEndDate,
    };

    setCohortSaving(true);

    try {
      const response = await fetch(`${API_BASE_URL}/cohorts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newCohort),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || `API request failed: ${response.status}`,
        );
      }

      const createdCohort = await response.json();

      setCohorts((currentCohorts) => [
        ...currentCohorts,
        createdCohort,
      ]);

      setCohortName("");
      setCohortDescription("");
      setCohortStartDate("");
      setCohortEndDate("");

      setCohortSaveSuccess(
        `${createdCohort.cohort_name} was created successfully.`,
      );
    } catch (err) {
      setCohortSaveError(err.message);
    } finally {
      setCohortSaving(false);
    }
  }

  async function loadMembers(cohortId, offset = 0) {
    setMembersLoading(true);
    setMembersError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/cohorts/${cohortId}/members?limit=${MEMBER_PAGE_SIZE}&offset=${offset}`,
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || `API request failed: ${response.status}`,
        );
      }

      const data = await response.json();

      setMembers(data.members);
      setMemberCount(data.member_count);
      setMemberOffset(data.offset);
    } catch (err) {
      setMembers([]);
      setMemberCount(0);
      setMembersError(err.message);
    } finally {
      setMembersLoading(false);
    }
  }

  async function openCohort(cohort) {
    setSelectedCohort(cohort);
    setCriteria([]);
    setCriteriaError("");
    setCriteriaLoading(true);

    setExecutionResult(null);
    setExecutionError("");

    setCriterionType("inclusion");
    setCriterionDomain("diagnosis");
    setCriterionField("diagnosis_code");
    setCriterionOperator("=");
    setCriterionValue("");
    setCriterionSaveError("");

    setCriterionDeletingId(null);
    setCriterionDeleteError("");

    setMembers([]);
    setMemberCount(0);
    setMemberOffset(0);
    setMembersError("");

    const criteriaRequest = fetch(
      `${API_BASE_URL}/cohorts/${cohort.cohort_definition_id}/criteria`,
    );

    const membersRequest = loadMembers(
      cohort.cohort_definition_id,
      0,
    );

    try {
      const response = await criteriaRequest;

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const data = await response.json();
      setCriteria(data);
    } catch (err) {
      setCriteriaError(err.message);
    } finally {
      setCriteriaLoading(false);
    }

    await membersRequest;
  }

  async function executeCohort() {
    if (!selectedCohort) {
      return;
    }

    setExecutionLoading(true);
    setExecutionError("");
    setExecutionResult(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/cohorts/${selectedCohort.cohort_definition_id}/execute`,
        {
          method: "POST",
        },
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || `API request failed: ${response.status}`,
        );
      }

      const data = await response.json();
      setExecutionResult(data);

      await loadMembers(
        selectedCohort.cohort_definition_id,
        0,
      );
    } catch (err) {
      setExecutionError(err.message);
    } finally {
      setExecutionLoading(false);
    }
  }

  function handleTypeChange(event) {
    const newType = event.target.value;

    setCriterionType(newType);
    setCriterionSaveError("");

    if (newType === "exclusion") {
      setCriterionDomain("diagnosis");
      setCriterionField("diagnosis_code");
      setCriterionOperator("=");
    }
  }

  function handleDomainChange(event) {
    const newDomain = event.target.value;
    const fields = Object.keys(CRITERION_OPTIONS[newDomain]);
    const firstField = fields[0];
    const firstOperator = CRITERION_OPTIONS[newDomain][firstField][0];

    setCriterionDomain(newDomain);
    setCriterionField(firstField);
    setCriterionOperator(firstOperator);
    setCriterionSaveError("");
  }

  function handleFieldChange(event) {
    const newField = event.target.value;
    const firstOperator =
      CRITERION_OPTIONS[criterionDomain][newField][0];

    setCriterionField(newField);
    setCriterionOperator(firstOperator);
    setCriterionSaveError("");
  }

  async function addCriterion(event) {
    event.preventDefault();

    if (!selectedCohort) {
      return;
    }

    const trimmedValue = criterionValue.trim();

    if (!trimmedValue) {
      setCriterionSaveError("Criterion value is required.");
      return;
    }

    const nextOrder =
      criteria.length === 0
        ? 1
        : Math.max(
            ...criteria.map((criterion) => criterion.criterion_order),
          ) + 1;

    const newCriterion = {
      criterion_order: nextOrder,
      criterion_type: criterionType,
      domain: criterionDomain,
      field_name: criterionField,
      operator: criterionOperator,
      value_text: trimmedValue,
    };

    setCriterionSaving(true);
    setCriterionSaveError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/cohorts/${selectedCohort.cohort_definition_id}/criteria`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(newCriterion),
        },
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || `API request failed: ${response.status}`,
        );
      }

      const createdCriterion = await response.json();

      setCriteria((currentCriteria) =>
        [...currentCriteria, createdCriterion].sort(
          (a, b) => a.criterion_order - b.criterion_order,
        ),
      );

      setCriterionValue("");
      setExecutionResult(null);
      setExecutionError("");
    } catch (err) {
      setCriterionSaveError(err.message);
    } finally {
      setCriterionSaving(false);
    }
  }

  async function deleteCriterion(criterionId) {
    if (!selectedCohort) {
      return;
    }

    setCriterionDeletingId(criterionId);
    setCriterionDeleteError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/cohorts/${selectedCohort.cohort_definition_id}/criteria/${criterionId}`,
        {
          method: "DELETE",
        },
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || `API request failed: ${response.status}`,
        );
      }

      setCriteria((currentCriteria) =>
        currentCriteria.filter(
          (criterion) =>
            criterion.cohort_criterion_id !== criterionId,
        ),
      );

      setExecutionResult(null);
      setExecutionError("");
    } catch (err) {
      setCriterionDeleteError(err.message);
    } finally {
      setCriterionDeletingId(null);
    }
  }

  function goToPreviousMemberPage() {
    if (!selectedCohort || memberOffset === 0) {
      return;
    }

    const newOffset = Math.max(
      0,
      memberOffset - MEMBER_PAGE_SIZE,
    );

    loadMembers(
      selectedCohort.cohort_definition_id,
      newOffset,
    );
  }

  function goToNextMemberPage() {
    if (
      !selectedCohort ||
      memberOffset + MEMBER_PAGE_SIZE >= memberCount
    ) {
      return;
    }

    loadMembers(
      selectedCohort.cohort_definition_id,
      memberOffset + MEMBER_PAGE_SIZE,
    );
  }

  const availableDomains =
    criterionType === "exclusion"
      ? ["diagnosis"]
      : Object.keys(CRITERION_OPTIONS);

  const availableFields = Object.keys(
    CRITERION_OPTIONS[criterionDomain],
  );

  const availableOperators =
    CRITERION_OPTIONS[criterionDomain][criterionField];

  const memberRangeStart =
    memberCount === 0 ? 0 : memberOffset + 1;

  const memberRangeEnd = Math.min(
    memberOffset + members.length,
    memberCount,
  );

  const apiStatusLabel =
    apiStatus === "connected"
      ? "API connected"
      : apiStatus === "unavailable"
        ? "API unavailable"
        : "Checking API...";

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <p className="eyebrow">Research Cohort Explorer</p>
          <h1>Cohort Management</h1>
          <p className="subtitle">
            Define, inspect, and execute research cohorts.
          </p>
        </div>

        <div className={`api-status ${apiStatus}`}>
          <span className="status-dot" />
          {apiStatusLabel}
        </div>
      </header>

      <main className="content">
        <section className="create-cohort-section">
          <div className="section-header">
            <div>
              <p className="section-eyebrow">Cohort builder</p>
              <h2>Create cohort</h2>
            </div>
          </div>

          <div className="create-cohort-card">
            <form
              className="create-cohort-form"
              onSubmit={createCohort}
            >
              <div className="form-field cohort-name-field">
                <label htmlFor="cohort-name">Cohort name</label>
                <input
                  id="cohort-name"
                  type="text"
                  value={cohortName}
                  onChange={(event) => {
                    setCohortName(event.target.value);
                    setCohortSaveError("");
                    setCohortSaveSuccess("");
                  }}
                  placeholder="Enter cohort name"
                />
              </div>

              <div className="form-field cohort-description-field">
                <label htmlFor="cohort-description">
                  Description
                </label>
                <input
                  id="cohort-description"
                  type="text"
                  value={cohortDescription}
                  onChange={(event) => {
                    setCohortDescription(event.target.value);
                    setCohortSaveError("");
                    setCohortSaveSuccess("");
                  }}
                  placeholder="Optional description"
                />
              </div>

              <div className="form-field">
                <label htmlFor="cohort-start-date">
                  Study start
                </label>
                <input
                  id="cohort-start-date"
                  type="date"
                  value={cohortStartDate}
                  onChange={(event) => {
                    setCohortStartDate(event.target.value);
                    setCohortSaveError("");
                    setCohortSaveSuccess("");
                  }}
                />
              </div>

              <div className="form-field">
                <label htmlFor="cohort-end-date">
                  Study end
                </label>
                <input
                  id="cohort-end-date"
                  type="date"
                  value={cohortEndDate}
                  onChange={(event) => {
                    setCohortEndDate(event.target.value);
                    setCohortSaveError("");
                    setCohortSaveSuccess("");
                  }}
                />
              </div>

              <button
                type="submit"
                className="create-cohort-button"
                disabled={cohortSaving}
              >
                {cohortSaving ? "Creating..." : "Create cohort"}
              </button>
            </form>

            {cohortSaveError && (
              <div className="form-error">
                {cohortSaveError}
              </div>
            )}

            {cohortSaveSuccess && (
              <div className="form-success">
                {cohortSaveSuccess}
              </div>
            )}
          </div>
        </section>

        <section className="cohort-list-section">
          <div className="section-header">
            <div>
              <p className="section-eyebrow">Cohorts</p>
              <h2>Available cohorts</h2>
            </div>

            <span className="cohort-count">
              {cohorts.length} cohort
              {cohorts.length === 1 ? "" : "s"}
            </span>
          </div>

          {loading && (
            <div className="state-card">
              <p>Loading cohorts...</p>
            </div>
          )}

          {error && (
            <div className="state-card error-card">
              <h3>Unable to load cohorts</h3>
              <p>{error}</p>
              <p>
                Make sure the FastAPI backend is running on port 8000.
              </p>
            </div>
          )}

          {!loading && !error && cohorts.length === 0 && (
            <div className="state-card">
              <h3>No cohorts found</h3>
              <p>
                Create a cohort to begin building a research
                population.
              </p>
            </div>
          )}

          {!loading && !error && cohorts.length > 0 && (
            <div className="cohort-grid">
              {cohorts.map((cohort) => (
                <article
                  className="cohort-card"
                  key={cohort.cohort_definition_id}
                >
                  <div className="card-top">
                    <span className="cohort-id">
                      Cohort #{cohort.cohort_definition_id}
                    </span>

                    <span
                      className={`status-badge ${cohort.status}`}
                    >
                      {cohort.status}
                    </span>
                  </div>

                  <h3>{cohort.cohort_name}</h3>

                  <p className="description">
                    {cohort.description ||
                      "No description provided."}
                  </p>

                  <div className="date-range">
                    <div>
                      <span>Study start</span>
                      <strong>{cohort.study_start_date}</strong>
                    </div>

                    <div>
                      <span>Study end</span>
                      <strong>{cohort.study_end_date}</strong>
                    </div>
                  </div>

                  <div className="card-footer">
                    <span>Version {cohort.version}</span>

                    <button
                      type="button"
                      onClick={() => openCohort(cohort)}
                    >
                      Open cohort
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        {selectedCohort && (
          <section className="criteria-section">
            <div className="section-header">
              <div>
                <p className="section-eyebrow">
                  Selected cohort
                </p>
                <h2>{selectedCohort.cohort_name}</h2>
              </div>

              <div className="selected-cohort-actions">
                <span className="cohort-count">
                  {criteria.length}{" "}
                  {criteria.length === 1
                    ? "criterion"
                    : "criteria"}
                </span>

                <button
                  type="button"
                  className="execute-button"
                  onClick={executeCohort}
                  disabled={executionLoading}
                >
                  {executionLoading
                    ? "Running..."
                    : "Run cohort"}
                </button>
              </div>
            </div>

            {executionError && (
              <div className="state-card error-card execution-message">
                <h3>Cohort execution failed</h3>
                <p>{executionError}</p>
              </div>
            )}

            {executionResult && (
              <div className="execution-result">
                <div>
                  <span className="result-label">
                    Execution status
                  </span>
                  <strong>{executionResult.status}</strong>
                </div>

                <div>
                  <span className="result-label">
                    Cohort members
                  </span>
                  <strong className="member-count">
                    {executionResult.member_count.toLocaleString()}
                  </strong>
                </div>
              </div>
            )}

            <section className="criterion-form-card">
              <div className="criterion-form-heading">
                <div>
                  <h3>Add criterion</h3>
                  <p>
                    Add a supported rule to the selected cohort
                    definition.
                  </p>
                </div>
              </div>

              <form
                className="criterion-form"
                onSubmit={addCriterion}
              >
                <div className="form-field">
                  <label htmlFor="criterion-type">Type</label>
                  <select
                    id="criterion-type"
                    value={criterionType}
                    onChange={handleTypeChange}
                  >
                    <option value="inclusion">
                      Inclusion
                    </option>
                    <option value="exclusion">
                      Exclusion
                    </option>
                  </select>
                </div>

                <div className="form-field">
                  <label htmlFor="criterion-domain">
                    Domain
                  </label>
                  <select
                    id="criterion-domain"
                    value={criterionDomain}
                    onChange={handleDomainChange}
                  >
                    {availableDomains.map((domain) => (
                      <option key={domain} value={domain}>
                        {domain}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-field">
                  <label htmlFor="criterion-field">Field</label>
                  <select
                    id="criterion-field"
                    value={criterionField}
                    onChange={handleFieldChange}
                  >
                    {availableFields.map((field) => (
                      <option key={field} value={field}>
                        {field}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-field">
                  <label htmlFor="criterion-operator">
                    Operator
                  </label>
                  <select
                    id="criterion-operator"
                    value={criterionOperator}
                    onChange={(event) => {
                      setCriterionOperator(event.target.value);
                      setCriterionSaveError("");
                    }}
                  >
                    {availableOperators.map((operator) => (
                      <option
                        key={operator}
                        value={operator}
                      >
                        {operator}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-field value-field">
                  <label htmlFor="criterion-value">
                    Value
                  </label>
                  <input
                    id="criterion-value"
                    type="text"
                    value={criterionValue}
                    onChange={(event) => {
                      setCriterionValue(event.target.value);
                      setCriterionSaveError("");
                    }}
                    placeholder="Enter criterion value"
                  />
                </div>

                <button
                  type="submit"
                  className="add-criterion-button"
                  disabled={criterionSaving}
                >
                  {criterionSaving
                    ? "Adding..."
                    : "Add criterion"}
                </button>
              </form>

              {criterionType === "exclusion" && (
                <p className="form-note">
                  Cohort Engine v1 supports exclusion criteria only
                  for the diagnosis domain.
                </p>
              )}

              {criterionSaveError && (
                <div className="form-error">
                  {criterionSaveError}
                </div>
              )}
            </section>

            {criterionDeleteError && (
              <div className="state-card error-card execution-message">
                <h3>Unable to delete criterion</h3>
                <p>{criterionDeleteError}</p>
              </div>
            )}

            {criteriaLoading && (
              <div className="state-card">
                <p>Loading criteria...</p>
              </div>
            )}

            {criteriaError && (
              <div className="state-card error-card">
                <h3>Unable to load criteria</h3>
                <p>{criteriaError}</p>
              </div>
            )}

            {!criteriaLoading &&
              !criteriaError &&
              criteria.length === 0 && (
                <div className="state-card">
                  <p>
                    No criteria have been defined for this cohort.
                  </p>
                </div>
              )}

            {!criteriaLoading &&
              !criteriaError &&
              criteria.length > 0 && (
                <div className="criteria-table-wrapper">
                  <table className="criteria-table">
                    <thead>
                      <tr>
                        <th>Order</th>
                        <th>Type</th>
                        <th>Domain</th>
                        <th>Field</th>
                        <th>Operator</th>
                        <th>Value</th>
                        <th>Action</th>
                      </tr>
                    </thead>

                    <tbody>
                      {criteria.map((criterion) => (
                        <tr
                          key={criterion.cohort_criterion_id}
                        >
                          <td>
                            {criterion.criterion_order}
                          </td>

                          <td>
                            <span
                              className={`criterion-type ${criterion.criterion_type}`}
                            >
                              {criterion.criterion_type}
                            </span>
                          </td>

                          <td>{criterion.domain}</td>
                          <td>{criterion.field_name}</td>

                          <td>
                            <code>{criterion.operator}</code>
                          </td>

                          <td>{criterion.value_text}</td>

                          <td>
                            <button
                              type="button"
                              className="delete-criterion-button"
                              onClick={() =>
                                deleteCriterion(
                                  criterion.cohort_criterion_id,
                                )
                              }
                              disabled={
                                criterionDeletingId ===
                                criterion.cohort_criterion_id
                              }
                            >
                              {criterionDeletingId ===
                              criterion.cohort_criterion_id
                                ? "Deleting..."
                                : "Delete"}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

            <section className="members-section">
              <div className="members-header">
                <div>
                  <p className="section-eyebrow">
                    Cohort population
                  </p>
                  <h3>Cohort members</h3>
                  <p className="members-description">
                    Patient demographics for the currently stored
                    cohort membership.
                  </p>
                </div>

                {!membersLoading && !membersError && (
                  <div className="members-summary">
                    <strong>
                      {memberCount.toLocaleString()}
                    </strong>
                    <span>
                      {memberCount === 1 ? "member" : "members"}
                    </span>
                  </div>
                )}
              </div>

              {membersLoading && (
                <div className="state-card">
                  <p>Loading cohort members...</p>
                </div>
              )}

              {membersError && (
                <div className="state-card error-card">
                  <h3>Unable to load cohort members</h3>
                  <p>{membersError}</p>
                </div>
              )}

              {!membersLoading &&
                !membersError &&
                memberCount === 0 && (
                  <div className="state-card">
                    <h3>No cohort members</h3>
                    <p>
                      Run this cohort to generate its membership.
                    </p>
                  </div>
                )}

              {!membersLoading &&
                !membersError &&
                memberCount > 0 && (
                  <>
                    <div className="members-table-wrapper">
                      <table className="members-table">
                        <thead>
                          <tr>
                            <th>Research ID</th>
                            <th>Date of birth</th>
                            <th>Age</th>
                            <th>Sex</th>
                            <th>Race</th>
                            <th>Ethnicity</th>
                            <th>ZIP3</th>
                          </tr>
                        </thead>

                        <tbody>
                          {members.map((member) => (
                            <tr key={member.research_id}>
                              <td>
                                <strong>
                                  {member.research_id}
                                </strong>
                              </td>
                              <td>{member.date_of_birth}</td>
                              <td>
                                {member.age_at_study_end}
                              </td>
                              <td>{member.sex}</td>
                              <td>{member.race}</td>
                              <td>{member.ethnicity}</td>
                              <td>{member.zip3}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    <div className="members-pagination">
                      <span>
                        Showing {memberRangeStart.toLocaleString()}
                        {"–"}
                        {memberRangeEnd.toLocaleString()} of{" "}
                        {memberCount.toLocaleString()}
                      </span>

                      <div className="pagination-actions">
                        <button
                          type="button"
                          onClick={goToPreviousMemberPage}
                          disabled={
                            memberOffset === 0 ||
                            membersLoading
                          }
                        >
                          Previous
                        </button>

                        <button
                          type="button"
                          onClick={goToNextMemberPage}
                          disabled={
                            memberOffset +
                              MEMBER_PAGE_SIZE >=
                              memberCount ||
                            membersLoading
                          }
                        >
                          Next
                        </button>
                      </div>
                    </div>
                  </>
                )}
            </section>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;