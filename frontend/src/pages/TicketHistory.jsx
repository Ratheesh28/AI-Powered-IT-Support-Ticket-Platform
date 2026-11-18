import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { RefreshCw, Ticket, Inbox } from "lucide-react";
import api from "../services/api";
import {
  categoryClass,
  formatConfidence,
  formatDate,
  priorityClass,
} from "../utils/format";

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
          offset: offset,
        },
      });

      setTickets(response.data.items);
      setTotal(response.data.total);
    } catch (fetchError) {
      console.error("Ticket history fetch failed:", fetchError);
      setError("Unable to load ticket history. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, [offset]);

  const pageStart = total === 0 ? 0 : offset + 1;
  const pageEnd = Math.min(offset + tickets.length, total);
  const pageCount = Math.max(1, Math.ceil(total / limit));
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <main className="main-content">
      <header className="page-header">
        <div>
          <p className="eyebrow">Records</p>
          <h1>Ticket History</h1>
          <p>View all submitted IT support tickets and AI predictions.</p>
        </div>

        <button
          type="button"
          className="button-secondary"
          onClick={fetchTickets}
          disabled={loading}
        >
          <RefreshCw size={16} className={loading ? "spin" : ""} />
          Refresh
        </button>
      </header>

      <section className="panel">
        <div className="panel-heading">
          <div className="form-heading">
            <Ticket size={20} />
            <div>
              <h2>Submitted Tickets ({total})</h2>
              <p>Paginated results from the ticket service.</p>
            </div>
          </div>
        </div>

        {loading ? (
          <p className="status-line">Loading ticket records...</p>
        ) : error ? (
          <p className="alert" role="alert">
            {error}
          </p>
        ) : tickets.length === 0 ? (
          <div className="empty-state">
            <Inbox size={28} />
            <h3>No tickets yet</h3>
            <p>No tickets have been submitted yet.</p>
            <Link to="/create-ticket" className="submit-ticket-btn">
              Create a ticket
            </Link>
          </div>
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
                    <td className="cell-id">#{ticket.id}</td>
                    <td className="cell-title">{ticket.title}</td>
                    <td>
                      <span className={categoryClass(ticket.predicted_category)}>
                        {ticket.predicted_category}
                      </span>
                    </td>
                    <td>
                      <span className={priorityClass(ticket.priority)}>
                        {ticket.priority || "Medium"}
                      </span>
                    </td>
                    <td>{formatConfidence(ticket.confidence)}</td>
                    <td className="cell-muted">{formatDate(ticket.created_at)}</td>
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
              Showing {pageStart}–{pageEnd} of {total}
              <span className="page-count">
                Page {currentPage} of {pageCount}
              </span>
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
