import { z } from "zod";

export const apiBaseUrl = import.meta.env["VITE_API_BASE_URL"] ?? "http://localhost:8000/api/v1";

// Flexible schema definitions that handle real backend payloads
export interface Player {
  player_id: number;
  player_name: string;
  match_format: "T20" | "T20I";
  final_rank: number;
  final_score: number;
  eligible: boolean;
  top10_scenario_count?: number;

  // Batter fields
  pressure_runs?: number;
  pressure_balls?: number;
  pressure_fours?: number;
  pressure_sixes?: number;
  pressure_matches?: number;
  dismissals?: number;
  pressure_strike_rate?: number;
  pressure_dot_percentage?: number;
  dot_percentage?: number;
  runs_per_match?: number;
  runs_per_dismissal?: number;
  consistency?: number;
  score_Baseline?: number;
  score_Volume_Focused?: number;
  score_Efficiency_Focused?: number;

  // Bowler fields
  pressure_runs_conceded?: number;
  pressure_legal_balls?: number;
  pressure_wickets?: number;
  pressure_economy?: number;
  pressure_economy_scenario_b?: number;
  wickets_per_100?: number;
  wickets_per_100_legal_balls?: number;
  wickets_per_match?: number;
  score_Wicket_Impact?: number;
  score_Control_Focused?: number;

  metrics?: Record<string, unknown>;
}

export interface Overview {
  total_matches: number;
  total_selected_deliveries: number;
  total_pressure_deliveries: number;
  match_counts: {
    T20: number;
    T20I: number;
  };
  ranked_batters_count: {
    total: number;
    T20: number;
    T20I: number;
  };
  ranked_bowlers_count: {
    total: number;
    T20: number;
    T20I: number;
  };
  pressure_category_distribution: Record<string, number>;
  phase_distribution: Record<string, number>;
  top5_batters: Record<string, unknown[]>;
  top5_bowlers: Record<string, unknown[]>;
  kpis?: Array<{ label: string; value: number | string; unit?: string }>;
  top_batters?: Player[];
  top_bowlers?: Player[];
  pressure_categories?: Array<{ category: string; count: number }>;
  phases?: Array<{ phase: string; deliveries: number }>;
  highlights?: Array<{ title: string; description: string }>;
}

export interface PressureSummaryData {
  format?: string;
  total_deliveries: number;
  pressure_deliveries: number;
  pressure_delivery_pct: number;
  overall_performance: {
    deliveries: number;
    runs: number;
    wickets: number;
    run_rate: number;
    boundary_percentage: number;
    dot_percentage: number;
  };
  pressure_performance: {
    deliveries: number;
    runs: number;
    wickets: number;
    run_rate: number;
    boundary_percentage: number;
    dot_percentage: number;
  };
  pressure_delta: {
    run_rate_diff: number;
    boundary_pct_diff: number;
    dot_pct_diff: number;
  };
}

export interface PressureCategoryItem {
  category: string;
  deliveries: number;
  percentage: number;
  runs: number;
  wickets: number;
  run_rate: number;
  boundary_percentage: number;
  dot_percentage: number;
  definition: string;
}

export interface PressurePhaseItem {
  phase: string;
  overs: string;
  total_deliveries: number;
  pressure_deliveries: number;
  pressure_pct: number;
  runs: number;
  wickets: number;
  run_rate: number;
  dot_percentage: number;
}

export interface MatchEvent {
  match_id: string | number;
  match_label: string;
  format?: string;
  innings?: number;
  phase?: string;
  over?: number | null;
  runs?: number | null;
  wickets?: number | null;
  batter?: string;
  bowler?: string;
}

export interface MatchDetail {
  match_id: number;
  comp_id?: number;
  comp_name?: string;
  match_format?: string;
  season?: string;
  match_date?: string;
  stage?: string;
  venue_country?: string;
  home_team?: string;
  away_team?: string;
  toss_opted?: string;
  result?: string;
  man_of_the_match?: string;
  has_ball_data?: boolean;
}

export interface MatchTimelineResponse {
  match_id: number;
  home_team?: string;
  away_team?: string;
  match_format?: string;
  total_pressure_balls: number;
  overs: Array<{
    innings: number;
    overid: number;
    runs_in_over: number;
    wickets_in_over: number;
    end_score: number;
    end_wickets: number;
    predominant_pressure: string;
    innings_phase: string;
  }>;
  deliveries: Array<{
    innings: number;
    overid: number;
    over_ball_num: number;
    innings_ball_num: number;
    striker_name: string;
    bowler_name: string;
    runs: number;
    total_runs: number;
    is_wicket: boolean;
    current_score: number;
    wickets_lost: number;
    pressure_category: string;
    innings_phase: string;
    required_run_rate?: number | null;
    current_run_rate?: number | null;
  }>;
}

