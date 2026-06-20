import { CheckerPage, buildMetadata } from "@/components/checker-page";
import { checkerPages } from "@/lib/page-config";

export const metadata = buildMetadata(checkerPages.home);

export default function Home() {
  return <CheckerPage config={checkerPages.home} />;
}
