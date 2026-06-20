import { CheckerPage, buildMetadata } from "@/components/checker-page";
import { checkerPages } from "@/lib/page-config";

export const metadata = buildMetadata(checkerPages.mx);

export default function MXCheckerPage() {
  return <CheckerPage config={checkerPages.mx} />;
}
