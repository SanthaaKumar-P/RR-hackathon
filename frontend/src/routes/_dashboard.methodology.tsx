import { createFileRoute } from "@tanstack/react-router";
import { AnalyticsSection } from "@/components/analytics-section";

export const Route = createFileRoute("/_dashboard/methodology")({
  head: () => ({
    meta: [
      { title: "Ranking Methodology · SupeRR Selector" },
      {
        name: "description",
        content: "Review project-defined eligibility thresholds and baseline ranking weights.",
      },
      { property: "og:title", content: "Ranking Methodology · SupeRR Selector" },
      {
        property: "og:description",
        content: "Transparent pressure-performance ranking rules and baseline weights.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: MethodologyRoute,
});

function MethodologyRoute() {
  return <AnalyticsSection section="methodology" />;
}
