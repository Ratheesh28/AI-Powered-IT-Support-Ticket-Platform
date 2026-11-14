
import { useState, useEffect } from "react";

import {
  Ticket,
  Activity,
  Layers,
  BrainCircuit
} from "lucide-react";

import StatCard from "../components/StatCard";
import api from "../services/api";

function Dashboard() {

  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await api.get("/analytics");
        setAnalytics(response.data);
      } catch (error) {
        console.error("Analytics fetch failed:", error);
        setError("Unable to load dashboard analytics.");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  const stats = [
    {
      title: "Total Tickets",
      value: loading ? "..." : analytics?.total_tickets ?? "—",
      description: "Total submitted support tickets",
      icon: Ticket
    },
    {
      title: "Average Confidence",
      value: loading
        ? "..."
        : analytics?.average_confidence != null
          ? `${(analytics.average_confidence * 100).toFixed(2)}%`
          : "—",
      description: "Average model prediction confidence",
      icon: Activity
    },
    {
      title: "Supported Categories",
      value: "4",
      description: "Network, Hardware, Software, Account Access",
      icon: Layers
    },
    {
      title: "ML Engine",
      value: "Ready",
      description: "TF-IDF + Logistic Regression",
      icon: BrainCircuit
    }
  ];

  return (
    <main className="main-content">

      <header className="dashboard-header">
        <div>
          <h1>Dashboard</h1>
          <p>
            Welcome to your AI-powered support intelligence platform.
          </p>
        </div>
      </header>

      {error && (
        <p className="form-message" role="alert">
          {error}
        </p>
      )}

      <section className="stats-grid">

        {stats.map((stat, index) => (
          <StatCard
            key={index}
            title={stat.title}
            value={stat.value}
            description={stat.description}
            icon={stat.icon}
          />
        ))}

      </section>

      <section className="dashboard-placeholder">
        <h2>Ticket Intelligence Overview</h2>

        {loading ? (
          <p>Loading analytics...</p>
        ) : analytics ? (
          <div>
            <h3>Tickets by Category</h3>

            {Object.entries(analytics.tickets_by_category).map(
              ([category, count]) => (
                <p key={category}>
                  <strong>{category}:</strong> {count}
                </p>
              )
            )}
          </div>
        ) : (
          <p>Analytics data is currently unavailable.</p>
        )}

      </section>

    </main>
  );
}

export default Dashboard;
