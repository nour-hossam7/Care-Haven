const tones: Record<string, string> = {
  Active: "bg-emerald-50 text-emerald-800",
  "Under Review": "bg-amber-50 text-amber-800",
  Funded: "bg-sky-50 text-sky-800",
  Completed: "bg-slate-100 text-slate-700",
  approved: "bg-emerald-50 text-emerald-800",
  rejected: "bg-rose-50 text-rose-800",
  unreviewed: "bg-amber-50 text-amber-800",
};

export function StatusBadge({ status }: { status: string | null }) {
  if (!status) return null;
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${
        tones[status] ?? "bg-slate-100 text-slate-700"
      }`}
    >
      {status}
    </span>
  );
}
