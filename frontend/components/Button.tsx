import Link from "next/link";

export function Button({
  children,
  className = "",
  variant = "primary",
  type = "button",
  disabled,
  onClick,
}: {
  children: React.ReactNode;
  className?: string;
  variant?: "primary" | "secondary" | "ghost" | "danger";
  type?: "button" | "submit";
  disabled?: boolean;
  onClick?: () => void;
}) {
  const variants = {
    primary: "bg-brand-700 text-white hover:bg-brand-800",
    secondary: "border border-slate-300 bg-white text-slate-800 hover:bg-slate-50",
    ghost: "text-brand-800 hover:bg-brand-50",
    danger: "bg-rose-700 text-white hover:bg-rose-800",
  };

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`inline-flex items-center justify-center rounded-lg px-4 py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-60 ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
}

export function TextLink({
  href,
  children,
}: {
  href: string;
  children: React.ReactNode;
}) {
  return (
    <Link href={href} className="font-semibold text-brand-700 hover:text-brand-800">
      {children}
    </Link>
  );
}
