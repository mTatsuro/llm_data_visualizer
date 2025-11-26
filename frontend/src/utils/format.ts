export function formatShortNumber(value: number | string): string {
  const num = typeof value === 'number' ? value : parseFloat(String(value));
  if (!Number.isFinite(num)) {
    return String(value);
  }
  const abs = Math.abs(num);

  const format = (n: number, suffix: string) =>
    `${n.toFixed(1).replace(/\.0$/, '')}${suffix}`;

  if (abs >= 1e12) return format(num / 1e12, 'T');
  if (abs >= 1e9) return format(num / 1e9, 'B');
  if (abs >= 1e6) return format(num / 1e6, 'M');
  if (abs >= 1e3) return format(num / 1e3, 'k');
  if (abs >= 1) return num.toFixed(0);

  // tiny values
  return num.toPrecision(2);
}
