import { createFileRoute } from "@tanstack/react-router";
import { AnalyticsSection } from "@/components/analytics-section";

export const Route = createFileRoute("/_dashboard/scenarios")({
  head: () => ({
    meta: [
      { title: "Scenario Analysis · SupeRR Selector" },
      {
        name: "description",
        content: "Review sensitivity analysis returned by the verified analytics service.",
      },
      { property: "og:title", content: "Scenario Analysis · SupeRR Selector" },
      {
        property: "og:description",
        content: "Compare methodology-defined pressure-performance ranking scenarios.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: ScenariosRoute,
});

function ScenariosRoute() {
  return <AnalyticsSection section="scenarios" />;
}
