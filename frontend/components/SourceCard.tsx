import { Card } from "@/components/Card";
import type { ChatSource } from "@/types";

export function SourceCard({ source }: { source: ChatSource }) {
  return (
    <Card className="p-4">
      <p className="text-sm font-semibold text-slate-900">
        {source.document || source.source || "Source"}
      </p>
      <p className="mt-1 text-xs text-slate-600">
        {source.page != null ? `Page ${source.page} · ` : ""}
        {source.chunk_id}
      </p>
    </Card>
  );
}
