"use client";

import { useState } from "react";
import { AppShell } from "@/components/AppShell";

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <AppShell menuOpen={menuOpen} setMenuOpen={setMenuOpen}>
      {children}
    </AppShell>
  );
}
