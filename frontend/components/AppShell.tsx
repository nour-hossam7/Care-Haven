"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { Navbar } from "@/components/Navbar";
import { NavLinks } from "@/components/Navbar";
import { Sidebar } from "@/components/Sidebar";
import { useAuth } from "@/hooks/useAuth";

export function AppShell({
  children,
  menuOpen,
  setMenuOpen,
}: {
  children: React.ReactNode;
  menuOpen: boolean;
  setMenuOpen: (open: boolean) => void;
}) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner label="Restoring session" />
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar onOpenMenu={() => setMenuOpen(true)} />
      <div className="flex">
        <Sidebar />
        {menuOpen ? (
          <div className="fixed inset-0 z-40 lg:hidden">
            <button
              type="button"
              className="absolute inset-0 bg-slate-900/40"
              aria-label="Close navigation"
              onClick={() => setMenuOpen(false)}
            />
            <div className="relative h-full w-72 bg-white p-5 shadow-xl">
              <p className="mb-4 font-semibold text-brand-800">CareHaven</p>
              <NavLinks onNavigate={() => setMenuOpen(false)} />
            </div>
          </div>
        ) : null}
        <main className="min-w-0 flex-1 px-4 py-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
