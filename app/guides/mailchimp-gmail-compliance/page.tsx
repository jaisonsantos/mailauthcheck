import { CheckerPage, buildMetadata } from "@/components/checker-page";
import { checkerPages } from "@/lib/page-config";

export const metadata = buildMetadata(checkerPages.mailchimpGmailCompliance);

export default function MailchimpGmailCompliancePage() {
  return <CheckerPage config={checkerPages.mailchimpGmailCompliance} />;
}
