import { createFileRoute } from "@tanstack/react-router";
import { AnalyticsSection } from "@/components/analytics-section";

export const Route = createFileRoute("/_dashboard/pressure")({
  head: () => ({
    meta: [
      { title: "Pressure Analytics · SupeRR Selector" },
      {
        name: "description",
        content:
          "Explore verified cricket pressure performance by category, match phase, and format.",
      },
      { property: "og:title", content: "Pressure Analytics · SupeRR Selector" },
      {
        property: "og:description",
        content: "Verified delivery, run, and wicket views across pressure situations.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: PressureRoute,
});

function PressureRoute() {
  return <AnalyticsSection section="pressure" />;
}
