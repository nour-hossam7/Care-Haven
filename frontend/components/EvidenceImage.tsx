"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export function EvidenceImage({
  imageUrl,
  alt,
  className,
}: {
  imageUrl: string;
  alt: string;
  className?: string;
}) {
  const [objectUrl, setObjectUrl] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    let createdUrl: string | null = null;

    void api
      .evidenceImage(imageUrl)
      .then((blob) => {
        if (!active) return;
        createdUrl = URL.createObjectURL(blob);
        setObjectUrl(createdUrl);
      })
      .catch(() => {
        if (active) setObjectUrl(null);
      });

    return () => {
      active = false;
      if (createdUrl) URL.revokeObjectURL(createdUrl);
    };
  }, [imageUrl]);

  if (!objectUrl) return null;
  return <img src={objectUrl} alt={alt} className={className} />;
}