"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { Button } from "@/components/Button";
import { CaseCard } from "@/components/CaseCard";
import { EmptyState, ErrorState } from "@/components/EmptyState";
import { Input } from "@/components/Input";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { Select } from "@/components/Select";
import { api, ApiError, NETWORK_ERROR_MESSAGE } from "@/lib/api";
import type { Case, CaseListParams } from "@/types";

const LEVELS = ["Low", "Medium", "High", "Critical"];
const STATUSES = ["Active", "Under Review", "Funded", "Completed"];

export default function CasesPage() {
  const [items, setItems] = useState<Case[]>([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<CaseListParams>({});

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.listCases({ ...filters, page, page_size: 12 });
      setItems(response.items);
      setPages(response.pages || 1);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => {
    void load();
  }, [load]);

  function applyFilters(event: FormEvent) {
    event.preventDefault();
    setPage(1);
    setFilters((current) => ({
      ...current,
      assistance_category: search.trim() || undefined,
    }));
  }

  const visible = items.filter((item) => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return [item.case_id, item.description, item.assistance_category, item.country, item.city]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(q));
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Cases</h1>
        <p className="mt-1 text-sm text-slate-600">
          Live humanitarian cases from the CareHaven backend. Category is sent as an API
          filter; search also matches the loaded page locally.
        </p>
      </div>

      <form
        onSubmit={applyFilters}
        className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 md:grid-cols-2 xl:grid-cols-4"
      >
        <Input
          id="search"
          label="Search / category"
          value={search}
          onChange={setSearch}
          placeholder="Food, CASE-…, city"
        />
        <Input
          id="country"
          label="Country"
          value={filters.country ?? ""}
          onChange={(value) => setFilters((c) => ({ ...c, country: value || undefined }))}
        />
        <Select
          id="priority"
          label="Priority"
          value={filters.priority ?? ""}
          allowEmpty
          onChange={(value) => setFilters((c) => ({ ...c, priority: value || undefined }))}
          options={LEVELS.map((value) => ({ value, label: value }))}
        />
        <Select
          id="status"
          label="Status"
          value={filters.status ?? ""}
          allowEmpty
          onChange={(value) => setFilters((c) => ({ ...c, status: value || undefined }))}
          options={STATUSES.map((value) => ({ value, label: value }))}
        />
        <Select
          id="severity"
          label="Severity"
          value={filters.severity ?? ""}
          allowEmpty
          onChange={(value) => setFilters((c) => ({ ...c, severity: value || undefined }))}
          options={LEVELS.map((value) => ({ value, label: value }))}
        />
        <Select
          id="urgency"
          label="Urgency"
          value={filters.urgency ?? ""}
          allowEmpty
          onChange={(value) => setFilters((c) => ({ ...c, urgency: value || undefined }))}
          options={LEVELS.map((value) => ({ value, label: value }))}
        />
        <div className="flex items-end">
          <Button type="submit">Apply filters</Button>
        </div>
      </form>

      {loading ? <LoadingSpinner label="Loading cases" /> : null}
      {error ? <ErrorState message={error} onRetry={load} /> : null}
      {!loading && !error && visible.length === 0 ? (
        <EmptyState
          title="No cases match these filters"
          description="Try clearing filters or submit a new case."
        />
      ) : null}
      <div className="grid gap-4 lg:grid-cols-2">
        {visible.map((item) => (
          <CaseCard key={item.case_id} item={item} href={`/cases/${item.case_id}`} />
        ))}
      </div>
      {!loading && !error && total > 0 ? (
        <div className="flex items-center justify-between text-sm text-slate-600">
          <p>
            {total} case{total === 1 ? "" : "s"} · page {page} of {pages}
          </p>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
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
