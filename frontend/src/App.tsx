import React, { useState } from 'react';
import { PromptForm } from './components/PromptForm';
import { VisualizationCard } from './components/VisualizationCard';
import type { VisualizationResult } from './types';
import { callVisualizeApi } from './api';

const App: React.FC = () => {
  const [visualizations, setVisualizations] = useState<VisualizationResult[]>([]);
  const [activeVizId, setActiveVizId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [globalError, setGlobalError] = useState<string | null>(null);

  const activeViz = activeVizId
    ? visualizations.find((v) => v.viz_id === activeVizId) ?? null
    : null;

  const handleSubmitPrompt = async (prompt: string) => {
    setLoading(true);
    setGlobalError(null);
    try {
      const viz = await callVisualizeApi(prompt, activeViz);
      setVisualizations((prev) => {
        if (viz.action === 'update_visualization' && viz.viz_id) {
          const exists = prev.some((v) => v.viz_id === viz.viz_id);
          if (!exists) {
            return [...prev, viz];
          }
          return prev.map((v) => (v.viz_id === viz.viz_id ? viz : v));
        }
        return [...prev, viz];
      });
      setActiveVizId(viz.viz_id);
    } catch (err: any) {
      console.error(err);
      setGlobalError(err.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectViz = (viz: VisualizationResult) => {
    setActiveVizId(viz.viz_id);
  };

  const activeVizLabel = activeViz?.style?.title ?? null;

  return (
    <div className="app-root">
      <div className="app-container">
        <header className="app-header">
          <h1>Natural-language Visualization UI</h1>
          <p>
            Talk to your dataset using free-form prompts. Select a visualization
            to tweak it with follow-up instructions.
          </p>
        </header>

        <main className="layout-main">
          <section>
            <PromptForm
              onSubmit={handleSubmitPrompt}
              loading={loading}
              activeVizLabel={activeVizLabel}
            />
            {globalError && (
              <div style={{ marginTop: '0.75rem' }}>
                <span className="badge-error">Backend: {globalError}</span>
              </div>
            )}
          </section>

          <section>
            <div className="card">
              <div className="card-title">
                Visualizations
                <span className="badge">
                  {visualizations.length || 0} created
                </span>
              </div>
              {visualizations.length === 0 ? (
                <div className="viz-message">
                  No visualizations yet. Submit a prompt to create one.
                </div>
              ) : (
                <div className="viz-list">
                  {visualizations.map((viz) => (
                    <VisualizationCard
                      key={viz.viz_id}
                      viz={viz}
                      isActive={viz.viz_id === activeVizId}
                      onSelect={() => handleSelectViz(viz)}
                    />
                  ))}
                </div>
              )}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
};

export default App;
