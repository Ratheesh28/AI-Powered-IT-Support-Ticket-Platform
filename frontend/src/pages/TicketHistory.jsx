
import { useState, useEffect } from "react";
import { RefreshCw, Ticket } from "lucide-react";
import api from "../services/api";

function TicketHistory() {

  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);

  const limit = 10;

  const fetchTickets = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("/tickets", {
        params: {
          limit: limit,
          offset: offset
        }
      });

      setTickets(response.data.items);
      setTotal(response.data.total);

    } catch (error) {
      console.error("Ticket history fetch failed:", error);
      setError("Unable to load ticket history. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, [offset]);

  return (
    <main className="main-content">

      <header className="dashboard-header">
        <div>
          <h1>Ticket History</h1>
          <p>View all submitted IT support tickets and AI predictions.</p>
        </div>

        <button
          type="button"
          className="submit-ticket-btn"
          onClick={fetchTickets}
          disabled={loading}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </header>

      <section className="dashboard-placeholder">

        <div className="form-heading">
          <Ticket size={24} />
          <h2>Submitted Tickets ({total})</h2>
        </div>

        {loading ? (
          <p>Loading ticket records...</p>
        ) : error ? (
          <p role="alert">{error}</p>
        ) : tickets.length === 0 ? (
          <p>No tickets have been submitted yet.</p>
        ) : (

          <div className="ticket-table-container">
            <table className="ticket-table">

              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Priority</th>
                  <th>Confidence</th>
                  <th>Created At</th>
                </tr>
              </thead>

              <tbody>
                {tickets.map((ticket) => (
                  <tr key={ticket.id}>
                    <td>#{ticket.id}</td>
                    <td>{ticket.title}</td>
                    <td>{ticket.predicted_category}</td>

                    <td>
  <span
    className={`priority-badge priority-${(ticket.priority || "Medium").toLowerCase()}`}
  >
    {ticket.priority || "Medium"}
  </span>
</td>

                    <td>
                      {(ticket.confidence * 100).toFixed(2)}%
                    </td>

                    <td>
                      {new Date(ticket.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>

            </table>
          </div>
        )}

        {!loading && !error && (
          <div className="pagination-controls">

            <button
              type="button"
              disabled={offset === 0}
              onClick={() => setOffset(Math.max(0, offset - limit))}
            >
              Previous
            </button>

            <span>
              Showing {total === 0 ? 0 : offset + 1}–
              {Math.min(offset + tickets.length, total)} of {total}
            </span>

            <button
              type="button"
              disabled={offset + limit >= total}
              onClick={() => setOffset(offset + limit)}
            >
              Next
            </button>

          </div>
        )}

      </section>

    </main>
  );
}

export default TicketHistory;
