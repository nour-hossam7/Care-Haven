"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { CaseEvidence } from "@/types";

export function useCaseEvidence(caseIds: string[]) {
  const [evidenceByCase, setEvidenceByCase] = useState<Record<string, CaseEvidence[]>>({});
  const caseIdsKey = caseIds.join("|");

  useEffect(() => {
    let active = true;
    const uniqueCaseIds = [...new Set(caseIds)];

    if (uniqueCaseIds.length === 0) {
      setEvidenceByCase({});
      return () => {
        active = false;
      };
    }

    void Promise.all(
      uniqueCaseIds.map(async (caseId) => {
        try {
          const evidence = await api.caseEvidence(caseId);
          return [
            caseId,
            evidence.filter((item) => item.case_id === caseId),
          ] as const;
        } catch {
          return [caseId, []] as const;
        }
      }),
    ).then((entries) => {
      if (active) setEvidenceByCase(Object.fromEntries(entries));
    });

    return () => {
      active = false;
    };
  }, [caseIdsKey]);

  return evidenceByCase;
}