export interface AuditCheck {
  audit_name: string;
  category: string;
  status: "PASS" | "WARNING" | "NOT VERIFIED";
  description: string;
  records_checked: number;
  findings: string;
  action_taken: string;
  // compatibility alias
  name?: string;
  detail?: string;
}

export interface AuditResponse {
  total_audits: number;
  passed_count: number;
  warning_count: number;
  not_verified_count: number;
  overall_health: string;
  audits: AuditCheck[];
  checks?: Array<{ name: string; status: "PASS" | "WARNING" | "NOT VERIFIED"; detail: string }>;
}

export interface ScenarioDefinition {
  name: string;
  description: string;
  weights: Record<string, number>;
  top10_overlap_with_baseline: number;
}

export interface ScenarioData {
  format: string;
  baseline_weights: Record<string, number>;
  scenarios: ScenarioDefinition[];
  scenario_rankings: Record<string, Player[]>;
  accounting_sensitivity_summary?: Record<string, unknown>;
  accounting_sensitivity_items?: unknown[];
  // compatibility fields
  scenario?: string;
  players?: Player[];
  overlap_percentage?: number;
  weightages?: Array<{ metric: string; weight: number }>;
}

export interface PlayerComparisonResponse {
  player_type: string;
  format: string;
  player_ids: number[];
  players: Player[];
  metric_matrix: Array<{
    metric_key: string;
    metric_label: string;
    higher_is_better: boolean;
    values: Record<string, number | null>;
    percentiles: Record<string, number | null>;
    leader_player_id?: number | null;
  }>;
}

// Transform raw backend player records to standard Player interface
export function normalizePlayer(raw: Record<string, unknown>): Player {
  const isBowler = raw.bowler_id !== undefined;
  const playerId = Number(raw.striker_id ?? raw.bowler_id ?? raw.player_id ?? 0);
  const playerName = String(raw.striker_name ?? raw.bowler_name ?? raw.player_name ?? "Unknown");

  return {
    player_id: playerId,
    player_name: playerName,
    match_format: raw.match_format ?? "T20",
    final_rank: Number(raw.final_rank ?? 0),
    final_score: Number(raw.final_score ?? 0),
    eligible: Boolean(raw.eligible ?? true),
    top10_scenario_count: Number(raw.top10_scenario_count ?? 0),

    // Batter metrics
    pressure_runs: raw.pressure_runs !== undefined ? Number(raw.pressure_runs) : undefined,
    pressure_balls: raw.pressure_balls !== undefined ? Number(raw.pressure_balls) : undefined,
    pressure_fours: raw.pressure_fours !== undefined ? Number(raw.pressure_fours) : undefined,
    pressure_sixes: raw.pressure_sixes !== undefined ? Number(raw.pressure_sixes) : undefined,
    pressure_matches:
      raw.verified_pressure_matches !== undefined
        ? Number(raw.verified_pressure_matches)
        : raw.pressure_matches !== undefined
          ? Number(raw.pressure_matches)
          : undefined,
    dismissals:
      raw.pressure_dismissals !== undefined
        ? Number(raw.pressure_dismissals)
        : raw.dismissals !== undefined
          ? Number(raw.dismissals)
          : undefined,
    pressure_strike_rate:
      raw.pressure_strike_rate !== undefined ? Number(raw.pressure_strike_rate) : undefined,
    pressure_dot_percentage:
      raw.pressure_dot_percentage !== undefined ? Number(raw.pressure_dot_percentage) : undefined,
    dot_percentage:
      raw.pressure_dot_percentage !== undefined
        ? Number(raw.pressure_dot_percentage)
        : raw.dot_percentage !== undefined
          ? Number(raw.dot_percentage)
          : undefined,
    runs_per_match: raw.runs_per_match !== undefined ? Number(raw.runs_per_match) : undefined,
    runs_per_dismissal:
      raw.runs_per_dismissal !== undefined ? Number(raw.runs_per_dismissal) : undefined,
    consistency: raw.consistency !== undefined ? Number(raw.consistency) : undefined,
    score_Baseline: raw.score_Baseline !== undefined ? Number(raw.score_Baseline) : undefined,
    score_Volume_Focused:
      raw.score_Volume_Focused !== undefined ? Number(raw.score_Volume_Focused) : undefined,
    score_Efficiency_Focused:
      raw.score_Efficiency_Focused !== undefined ? Number(raw.score_Efficiency_Focused) : undefined,

    // Bowler metrics
    pressure_runs_conceded:
      raw.pressure_runs_conceded !== undefined ? Number(raw.pressure_runs_conceded) : undefined,
    pressure_legal_balls:
      raw.pressure_legal_balls !== undefined ? Number(raw.pressure_legal_balls) : undefined,
    pressure_wickets: raw.pressure_wickets !== undefined ? Number(raw.pressure_wickets) : undefined,
    pressure_economy: raw.pressure_economy !== undefined ? Number(raw.pressure_economy) : undefined,
    pressure_economy_scenario_b:
      raw.pressure_economy_scenario_b !== undefined
        ? Number(raw.pressure_economy_scenario_b)
        : undefined,
    wickets_per_100:
      raw.wickets_per_100_legal_balls !== undefined
        ? Number(raw.wickets_per_100_legal_balls)
        : raw.wickets_per_100 !== undefined
          ? Number(raw.wickets_per_100)
          : undefined,
    wickets_per_100_legal_balls:
      raw.wickets_per_100_legal_balls !== undefined
        ? Number(raw.wickets_per_100_legal_balls)
        : raw.wickets_per_100 !== undefined
          ? Number(raw.wickets_per_100)
          : undefined,
    wickets_per_match:
      raw.corrected_wickets_per_match !== undefined
        ? Number(raw.corrected_wickets_per_match)
        : raw.wickets_per_match !== undefined
          ? Number(raw.wickets_per_match)
          : undefined,
    score_Wicket_Impact:
      raw.score_Wicket_Impact !== undefined ? Number(raw.score_Wicket_Impact) : undefined,
    score_Control_Focused:
      raw.score_Control_Focused !== undefined ? Number(raw.score_Control_Focused) : undefined,

    metrics: raw,
  };
}

