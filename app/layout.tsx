import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MailAuthCheck - Check if your domain is ready to send email",
  description:
    "Run a quick SPF, DMARC, MX and Gmail/Yahoo readiness check. Get a simple explanation of what is missing and what to fix next.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
