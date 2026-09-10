"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/Button";
import { useAuth } from "@/hooks/useAuth";

export const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/cases", label: "Cases" },
  { href: "/cases/new", label: "Submit case" },
  { href: "/donations", label: "Donations" },
  { href: "/recommendations", label: "Recommendations" },
  { href: "/assistant", label: "AI assistant" },
];

export function navItemsForRole(role: string | undefined) {
  if (role === "admin") {
    return [...NAV_ITEMS, { href: "/review", label: "Review queue" }];
  }
  return NAV_ITEMS;
}

export function Navbar({
  onOpenMenu,
}: {
  onOpenMenu: () => void;
}) {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="flex items-center justify-between gap-3 px-4 py-3 lg:px-8">
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="rounded-lg p-2 text-slate-700 hover:bg-slate-100 lg:hidden"
            onClick={onOpenMenu}
            aria-label="Open navigation"
          >
            ☰
          </button>
          <Link href="/dashboard" className="font-semibold text-brand-800">
            CareHaven
          </Link>
        </div>
        <div className="flex items-center gap-3 text-sm text-slate-600">
          {user ? (
            <span className="hidden sm:inline">
              {user.email} · {user.role}
            </span>
          ) : null}
          <Button variant="secondary" onClick={logout}>
            Sign out
          </Button>
        </div>
      </div>
    </header>
  );
}

export function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  const { user } = useAuth();
  const items = navItemsForRole(user?.role);

  return (
    <nav aria-label="Main" className="space-y-1">
      {items.map((item) => {
        const active =
          pathname === item.href ||
          (item.href !== "/cases/new" &&
            item.href !== "/cases" &&
            pathname.startsWith(item.href)) ||
          (item.href === "/cases" && pathname.startsWith("/cases") && pathname !== "/cases/new");
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            className={`block rounded-lg px-3 py-2 text-sm font-medium ${
              active
                ? "bg-brand-50 text-brand-800"
                : "text-slate-700 hover:bg-slate-100"
            }`}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
