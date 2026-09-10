import { formatMoney, fundingPercent } from "@/lib/format";

export function FundingProgress({
  current,
  estimated,
}: {
  current: unknown;
  estimated: unknown;
}) {
  const percent = fundingPercent(current, estimated);

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs text-slate-600">
        <span>Raised {formatMoney(current)}</span>
        <span>Need {formatMoney(estimated)}</span>
      </div>
      <div
        className="h-2 overflow-hidden rounded-full bg-slate-100"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percent ?? 0}
        aria-label="Funding progress"
      >
        <div
          className="h-full rounded-full bg-brand-700"
          style={{ width: `${percent ?? 0}%` }}
        />
      </div>
    </div>
  );
}
