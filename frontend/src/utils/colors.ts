const NAMED_COLORS: Record<string, string> = {
  'light blue': 'lightblue',
  lightblue: 'lightblue',
  blue: 'steelblue',
  'dark blue': 'darkblue',
  red: 'tomato',
  green: 'seagreen',
  orange: 'orange',
  purple: 'rebeccapurple',
  teal: 'teal',
  yellow: 'gold',
};

export function normalizeColor(raw?: string | null): string | undefined {
  if (!raw) return undefined;
  const key = raw.trim().toLowerCase();
  return NAMED_COLORS[key] ?? raw;
}
