export const BATTER_WEIGHTS = [
  { label: "Strike Rate", weight: 25 },
  { label: "Runs Per Match", weight: 20 },
  { label: "Runs Per Dismissal", weight: 15 },
  { label: "Dot Percentage", weight: 15 },
  { label: "Consistency", weight: 25 },
] as const;

export const BOWLER_WEIGHTS = [
  { label: "Wickets Per 100 Legal Balls", weight: 25 },
  { label: "Pressure Economy", weight: 20 },
  { label: "Pressure Dot Percentage", weight: 15 },
  { label: "Consistency", weight: 20 },
  { label: "Wickets Per Match", weight: 20 },
] as const;

export const eligibility = {
  batter: { pressureBalls: 100, pressureMatches: 10 },
  bowler: { pressureLegalBalls: 60, verifiedPressureMatches: 10 },
} as const;
