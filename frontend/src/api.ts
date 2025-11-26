import type { VisualizationResult } from './types';

export interface VisualizeRequest {
  prompt: string;
  current_viz: any | null;
  target_viz_id: string | null;
}

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || '';

export async function callVisualizeApi(
  prompt: string,
  currentViz: VisualizationResult | null,
): Promise<VisualizationResult> {
  const body: VisualizeRequest = {
    prompt,
    current_viz: currentViz
      ? {
          action: currentViz.action,
          target_viz_id: currentViz.viz_id,
          chart: {
            viz_type: currentViz.viz_type,
            transforms: currentViz.transforms ?? [],
            encoding: currentViz.encoding,
            style: currentViz.style,
          },
        }
      : null,
    target_viz_id: currentViz ? currentViz.viz_id : null,
  };

  const res = await fetch(`${API_BASE_URL}/api/visualize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Backend error ${res.status}: ${text}`);
  }

  const payload = await res.json();

  // Normalize payload into our VisualizationResult shape
  const viz: VisualizationResult = {
    viz_id: payload.viz_id,
    action: payload.action,
    target_viz_id: payload.target_viz_id ?? null,
    viz_type: payload.viz_type,
    encoding: payload.encoding ?? {},
    style: payload.style ?? {},
    transforms: payload.transforms ?? [],
    data: payload.data ?? [],
    errors: payload.errors,
    insights: payload.insights ?? {},
  };

  return viz;
}
