import type { Metadata } from "next";

import { DomainChecker } from "@/components/domain-checker";
import type { CheckerPageConfig } from "@/lib/page-config";

export function buildMetadata(config: CheckerPageConfig): Metadata {
  return {
    title: config.title,
    description: config.description,
    alternates: {
      canonical: config.pathname,
    },
  };
}

export function CheckerPage({ config }: { config: CheckerPageConfig }) {
  return <DomainChecker config={config} />;
}
