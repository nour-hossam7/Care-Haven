import { Button } from "@/components/Button";

export function EmptyState({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center">
      <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
      <p className="mt-2 text-sm text-slate-600">{description}</p>
    </div>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div
      className="rounded-2xl border border-rose-200 bg-rose-50 px-6 py-8 text-center"
      role="alert"
    >
      <p className="font-medium text-rose-900">{message}</p>
      {onRetry ? (
        <div className="mt-4">
          <Button onClick={onRetry}>Retry</Button>
        </div>
      ) : null}
    </div>
  );
}
