export function asNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

export function formatMoney(value: unknown): string {
  const amount = asNumber(value);
  if (amount === null) return "Not reported";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: amount % 1 === 0 ? 0 : 2,
  }).format(amount);
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "Unknown date";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown date";
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
  }).format(date);
}

export function locationLabel(item: {
  city?: string | null;
  governorate?: string | null;
  country?: string | null;
}): string {
  return [item.city, item.governorate, item.country].filter(Boolean).join(", ") || "Location not reported";
}

export function fundingPercent(current: unknown, estimated: unknown): number | null {
  const raised = asNumber(current);
  const goal = asNumber(estimated);
  if (raised === null || goal === null || goal <= 0) return null;
  return Math.min(100, Math.round((raised / goal) * 100));
}
