import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [cohorts, setCohorts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selectedCohort, setSelectedCohort] = useState(null);
  const [criteria, setCriteria] = useState([]);
  const [criteriaLoading, setCriteriaLoading] = useState(false);
  const [criteriaError, setCriteriaError] = useState("");

  const [executionLoading, setExecutionLoading] = useState(false);
  const [executionError, setExecutionError] = useState("");
  const [executionResult, setExecutionResult] = useState(null);

  useEffect(() => {
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

    loadCohorts();
  }, []);

  async function openCohort(cohort) {
    setSelectedCohort(cohort);
    setCriteria([]);
    setCriteriaError("");
    setCriteriaLoading(true);

    setExecutionResult(null);
    setExecutionError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/cohorts/${cohort.cohort_definition_id}/criteria`,
      );

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
        throw new Error(`API request failed: ${response.status}`);
      }

      const data = await response.json();
      setExecutionResult(data);
    } catch (err) {
      setExecutionError(err.message);
    } finally {
      setExecutionLoading(false);
    }
  }

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

        <div className="api-status">
          <span className="status-dot" />
          API connected
        </div>
      </header>

      <main className="content">
        <section className="section-header">
          <div>
            <p className="section-eyebrow">Cohorts</p>
            <h2>Available cohorts</h2>
          </div>

          <span className="cohort-count">
            {cohorts.length} cohort{cohorts.length === 1 ? "" : "s"}
          </span>
        </section>

        {loading && (
          <div className="state-card">
            <p>Loading cohorts...</p>
          </div>
        )}

        {error && (
          <div className="state-card error-card">
            <h3>Unable to load cohorts</h3>
            <p>{error}</p>
            <p>Make sure the FastAPI backend is running on port 8000.</p>
          </div>
        )}

        {!loading && !error && cohorts.length === 0 && (
          <div className="state-card">
            <h3>No cohorts found</h3>
            <p>Create a cohort to begin building a research population.</p>
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

                  <span className={`status-badge ${cohort.status}`}>
                    {cohort.status}
                  </span>
                </div>

                <h3>{cohort.cohort_name}</h3>

                <p className="description">
                  {cohort.description || "No description provided."}
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

        {selectedCohort && (
          <section className="criteria-section">
            <div className="section-header">
              <div>
                <p className="section-eyebrow">Selected cohort</p>
                <h2>{selectedCohort.cohort_name}</h2>
              </div>

              <div className="selected-cohort-actions">
                <span className="cohort-count">
                  {criteria.length}{" "}
                  {criteria.length === 1 ? "criterion" : "criteria"}
                </span>

                <button
                  type="button"
                  className="execute-button"
                  onClick={executeCohort}
                  disabled={executionLoading}
                >
                  {executionLoading ? "Running..." : "Run cohort"}
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
                  <span className="result-label">Execution status</span>
                  <strong>{executionResult.status}</strong>
                </div>

                <div>
                  <span className="result-label">Cohort members</span>
                  <strong className="member-count">
                    {executionResult.member_count.toLocaleString()}
                  </strong>
                </div>
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
                  <p>No criteria have been defined for this cohort.</p>
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
                      </tr>
                    </thead>

                    <tbody>
                      {criteria.map((criterion) => (
                        <tr key={criterion.cohort_criterion_id}>
                          <td>{criterion.criterion_order}</td>

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
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
          </section>
        )}
      </main>
    </div>
  );
}

export default App;