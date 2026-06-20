import { CheckerPage, buildMetadata } from "@/components/checker-page";
import { checkerPages } from "@/lib/page-config";

export const metadata = buildMetadata(checkerPages.dmarc);

export default function DMARCCheckerPage() {
  return <CheckerPage config={checkerPages.dmarc} />;
}