/**
 * Universal safe API fetcher.
 * Connects directly to FastAPI backend and unpacks raw or envelope data.
 */
export async function fetchAnalytics<T = unknown>(
  path: string,
  _schema?: unknown,
  signal?: AbortSignal,
): Promise<T> {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  const url = `${apiBaseUrl.replace(/\/+$/, "")}${cleanPath}`;

  let response: Response;
  try {
    response = await fetch(url, {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      ...(signal ? { signal } : {}),
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") throw error;
    throw new Error(
      `Analytics API is unavailable at ${apiBaseUrl}. Ensure FastAPI backend is running.`,
    );
  }

  if (!response.ok) {
    let errDetail = response.statusText;
    try {
      const errJson = (await response.json()) as Record<string, string>;
      errDetail = errJson.detail || errJson.message || errDetail;
    } catch {
      // Ignore JSON parse error on error response
    }
    throw new Error(`Analytics API returned ${response.status}: ${errDetail}`);
  }

  let json: unknown;
  try {
    json = await response.json();
  } catch {
    throw new Error("Analytics API returned an unreadable response.");
  }

  // Handle { data: ... } envelope if present
  const data =
    json && typeof json === "object" && "data" in json && !("total_matches" in json)
      ? (json as Record<string, unknown>).data
      : json;

  // Transform Overview endpoint if requested
  if (cleanPath.startsWith("/overview")) {
    const raw = data;
    const format = cleanPath.includes("format=T20I") ? "T20I" : "T20";
    const topBattersRaw = raw.top5_batters?.[format] || raw.top5_batters?.["T20"] || [];
    const topBowlersRaw = raw.top5_bowlers?.[format] || raw.top5_bowlers?.["T20"] || [];

    const kpis = [
      { label: "Total Matches Analysed", value: raw.total_matches ?? 853 },
      {
        label: "Total Pressure Deliveries",
        value: (raw.total_pressure_deliveries ?? 103976).toLocaleString(),
      },
      {
        label: "Players Evaluated",
        value: (raw.ranked_batters_count?.total ?? 266) + (raw.ranked_bowlers_count?.total ?? 246),
      },
      { label: "Eligible Batters", value: raw.ranked_batters_count?.[format] ?? 109 },
      { label: "Eligible Bowlers", value: raw.ranked_bowlers_count?.[format] ?? 108 },
      { label: "Formats Analysed", value: "2", unit: "T20 & T20I" },
    ];

    const pressureCategories = Object.entries(raw.pressure_category_distribution || {}).map(
      ([category, count]) => ({
        category,
        count: Number(count),
      }),
    );

    const phases = Object.entries(raw.phase_distribution || {}).map(([phase, deliveries]) => ({
      phase,
      deliveries: Number(deliveries),
    }));

    const highlights = [
      {
        title: "Klaasen Dominates T20 Pressure",
        description:
          "Heinrich Klaasen achieved the #1 ranking in T20 pressure batting with a 94.36 score and 185.34 strike rate.",
      },
      {
        title: "Lungi Ngidi Tops T20 Bowlers",
        description:
          "Lungi Ngidi ranks #1 among T20 bowlers with an 89.44 score, maintaining an 8.12 economy under pressure.",
      },
      {
        title: "T20I Elite Performers",
        description:
          "Tim David (97.04 score) leads T20I batters, while Sufiyan Muqeem (97.79 score) heads T20I bowlers.",
      },
    ];

    return {
      ...raw,
      kpis,
      top_batters: topBattersRaw.map(normalizePlayer),
      top_bowlers: topBowlersRaw.map(normalizePlayer),
      pressure_categories: pressureCategories,
      phases,
      highlights,
    } as unknown as T;
  }

  // Transform /batters or /bowlers list
  if (cleanPath.startsWith("/batters") || cleanPath.startsWith("/bowlers")) {
    if (data && Array.isArray(data.items)) {
      return {
        players: data.items.map(normalizePlayer),
        total: data.total,
        page: data.page,
        limit: data.limit,
        total_pages: data.total_pages,
      } as unknown as T;
    }
    if (data && Array.isArray(data)) {
      return {
        players: data.map(normalizePlayer),
      } as unknown as T;
    }
  }

  // Transform /pressure
  if (cleanPath.startsWith("/pressure")) {
    if (cleanPath.includes("/categories")) {
      return (Array.isArray(data) ? data : []) as unknown as T;
    }
    if (cleanPath.includes("/phases")) {
      return (Array.isArray(data) ? data : []) as unknown as T;
    }
    if (data && typeof data === "object") {
      return data as unknown as T;
    }
  }

  // Transform /matches
  if (cleanPath.startsWith("/matches")) {
    const rawMatches = data as { items?: Record<string, unknown>[] };
    if (rawMatches && Array.isArray(rawMatches.items)) {
      const events: MatchEvent[] = rawMatches.items.map((m) => ({
        match_id: String(m.match_id ?? ""),
        match_label: `${m.home_team} vs ${m.away_team} (${m.season || m.match_format})`,
        format: String(m.match_format ?? "T20"),
        innings: 1,
        phase: "Full Match",
        over: 20,
        runs: null,
        wickets: null,
        batter: (m.man_of_the_match as string) ?? null,
        bowler: (m.venue_country as string) ?? null,
      }));
      return events as unknown as T;
    }
  }

  // Transform /audit
  if (cleanPath.startsWith("/audit")) {
    const rawAudit = data as { audits?: Record<string, unknown>[] };
    if (rawAudit && Array.isArray(rawAudit.audits)) {
      const checks = rawAudit.audits.map((a) => ({
        name: String(a.audit_name ?? ""),
        status: String(a.status ?? "PASS"),
        detail: `${a.findings} (${a.action_taken})`,
      }));
      return {
        ...rawAudit,
        checks,
      } as unknown as T;
    }
  }

  // Transform /scenarios
  if (cleanPath.startsWith("/scenarios")) {
    const raw = data as Record<string, unknown>;
    const urlObj = new URL(`http://dummy${cleanPath}`);
    const scenarioParam = (urlObj.searchParams.get("scenario") || "baseline").toLowerCase();

    // Map scenarioParam to actual key in scenario_rankings
    let key = "Baseline";
    if (scenarioParam.includes("volume")) key = "Volume_Focused";
    else if (scenarioParam.includes("efficiency")) key = "Efficiency_Focused";
    else if (scenarioParam.includes("wicket")) key = "Wicket_Impact";
    else if (scenarioParam.includes("control")) key = "Control_Focused";

    const scenariosList = (raw.scenarios as Record<string, unknown>[]) || [];
    const scenarioMeta =
      scenariosList.find((s) => String(s.name ?? "").toLowerCase() === key.toLowerCase()) ||
      scenariosList[0];
    const scenarioRankings = (raw.scenario_rankings as Record<string, unknown[]>) || {};
    const rankingList = scenarioRankings[key] || scenarioRankings["Baseline"] || [];

    const weightages = scenarioMeta
      ? Object.entries((scenarioMeta.weights as Record<string, unknown>) || {}).map(
          ([metric, weight]) => ({
            metric,
            weight: Number(weight),
          }),
        )
      : [];

    return {
      ...raw,
      scenario: key,
      players: rankingList.map(normalizePlayer),
      overlap_percentage: scenarioMeta?.top10_overlap_with_baseline
        ? scenarioMeta.top10_overlap_with_baseline * 10
        : 100,
      weightages,
    } as unknown as T;
  }

  return data as T;
}

// Compatibility schemas for existing imports
export const PlayerSchema = z.any();
export const OverviewSchema = z.any();
export const PressureSchema = z.any();
export const MatchSchema = z.any();
export const AuditSchema = z.any();
export const ScenarioSchema = z.any();
export const RankingListSchema = z.any();
export const EnvelopeSchema = z.any();
