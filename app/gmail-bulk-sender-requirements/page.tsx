import { CheckerPage, buildMetadata } from "@/components/checker-page";
import { checkerPages } from "@/lib/page-config";

export const metadata = buildMetadata(checkerPages.gmailBulkSenderRequirements);

export default function GmailBulkSenderRequirementsPage() {
  return <CheckerPage config={checkerPages.gmailBulkSenderRequirements} />;
}
