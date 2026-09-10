export function Input({
  id,
  label,
  type = "text",
  value,
  onChange,
  required,
  min,
  step,
  placeholder,
  autoComplete,
}: {
  id: string;
  label: string;
  type?: string;
  value: string | number;
  onChange: (value: string) => void;
  required?: boolean;
  min?: number;
  step?: string;
  placeholder?: string;
  autoComplete?: string;
}) {
  return (
    <label className="block space-y-1.5" htmlFor={id}>
      <span className="text-sm font-medium text-slate-800">{label}</span>
      <input
        id={id}
        type={type}
        value={value}
        required={required}
        min={min}
        step={step}
        placeholder={placeholder}
        autoComplete={autoComplete}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none ring-brand-600 focus:ring-2"
      />
    </label>
  );
}

export function Textarea({
  id,
  label,
  value,
  onChange,
  required,
  rows = 5,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  rows?: number;
}) {
  return (
    <label className="block space-y-1.5" htmlFor={id}>
      <span className="text-sm font-medium text-slate-800">{label}</span>
      <textarea
        id={id}
        value={value}
        required={required}
        rows={rows}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none ring-brand-600 focus:ring-2"
      />
    </label>
  );
}
