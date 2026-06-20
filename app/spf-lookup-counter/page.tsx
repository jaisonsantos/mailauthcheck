import { CheckerPage, buildMetadata } from "@/components/checker-page";
import { checkerPages } from "@/lib/page-config";

export const metadata = buildMetadata(checkerPages.spfLookup);

export default function SPFLookupCounterPage() {
  return <CheckerPage config={checkerPages.spfLookup} />;
}
