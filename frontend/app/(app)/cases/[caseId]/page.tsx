"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { ErrorState } from "@/components/ErrorState";
import { FundingProgress } from "@/components/FundingProgress";
import { Input } from "@/components/Input";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { Modal } from "@/components/Modal";
import { PriorityBadge } from "@/components/PriorityBadge";
import { Select } from "@/components/Select";
import { StatusBadge } from "@/components/StatusBadge";
import { useAuth } from "@/hooks/useAuth";
import { api, ApiError, NETWORK_ERROR_MESSAGE } from "@/lib/api";
import { formatDate, formatMoney, locationLabel } from "@/lib/format";
import type { Case, CaseStatus, Donation, HybridAnalysisResponse } from "@/types";

const STATUSES: CaseStatus[] = ["Active", "Under Review", "Funded", "Completed"];

export default function CaseDetailsPage() {
  const params = useParams<{ caseId: string }>();
  const caseId = decodeURIComponent(params.caseId);
  const { user } = useAuth();
  const [item, setItem] = useState<Case | null>(null);
  const [donations, setDonations] = useState<Donation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [donateOpen, setDonateOpen] = useState(false);
  const [amount, setAmount] = useState("50");
  const [status, setStatus] = useState<CaseStatus>("Under Review");
  const [message, setMessage] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<HybridAnalysisResponse | null>(null);
  const [busy, setBusy] = useState(false);

  const canModify =
    user?.role === "admin" || (item?.created_by != null && item.created_by === user?.user_id);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [caseItem, caseDonations] = await Promise.all([
        api.getCase(caseId),
        api.caseDonations(caseId, 1, 20),
      ]);
      setItem(caseItem);
      setStatus((caseItem.status as CaseStatus) || "Under Review");
      setDonations(caseDonations.items);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE);
      setItem(null);
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function donate(event: FormEvent) {
    event.preventDefault();
    const value = Number(amount);
    if (!Number.isFinite(value) || value <= 0) {
      setMessage("Enter a positive donation amount.");
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      await api.createDonation({ case_id: caseId, amount: value });
      setDonateOpen(false);
      await load();
      setMessage("Donation recorded.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE);
    } finally {
      setBusy(false);
    }
  }

  async function saveStatus() {
    setBusy(true);
    setMessage(null);
    try {
      const updated = await api.updateCaseStatus(caseId, { status });
      setItem(updated);
      setMessage("Case status updated.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE);
    } finally {
      setBusy(false);
    }
  }

  async function uploadEvidence(file: File) {
    setBusy(true);
    setMessage(null);
    try {
      await api.uploadEvidence(caseId, file, item?.description ?? undefined);
      setMessage("Evidence uploaded and queued for review.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE);
    } finally {
      setBusy(false);
    }
  }

  async function runAnalysis() {
    setBusy(true);
    setMessage(null);
    try {
      setAnalysis(await api.hybridAnalysis(caseId));
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE);
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <LoadingSpinner label="Loading case" />;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!item) return <ErrorState message="Case not found." onRetry={load} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="font-mono text-sm text-slate-500">{item.case_id}</p>
          <h1 className="text-2xl font-semibold text-slate-900">
            {item.assistance_category || "Humanitarian case"}
          </h1>
          <p className="mt-1 text-sm text-slate-600">{locationLabel(item)}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusBadge status={item.status} />
          <PriorityBadge value={item.priority} />
          <PriorityBadge label="Severity" value={item.severity} />
          <PriorityBadge label="Urgency" value={item.urgency} />
        </div>
      </div>

      {message ? (
        <p className="rounded-xl bg-slate-100 px-4 py-3 text-sm" role="status">
          {message}
        </p>
      ) : null}

      <Card>
        <h2 className="font-semibold">Description</h2>
        <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-700">
          {item.description || "No description provided."}
        </p>
        <dl className="mt-6 grid gap-4 sm:grid-cols-2">
          <Field label="People affected" value={item.people_affected ?? "—"} />
          <Field label="Required resources" value={item.required_resources ?? "—"} />
          <Field label="Submitted" value={formatDate(item.submission_date)} />
          <Field label="Created by" value={item.created_by ?? "—"} />
        </dl>
        <div className="mt-6">
          <FundingProgress current={item.current_funding} estimated={item.estimated_funding} />
        </div>
        <div className="mt-6">
          <Button onClick={() => setDonateOpen(true)}>Record a donation</Button>
        </div>
      </Card>

      {canModify ? (
        <Card className="space-y-4">
          <h2 className="font-semibold">Case actions</h2>
          <div className="grid gap-3 sm:grid-cols-[1fr_auto] sm:items-end">
            <Select
              id="status"
              label="Status"
              value={status}
              onChange={(value) => setStatus(value as CaseStatus)}
              options={STATUSES.map((value) => ({ value, label: value }))}
            />
            <Button onClick={saveStatus} disabled={busy}>
              Update status
            </Button>
          </div>
          <label className="block text-sm font-medium text-slate-800" htmlFor="evidence">
            Upload evidence image (JPG, PNG, or WEBP)
            <input
              id="evidence"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="mt-2 block w-full text-sm"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) void uploadEvidence(file);
              }}
            />
          </label>
        </Card>
      ) : null}

      <Card>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="font-semibold">AI decision support</h2>
            <p className="mt-1 text-sm text-slate-600">
              Hybrid analysis is a review aid, not a final eligibility or fraud decision.
            </p>
          </div>
          <Button variant="secondary" onClick={runAnalysis} disabled={busy}>
            Run hybrid analysis
          </Button>
        </div>
        {analysis ? (
          <div className="mt-4 space-y-3 text-sm">
            {analysis.llm_analysis ? (
              <p>{analysis.llm_analysis.summary}</p>
            ) : null}
            {analysis.priority ? (
              <p>
                Priority score {analysis.priority.score} ({analysis.priority.priority_level})
              </p>
            ) : null}
            {analysis.unavailable_components.length ? (
              <p className="text-amber-800">
                Unavailable components: {analysis.unavailable_components.join(", ")}
              </p>
            ) : null}
          </div>
        ) : null}
      </Card>

      <Card>
        <h2 className="font-semibold">Donations for this case</h2>
        {donations.length === 0 ? (
          <p className="mt-3 text-sm text-slate-600">No donations recorded yet.</p>
        ) : (
          <ul className="mt-3 divide-y divide-slate-100">
            {donations.map((donation) => (
              <li key={donation.donation_id} className="flex justify-between py-3 text-sm">
                <span>{donation.donation_id}</span>
                <span>{formatMoney(donation.amount)}</span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Modal title="Record a donation" open={donateOpen} onClose={() => setDonateOpen(false)}>
        <form className="space-y-4" onSubmit={donate}>
          <p className="text-sm text-slate-600">
            This records a donation in CareHaven. It does not process a real payment.
          </p>
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
          <Button type="submit" disabled={busy}>
            Confirm donation
          </Button>
        </form>
      </Modal>
    </div>
  );
}

function Field({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm text-slate-800">{value}</dd>
    </div>
  );
}
