import { CheckerPage, buildMetadata } from "@/components/checker-page";
import { checkerPages } from "@/lib/page-config";

export const metadata = buildMetadata(checkerPages.dmarcPolicyBulkEmail);

export default function DmarcPolicyBulkEmailPage() {
  return <CheckerPage config={checkerPages.dmarcPolicyBulkEmail} />;
}
