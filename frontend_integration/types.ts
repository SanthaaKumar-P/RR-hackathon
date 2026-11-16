/**
 * SupeRR Selector – Cricket Intelligence Platform
 * TypeScript Data Models & API Contracts
 */

export type MatchFormat = 'T20' | 'T20I';
export type SortOrder = 'asc' | 'desc';

export interface HealthResponse {
  status: string;
  version: string;
  project: string;
  datasets_loaded: boolean;
  total_matches: number;
  total_pressure_deliveries: number;
}

export interface OverviewResponse {
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
  top5_batters: Record<MatchFormat, BatterRankingItem[]>;
  top5_bowlers: Record<MatchFormat, BowlerRankingItem[]>;
}

export interface BatterRankingItem {
  match_format: MatchFormat;
  striker_id: number;
  striker_name: string;
  final_rank: number;
  final_score: number;
  eligible: boolean;
  top10_scenario_count: number;
  pressure_runs: number;
  pressure_balls: number;
  pressure_fours: number;
  pressure_sixes: number;
  pressure_deliveries: number;
  pressure_dot_balls: number;
  pressure_matches: number;
  pressure_dismissals: number;
  pressure_strike_rate: number;
  pressure_dot_percentage: number;
  runs_per_match: number;
  runs_per_dismissal: number;
  consistency: number;
  matches_10_plus: number;
  matches_20_plus: number;
  matches_10_plus_pct: number;
  matches_20_plus_pct: number;
  score_pressure_strike_rate: number;
  score_runs_per_match: number;
  score_runs_per_dismissal: number;
  score_pressure_dot_percentage: number;
  score_consistency: number;
  score_Baseline: number;
  score_Volume_Focused: number;
  score_Efficiency_Focused: number;
}

export interface BowlerRankingItem {
  match_format: MatchFormat;
  bowler_id: number;
  bowler_name: string;
  final_rank: number;
  final_score: number;
  eligible: boolean;
  top10_scenario_count: number;
  pressure_runs_conceded: number;
  pressure_runs_conceded_scenario_b: number;
  pressure_legal_balls: number;
  pressure_wickets: number;
  pressure_dot_balls: number;
  pressure_deliveries: number;
  pressure_matches: number;
  pressure_overs: number;
  pressure_economy: number;
  pressure_economy_scenario_b: number;
  pressure_dot_percentage: number;
  wickets_per_100: number;
  wickets_per_match: number;
  consistency: number;
  matches_1_plus: number;
  matches_2_plus: number;
  matches_1_plus_pct: number;
  matches_2_plus_pct: number;
  score_wickets_per_100: number;
  score_pressure_economy: number;
  score_pressure_dot_percentage: number;
  score_consistency: number;
  score_wickets_per_match: number;
  score_Baseline: number;
  score_Wicket_Impact: number;
  score_Control_Focused: number;
}

export interface PaginatedList<T> {
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  format?: string;
  items: T[];
}

export interface BatterDetailResponse {
  player_id: number;
  player_name: string;
  match_format: MatchFormat;
  ranking: BatterRankingItem;
  methodology_weights: Record<string, number>;
  scenarios: Record<string, number | null>;
  raw_stats: Record<string, any>;
}

export interface BowlerDetailResponse {
  player_id: number;
  player_name: string;
  match_format: MatchFormat;
  ranking: BowlerRankingItem;
  methodology_weights: Record<string, number>;
  scenarios: Record<string, number | null>;
  accounting_sensitivity?: Record<string, any> | null;
  raw_stats: Record<string, any>;
}

export interface PressureSummaryResponse {
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

export interface MatchItem {
  match_id: number;
  comp_id?: number;
  comp_name?: string;
  match_format?: MatchFormat;
  season?: string;
  match_date?: string;
  stage?: string;
  venue_id?: number;
  venue_country?: string;
  home_team?: string;
  away_team?: string;
  toss_win_team_id?: number;
  toss_opted?: string;
  result?: string;
  win_team_id?: number;
  man_of_the_match?: string;
  has_ball_data?: boolean;
}

export interface OverSummary {
  innings: number;
  overid: number;
  runs_in_over: number;
  wickets_in_over: number;
  end_score: number;
  end_wickets: number;
  predominant_pressure: string;
  innings_phase: string;
}

export interface PressureTimelineDelivery {
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
}

export interface MatchPressureTimelineResponse {
  match_id: number;
  home_team?: string;
  away_team?: string;
  match_format?: MatchFormat;
  total_pressure_balls: number;
  overs: OverSummary[];
  deliveries: PressureTimelineDelivery[];
}

export interface MetricComparisonRow {
  metric_key: string;
  metric_label: string;
  higher_is_better: boolean;
  values: Record<string, number | null>;
  percentiles: Record<string, number | null>;
  leader_player_id?: number | null;
}

export interface PlayerComparisonResponse {
  player_type: 'Batter' | 'Bowler';
  format: MatchFormat;
  player_ids: number[];
  players: any[];
  metric_matrix: MetricComparisonRow[];
}

export interface MethodologyResponse {
  title: string;
  season: string;
  round: string;
  competition_segmentation: string;
  pressure_definition: string;
  eligibility_thresholds: Record<string, any>;
  batter_baseline_weights: Record<string, number>;
  bowler_baseline_weights: Record<string, number>;
  scoring_directions: Record<string, Record<string, string>>;
  consistency_formulas: Record<string, string>;
  wicket_credit_rules: Record<string, string[]>;
  extras_accounting_scenarios: Record<string, string>;
  alternative_weight_scenarios: Record<string, any>;
  project_assumptions_and_limitations: string[];
}

export interface AuditCheckItem {
  audit_name: string;
  category: string;
  status: 'PASS' | 'WARNING' | 'NOT VERIFIED';
  description: string;
  records_checked: number;
  findings: string;
  action_taken: string;
}

export interface AuditSummaryResponse {
  total_audits: number;
  passed_count: number;
  warning_count: number;
  not_verified_count: number;
  overall_health: string;
  audits: AuditCheckItem[];
}
