import React, { useState } from 'react';

interface PromptFormProps {
  onSubmit: (prompt: string) => Promise<void> | void;
  loading: boolean;
  activeVizLabel?: string | null;
}

const examplePrompts = [
  'Create a pie chart representing industry breakdown',
  'Create a scatter plot of founded year and valuation',
  'Create a table to see which investors appear most frequently',
  'Give me the best representation of data if I want to understand the correlation of ARR and Valuation',
];

export const PromptForm: React.FC<PromptFormProps> = ({
  onSubmit,
  loading,
  activeVizLabel,
}) => {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || loading) return;
    await onSubmit(prompt.trim());
    setPrompt('');
  };

  const handleExampleClick = (p: string) => {
    setPrompt(p);
  };

  return (
    <div className="card">
      <div className="card-title">
        Prompt
        <span className="badge">Natural language → viz</span>
      </div>
      <form onSubmit={handleSubmit}>
        <textarea
          className="textarea"
          placeholder={
            activeVizLabel
              ? `Tweaking visualization: ${activeVizLabel}`
              : 'Ask anything about the dataset, e.g. "Create a scatter plot of ARR and Valuation"'
          }
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <div className="button-row">
          <button type="submit" className="button-primary" disabled={loading}>
            {loading ? 'Thinking…' : 'Run'}
          </button>
          <div className="small-muted">
            {activeVizLabel
              ? 'Updates apply to the selected visualization.'
              : 'No visualization selected — this will create a new one.'}
          </div>
        </div>
      </form>
      <div style={{ marginTop: '0.6rem' }}>
        <div className="small-muted" style={{ marginBottom: '0.25rem' }}>
          Examples:
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem' }}>
          {examplePrompts.map((p) => (
            <button
              key={p}
              type="button"
              className="button-secondary"
              onClick={() => handleExampleClick(p)}
            >
              {p.length > 40 ? p.slice(0, 37) + '…' : p}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
