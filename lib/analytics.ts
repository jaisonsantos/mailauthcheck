"use client";

declare global {
  interface Window {
    plausible?: (
      eventName: string,
      options?: {
        props?: Record<string, string | number | boolean | null>;
      },
    ) => void;
  }
}

type EventProps = Record<string, string | number | boolean | null>;

export function trackEvent(eventName: string, props?: EventProps) {
  if (typeof window === "undefined") {
    return;
  }

  window.plausible?.(eventName, props ? { props } : undefined);
}
