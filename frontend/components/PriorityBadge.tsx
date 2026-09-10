const tones: Record<string, string> = {
  Critical: "bg-rose-100 text-rose-800",
  High: "bg-orange-100 text-orange-800",
  Medium: "bg-sky-100 text-sky-800",
  Low: "bg-slate-100 text-slate-700",
};

export function PriorityBadge({
  label = "Priority",
  value,
}: {
  label?: string;
  value: string | null;
}) {
  if (!value) return null;
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${
        tones[value] ?? "bg-slate-100 text-slate-700"
      }`}
    >
      {label}: {value}
    </span>
  );
}
