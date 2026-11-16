import { createFileRoute } from "@tanstack/react-router";
import { AnalyticsSection } from "@/components/analytics-section";

export const Route = createFileRoute("/_dashboard/bowlers")({
  head: () => ({
    meta: [
      { title: "Bowler Intelligence · SupeRR Selector" },
      {
        name: "description",
        content: "Review eligible bowler rankings and verified pressure-performance metrics.",
      },
      { property: "og:title", content: "Bowler Intelligence · SupeRR Selector" },
      {
        property: "og:description",
        content: "Verified pressure-performance rankings for eligible bowlers.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: BowlersRoute,
});

function BowlersRoute() {
  return <AnalyticsSection section="bowlers" />;
}
