"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { EmptyState, ErrorState } from "@/components/EmptyState";
import { Input } from "@/components/Input";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { api, ApiError, NETWORK_ERROR_MESSAGE } from "@/lib/api";
import { formatDate, formatMoney } from "@/lib/format";
import type { Donation } from "@/types";

export default function DonationsPage() {
  const [items, setItems] = useState<Donation[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [mineOnly, setMineOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [caseId, setCaseId] = useState("");
  const [amount, setAmount] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = mineOnly
        ? await api.myDonationHistory(page, 20)
        : await api.listDonations(page, 20);
      setItems(response.items);
      setTotal(response.total);
      setPages(response.pages || 1);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [mineOnly, page]);

  useEffect(() => {
    void load();
  }, [load]);

  async function donate(event: FormEvent) {
    event.preventDefault();
    const value = Number(amount);
    if (!caseId.trim()) {
      setFormError("Case ID is required.");
      return;
    }
    if (!Number.isFinite(value) || value <= 0) {
      setFormError("Amount must be greater than 0.");
      return;
    }
    setSubmitting(true);
    setFormError(null);
    setFormSuccess(null);
    try {
      const created = await api.createDonation({
        case_id: caseId.trim(),
        amount: value,
      });
      setFormSuccess(`Recorded ${created.donation_id}.`);
      setAmount("");
      await load();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Donations</h1>
        <p className="mt-1 text-sm text-slate-600">
          Donations are application records in CareHaven. No payment gateway is used.
        </p>
      </div>

      <Card>
        <h2 className="font-semibold">Record a donation</h2>
        <form className="mt-4 grid gap-4 sm:grid-cols-2" onSubmit={donate}>
          <Input
            id="case-id"
            label="Case ID"
            value={caseId}
            onChange={setCaseId}
            required
            placeholder="CASE-…"
          />
          <Input
            id="amount"
            label="Amount"
            type="number"
            min={0.01}
            step="0.01"
            value={amount}
            onChange={setAmount}
            required
          />
          {formError ? (
            <p className="text-sm text-rose-700 sm:col-span-2" role="alert">
              {formError}
            </p>
          ) : null}
          {formSuccess ? (
            <p className="text-sm text-emerald-800 sm:col-span-2" role="status">
              {formSuccess}
            </p>
          ) : null}
          <Button type="submit" disabled={submitting}>
            {submitting ? "Saving…" : "Save donation"}
          </Button>
        </form>
      </Card>

      <div className="flex flex-wrap gap-2">
        <Button
          variant={mineOnly ? "secondary" : "primary"}
          onClick={() => {
            setMineOnly(false);
            setPage(1);
          }}
        >
          Donation list
        </Button>
        <Button
          variant={mineOnly ? "primary" : "secondary"}
          onClick={() => {
            setMineOnly(true);
            setPage(1);
          }}
        >
          My history
        </Button>
      </div>

      {loading ? <LoadingSpinner label="Loading donations" /> : null}
      {error ? <ErrorState message={error} onRetry={load} /> : null}
      {!loading && !error && items.length === 0 ? (
        <EmptyState
          title="No donations yet"
          description="Record a donation against an existing case ID."
        />
      ) : null}
      {!loading && !error && items.length > 0 ? (
        <Card className="overflow-x-auto p-0">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Donation</th>
                <th className="px-4 py-3 font-medium">Case</th>
                <th className="px-4 py-3 font-medium">Amount</th>
                <th className="px-4 py-3 font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.donation_id} className="border-t border-slate-100">
                  <td className="px-4 py-3 font-mono text-xs">{item.donation_id}</td>
                  <td className="px-4 py-3">{item.case_id ?? "—"}</td>
                  <td className="px-4 py-3">{formatMoney(item.amount)}</td>
                  <td className="px-4 py-3">{formatDate(item.date)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      ) : null}
      {total > 0 ? (
        <div className="flex items-center justify-between text-sm text-slate-600">
          <p>
            {total} record{total === 1 ? "" : "s"}
          </p>
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
