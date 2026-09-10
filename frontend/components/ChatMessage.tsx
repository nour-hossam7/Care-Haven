export function ChatMessage({
  role,
  content,
}: {
  role: "user" | "assistant";
  content: string;
}) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 ${
          isUser
            ? "bg-brand-700 text-white"
            : "border border-slate-200 bg-white text-slate-800"
        }`}
      >
        <p className="mb-1 text-xs font-semibold opacity-80">
          {isUser ? "You" : "CareHaven assistant"}
        </p>
        <p className="whitespace-pre-wrap">{content}</p>
      </div>
    </div>
  );
}
