import { useState } from "react";
import { Send, FileText, BookOpen, Lightbulb } from "lucide-react";
import api from "../services/api";
import {
  categoryClass,
  formatConfidence,
  formatDate,
  priorityClass,
} from "../utils/format";

function CreateTicket() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const [ticketResult, setTicketResult] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [recommendationError, setRecommendationError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!title.trim() || !description.trim()) {
      setMessage("Please enter both title and description.");
      setTicketResult(null);
      setRecommendations([]);
      return;
    }

    const submittedTitle = title.trim();
    const submittedDescription = description.trim();

    setLoading(true);
    setMessage("");
    setTicketResult(null);
    setRecommendations([]);
    setRecommendationError("");

    try {
      const response = await api.post("/tickets", {
        title: submittedTitle,
        description: submittedDescription,
      });

      setTicketResult(response.data);
      setMessage("Ticket created successfully!");

      setTitle("");
      setDescription("");

      try {
        const recommendationResponse = await api.post("/recommendations", {
          title: submittedTitle,
          description: submittedDescription,
        });

        setRecommendations(recommendationResponse.data.recommendations || []);
      } catch (error) {
        console.error("Recommendation fetch failed:", error);

        setRecommendationError(
          "Ticket created successfully, but recommendations could not be loaded."
        );
      }
    } catch (error) {
      console.error("Ticket submission failed:", error);

      const errorMessage =
        error.response?.data?.detail ||
        "Unable to connect to the backend. Please try again.";

      setMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const confidencePercent = ticketResult
    ? Math.max(0, Math.min(100, Number(ticketResult.confidence) * 100))
    : 0;

  return (
    <main className="main-content">
      <header className="page-header">
        <div>
          <p className="eyebrow">Intake</p>
          <h1>Create Support Ticket</h1>
          <p>Describe your IT issue for AI-powered classification.</p>
        </div>
      </header>

      <div className={`create-layout ${ticketResult ? "has-result" : ""}`}>
        <section className="panel ticket-form-container">
          <div className="form-heading">
            <FileText size={20} />
            <div>
              <h2>Ticket Information</h2>
              <p>Title and description are sent to the classifier as entered.</p>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="title">Ticket Title</label>
              <input
                id="title"
                type="text"
                placeholder="Example: Cannot connect to office Wi-Fi"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                maxLength={200}
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Issue Description</label>
              <textarea
                id="description"
                placeholder="Explain your IT issue in detail..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={6}
                maxLength={5000}
              />
            </div>

            <button
              type="submit"
              className="submit-ticket-btn"
              disabled={loading}
            >
              <Send size={18} />
              {loading ? "Submitting..." : "Submit Ticket"}
            </button>

            {message && (
              <p
                className={`form-message ${ticketResult ? "is-success" : "is-error"}`}
                role="status"
              >
                {message}
              </p>
            )}
          </form>
        </section>

        {ticketResult && (
          <aside className="panel result-panel">
            <div className="form-heading">
              <FileText size={20} />
              <div>
                <h2>AI Classification Result</h2>
                <p>Prediction returned for this submission.</p>
              </div>
            </div>

            <dl className="result-meta">
              <div>
                <dt>Ticket ID</dt>
                <dd>#{ticketResult.id}</dd>
              </div>
              <div>
                <dt>Predicted Category</dt>
                <dd>
                  <span className={categoryClass(ticketResult.predicted_category)}>
                    {ticketResult.predicted_category}
                  </span>
                </dd>
              </div>
              <div>
                <dt>Priority</dt>
                <dd>
                  <span className={priorityClass(ticketResult.priority)}>
                    {ticketResult.priority || "Medium"}
                  </span>
                </dd>
              </div>
              <div>
                <dt>Created At</dt>
                <dd>{formatDate(ticketResult.created_at)}</dd>
              </div>
            </dl>

            <div className="confidence-block">
              <div className="category-list-row">
                <span>Confidence</span>
                <strong>{formatConfidence(ticketResult.confidence)}</strong>
              </div>
              <div
                className="meter meter-lg"
                role="meter"
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={Number(confidencePercent.toFixed(2))}
                aria-label="Prediction confidence"
              >
                <span style={{ width: `${confidencePercent}%` }} />
              </div>
            </div>

            <section className="recommendations-section">
              <div className="form-heading">
                <BookOpen size={20} />
                <div>
                  <h2>Recommended Knowledge Base Articles</h2>
                </div>
              </div>

              <p>
                Troubleshooting resources based on your predicted ticket
                category: <strong>{ticketResult.predicted_category}</strong>
              </p>

              {recommendationError ? (
                <p className="alert" role="alert">
                  {recommendationError}
                </p>
              ) : recommendations.length === 0 ? (
                <p className="status-line">
                  No matching knowledge base articles were found for this ticket.
                </p>
              ) : (
                <div className="recommendation-list">
                  {recommendations.map((article) => (
                    <article className="recommendation-card" key={article.id}>
                      <div className="recommendation-card-header">
                        <Lightbulb size={18} />
                        <h3>{article.title}</h3>
                      </div>

                      <p>{article.content}</p>

                      <p>
                        <span className={categoryClass(article.category)}>
                          {article.category}
                        </span>
                      </p>

                      <span className="relevance-badge">
                        Relevance Score: {article.relevance_score}
                      </span>

                      <h4>Troubleshooting Steps</h4>
                      <ol>
                        {article.steps.map((step, index) => (
                          <li key={index}>{step}</li>
                        ))}
                      </ol>
                    </article>
                  ))}
                </div>
              )}
            </section>
          </aside>
        )}
      </div>
    </main>
  );
}

export default CreateTicket;
