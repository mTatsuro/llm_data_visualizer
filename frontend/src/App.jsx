import React, { useState } from "react";
import { VizCard } from "./VizCard";

/**
 * @typedef {import("./types").Visualization} Visualization
 */

function App() {
  const [prompt, setPrompt] = useState("");
  const [visualizations, setVisualizations] = useState([]);
  const [selectedVizId, setSelectedVizId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const selectedViz = visualizations.find(v => v.viz_id === selectedVizId) || null;

  async function handleSubmit() {
    if (!prompt.trim()) return;
    setLoading(true);
    setError(null);

    const body = {
      prompt,
      target_viz_id: selectedViz ? selectedViz.viz_id : null,
      current_viz: selectedViz
        ? {
            viz_type: selectedViz.viz_type,
            encoding: selectedViz.encoding,
            style: selectedViz.style,
            transforms: selectedViz.transforms || []
          }
        : null
    };

    try {
      const res = await fetch("/api/visualize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });

      if (!res.ok) {
        throw new Error(`Backend error: ${res.status}`);
      }

      const payload = await res.json();

      const viz = {
        viz_id: payload.viz_id,
        viz_type: payload.viz_type,
        data: payload.data,
        encoding: payload.encoding,
        style: payload.style,
        transforms: payload.transforms || [],
        insights: payload.insights || {}
      };

      if (payload.action === "new_visualization") {
        setVisualizations(prev => [...prev, viz]);
        setSelectedVizId(viz.viz_id);
      } else {
        setVisualizations(prev =>
          prev.map(v => (v.viz_id === viz.viz_id ? viz : v))
        );
      }

      setPrompt("");
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-root">
      <header>
        <h1>Natural Language Visualizations – Top 100 SaaS (2025)</h1>
        <p style={{ margin: 0, fontSize: "0.9rem", color: "#4b5563" }}>
          Ask in plain English, e.g. "Create a pie chart of industry breakdown" or
          "Scatter plot of founded year vs valuation".
        </p>
      </header>

      <section className="prompt-section">
        <textarea
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder={
            selectedViz
              ? "Tweak the selected visualization, e.g. 'Change color to light blue'"
              : "Describe the visualization you want, e.g. 'Create a scatter plot of ARR vs valuation'"
          }
        />
        <button onClick={handleSubmit} disabled={loading}>
          {loading ? "Thinking..." : "Run"}
        </button>
        {error && (
          <p style={{ color: "#b91c1c", fontSize: "0.85rem" }}>
            {error}
          </p>
        )}
      </section>

      <section className="viz-list">
        {visualizations.map(viz => (
          <VizCard
            key={viz.viz_id}
            viz={viz}
            selected={viz.viz_id === selectedVizId}
            onSelect={() => setSelectedVizId(viz.viz_id)}
          />
        ))}
        {!visualizations.length && !loading && (
          <p style={{ fontSize: "0.9rem", color: "#6b7280" }}>
            No visualizations yet. Try something like{" "}
            <code>Create a pie chart representing industry breakdown</code>.
          </p>
        )}
      </section>
    </div>
  );
}

export default App;
