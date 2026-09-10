import Link from "next/link";
import { Card } from "@/components/Card";
import { EvidenceImage } from "@/components/EvidenceImage";
import { FundingProgress } from "@/components/FundingProgress";
import { PriorityBadge } from "@/components/PriorityBadge";
import { StatusBadge } from "@/components/StatusBadge";
import { locationLabel } from "@/lib/format";
import type { Case, RecommendationCase } from "@/types";

function isRecommendation(item: Case | RecommendationCase): item is RecommendationCase {
  return "recommendation_score" in item;
}

export function CaseCard({
  item,
  href,
  evidenceImageUrl,
}: {
  item: Case | RecommendationCase;
  href?: string;
  evidenceImageUrl?: string | null;
}) {
  const content = (
    <Card className="h-full transition hover:border-brand-700/40">
      {evidenceImageUrl ? (
        <EvidenceImage
          imageUrl={evidenceImageUrl}
          alt={`Evidence for ${item.case_id}`}
          className="mb-4 max-h-40 w-full rounded-xl object-contain"
        />
      ) : null}
      <div className="flex flex-wrap items-start justify-between gap-2">
        <p className="font-mono text-sm font-semibold text-slate-900">{item.case_id}</p>
        <div className="flex flex-wrap gap-2">
          <StatusBadge status={item.status} />
          <PriorityBadge value={item.priority} />
        </div>
      </div>
      <p className="mt-3 line-clamp-3 text-sm text-slate-700">
        {item.description || "No description provided."}
      </p>
      <dl className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-600">
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Category</dt>
          <dd>{item.assistance_category || "—"}</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Location</dt>
          <dd>{locationLabel(item)}</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">People affected</dt>
          <dd>{item.people_affected ?? "—"}</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Urgency</dt>
          <dd>{item.urgency || "—"}</dd>
        </div>
      </dl>
      <div className="mt-4">
        <FundingProgress current={item.current_funding} estimated={item.estimated_funding} />
      </div>
      {isRecommendation(item) ? (
        <div className="mt-4 rounded-xl bg-brand-50 p-3 text-sm text-brand-900">
          <p className="font-semibold">
            Rank {item.recommendation_rank} · Score {item.recommendation_score.toFixed(2)}
          </p>
          {item.recommendation_reasons.length ? (
            <ul className="mt-2 list-disc space-y-1 pl-4">
              {item.recommendation_reasons.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}
    </Card>
  );

  if (!href) return content;
  return (
    <Link href={href} className="block h-full focus:outline-none focus:ring-2 focus:ring-brand-600 rounded-2xl">
      {content}
    </Link>
  );
}
