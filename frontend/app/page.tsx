"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Button } from "@/components/Button";
import { api } from "@/lib/api";

export default function HomePage() {
  const [backendOk, setBackendOk] = useState<boolean | null>(null);

  useEffect(() => {
    api
      .health()
      .then(() => setBackendOk(true))
      .catch(() => setBackendOk(false));
  }, []);

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#f0fdfa_0%,#f8fafc_28%,#f8fafc_100%)]">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-4 py-5">
        <p className="text-lg font-semibold text-brand-800">CareHaven</p>
        <div className="flex gap-3">
          <Link href="/login">
            <Button variant="secondary">Sign in</Button>
          </Link>
          <Link href="/register">
            <Button>Create account</Button>
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 pb-20 pt-10">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-brand-700">
          Humanitarian aid platform
        </p>
        <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
          Connect urgent humanitarian cases with the people who can help.
        </h1>
        <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600">
          CareHaven helps beneficiaries submit needs, donors find high-priority cases,
          and reviewers work from evidence and AI decision-support — without replacing
          human judgment.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link href="/register">
            <Button>Get started</Button>
          </Link>
          <Link href="/login">
            <Button variant="secondary">I already have an account</Button>
          </Link>
        </div>
        {backendOk === false ? (
          <p className="mt-6 text-sm text-rose-700" role="status">
            Unable to connect to CareHaven backend.
          </p>
        ) : null}

        <section className="mt-16 grid gap-5 md:grid-cols-3">
          {[
            {
              title: "Submit and review cases",
              body: "Record assistance needs, location, urgency, and evidence for human review.",
            },
            {
              title: "Donate where it matters",
              body: "Browse real cases, track funding progress, and record donations through the CareHaven API.",
            },
            {
              title: "Ask the knowledge assistant",
              body: "Use the existing RAG assistant for grounded humanitarian guidance and cited sources.",
            },
          ].map((item) => (
            <article
              key={item.title}
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <h2 className="text-lg font-semibold text-slate-900">{item.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.body}</p>
            </article>
          ))}
        </section>
      </main>
    </div>
  );
}
