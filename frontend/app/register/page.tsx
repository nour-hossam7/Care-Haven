"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Button } from "@/components/Button";
import { Card } from "@/components/Card";
import { Input } from "@/components/Input";
import { ApiError } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";

export default function RegisterPage() {
  const { register, user, loading } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!loading && user) {
    router.replace("/dashboard");
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await register(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to register.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <Card className="w-full max-w-md">
        <h1 className="text-2xl font-semibold text-slate-900">Create an account</h1>
        <p className="mt-2 text-sm text-slate-600">
          New accounts are created with the standard user role. Admin access is assigned
          separately by the backend.
        </p>
        <form className="mt-6 space-y-4" onSubmit={onSubmit}>
          <Input
            id="email"
            label="Email"
            type="email"
            value={email}
            onChange={setEmail}
            required
            autoComplete="email"
          />
          <Input
            id="password"
            label="Password (min 8 characters)"
            type="password"
            value={password}
            onChange={setPassword}
            required
            autoComplete="new-password"
          />
          {error ? (
            <p className="text-sm text-rose-700" role="alert">
              {error}
            </p>
          ) : null}
          <Button type="submit" className="w-full" disabled={submitting}>
            {submitting ? "Creating account…" : "Register"}
          </Button>
        </form>
        <p className="mt-4 text-sm text-slate-600">
          Already registered?{" "}
          <Link href="/login" className="font-semibold text-brand-700">
            Sign in
          </Link>
        </p>
      </Card>
    </div>
  );
}
