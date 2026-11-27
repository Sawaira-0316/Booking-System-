// The backend stores everything in UTC. Postgres returns timestamps with an
// offset ("...+00:00"), but some databases (e.g. SQLite) drop it and the API
// sends "2026-12-05T05:30:00". `new Date()` would then read that as LOCAL
// time and shift every booking by the viewer's UTC offset.
// So: if there's no "Z" / "+hh:mm" / "-hh:mm" suffix, treat it as UTC.
export function parseApiDate(value) {
  if (!value) return null;
  const hasZone = /(Z|[+-]\d{2}:?\d{2})$/i.test(value);
  return new Date(hasZone ? value : `${value}Z`);
}

export const formatDateTime = (value) => parseApiDate(value)?.toLocaleString() ?? "";
export const formatDate = (value) => parseApiDate(value)?.toLocaleDateString() ?? "";
