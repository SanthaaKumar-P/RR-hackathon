import { createFileRoute } from "@tanstack/react-router";
import { AnalyticsSection } from "@/components/analytics-section";

export const Route = createFileRoute("/_dashboard/matches")({
  head: () => ({
    meta: [
      { title: "Match Insights · SupeRR Selector" },
      {
        name: "description",
        content: "Inspect match-level innings and verified pressure-delivery events.",
      },
      { property: "og:title", content: "Match Insights · SupeRR Selector" },
      {
        property: "og:description",
        content: "Match-level pressure-performance insights from verified data.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: MatchesRoute,
});

function MatchesRoute() {
  return <AnalyticsSection section="matches" />;
}
