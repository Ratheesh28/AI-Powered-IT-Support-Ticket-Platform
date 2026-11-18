import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Ticket,
  Activity,
  Layers,
  BrainCircuit,
} from "lucide-react";

import StatCard from "../components/StatCard";
import api from "../services/api";
import {
  categoryClass,
  formatConfidence,
  formatDate,
  priorityClass,
} from "../utils/format";

function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [recentTickets, setRecentTickets] = useState([]);
  const [recentLoading, setRecentLoading] = useState(true);
  const [recentError, setRecentError] = useState("");

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await api.get("/analytics");
        setAnalytics(response.data);
      } catch (fetchError) {
        console.error("Analytics fetch failed:", fetchError);
        setError("Unable to load dashboard analytics.");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  useEffect(() => {
    const fetchRecentTickets = async () => {
      try {
        const response = await api.get("/tickets", {
          params: {
            limit: 5,
            offset: 0,
          },
        });
        setRecentTickets(response.data.items || []);
      } catch (fetchError) {
        console.error("Recent tickets fetch failed:", fetchError);
        setRecentError("Unable to load recent tickets.");
      } finally {
        setRecentLoading(false);
      }
    };

    fetchRecentTickets();
  }, []);

  const categoryEntries = analytics
    ? Object.entries(analytics.tickets_by_category || {})
    : [];
  const maxCategoryCount = Math.max(
    1,
    ...categoryEntries.map(([, count]) => Number(count) || 0)
  );

  const stats = [
    {
      title: "Total Tickets",
      value: loading ? "..." : analytics?.total_tickets ?? "—",
      description: "Total submitted support tickets",
      icon: Ticket,
      tone: "indigo",
    },
    {
      title: "Average Confidence",
      value: loading
        ? "..."
        : analytics?.average_confidence != null
          ? formatConfidence(analytics.average_confidence)
          : "—",
      description: "Average model prediction confidence",
      icon: Activity,
      tone: "sky",
    },
    {
      title: "Supported Categories",
      value: "4",
      description: "Network, Hardware, Software, Account Access",
      icon: Layers,
      tone: "violet",
    },
    {
      title: "ML Engine",
      value: "Ready",
      description: "TF-IDF + Logistic Regression",
      icon: BrainCircuit,
      tone: "emerald",
    },
  ];

  return (
    <main className="main-content">
      <header className="page-header">
        <div>
          <p className="eyebrow">Operations</p>
          <h1>Dashboard</h1>
          <p>Welcome to your AI-powered support intelligence platform.</p>
        </div>
        <Link to="/create-ticket" className="submit-ticket-btn">
          New ticket
        </Link>
      </header>

      {error && (
        <p className="alert" role="alert">
          {error}
        </p>
      )}

      <section className="stats-grid" aria-label="Key metrics">
        {stats.map((stat) => (
          <StatCard
            key={stat.title}
            title={stat.title}
            value={stat.value}
            description={stat.description}
            icon={stat.icon}
            tone={stat.tone}
          />
        ))}
      </section>

      <section className="overview-grid">
        <article className="panel">
          <div className="panel-heading">
            <div>
              <h2>Category overview</h2>
              <p>Ticket volume by predicted category.</p>
            </div>
          </div>

          {loading ? (
            <p className="status-line">Loading analytics...</p>
          ) : analytics ? (
            <ul className="category-list">
              {categoryEntries.map(([category, count]) => {
                const width = `${Math.max(
                  4,
                  ((Number(count) || 0) / maxCategoryCount) * 100
                )}%`;

                return (
                  <li key={category}>
                    <div className="category-list-row">
                      <span className={categoryClass(category)}>{category}</span>
                      <strong>{count}</strong>
                    </div>
                    <div className="meter" aria-hidden="true">
                      <span style={{ width }} />
                    </div>
                  </li>
                );
              })}
            </ul>
          ) : (
            <p className="status-line">Analytics data is currently unavailable.</p>
          )}
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <h2>Recent tickets</h2>
              <p>Latest submissions and AI predictions.</p>
            </div>
            <Link to="/tickets" className="text-link">
              View history
            </Link>
          </div>

          {recentLoading ? (
            <p className="status-line">Loading ticket records...</p>
          ) : recentError ? (
            <p className="alert" role="alert">
              {recentError}
            </p>
          ) : recentTickets.length === 0 ? (
            <div className="empty-state compact">
              <Ticket size={22} />
              <h3>No tickets yet</h3>
              <p>No tickets have been submitted yet.</p>
            </div>
          ) : (
            <div className="ticket-table-container">
              <table className="ticket-table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Priority</th>
                    <th>Confidence</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {recentTickets.map((ticket) => (
                    <tr key={ticket.id}>
                      <td className="cell-title">
                        <span className="ticket-id">#{ticket.id}</span>
                        {ticket.title}
                      </td>
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
        </article>
      </section>
    </main>
  );
}

export default Dashboard;
