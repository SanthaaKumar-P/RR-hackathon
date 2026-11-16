import { createFileRoute } from "@tanstack/react-router";
import { AnalyticsSection } from "@/components/analytics-section";

export const Route = createFileRoute("/_dashboard/audit")({
  head: () => ({
    meta: [
      { title: "Audit & Data Quality · SupeRR Selector" },
      {
        name: "description",
        content: "Review data validation status, known audit findings, and limitations.",
      },
      { property: "og:title", content: "Audit & Data Quality · SupeRR Selector" },
      {
        property: "og:description",
        content:
          "Transparent data quality checks and known limitations for the analytics workspace.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: AuditRoute,
});

function AuditRoute() {
  return <AnalyticsSection section="audit" />;
}
