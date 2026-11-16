import { createFileRoute } from "@tanstack/react-router";
import { AnalyticsSection } from "@/components/analytics-section";

export const Route = createFileRoute("/_dashboard/batters")({
  head: () => ({
    meta: [
      { title: "Batter Intelligence · SupeRR Selector" },
      {
        name: "description",
        content: "Review eligible batter rankings and verified pressure-performance metrics.",
      },
      { property: "og:title", content: "Batter Intelligence · SupeRR Selector" },
      {
        property: "og:description",
        content: "Verified pressure-performance rankings for eligible batters.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: BattersRoute,
});

function BattersRoute() {
  return <AnalyticsSection section="batters" />;
}
