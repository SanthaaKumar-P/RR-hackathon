import { createFileRoute } from "@tanstack/react-router";
import { AnalyticsSection } from "@/components/analytics-section";

export const Route = createFileRoute("/_dashboard/comparison")({
  head: () => ({
    meta: [
      { title: "Player Comparison · SupeRR Selector" },
      {
        name: "description",
        content: "Compare eligible players using verified pressure-performance metrics.",
      },
      { property: "og:title", content: "Player Comparison · SupeRR Selector" },
      {
        property: "og:description",
        content: "Side-by-side verified player rankings and performance metrics.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: ComparisonRoute,
});

function ComparisonRoute() {
  return <AnalyticsSection section="comparison" />;
}
