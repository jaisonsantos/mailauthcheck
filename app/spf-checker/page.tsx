import { CheckerPage, buildMetadata } from "@/components/checker-page";
import { checkerPages } from "@/lib/page-config";

export const metadata = buildMetadata(checkerPages.spf);

export default function SPFCheckerPage() {
  return <CheckerPage config={checkerPages.spf} />;
}
