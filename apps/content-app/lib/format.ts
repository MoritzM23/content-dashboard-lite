/**
 * Formatierung-Helper, gleiche Konventionen wie das alte Dashboard.
 */

export function fmtNum(n: number | null | undefined): string {
  if (n == null || !isFinite(n)) return '—';
  if (Math.abs(n) >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (Math.abs(n) >= 1_000) return (n / 1_000).toFixed(1) + 'k';
  return String(Math.round(n));
}

export function fmtPct(n: number | null | undefined, decimals = 2): string {
  if (n == null || !isFinite(n)) return '—';
  return n.toFixed(decimals) + '%';
}

export function fmtDate(s: string | null | undefined): string {
  if (!s) return '—';
  const m = String(s).match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!m) return String(s).slice(0, 10);
  const [, y, mo, d] = m;
  const months = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'];
  return `${parseInt(d, 10)}. ${months[parseInt(mo, 10) - 1]} ${y.slice(2)}`;
}

export function fmtRelDays(s: string | null | undefined): string {
  if (!s) return '—';
  const d = new Date(s);
  if (isNaN(d.getTime())) return '—';
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const days = Math.floor(diffMs / 86400000);
  if (days === 0) return 'heute';
  if (days === 1) return 'gestern';
  if (days < 7) return `vor ${days}d`;
  if (days < 30) return `vor ${Math.floor(days / 7)}w`;
  return `vor ${Math.floor(days / 30)}m`;
}
