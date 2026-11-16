import { createFileRoute } from "@tanstack/react-router";
import { AnalyticsSection } from "@/components/analytics-section";

export const Route = createFileRoute("/_dashboard/")({
  head: () => ({
    meta: [
      { title: "Overview · SupeRR Selector" },
      {
        name: "description",
        content: "Review verified pressure-performance indicators for Rajasthan Royals.",
      },
      { property: "og:title", content: "Overview · SupeRR Selector" },
      {
        property: "og:description",
        content: "Pressure-performance overview for the SupeRR Selector workspace.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: OverviewRoute,
});

function OverviewRoute() {
  return <AnalyticsSection section="overview" />;
}
