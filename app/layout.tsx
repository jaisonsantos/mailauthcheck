import type { Metadata } from "next";

import { PlausibleProvider } from "@/components/plausible-provider";

import "./globals.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "MailAuthCheck - Bulk Email Readiness Checker",
  description:
    "Check SPF, DKIM, DMARC, MX, SPF lookups and manual Gmail/Yahoo bulk sender requirements before your next campaign.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <PlausibleProvider />
        {children}
      </body>
    </html>
  );
}
