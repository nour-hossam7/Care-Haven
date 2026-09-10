"use client";

import { useCallback, useEffect, useState } from "react";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { EmptyState, ErrorState } from "@/components/EmptyState";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { StatusBadge } from "@/components/StatusBadge";
import { useAuth } from "@/hooks/useAuth";
import { api, ApiError, NETWORK_ERROR_MESSAGE } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { Evidence, VerificationStatus } from "@/types";

export default function ReviewQueuePage() {
  const { user } = useAuth();
  const [items, setItems] = useState<Evidence[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.reviewQueue(page, 20);
      setItems(response.items);
      setTotal(response.total);
      setPages(response.pages || 1);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    if (user?.role === "admin") void load();
    else setLoading(false);
  }, [load, user?.role]);

  async function setStatus(evidenceId: string, verification_status: VerificationStatus) {
    setMessage(null);
    try {
      await api.updateVerification(evidenceId, verification_status);
      setMessage(`Evidence ${evidenceId} marked ${verification_status}.`);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE);
    }
  }

  if (user?.role !== "admin") {
    return (
      <ErrorState message="Admin access required to view the evidence review queue." />
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Review queue</h1>
        <p className="mt-1 text-sm text-slate-600">
          Unreviewed case evidence. Image quality and AI signals are decision-support
          only — they are not a fraud determination.
        </p>
      </div>
      {message ? (
        <p className="rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-900" role="status">
          {message}
        </p>
      ) : null}
      {loading ? <LoadingSpinner label="Loading review queue" /> : null}
      {error ? <ErrorState message={error} onRetry={load} /> : null}
      {!loading && !error && items.length === 0 ? (
        <EmptyState
          title="No unreviewed evidence"
          description="New uploads will appear here for admin verification."
        />
      ) : null}
      <div className="space-y-3">
        {items.map((item) => (
          <Card key={item.evidence_id}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="font-mono text-sm font-semibold">{item.evidence_id}</p>
                <p className="mt-1 text-sm text-slate-600">
                  Case {item.case_id ?? "unknown"} · {item.evidence_type ?? "file"} ·{" "}
                  {formatDate(item.uploaded_at)}
                </p>
                {item.description ? (
                  <p className="mt-2 text-sm text-slate-700">{item.description}</p>
                ) : null}
                {item.file_path ? (
                  <p className="mt-2 text-xs text-slate-500">{item.file_path}</p>
                ) : null}
              </div>
              <StatusBadge status={item.verification_status} />
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <Button onClick={() => void setStatus(item.evidence_id, "approved")}>
                Approve
              </Button>
              <Button
                variant="danger"
                onClick={() => void setStatus(item.evidence_id, "rejected")}
              >
                Reject
              </Button>
            </div>
          </Card>
        ))}
      </div>
      {total > 0 ? (
        <div className="flex items-center justify-between text-sm text-slate-600">
          <p>{total} items</p>
          <div className="flex gap-2">
            <Button variant="secondary" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              Previous
            </Button>
            <Button
              variant="secondary"
              disabled={page >= pages}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
