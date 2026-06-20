import type { MetadataRoute } from "next";

import { checkerPages } from "@/lib/page-config";

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

  return Object.values(checkerPages).map((page) => ({
    url: `${baseUrl}${page.pathname}`,
    changeFrequency: "weekly",
    priority: page.pathname === "/" ? 1 : 0.8,
  }));
}
