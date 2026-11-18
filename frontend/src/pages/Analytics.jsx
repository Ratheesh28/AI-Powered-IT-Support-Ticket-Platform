import { useEffect, useState } from "react";
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
  Legend,
} from "recharts";

import { Activity, Ticket, BrainCircuit } from "lucide-react";
import StatCard from "../components/StatCard";
import api from "../services/api";
import { formatConfidence } from "../utils/format";

const CATEGORY_COLORS = {
  Network: "#6366f1",
  Hardware: "#38bdf8",
  Software: "#a78bfa",
  "Account Access": "#34d399",
};

const FALLBACK_COLORS = ["#6366f1", "#38bdf8", "#fbbf24", "#a78bfa", "#34d399"];
const METRIC_COLORS = ["#818cf8", "#38bdf8", "#34d399", "#fbbf24"];

const axisTick = { fill: "#94a3b8", fontSize: 12 };
const gridStroke = "rgba(148, 163, 184, 0.16)";

function ChartTooltip({ active, payload, label, valueFormatter }) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="chart-tooltip">
      {label ? <p className="chart-tooltip-label">{label}</p> : null}
      {payload.map((item) => (
        <p key={item.name}>
          <span
            className="chart-swatch"
            style={{ background: item.color || item.fill || "#818cf8" }}
          />
          {item.name}: {valueFormatter ? valueFormatter(item.value, item) : item.value}
        </p>
      ))}
    </div>
  );
}

function categoryColor(name, index) {
  return CATEGORY_COLORS[name] || FALLBACK_COLORS[index % FALLBACK_COLORS.length];
}

