
import { useState, useEffect } from "react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from "recharts";

import { Activity, Ticket, BrainCircuit } from "lucide-react";
import StatCard from "../components/StatCard";
import api from "../services/api";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#a78bfa"];

function Analytics() {

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
        setError("Unable to load analytics data.");
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <main className="main-content">
        <h1>Analytics</h1>
        <p>Loading analytics data...</p>
      </main>
    );
  }

  if (error || !analytics) {
    return (
      <main className="main-content">
        <h1>Analytics</h1>
        <p role="alert">{error || "Analytics data unavailable."}</p>
      </main>
    );
  }

  const categoryData = Object.entries(
    analytics.tickets_by_category
  ).map(([category, count]) => ({
    category,
    count
  }));

  const pieData = categoryData.filter(item => item.count > 0);

  const metrics = analytics.model_metrics;

  const stats = [
    {
      title: "Total Tickets",
      value: analytics.total_tickets,
      description: "Total submitted support tickets",
      icon: Ticket
    },
    {
      title: "Average Confidence",
      value: analytics.average_confidence != null
        ? `${(analytics.average_confidence * 100).toFixed(2)}%`
        : "N/A",
      description: "Average prediction confidence",
      icon: Activity
    },
    {
      title: "Model Accuracy",
      value: metrics
        ? `${(metrics.accuracy * 100).toFixed(2)}%`
        : "N/A",
      description: "Evaluation dataset accuracy",
      icon: BrainCircuit
    }
  ];

  const metricData = metrics
    ? [
        { name: "Accuracy", value: metrics.accuracy },
        { name: "Precision", value: metrics.macro_precision },
        { name: "Recall", value: metrics.macro_recall },
        { name: "F1 Score", value: metrics.macro_f1 }
      ]
    : [];

  return (
    <main className="main-content">

      <header className="dashboard-header">
        <div>
          <h1>Analytics</h1>
          <p>
            Insights into support tickets and machine learning performance.
          </p>
        </div>
      </header>

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

      <section className="analytics-grid">

        <div className="analytics-card">
          <h2>Tickets by Category</h2>

          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="category" stroke="#9ca3af" />
              <YAxis allowDecimals={false} stroke="#9ca3af" />
              <Tooltip />
              <Bar
                dataKey="count"
                fill="#3b82f6"
                radius={[5, 5, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="analytics-card">
          <h2>Category Distribution</h2>

          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="count"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  outerRadius={95}
                  label
                >
                  {pieData.map((entry, index) => (
                    <Cell
                      key={entry.category}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p>No ticket category data available yet.</p>
          )}
        </div>

      </section>

      <section className="analytics-card model-metrics-card">
        <h2>Machine Learning Model Performance</h2>

        {metrics ? (
          <>
            <p>
              Evaluation dataset size: {metrics.test_size}
            </p>

            <p>
              Trained at: {metrics.trained_at}
            </p>

            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={metricData}
                margin={{ top: 20, right: 20, left: 10, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9ca3af" />
                <YAxis
                  domain={[0, 1]}
                  tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                  stroke="#9ca3af"
                />
                <Tooltip
                  formatter={(value) =>
                    `${(Number(value) * 100).toFixed(2)}%`
                  }
                />
                <Bar
                  dataKey="value"
                  fill="#10b981"
                  radius={[5, 5, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </>
        ) : (
          <p>Model evaluation metrics are unavailable.</p>
        )}
      </section>

    </main>
  );
}

export default Analytics;
