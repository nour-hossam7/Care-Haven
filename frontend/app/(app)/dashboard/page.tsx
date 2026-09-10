"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Card } from "@/components/Card";
import { CaseCard } from "@/components/CaseCard";
import { EmptyState, ErrorState } from "@/components/EmptyState";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { api, ApiError, NETWORK_ERROR_MESSAGE } from "@/lib/api";
import { formatMoney } from "@/lib/format";
import { useCaseEvidence } from "@/hooks/useCaseEvidence";
import type { Case } from "@/types";

interface Metrics {
  totalCases: number;
  activeCases: number;
  criticalCases: number;
  donations: number;
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [recent, setRecent] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const evidenceByCase = useCaseEvidence(recent.map((item) => item.case_id));

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [all, active, critical, donations] = await Promise.all([
        api.listCases({ page: 1, page_size: 6 }),
        api.listCases({ page: 1, page_size: 1, status: "Active" }),
        api.listCases({ page: 1, page_size: 1, priority: "Critical" }),
        api.listDonations(1, 1),
      ]);
      setRecent(all.items);
      setMetrics({
        totalCases: all.total,
        activeCases: active.total,
        criticalCases: critical.total,
        donations: donations.total,
      });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE);
      setMetrics(null);
      setRecent([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Dashboard</h1>
        <p className="mt-1 text-sm text-slate-600">
          Counts below come from the CareHaven API. Metrics that the backend does not
          provide are omitted.
        </p>
      </div>
      {loading ? <LoadingSpinner label="Loading dashboard" /> : null}
      {error ? <ErrorState message={error} onRetry={load} /> : null}
      {metrics ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <Metric label="Total cases" value={String(metrics.totalCases)} />
          <Metric label="Active cases" value={String(metrics.activeCases)} />
          <Metric label="Critical priority" value={String(metrics.criticalCases)} />
          <Metric label="Donation records" value={String(metrics.donations)} />
        </div>
      ) : null}
      {!loading && !error ? (
        <section>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Recent cases</h2>
            <Link href="/cases" className="text-sm font-semibold text-brand-700">
              View all
            </Link>
          </div>
          {recent.length === 0 ? (
            <EmptyState
              title="No cases yet"
              description="When cases are submitted, they will appear here."
            />
          ) : (
            <div className="grid gap-4 lg:grid-cols-2">
              {recent.map((item) => (
                <CaseCard
                  key={item.case_id}
                  item={item}
                  href={`/cases/${item.case_id}`}
                  evidenceImageUrl={evidenceByCase[item.case_id]?.find((evidence) => evidence.image_url)?.image_url}
                />
              ))}
            </div>
          )}
        </section>
      ) : null}
      {recent.length > 0 ? (
        <Card>
          <p className="text-sm text-slate-600">
            Combined reported funding on this page:{" "}
            <span className="font-semibold text-slate-900">
              {formatMoney(
                recent.reduce((sum, item) => {
                  const value = Number(item.current_funding);
                  return sum + (Number.isFinite(value) ? value : 0);
                }, 0),
              )}
            </span>{" "}
            across the {recent.length} most recently listed cases.
          </p>
        </Card>
      ) : null}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-slate-900">{value}</p>
    </Card>
  );
}
