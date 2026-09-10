"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { Input, Textarea } from "@/components/Input";
import { Select } from "@/components/Select";
import { api, ApiError, NETWORK_ERROR_MESSAGE } from "@/lib/api";
import type { CaseCreate, CaseLevel } from "@/types";

const LEVELS: CaseLevel[] = ["Low", "Medium", "High", "Critical"];

export default function SubmitCasePage() {
  const router = useRouter();
  const [form, setForm] = useState({
    description: "",
    assistance_category: "",
    people_affected: "1",
    country: "",
    governorate: "",
    city: "",
    severity: "Medium" as CaseLevel,
    urgency: "Medium" as CaseLevel,
    required_resources: "",
    estimated_funding: "",
  });
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    const people = Number(form.people_affected);
    if (!form.description.trim() || !form.assistance_category.trim() || !form.country.trim()) {
      setError("Description, assistance category, and country are required.");
      return;
    }
    if (!Number.isInteger(people) || people < 1) {
      setError("People affected must be a whole number of at least 1.");
      return;
    }

    const payload: CaseCreate = {
      description: form.description.trim(),
      assistance_category: form.assistance_category.trim(),
      people_affected: people,
      country: form.country.trim(),
      severity: form.severity,
      urgency: form.urgency,
    };
    if (form.governorate.trim()) payload.governorate = form.governorate.trim();
    if (form.city.trim()) payload.city = form.city.trim();
    if (form.required_resources.trim()) payload.required_resources = form.required_resources.trim();
    if (form.estimated_funding.trim()) {
      const funding = Number(form.estimated_funding);
      if (!Number.isFinite(funding) || funding < 0) {
        setError("Estimated funding must be a valid number.");
        return;
      }
      payload.estimated_funding = funding;
    }

    setSubmitting(true);
    try {
      const created = await api.createCase(payload);
      if (file) {
        try {
          await api.uploadEvidence(created.case_id, file, form.description.trim());
          setSuccess(`${created.case_id} submitted with evidence.`);
        } catch (err) {
          setSuccess(`${created.case_id} was created, but evidence could not be uploaded.`);
          setError(err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE);
        }
      } else {
        setSuccess(`${created.case_id} submitted.`);
      }
      setTimeout(() => router.push(`/cases/${created.case_id}`), 800);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : NETWORK_ERROR_MESSAGE);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Submit a case</h1>
        <p className="mt-1 text-sm text-slate-600">
          Fields match the backend case schema. New cases start as Under Review.
        </p>
      </div>
      <Card>
        <form className="grid gap-4" onSubmit={onSubmit}>
          <Textarea
            id="description"
            label="Description"
            value={form.description}
            onChange={(value) => setForm((c) => ({ ...c, description: value }))}
            required
          />
          <Input
            id="category"
            label="Assistance category"
            value={form.assistance_category}
            onChange={(value) => setForm((c) => ({ ...c, assistance_category: value }))}
            required
          />
          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              id="people"
              label="People affected"
              type="number"
              min={1}
              value={form.people_affected}
              onChange={(value) => setForm((c) => ({ ...c, people_affected: value }))}
              required
            />
            <Input
              id="country"
              label="Country"
              value={form.country}
              onChange={(value) => setForm((c) => ({ ...c, country: value }))}
              required
            />
            <Input
              id="governorate"
              label="Governorate (optional)"
              value={form.governorate}
              onChange={(value) => setForm((c) => ({ ...c, governorate: value }))}
            />
            <Input
              id="city"
              label="City (optional)"
              value={form.city}
              onChange={(value) => setForm((c) => ({ ...c, city: value }))}
            />
            <Select
              id="severity"
              label="Severity"
              value={form.severity}
              onChange={(value) => setForm((c) => ({ ...c, severity: value as CaseLevel }))}
              options={LEVELS.map((value) => ({ value, label: value }))}
            />
            <Select
              id="urgency"
              label="Urgency"
              value={form.urgency}
              onChange={(value) => setForm((c) => ({ ...c, urgency: value as CaseLevel }))}
              options={LEVELS.map((value) => ({ value, label: value }))}
            />
          </div>
          <Input
            id="resources"
            label="Required resources (optional)"
            value={form.required_resources}
            onChange={(value) => setForm((c) => ({ ...c, required_resources: value }))}
          />
          <Input
            id="funding"
            label="Estimated funding (optional)"
            type="number"
            min={0}
            step="0.01"
            value={form.estimated_funding}
            onChange={(value) => setForm((c) => ({ ...c, estimated_funding: value }))}
          />
          <label className="block space-y-1.5 text-sm font-medium" htmlFor="file">
            Evidence image (optional)
            <input
              id="file"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="block w-full font-normal"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
          </label>
          {error ? (
            <p className="text-sm text-rose-700" role="alert">
              {error}
            </p>
          ) : null}
          {success ? (
            <p className="text-sm text-emerald-800" role="status">
              {success}
            </p>
          ) : null}
          <Button type="submit" disabled={submitting}>
            {submitting ? "Submitting…" : "Submit case"}
          </Button>
        </form>
      </Card>
    </div>
  );
}
