
import { useState } from "react";
import { Send, FileText, BookOpen, Lightbulb } from "lucide-react";
import api from "../services/api";

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

    // Preserve the submitted values before clearing the form
    const submittedTitle = title.trim();
    const submittedDescription = description.trim();

    setLoading(true);
    setMessage("");
    setTicketResult(null);
    setRecommendations([]);
    setRecommendationError("");

    try {
      // Step 1: Create and save the ticket
      const response = await api.post("/tickets", {
        title: submittedTitle,
        description: submittedDescription,
      });

      setTicketResult(response.data);
      setMessage("Ticket created successfully!");

      // Clear the form after successful ticket creation
      setTitle("");
      setDescription("");

      // Step 2: Retrieve relevant knowledge base articles
      try {
        const recommendationResponse = await api.post(
          "/recommendations",
          {
            title: submittedTitle,
            description: submittedDescription,
          }
        );

        setRecommendations(
          recommendationResponse.data.recommendations || []
        );

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

  return (
    <main className="main-content">

      <header className="dashboard-header">
        <div>
          <h1>Create Support Ticket</h1>
          <p>
            Describe your IT issue for AI-powered classification.
          </p>
        </div>
      </header>

      <section className="ticket-form-container">

        <div className="form-heading">
          <FileText size={24} />
          <h2>Ticket Information</h2>
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
            <p className="form-message" role="status">
              {message}
            </p>
          )}

          {ticketResult && (
            <div className="ticket-result">

              <h3>AI Classification Result</h3>

              <p>
                <strong>Ticket ID:</strong> {ticketResult.id}
              </p>

              <p>
                <strong>Predicted Category:</strong>{" "}
                {ticketResult.predicted_category}
              </p>

              <p>
                <strong>Priority:</strong>{" "}
                <span
                  className={`priority-badge priority-${(ticketResult.priority || "Medium").toLowerCase()}`}
                >
                  {ticketResult.priority || "Medium"}
                </span>
              </p>

              <p>
                <strong>Confidence:</strong>{" "}
                {(ticketResult.confidence * 100).toFixed(2)}%
              </p>

              <p>
                <strong>Created At:</strong>{" "}
                {new Date(ticketResult.created_at).toLocaleString()}
              </p>

            </div>
          )}

          {ticketResult && (
            <section className="recommendations-section">

              <div className="form-heading">
                <BookOpen size={24} />
                <h2>Recommended Knowledge Base Articles</h2>
              </div>

              <p>
                Troubleshooting resources based on your predicted ticket
                category: <strong>{ticketResult.predicted_category}</strong>
              </p>

              {recommendationError ? (
                <p role="alert">{recommendationError}</p>
              ) : recommendations.length === 0 ? (
                <p>
                  No matching knowledge base articles were found
                  for this ticket.
                </p>
              ) : (
                <div className="recommendation-list">

                  {recommendations.map((article) => (
                    <article
                      className="recommendation-card"
                      key={article.id}
                    >

                      <div className="recommendation-card-header">
                        <Lightbulb size={20} />

                        <h3>{article.title}</h3>
                      </div>

                      <p>
                        {article.content}
                      </p>

                      <p>
                        <strong>Category:</strong> {article.category}
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
          )}

        </form>

      </section>

    </main>
  );
}

export default CreateTicket;
