import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { z } from "zod";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { LucideIcon } from "lucide-react";
import {
  Activity,
  AlertTriangle,
  ArrowDownWideNarrow,
  ArrowUpWideNarrow,
  BarChart3,
  Check,
  CircleHelp,
  ClipboardCheck,
  Database,
  Download,
  GitCompareArrows,
  Info,
  Search,
  ShieldCheck,
  Target,
  Users,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { BATTER_WEIGHTS, BOWLER_WEIGHTS, eligibility } from "@/lib/analytics-rules";
import {
  AuditSchema,
  fetchAnalytics,
  MatchSchema,
  OverviewSchema,
  PressureSchema,
  RankingListSchema,
  ScenarioSchema,
  type Overview,
  type Player,
} from "@/lib/analytics-api";
import { useDashboard, SectionHeader, Surface } from "@/lib/dashboard-context";

type Section =
  | "overview"
  | "batters"
  | "bowlers"
  | "pressure"
  | "matches"
  | "comparison"
  | "methodology"
  | "scenarios"
  | "audit";

const labelsByMetric: Record<string, string> = {
  final_rank: "Rank",
  player_name: "Player",
  final_score: "Final score",
  pressure_strike_rate: "Pressure SR",
  runs_per_match: "Runs / match",
  runs_per_dismissal: "Runs / dismissal",
  dot_percentage: "Dot %",
  consistency: "Consistency",
  pressure_runs: "Pressure runs",
  pressure_balls: "Pressure balls",
  fours: "Fours",
  sixes: "Sixes",
  pressure_matches: "Pressure matches",
  dismissals: "Dismissals",
  pressure_wickets: "Pressure wickets",
  pressure_economy: "Pressure economy",
  wickets_per_100_legal_balls: "Wickets / 100",
  pressure_dot_percentage: "Pressure dot %",
  wickets_per_match: "Wickets / match",
  pressure_legal_balls: "Legal balls",
};
const batterMetrics = [
  "pressure_strike_rate",
  "runs_per_match",
  "runs_per_dismissal",
  "dot_percentage",
  "consistency",
  "pressure_runs",
  "pressure_balls",
  "fours",
  "sixes",
  "pressure_matches",
  "dismissals",
];
const bowlerMetrics = [
  "pressure_wickets",
  "pressure_economy",
  "wickets_per_100_legal_balls",
  "pressure_dot_percentage",
  "wickets_per_match",
  "consistency",
  "pressure_legal_balls",
  "pressure_matches",
];
const pressureColors = ["var(--color-teal)", "var(--color-amber)", "var(--color-rr-pink)"];

function useAnalytics<T>(key: string, schema: Parameters<typeof fetchAnalytics<T>>[1]) {
  const { format } = useDashboard();
  return useQuery({
    queryKey: ["analytics", key, format],
    queryFn: async ({ signal }) => {
      const data = await fetchAnalytics(key, schema, signal);
      return data;
    },
    retry: false,
    staleTime: 60_000,
  });
}

function PageTitle({
  title,
  subtitle,
  icon: Icon,
  eyebrow = "TEAM ANALYTICS",
}: {
  title: string;
  subtitle: string;
  icon: LucideIcon;
  eyebrow?: string;
}) {
  const { format } = useDashboard();
  return (
    <SectionHeader
      eyebrow={`${eyebrow} · ${format}`}
      title={title}
      description={subtitle}
      icon={Icon}
    />
  );
}

function EmptyChart({
  title,
  note = "Verified match data will appear here when the analytics API is available.",
}: {
  title: string;
  note?: string;
}) {
  return (
    <div className="flex min-h-[208px] flex-col items-center justify-center px-6 text-center">
      <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-md bg-muted text-muted-foreground">
        <BarChart3 className="h-[18px] w-[18px]" />
      </div>
      <p className="text-[12px] font-bold">{title}</p>
      <p className="mt-1.5 max-w-[290px] text-[10px] leading-relaxed text-muted-foreground">
        {note}
      </p>
    </div>
  );
}

function ApiStatus({ error, refetch }: { error: Error | null; refetch: () => void }) {
  if (!error) return null;
  return (
    <div className="mb-5 flex flex-wrap items-center gap-3 rounded-md border border-amber/30 bg-amber/5 px-4 py-3">
      <AlertTriangle className="h-4 w-4 shrink-0 text-amber" />
      <div className="min-w-0 flex-1">
        <p className="text-[11px] font-bold">Analytics data is not available</p>
        <p className="mt-0.5 break-words text-[10px] text-muted-foreground">
          {error.message} No statistics are being substituted.
        </p>
      </div>
      <Button onClick={refetch} variant="outline" size="sm" className="h-8 text-[10px]">
        Try again
      </Button>
    </div>
  );
}

function LoadingRows() {
  return (
    <div className="space-y-3 p-5" role="status" aria-label="Loading analytics data">
      {Array.from({ length: 4 }, (_, index) => (
        <div key={index} className="h-8 animate-pulse rounded bg-muted" />
      ))}
    </div>
  );
}

function MetricValue({ value, unit }: { value: string | number | null; unit?: string }) {
  if (value === null) return <span className="text-muted-foreground">—</span>;
  return (
    <>
      {value}
      {unit && <span className="ml-1 text-muted-foreground">{unit}</span>}
    </>
  );
}

function OverviewPage() {
  const { format } = useDashboard();
  const query = useAnalytics<Overview>(`/overview?format=${format}`, OverviewSchema);
  const data = query.data;
  const kpis = data?.kpis ?? [];
  const categoryData = data?.pressure_categories ?? [];
  const phaseData = data?.phases ?? [];
  return (
    <>
      <PageTitle
        title="Pressure performance overview"
        subtitle="Executive snapshot of cricket performance under pressure, grounded in verified match data."
        icon={BarChart3}
        eyebrow="ROUND INTELLIGENCE"
      />
      <ApiStatus error={query.error} refetch={() => void query.refetch()} />
      <div className="mb-5 grid grid-cols-2 gap-3 xl:grid-cols-3">
        {[
          "Total Matches Analysed",
          "Total Pressure Deliveries",
          "Players Evaluated",
          "Eligible Batters",
          "Eligible Bowlers",
          "Formats Analysed",
        ].map((name) => {
          const item = kpis.find((kpi) => kpi.label.toLowerCase() === name.toLowerCase());
          return (
            <Surface key={name} className="relative min-h-[108px] overflow-hidden p-4">
              <div className="flex items-center justify-between gap-2">
                <p className="text-[10px] font-semibold text-muted-foreground">{name}</p>
                <span className="rounded bg-muted px-1.5 py-0.5 text-[9px] font-semibold text-muted-foreground">
                  {item ? "LIVE" : "PENDING"}
                </span>
              </div>
              <p className="mt-4 text-[24px] font-extrabold leading-none tabular-nums">
                {query.isLoading ? (
                  "···"
                ) : (
                  <MetricValue
                    value={item?.value ?? null}
                    {...(item?.unit ? { unit: item.unit } : {})}
                  />
                )}
              </p>
            </Surface>
          );
        })}
      </div>
      <div className="mb-5 grid grid-cols-1 gap-5 xl:grid-cols-2">
        <Surface>
          <div className="border-b border-border px-4 py-3.5">
            <p className="text-[12px] font-bold">Pressure delivery distribution</p>
            <p className="mt-0.5 text-[10px] text-muted-foreground">Moderate · High · Extreme</p>
          </div>
          {categoryData.length ? (
            <div className="flex flex-wrap items-center justify-center gap-7 p-5">
              <div className="h-[180px] w-[180px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryData}
                      dataKey="count"
                      nameKey="category"
                      innerRadius={52}
                      outerRadius={76}
                      paddingAngle={4}
                    >
                      {categoryData.map((item, index) => (
                        <Cell
                          key={item.category}
                          fill={pressureColors[index % pressureColors.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-3">
                {categoryData.map((item, index) => (
                  <div key={item.category} className="flex items-center gap-2 text-[11px]">
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{ background: pressureColors[index % pressureColors.length] }}
                    />
                    <span>{item.category}</span>
                    <strong className="ml-auto tabular-nums">{item.count.toLocaleString()}</strong>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <EmptyChart title="Awaiting pressure distribution" />
          )}
        </Surface>
        <Surface>
          <div className="border-b border-border px-4 py-3.5">
            <p className="text-[12px] font-bold">Pressure by match phase</p>
            <p className="mt-0.5 text-[10px] text-muted-foreground">Powerplay · Middle · Death</p>
          </div>
          {phaseData.length ? (
            <div className="h-[250px] p-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={phaseData} margin={{ left: -18, right: 8 }}>
                  <CartesianGrid
                    stroke="var(--color-border)"
                    strokeDasharray="3 3"
                    vertical={false}
                  />
                  <XAxis
                    dataKey="phase"
                    tick={{ fill: "var(--color-muted-foreground)", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: "var(--color-muted-foreground)", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip />
                  <Bar
                    dataKey="deliveries"
                    fill="var(--color-primary)"
                    radius={[3, 3, 0, 0]}
                    maxBarSize={48}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyChart title="Awaiting phase breakdown" />
          )}
        </Surface>
      </div>
      <div className="mb-5 grid grid-cols-1 gap-5 xl:grid-cols-2">
        {[
          ["Top pressure batters", data?.top_batters],
          ["Top pressure bowlers", data?.top_bowlers],
        ].map(([title, list]) => (
          <Surface key={String(title)}>
            <div className="flex items-center justify-between border-b border-border px-4 py-3.5">
              <p className="text-[12px] font-bold">{String(title)}</p>
              <span className="text-[9px] font-bold uppercase tracking-wider text-muted-foreground">
                Final score
              </span>
            </div>
            {Array.isArray(list) && list.length ? (
              list.slice(0, 5).map((player) => (
                <div
                  key={player.player_name}
                  className="flex items-center gap-3 border-b border-border/70 px-4 py-3 last:border-0"
                >
                  <span className="w-5 text-[11px] font-extrabold tabular-nums text-muted-foreground">
                    {player.final_rank}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-[11px] font-bold">{player.player_name}</p>
                    <div className="mt-1 h-1 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-primary"
                        style={{ width: `${Math.max(0, Math.min(100, player.final_score))}%` }}
                      />
                    </div>
                  </div>
                  <strong className="text-[12px] tabular-nums">
                    {player.final_score.toFixed(2)}
                  </strong>
                </div>
              ))
            ) : (
              <EmptyChart
                title="Rankings await verified results"
                note="Player positions and final scores will be shown when returned by the analytics API."
              />
            )}
          </Surface>
        ))}
      </div>
      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <Surface>
          <div className="border-b border-border px-4 py-3.5">
            <p className="text-[12px] font-bold">Recent analytical highlights</p>
          </div>
          {data?.highlights?.length ? (
            data.highlights.map((item) => (
              <div key={item.title} className="border-b border-border/70 px-4 py-3 last:border-0">
                <p className="text-[11px] font-bold">{item.title}</p>
                <p className="mt-1 text-[10px] leading-relaxed text-muted-foreground">
                  {item.description}
                </p>
              </div>
            ))
          ) : (
            <EmptyChart title="No highlights available" />
          )}
        </Surface>
        <Surface>
          <div className="border-b border-border px-4 py-3.5">
            <p className="text-[12px] font-bold">Methodology & data status</p>
          </div>
          <div className="space-y-4 p-4">
            <div className="flex items-start gap-3">
              <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-success" />
              <div>
                <p className="text-[11px] font-bold">Audited baseline rankings</p>
                <p className="mt-1 text-[10px] leading-relaxed text-muted-foreground">
                  Batter and bowler baseline rankings were independently reproduced, per the
                  supplied project audit.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Database className="mt-0.5 h-4 w-4 shrink-0 text-cyan" />
              <div>
                <p className="text-[11px] font-bold">Verified dataset required</p>
                <p className="mt-1 text-[10px] leading-relaxed text-muted-foreground">
                  Player scores and charts appear only when supported by the live analytics service.
                </p>
              </div>
            </div>
          </div>
        </Surface>
      </div>
    </>
  );
}

function PlayersPage({ kind }: { kind: "batters" | "bowlers" }) {
  const { format, search } = useDashboard();
  const path = `/${kind}?format=${format}&limit=500`;
  const query = useAnalytics<z.infer<typeof RankingListSchema>>(path, RankingListSchema);
  const [sort, setSort] = useState<{ key: string; descending: boolean }>({
    key: "final_rank",
    descending: false,
  });
  const [selected, setSelected] = useState<string[]>([]);
  const metricKeys = kind === "batters" ? batterMetrics : bowlerMetrics;
  const players = useMemo(
    () =>
      (query.data?.players ?? [])
        .filter((player) => player.player_name.toLowerCase().includes(search.toLowerCase()))
        .sort((a, b) => {
          const first = a[sort.key as keyof Player];
          const second = b[sort.key as keyof Player];
          const comparison =
            typeof first === "number" && typeof second === "number"
              ? first - second
              : String(first ?? "").localeCompare(String(second ?? ""));
          return sort.descending ? -comparison : comparison;
        }),
    [query.data?.players, search, sort],
  );
  const title = kind === "batters" ? "Batter intelligence" : "Bowler intelligence";
  const toggleSort = (key: string) =>
    setSort((current) => ({ key, descending: current.key === key ? !current.descending : false }));
  const togglePlayer = (name: string) =>
    setSelected((current) =>
      current.includes(name)
        ? current.filter((item) => item !== name)
        : current.length < 4
          ? [...current, name]
          : current,
    );

  const summaryCards = useMemo(() => {
    if (!players.length) {
      return kind === "batters"
        ? [
            { label: "Pressure strike rate", value: "—", sub: "Awaiting data" },
            { label: "Runs per match", value: "—", sub: "Awaiting data" },
            { label: "Runs per dismissal", value: "—", sub: "Awaiting data" },
            { label: "Consistency index", value: "—", sub: "Awaiting data" },
          ]
        : [
            { label: "Pressure wickets", value: "—", sub: "Awaiting data" },
            { label: "Pressure economy", value: "—", sub: "Awaiting data" },
            { label: "Wickets per 100 legal balls", value: "—", sub: "Awaiting data" },
            { label: "Consistency index", value: "—", sub: "Awaiting data" },
          ];
    }
    if (kind === "batters") {
      const topSr = [...players].sort(
        (a, b) => (b.pressure_strike_rate || 0) - (a.pressure_strike_rate || 0),
      )[0];
      const topRpm = [...players].sort(
        (a, b) => (b.runs_per_match || 0) - (a.runs_per_match || 0),
      )[0];
      const topRpd = [...players].sort(
        (a, b) => (b.runs_per_dismissal || 0) - (a.runs_per_dismissal || 0),
      )[0];
      const topCons = [...players].sort((a, b) => (b.consistency || 0) - (a.consistency || 0))[0];

      return [
        {
          label: "Pressure strike rate",
          value: topSr?.pressure_strike_rate ? topSr.pressure_strike_rate.toFixed(1) : "—",
          sub: topSr ? `Top: ${topSr.player_name}` : "Leader benchmark",
        },
        {
          label: "Runs per match",
          value: topRpm?.runs_per_match ? topRpm.runs_per_match.toFixed(1) : "—",
          sub: topRpm ? `Top: ${topRpm.player_name}` : "Leader benchmark",
        },
        {
          label: "Runs per dismissal",
          value: topRpd?.runs_per_dismissal ? topRpd.runs_per_dismissal.toFixed(1) : "—",
          sub: topRpd ? `Top: ${topRpd.player_name}` : "Leader benchmark",
        },
        {
          label: "Consistency index",
          value: topCons?.consistency
            ? `${(topCons.consistency <= 1 ? topCons.consistency * 100 : topCons.consistency).toFixed(1)}%`
            : "—",
          sub: topCons ? `Top: ${topCons.player_name}` : "10+ & 20+ runs formula",
        },
      ];
    } else {
      const topWkts = [...players].sort(
        (a, b) => (b.pressure_wickets || 0) - (a.pressure_wickets || 0),
      )[0];
      const topEcon = [...players]
        .filter((p) => (p.pressure_economy || 0) > 0)
        .sort((a, b) => (a.pressure_economy || 99) - (b.pressure_economy || 99))[0];
      const topW100 = [...players].sort(
        (a, b) => (b.wickets_per_100_legal_balls || 0) - (a.wickets_per_100_legal_balls || 0),
      )[0];
      const topCons = [...players].sort((a, b) => (b.consistency || 0) - (a.consistency || 0))[0];

      return [
        {
          label: "Pressure wickets",
          value: topWkts?.pressure_wickets ? String(topWkts.pressure_wickets) : "—",
          sub: topWkts ? `Top: ${topWkts.player_name}` : "Creditable dismissals",
        },
        {
          label: "Pressure economy",
          value: topEcon?.pressure_economy ? topEcon.pressure_economy.toFixed(2) : "—",
          sub: topEcon ? `Top: ${topEcon.player_name}` : "Lower is better",
        },
        {
          label: "Wickets / 100 legal balls",
          value: topW100?.wickets_per_100_legal_balls
            ? topW100.wickets_per_100_legal_balls.toFixed(2)
            : "—",
          sub: topW100 ? `Top: ${topW100.player_name}` : "Strike effectiveness",
        },
        {
          label: "Consistency index",
          value: topCons?.consistency
            ? `${(topCons.consistency <= 1 ? topCons.consistency * 100 : topCons.consistency).toFixed(1)}%`
            : "—",
          sub: topCons ? `Top: ${topCons.player_name}` : "1+ & 2+ wickets formula",
        },
      ];
    }
  }, [players, kind]);

  return (
    <>
      <PageTitle
        title={title}
        subtitle={`Eligible ${kind} ranked on verified ${format} pressure-performance metrics and the project baseline scoring.`}
        icon={kind === "batters" ? Target : Activity}
      />
      <ApiStatus error={query.error} refetch={() => void query.refetch()} />
      <div className="mb-5 grid grid-cols-2 gap-3 xl:grid-cols-4">
        {summaryCards.map((metric) => (
          <Surface key={metric.label} className="p-4">
            <p className="text-[10px] font-semibold text-muted-foreground">{metric.label}</p>
            <p className="mt-3 text-[22px] font-extrabold tabular-nums">
              {query.isLoading ? "···" : metric.value}
            </p>
            <p className="mt-1 text-[10px] font-medium text-muted-foreground truncate">
              {metric.sub}
            </p>
          </Surface>
        ))}
      </div>
      <Surface>
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-4 py-3.5">
          <div>
            <p className="text-[12px] font-bold">Eligible player rankings</p>
            <p className="mt-1 text-[10px] text-muted-foreground">
              {players.length} verified player{players.length === 1 ? "" : "s"}
              {selected.length ? ` · ${selected.length} selected` : ""}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative hidden w-44 sm:block">
              <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
              <Input
                aria-label="Filter player rankings"
                placeholder="Filter players"
                value={search}
                readOnly
                className="h-8 pl-8 text-[11px]"
              />
            </div>
            <Button
              variant="outline"
              size="sm"
              className="h-8 gap-2 text-[10px]"
              disabled={!players.length}
              onClick={() => {
                const head = [
                  "Rank",
                  "Player",
                  "Final score",
                  ...metricKeys.map((key) => labelsByMetric[key]),
                ];
                const rows = players.map((player) => [
                  player.final_rank,
                  player.player_name,
                  player.final_score,
                  ...metricKeys.map((key) => {
                    const value = player[key as keyof Player];
                    return typeof value === "object" ? "" : (value ?? player.metrics?.[key] ?? "");
                  }),
                ]);
                const csv = [head, ...rows]
                  .map((row) =>
                    row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(","),
                  )
                  .join("\n");
                const link = document.createElement("a");
                link.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
                link.download = `${kind}-${format.toLowerCase()}-rankings.csv`;
                link.click();
                URL.revokeObjectURL(link.href);
              }}
            >
              <Download className="h-3.5 w-3.5" />
              Export
            </Button>
          </div>
        </div>
        {query.isLoading ? (
          <LoadingRows />
        ) : players.length ? (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  {["final_rank", "player_name", "final_score", ...metricKeys].map((key) => (
                    <TableHead key={key} className="whitespace-nowrap px-3 text-[9px]">
                      <Button
                        variant="ghost"
                        onClick={() => toggleSort(key)}
                        className="h-7 px-1.5 text-[9px] font-bold text-muted-foreground hover:text-foreground"
                      >
                        {labelsByMetric[key] ?? key}
                        {sort.key === key ? (
                          sort.descending ? (
                            <ArrowDownWideNarrow className="h-3 w-3" />
                          ) : (
                            <ArrowUpWideNarrow className="h-3 w-3" />
                          )
                        ) : null}
                      </Button>
                    </TableHead>
                  ))}
                  <TableHead className="text-[9px]">Compare</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {players.map((player) => (
                  <TableRow key={player.player_name}>
                    <TableCell className="px-4 text-[11px] font-bold tabular-nums">
                      {player.final_rank}
                    </TableCell>
                    <TableCell className="whitespace-nowrap px-3 text-[11px] font-semibold">
                      {player.player_name}
                    </TableCell>
                    <TableCell className="px-3 text-[11px] font-extrabold tabular-nums">
                      {player.final_score.toFixed(2)}
                    </TableCell>
                    {metricKeys.map((key) => {
                      const value = player[key as keyof Player];
                      return (
                        <TableCell key={key} className="px-3 text-[10px] tabular-nums">
                          {typeof value === "object"
                            ? "—"
                            : (value ?? player.metrics?.[key] ?? "—")}
                        </TableCell>
                      );
                    })}
                    <TableCell>
                      <Button
                        aria-label={`${selected.includes(player.player_name) ? "Remove" : "Add"} ${player.player_name} to comparison`}
                        title="Compare player"
                        size="icon"
                        variant="ghost"
                        className={`h-7 w-7 ${selected.includes(player.player_name) ? "text-primary" : "text-muted-foreground"}`}
                        onClick={() => togglePlayer(player.player_name)}
                      >
                        {selected.includes(player.player_name) ? <Check /> : <GitCompareArrows />}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <p className="border-t border-border px-4 py-3 text-[9px] text-muted-foreground">
              Eligibility:{" "}
              {kind === "batters"
                ? `${eligibility.batter.pressureBalls} pressure balls and ${eligibility.batter.pressureMatches} pressure matches minimum.`
                : `${eligibility.bowler.pressureLegalBalls} pressure legal balls and ${eligibility.bowler.verifiedPressureMatches} verified pressure matches minimum.`}{" "}
              Use column headings to sort.
            </p>
          </div>
        ) : (
          <EmptyChart
            title="No verified rankings available"
            note={
              search
                ? "No matching players in the verified API response."
                : "Ranking values are not fabricated. Player data will appear here when the FastAPI service returns eligible players."
            }
          />
        )}
      </Surface>
    </>
  );
}

function PressurePage() {
  const { format } = useDashboard();
  const query = useAnalytics<z.infer<typeof PressureSchema>>(
    `/pressure?format=${format}`,
    PressureSchema,
  );
  const categories = query.data?.categories ?? [];
  const phases = query.data?.phases ?? [];
  return (
    <>
      <PageTitle
        title="Pressure analytics"
        subtitle="Explore delivery volume, runs, and wickets across verified pressure categories, match phases, and formats."
        icon={Activity}
      />
      <ApiStatus error={query.error} refetch={() => void query.refetch()} />
      <Surface className="mb-5">
        <div className="border-b border-border px-4 py-3.5">
          <p className="text-[12px] font-bold">Pressure category distribution</p>
          <p className="mt-1 text-[10px] text-muted-foreground">
            Category thresholds follow the project methodology; no definitions are assumed here.
          </p>
        </div>
        {categories.length ? (
          <div className="grid gap-4 p-4 sm:grid-cols-3">
            {["Moderate", "High", "Extreme"].map((name, index) => {
              const item = categories.find(
                (category) => category.category.toLowerCase() === name.toLowerCase(),
              );
              return (
                <div
                  key={name}
                  className="border-l-2 p-4"
                  style={{ borderColor: pressureColors[index] }}
                >
                  <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                    {name}
                  </p>
                  <p className="mt-3 text-[28px] font-extrabold tabular-nums">
                    {item?.deliveries.toLocaleString() ?? "—"}
                  </p>
                  <div className="mt-2 flex flex-wrap gap-3 text-[10px] text-muted-foreground">
                    <span>
                      Runs <b className="text-foreground">{item?.runs ?? "—"}</b>
                    </span>
                    <span>
                      Wickets <b className="text-foreground">{item?.wickets ?? "—"}</b>
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <EmptyChart
            title="Pressure classifications are awaiting verified data"
            note="Category cut-offs are intentionally not inferred or replaced with official cricket definitions."
          />
        )}
      </Surface>
      <div className="grid gap-5 xl:grid-cols-2">
        {[
          ["Phase breakdown", phases],
          ["Format comparison", query.data?.by_format ?? []],
        ].map(([name, values]) => (
          <Surface key={String(name)}>
            <div className="border-b border-border px-4 py-3.5">
              <p className="text-[12px] font-bold">{String(name)}</p>
              <p className="mt-1 text-[10px] text-muted-foreground">
                Verified pressure delivery counts
              </p>
            </div>
            {Array.isArray(values) && values.length ? (
              <div className="h-[260px] p-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={values} margin={{ left: -20, right: 5 }}>
                    <CartesianGrid
                      stroke="var(--color-border)"
                      strokeDasharray="3 3"
                      vertical={false}
                    />
                    <XAxis
                      dataKey={name === "Phase breakdown" ? "phase" : "format"}
                      tick={{ fill: "var(--color-muted-foreground)", fontSize: 10 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fill: "var(--color-muted-foreground)", fontSize: 10 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip />
                    <Bar
                      dataKey="deliveries"
                      fill="var(--color-cyan)"
                      radius={[3, 3, 0, 0]}
                      maxBarSize={50}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <EmptyChart title="Awaiting verified phase and format data" />
            )}
          </Surface>
        ))}
      </div>
      <Surface className="mt-5">
        <div className="border-b border-border px-4 py-3.5">
          <p className="text-[12px] font-bold">Methodology guardrail</p>
        </div>
        <p className="p-4 text-[11px] leading-relaxed text-muted-foreground">
          Pressure category definitions must come from the project methodology. The thresholds are
          not specified in the supplied brief; these charts will only display the classifications
          returned by the verified API.
        </p>
      </Surface>
    </>
  );
}

function MatchesPage() {
  const { format, search } = useDashboard();
  const query = useAnalytics<z.infer<typeof MatchSchema>[]>(
    `/matches?format=${format}&limit=100`,
    MatchSchema.array(),
  );
  const [match, setMatch] = useState<string>("");
  const matches = useMemo(
    () =>
      (query.data ?? []).filter(
        (item) => !search || item.match_label.toLowerCase().includes(search.toLowerCase()),
      ),
    [query.data, search],
  );
  const currentId = match || String(matches[0]?.match_id ?? "");
  const currentEvents = matches.filter((item) => String(item.match_id) === currentId);
  const first = matches.find((item) => String(item.match_id) === currentId);
  useEffect(() => {
    if (match && !matches.some((item) => String(item.match_id) === match)) setMatch("");
  }, [match, matches]);
  return (
    <>
      <PageTitle
        title="Match insights"
        subtitle="Inspect match-level innings, phases, and verified pressure-delivery events."
        icon={BarChart3}
      />
      <ApiStatus error={query.error} refetch={() => void query.refetch()} />
      <Surface>
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-4 py-3.5">
          <div>
            <p className="text-[12px] font-bold">Match selector</p>
            <p className="mt-1 text-[10px] text-muted-foreground">
              {matches.length} match record{matches.length === 1 ? "" : "s"} available
            </p>
          </div>
          <select
            aria-label="Select a match"
            value={currentId}
            onChange={(event) => setMatch(event.target.value)}
            className="h-9 max-w-full rounded-md border border-input bg-background px-3 text-[11px] text-foreground"
          >
            <option value="">Select verified match</option>
            {matches.map((item) => (
              <option key={String(item.match_id)} value={String(item.match_id)}>
                {item.match_label}
              </option>
            ))}
          </select>
        </div>
        {query.isLoading ? (
          <LoadingRows />
        ) : currentEvents.length ? (
          <>
            <div className="grid grid-cols-2 gap-3 border-b border-border p-4 sm:grid-cols-4">
              {[
                { label: "Match", value: first?.match_label ?? "—" },
                { label: "Format", value: first?.format ?? format },
                { label: "Innings", value: first?.innings ?? "—" },
                { label: "Delivery events", value: currentEvents.length },
              ].map((item) => (
                <div key={item.label} className="min-w-0">
                  <p className="text-[9px] font-semibold uppercase tracking-wider text-muted-foreground">
                    {item.label}
                  </p>
                  <p className="mt-1.5 truncate text-[12px] font-bold">{item.value}</p>
                </div>
              ))}
            </div>
            <Table>
              <TableHeader>
                <TableRow>
                  {["Phase", "Over", "Batter", "Bowler", "Runs", "Wickets"].map((column) => (
                    <TableHead key={column} className="text-[9px]">
                      {column}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {currentEvents.map((event, index) => (
                  <TableRow key={`${event.match_id}-${index}`}>
                    <TableCell className="text-[10px]">{event.phase ?? "—"}</TableCell>
                    <TableCell className="text-[10px] tabular-nums">{event.over ?? "—"}</TableCell>
                    <TableCell className="text-[10px]">{event.batter ?? "—"}</TableCell>
                    <TableCell className="text-[10px]">{event.bowler ?? "—"}</TableCell>
                    <TableCell className="text-[10px] tabular-nums">{event.runs ?? "—"}</TableCell>
                    <TableCell className="text-[10px] tabular-nums">
                      {event.wickets ?? "—"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </>
        ) : (
          <EmptyChart
            title="No verified match events available"
            note="Innings and delivery timelines are generated from API match data, never from sample records."
          />
        )}
      </Surface>
    </>
  );
}

function ComparisonPage() {
  const { format, search } = useDashboard();
  const [kind, setKind] = useState<"batters" | "bowlers">("batters");
  const key = `/${kind}?format=${format}&limit=500`;
  const query = useAnalytics<z.infer<typeof RankingListSchema>>(key, RankingListSchema);
  const [picked, setPicked] = useState<string[]>([]);
  const available = useMemo(
    () =>
      (query.data?.players ?? []).filter((player) =>
        player.player_name.toLowerCase().includes(search.toLowerCase()),
      ),
    [query.data?.players, search],
  );
  const selected = available.filter((player) => picked.includes(player.player_name));
  return (
    <>
      <PageTitle
        title="Player comparison studio"
        subtitle="Select two or more eligible players and compare their actual final scores and performance metrics."
        icon={GitCompareArrows}
      />
      <ApiStatus error={query.error} refetch={() => void query.refetch()} />
      <div className="mb-4 flex items-center gap-1 rounded-md border border-border bg-card p-1 w-fit">
        {(["batters", "bowlers"] as const).map((option) => (
          <Button
            key={option}
            variant="ghost"
            aria-pressed={kind === option}
            onClick={() => {
              setKind(option);
              setPicked([]);
            }}
            className={`h-8 px-3 text-[11px] font-bold capitalize ${kind === option ? "bg-primary text-primary-foreground hover:bg-primary/90" : "text-muted-foreground"}`}
          >
            {option}
          </Button>
        ))}
      </div>
      <Surface className="mb-5">
        <div className="border-b border-border px-4 py-3.5">
          <p className="text-[12px] font-bold">Select up to four {kind}</p>
          <p className="mt-1 text-[10px] text-muted-foreground">
            {picked.length} selected · {format} rankings
          </p>
        </div>
        {query.isLoading ? (
          <LoadingRows />
        ) : available.length ? (
          <div className="flex flex-wrap gap-2 p-4">
            {available.map((player) => {
              const active = picked.includes(player.player_name);
              return (
                <Button
                  key={player.player_name}
                  variant={active ? "default" : "outline"}
                  size="sm"
                  className="h-9 gap-2 text-[10px]"
                  onClick={() =>
                    setPicked((current) =>
                      active
                        ? current.filter((name) => name !== player.player_name)
                        : current.length < 4
                          ? [...current, player.player_name]
                          : current,
                    )
                  }
                >
                  {active ? <Check /> : <Users />}
                  {player.player_name}
                </Button>
              );
            })}
          </div>
        ) : (
          <EmptyChart
            title="No eligible players to compare"
            note="Player selection is populated only from verified API rankings."
          />
        )}
      </Surface>
      {selected.length >= 2 ? (
        <Surface>
          <div className="border-b border-border px-4 py-3.5">
            <p className="text-[12px] font-bold">Performance comparison</p>
          </div>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="text-[10px]">Metric</TableHead>
                  {selected.map((player) => (
                    <TableHead key={player.player_name} className="text-[10px]">
                      {player.player_name}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {[
                  "final_rank",
                  "final_score",
                  ...(kind === "batters" ? batterMetrics : bowlerMetrics),
                ].map((metric) => (
                  <TableRow key={metric}>
                    <TableCell className="whitespace-nowrap text-[10px] font-semibold">
                      {labelsByMetric[metric]}
                    </TableCell>
                    {selected.map((player) => {
                      const value = player[metric as keyof Player];
                      return (
                        <TableCell key={player.player_name} className="text-[10px] tabular-nums">
                          {typeof value === "object"
                            ? "—"
                            : (value ?? player.metrics?.[metric] ?? "—")}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Surface>
      ) : (
        <EmptyChart
          title="Select at least two eligible players"
          note="Comparison charts and score breakdowns appear when verified player rankings include comparable metrics."
        />
      )}
    </>
  );
}

function MethodologyPage() {
  const batterWeights = BATTER_WEIGHTS;
  const bowlerWeights = BOWLER_WEIGHTS;
  const WeightTable = ({
    title,
    items,
  }: {
    title: string;
    items: readonly { label: string; weight: number }[];
  }) => (
    <Surface>
      <div className="border-b border-border px-4 py-3.5">
        <p className="text-[12px] font-bold">{title} baseline</p>
      </div>
      {items.map((item) => (
        <div
          key={item.label}
          className="flex items-center gap-3 border-b border-border/70 px-4 py-3 last:border-0"
        >
          <span className="flex-1 text-[11px]">{item.label}</span>
          <div className="h-1.5 w-[min(36%,180px)] overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary"
              style={{ width: `${item.weight * 4}%` }}
            />
          </div>
          <span className="w-9 text-right text-[11px] font-extrabold tabular-nums">
            {item.weight}%
          </span>
        </div>
      ))}
    </Surface>
  );
  return (
    <>
      <PageTitle
        title="Ranking methodology"
        subtitle="Project-defined eligibility and baseline weights for transparent pressure-performance rankings."
        icon={CircleHelp}
        eyebrow="GOVERNANCE"
      />
      <div className="mb-5 grid gap-5 xl:grid-cols-2">
        <WeightTable title="Batter scoring weights" items={batterWeights} />
        <WeightTable title="Bowler scoring weights" items={bowlerWeights} />
      </div>
      <div className="mb-5 grid gap-5 md:grid-cols-2">
        <Surface>
          <div className="border-b border-border px-4 py-3.5">
            <p className="text-[12px] font-bold">Eligibility thresholds</p>
            <p className="mt-1 text-[10px] text-muted-foreground">
              As specified in the supplied project brief
            </p>
          </div>
          <div className="space-y-4 p-4">
            <div className="flex items-start gap-3">
              <Target className="h-4 w-4 text-rr-pink" />
              <div>
                <p className="text-[11px] font-bold">Batters</p>
                <p className="mt-1 text-[10px] text-muted-foreground">
                  At least {eligibility.batter.pressureBalls} pressure balls and{" "}
                  {eligibility.batter.pressureMatches} pressure matches.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Activity className="h-4 w-4 text-cyan" />
              <div>
                <p className="text-[11px] font-bold">Bowlers</p>
                <p className="mt-1 text-[10px] text-muted-foreground">
                  At least {eligibility.bowler.pressureLegalBalls} pressure legal balls and{" "}
                  {eligibility.bowler.verifiedPressureMatches} verified pressure matches.
                </p>
              </div>
            </div>
          </div>
        </Surface>
        <Surface>
          <div className="border-b border-border px-4 py-3.5">
            <p className="text-[12px] font-bold">Scoring transparency</p>
          </div>
          <div className="space-y-3 p-4">
            <p className="text-[11px] leading-relaxed text-muted-foreground">
              Metric contribution view: each metric contributes its project-assigned share of the
              final score. Lower-is-better metric direction, percentile methodology, consistency
              formula, and normalization details require the project's implementation before they
              can be published accurately.
            </p>
            <div className="flex items-start gap-2 rounded-md border border-amber/30 bg-amber/5 p-3">
              <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber" />
              <p className="text-[10px] leading-relaxed text-muted-foreground">
                Pressure levels and cricket rules are project-defined where applicable; no
                additional thresholds or official definitions are assumed.
              </p>
            </div>
          </div>
        </Surface>
      </div>
      <div className="grid gap-5 xl:grid-cols-2">
        <WeightTable title="Score contribution · batters" items={batterWeights} />
        <WeightTable title="Score contribution · bowlers" items={bowlerWeights} />
      </div>
    </>
  );
}

function ScenariosPage() {
  const { format } = useDashboard();
  const [discipline, setDiscipline] = useState<"batter" | "bowler">("batter");
  const [scenario, setScenario] = useState("baseline");
  const choices =
    discipline === "batter"
      ? ["baseline", "volume_focused", "efficiency_focused"]
      : ["baseline", "wicket_impact", "control_focused"];
  const query = useAnalytics<z.infer<typeof ScenarioSchema>>(
    `/scenarios?format=${format}&discipline=${discipline}&scenario=${scenario}`,
    ScenarioSchema,
  );
  const players = query.data?.players ?? [];
  useEffect(() => setScenario("baseline"), [discipline]);
  return (
    <>
      <PageTitle
        title="Scenario analysis"
        subtitle="Review methodology-defined weighting scenarios and compare rankings returned by the analytical service."
        icon={Activity}
        eyebrow="SENSITIVITY ANALYSIS"
      />
      <ApiStatus error={query.error} refetch={() => void query.refetch()} />
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <div className="flex gap-1 rounded-md border border-border bg-card p-1">
          {(["batter", "bowler"] as const).map((option) => (
            <Button
              key={option}
              variant="ghost"
              aria-pressed={discipline === option}
              onClick={() => setDiscipline(option)}
              className={`h-8 px-3 text-[10px] font-bold capitalize ${discipline === option ? "bg-primary text-primary-foreground hover:bg-primary/90" : "text-muted-foreground"}`}
            >
              {option}
            </Button>
          ))}
        </div>
        <div className="flex flex-wrap gap-1 rounded-md border border-border bg-card p-1">
          {choices.map((option) => (
            <Button
              key={option}
              variant="ghost"
              aria-pressed={scenario === option}
              onClick={() => setScenario(option)}
              className={`h-8 px-3 text-[10px] font-semibold ${scenario === option ? "bg-secondary text-secondary-foreground" : "text-muted-foreground"}`}
            >
              {option.replaceAll("_", " ")}
            </Button>
          ))}
        </div>
      </div>
      <div className="mb-5 grid grid-cols-1 gap-5 md:grid-cols-2">
        <Surface>
          <div className="border-b border-border px-4 py-3.5">
            <p className="text-[12px] font-bold">Scenario overlap</p>
          </div>
          <div className="p-5">
            <p className="text-[10px] text-muted-foreground">
              API-calculated Top 10 membership overlap
            </p>
            <p className="mt-3 text-[30px] font-extrabold tabular-nums">
              {query.data?.overlap_percentage ?? "—"}
              {query.data?.overlap_percentage !== undefined &&
              query.data?.overlap_percentage !== null
                ? "%"
                : ""}
            </p>
          </div>
        </Surface>
        <Surface>
          <div className="border-b border-border px-4 py-3.5">
            <p className="text-[12px] font-bold">Active weighting</p>
          </div>
          {query.data?.weightages?.length ? (
            query.data.weightages.map((weight) => (
              <div
                key={weight.metric}
                className="flex items-center border-b border-border/70 px-4 py-3 last:border-0"
              >
                <span className="flex-1 text-[10px]">{weight.metric}</span>
                <span className="text-[11px] font-bold tabular-nums">{weight.weight}%</span>
              </div>
            ))
          ) : (
            <EmptyChart title="Awaiting scenario weights" />
          )}
        </Surface>
      </div>
      <Surface>
        <div className="border-b border-border px-4 py-3.5">
          <p className="text-[12px] font-bold">Scenario ranking movement</p>
          <p className="mt-1 text-[10px] text-muted-foreground">
            Only calculations returned for the selected weighting are shown.
          </p>
        </div>
        {query.isLoading ? (
          <LoadingRows />
        ) : players.length ? (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  {["final_rank", "player_name", "final_score"].map((key) => (
                    <TableHead key={key} className="text-[10px]">
                      {labelsByMetric[key]}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {players.map((player) => (
                  <TableRow key={player.player_name}>
                    <TableCell className="text-[10px] tabular-nums">{player.final_rank}</TableCell>
                    <TableCell className="text-[10px] font-semibold">
                      {player.player_name}
                    </TableCell>
                    <TableCell className="text-[10px] tabular-nums">
                      {player.final_score.toFixed(2)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <EmptyChart
            title="Alternative scenario rankings are not available"
            note="No alternative rankings are invented. Connect the API's scenario calculations to display score movement and Top 10 changes."
          />
        )}
      </Surface>
    </>
  );
}

const knownAudit = [
  { name: "Run reconciliation", status: "PASS", detail: "Zero mismatches." },
  { name: "Legal-ball classification", status: "PASS", detail: "Reconciled with project rules." },
  { name: "Batter baseline ranking", status: "PASS", detail: "Independently reproduced." },
  { name: "Bowler baseline ranking", status: "PASS", detail: "Independently reproduced." },
  {
    name: "Alternative bowler scenario scores",
    status: "PASS",
    detail: "Independently reproduced.",
  },
  {
    name: "Retire Out dismissal ID",
    status: "WARNING",
    detail: "One missing dismissed_player_id for a Retire Out event.",
  },
  {
    name: "Other extras category",
    status: "WARNING",
    detail: "Ambiguous `other` extras category.",
  },
  {
    name: "Legacy pressure wickets per match",
    status: "WARNING",
    detail: "Legacy field uses the original denominator; ranking uses the corrected denominator.",
  },
];

function AuditPage() {
  const query = useAnalytics<z.infer<typeof AuditSchema>>("/audit", AuditSchema);
  const checks = query.data?.checks ?? knownAudit;
  return (
    <>
      <PageTitle
        title="Audit & data quality"
        subtitle="Transparent validation status and known limitations supplied for this project."
        icon={ClipboardCheck}
        eyebrow="DATA GOVERNANCE"
      />
      <ApiStatus error={query.error} refetch={() => void query.refetch()} />
      <div className="mb-5 grid grid-cols-1 gap-5 md:grid-cols-3">
        <Surface className="flex items-center gap-3 p-4">
          <span className="flex h-9 w-9 items-center justify-center rounded-md bg-success/10 text-success">
            <Check className="h-4 w-4" />
          </span>
          <div>
            <p className="text-[10px] font-semibold text-muted-foreground">Confirmed checks</p>
            <p className="mt-1 text-[19px] font-extrabold tabular-nums">
              {checks.filter((item) => item.status === "PASS").length}
            </p>
          </div>
        </Surface>
        <Surface className="flex items-center gap-3 p-4">
          <span className="flex h-9 w-9 items-center justify-center rounded-md bg-amber/10 text-amber">
            <AlertTriangle className="h-4 w-4" />
          </span>
          <div>
            <p className="text-[10px] font-semibold text-muted-foreground">Known warnings</p>
            <p className="mt-1 text-[19px] font-extrabold tabular-nums">
              {checks.filter((item) => item.status === "WARNING").length}
            </p>
          </div>
        </Surface>
        <Surface className="flex items-center gap-3 p-4">
          <span className="flex h-9 w-9 items-center justify-center rounded-md bg-cyan/10 text-cyan">
            <Database className="h-4 w-4" />
          </span>
          <div>
            <p className="text-[10px] font-semibold text-muted-foreground">Dataset connection</p>
            <p className="mt-1 text-[12px] font-bold">
              {query.data ? "Connected" : "Awaiting API"}
            </p>
          </div>
        </Surface>
      </div>
      <Surface>
        <div className="border-b border-border px-4 py-3.5">
          <p className="text-[12px] font-bold">Audit checks & known limitations</p>
          <p className="mt-1 text-[10px] text-muted-foreground">
            Warnings are visible by design and are not silently dismissed.
          </p>
        </div>
        {checks.map((item) => {
          const pass = item.status === "PASS";
          return (
            <div
              key={item.name}
              className="flex flex-wrap items-start gap-3 border-b border-border/70 px-4 py-3.5 last:border-0"
            >
              <span
                className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md ${pass ? "bg-success/10 text-success" : "bg-amber/10 text-amber"}`}
              >
                {pass ? (
                  <Check className="h-3.5 w-3.5" />
                ) : (
                  <AlertTriangle className="h-3.5 w-3.5" />
                )}
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-[11px] font-bold">{item.name}</p>
                <p className="mt-1 text-[10px] leading-relaxed text-muted-foreground">
                  {item.detail}
                </p>
              </div>
              <span
                className={`rounded px-2 py-1 text-[9px] font-extrabold tracking-wider ${pass ? "bg-success/10 text-success" : "bg-amber/10 text-amber"}`}
              >
                {item.status}
              </span>
            </div>
          );
        })}
      </Surface>
      <div className="mt-5 rounded-md border border-border bg-muted/50 p-4">
        <div className="flex gap-2">
          <Info className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
          <p className="text-[10px] leading-relaxed text-muted-foreground">
            Dataset coverage, duplicate checks, wicket reconciliation, and pressure classification
            validation are not assumed. They must be explicitly returned by the live audit API
            before receiving a verified status.
          </p>
        </div>
      </div>
    </>
  );
}

export function AnalyticsSection({ section }: { section: Section }) {
  if (section === "overview") return <OverviewPage />;
  if (section === "batters" || section === "bowlers") return <PlayersPage kind={section} />;
  if (section === "pressure") return <PressurePage />;
  if (section === "matches") return <MatchesPage />;
  if (section === "comparison") return <ComparisonPage />;
  if (section === "methodology") return <MethodologyPage />;
  if (section === "scenarios") return <ScenariosPage />;
  return <AuditPage />;
}
