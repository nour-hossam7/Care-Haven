"use client";

import { NavLinks } from "@/components/Navbar";

export function Sidebar() {
  return (
    <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white p-5 lg:block">
      <p className="mb-6 text-sm font-semibold uppercase tracking-wide text-slate-500">
        Humanitarian aid
      </p>
      <NavLinks />
    </aside>
  );
}