function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await api.get("/analytics");
        setAnalytics(response.data);
      } catch (fetchError) {
        console.error("Analytics fetch failed:", fetchError);
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
        <header className="page-header">
          <div>
            <p className="eyebrow">Insights</p>
            <h1>Analytics</h1>
            <p>Loading analytics data...</p>
          </div>
        </header>
      </main>
    );
  }

  if (error || !analytics) {
    return (
      <main className="main-content">
        <header className="page-header">
          <div>
            <p className="eyebrow">Insights</p>
            <h1>Analytics</h1>
          </div>
        </header>
        <p className="alert" role="alert">
          {error || "Analytics data unavailable."}
        </p>
      </main>
    );
  }

  const categoryData = Object.entries(analytics.tickets_by_category).map(
    ([category, count]) => ({
      category,
      count,
    })
  );

  const pieData = categoryData.filter((item) => item.count > 0);

  const confidenceData = Object.entries(
    analytics.average_confidence_by_category || {}
  ).map(([category, value]) => ({
    category,
    confidence: value == null ? 0 : Number(value) * 100,
    raw: value,
  }));

  const metrics = analytics.model_metrics;

  const stats = [
    {
      title: "Total Tickets",
      value: analytics.total_tickets,
      description: "Total submitted support tickets",
      icon: Ticket,
      tone: "indigo",
    },
    {
      title: "Average Confidence",
      value:
        analytics.average_confidence != null
          ? formatConfidence(analytics.average_confidence)
          : "N/A",
      description: "Average prediction confidence",
      icon: Activity,
      tone: "sky",
    },
    {
      title: "Model Accuracy",
      value: metrics ? formatConfidence(metrics.accuracy) : "N/A",
      description: "Evaluation dataset accuracy",
      icon: BrainCircuit,
      tone: "emerald",
    },
  ];

  const metricData = metrics
    ? [
        { name: "Accuracy", value: metrics.accuracy },
        { name: "Precision", value: metrics.macro_precision },
        { name: "Recall", value: metrics.macro_recall },
        { name: "F1 Score", value: metrics.macro_f1 },
      ]
    : [];

  return (
    <main className="main-content">
      <header className="page-header">
        <div>
          <p className="eyebrow">Insights</p>
          <h1>Analytics</h1>
          <p>Insights into support tickets and machine learning performance.</p>
        </div>
      </header>

      <section className="stats-grid">
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

      <section className="analytics-grid">
        <div className="panel analytics-card">
          <h2>Tickets by Category</h2>
          <p className="chart-caption">Count of stored tickets in each predicted category.</p>

          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={categoryData} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />
              <XAxis dataKey="category" tick={axisTick} axisLine={false} tickLine={false} interval={0} />
              <YAxis allowDecimals={false} tick={axisTick} axisLine={false} tickLine={false} width={36} />
              <Tooltip
                cursor={{ fill: "rgba(99, 102, 241, 0.08)" }}
                content={
                  <ChartTooltip valueFormatter={(value) => `${value} tickets`} />
                }
              />
              <Legend wrapperStyle={{ color: "#cbd5e1", fontSize: 13 }} />
              <Bar dataKey="count" name="Tickets" radius={[6, 6, 0, 0]} maxBarSize={48}>
                {categoryData.map((entry, index) => (
                  <Cell key={entry.category} fill={categoryColor(entry.category, index)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="panel analytics-card">
          <h2>Category Distribution</h2>
          <p className="chart-caption">Share of tickets among categories that have volume.</p>

          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="count"
                  nameKey="category"
                  cx="50%"
                  cy="46%"
                  innerRadius={62}
                  outerRadius={96}
                  paddingAngle={3}
                  stroke="rgba(7, 13, 26, 0.8)"
                >
                  {pieData.map((entry, index) => (
                    <Cell
                      key={entry.category}
                      fill={categoryColor(entry.category, index)}
                    />
                  ))}
                </Pie>
                <Tooltip
                  content={<ChartTooltip valueFormatter={(value) => `${value} tickets`} />}
                />
                <Legend wrapperStyle={{ color: "#cbd5e1", fontSize: 13 }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="status-line">No ticket category data available yet.</p>
          )}
        </div>
      </section>

      <section className="panel analytics-card">
        <h2>Average Confidence by Category</h2>
        <p className="chart-caption">Mean model confidence for tickets already stored in each category.</p>

        {confidenceData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={confidenceData} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />
              <XAxis dataKey="category" tick={axisTick} axisLine={false} tickLine={false} interval={0} />
              <YAxis
                domain={[0, 100]}
                tick={axisTick}
                axisLine={false}
                tickLine={false}
                tickFormatter={(value) => `${value}%`}
                width={42}
              />
              <Tooltip
                cursor={{ fill: "rgba(99, 102, 241, 0.08)" }}
                content={
                  <ChartTooltip
                    valueFormatter={(value, item) =>
                      item?.payload?.raw == null
                        ? "No tickets in this category"
                        : `${Number(value).toFixed(2)}%`
                    }
                  />
                }
              />
              <Legend wrapperStyle={{ color: "#cbd5e1", fontSize: 13 }} />
              <Bar
                dataKey="confidence"
                name="Average confidence"
                fill="#818cf8"
                radius={[6, 6, 0, 0]}
                maxBarSize={48}
              />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="status-line">Category confidence data is unavailable.</p>
        )}
      </section>

      <section className="panel analytics-card model-metrics-card">
        <h2>Machine Learning Model Performance</h2>

        {metrics ? (
          <>
            <div className="metric-notes">
              <p>Evaluation dataset size: {metrics.test_size}</p>
              <p>Trained at: {metrics.trained_at}</p>
            </div>

            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={metricData}
                margin={{ top: 12, right: 12, left: 0, bottom: 8 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} vertical={false} />
                <XAxis dataKey="name" tick={axisTick} axisLine={false} tickLine={false} />
                <YAxis
                  domain={[0, 1]}
                  tick={axisTick}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                  width={42}
                />
                <Tooltip
                  cursor={{ fill: "rgba(16, 185, 129, 0.08)" }}
                  content={
                    <ChartTooltip
                      valueFormatter={(value) => `${(Number(value) * 100).toFixed(2)}%`}
                    />
                  }
                />
                <Legend wrapperStyle={{ color: "#cbd5e1", fontSize: 13 }} />
                <Bar dataKey="value" name="Score" radius={[6, 6, 0, 0]} maxBarSize={56}>
                  {metricData.map((entry, index) => (
                    <Cell key={entry.name} fill={METRIC_COLORS[index % METRIC_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </>
        ) : (
          <p className="status-line">Model evaluation metrics are unavailable.</p>
        )}
      </section>
    </main>
  );
}

export default Analytics;
