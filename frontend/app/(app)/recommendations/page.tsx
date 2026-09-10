"use client";

import { FormEvent, useState } from "react";
import { Button } from "@/components/Button";
import { CaseCard } from "@/components/CaseCard";
import { EmptyState, ErrorState } from "@/components/EmptyState";
import { Input } from "@/components/Input";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { api, ApiError, NETWORK_ERROR_MESSAGE } from "@/lib/api";
import type { RecommendationCase } from "@/types";

export default function RecommendationsPage() {
  const [donorId, setDonorId] = useState("");
  const [items, setItems] = useState<RecommendationCase[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!donorId.trim()) {
      setError("Enter a donor ID from the CareHaven donors table.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const results = await api.recommendations(donorId.trim());
      setItems(results);
    } catch (err) {
      setItems(null);
      setError(err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Recommendations</h1>
        <p className="mt-1 text-sm text-slate-600">
          Matching is performed by the existing backend recommender using a donor ID
          from the donors table, not your login account.
        </p>
      </div>
      <form className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-4 sm:flex-row sm:items-end" onSubmit={onSubmit}>
        <div className="flex-1">
          <Input
            id="donor"
            label="Donor ID"
            value={donorId}
            onChange={setDonorId}
            placeholder="DONOR-001"
            required
          />
        </div>
        <Button type="submit" disabled={loading}>
          Get recommendations
        </Button>
      </form>
      {loading ? <LoadingSpinner label="Loading recommendations" /> : null}
      {error ? <ErrorState message={error} onRetry={() => void onSubmit({ preventDefault() {} } as FormEvent)} /> : null}
      {!loading && !error && items && items.length === 0 ? (
        <EmptyState
          title="No eligible recommendations"
          description="The recommender did not return cases for this donor."
        />
      ) : null}
      {items && items.length > 0 ? (
        <div className="grid gap-4 lg:grid-cols-2">
          {items.map((item) => (
            <CaseCard key={item.case_id} item={item} href={`/cases/${item.case_id}`} />
          ))}
        </div>
      ) : null}
    </div>
  );
}
