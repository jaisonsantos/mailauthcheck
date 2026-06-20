import { CheckerPage, buildMetadata } from "@/components/checker-page";
import { checkerPages } from "@/lib/page-config";

export const metadata = buildMetadata(checkerPages.bulkReadiness);

export default function BulkEmailReadinessCheckerPage() {
  return <CheckerPage config={checkerPages.bulkReadiness} />;
}
