# Frontend Integration Guide – SupeRR Selector

This directory contains everything required to connect your Lovable React / Vite dashboard to the live FastAPI Python backend.

---

## 1. Setup Environment Variable in Frontend

In your React/Vite root directory, add or update `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 2. Integration Files

| File | Purpose |
|------|---------|
| `apiClient.ts` | Centralized typed HTTP client with error handling & query param serialization |
| `types.ts` | TypeScript interfaces for all cricket analytics endpoints |
| `useCricketData.ts` | Ready-to-use React hooks with loading, error, and empty states |

---

## 3. Quickstart Examples

### A. Fetch Overview Dashboard Stats
```tsx
import { useOverview } from '@/services/useCricketData';

export function OverviewWidget() {
  const { data, loading, error } = useOverview();

  if (loading) return <div>Loading cricket intelligence...</div>;
  if (error) return <div>Error loading data: {error}</div>;

  return (
    <div>
      <h3>Total Matches: {data?.total_matches}</h3>
      <p>Pressure Deliveries: {data?.total_pressure_deliveries}</p>
      <p>T20 Matches: {data?.match_counts.T20} | T20I: {data?.match_counts.T20I}</p>
    </div>
  );
}
```

### B. Format-Switched Top 10 Leaderboard
```tsx
import { useState } from 'react';
import { useTop10Batters } from '@/services/useCricketData';

export function Top10Leaderboard() {
  const [format, setFormat] = useState<'T20' | 'T20I'>('T20');
  const { data: batters, loading } = useTop10Batters(format);

  return (
    <div>
      <div className="flex gap-2">
        <button onClick={() => setFormat('T20')}>T20 (IPL)</button>
        <button onClick={() => setFormat('T20I')}>T20 International</button>
      </div>

      {loading ? (
        <p>Updating Top 10 rankings...</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Player</th>
              <th>Score</th>
              <th>Strike Rate</th>
            </tr>
          </thead>
          <tbody>
            {batters?.map((b) => (
              <tr key={b.striker_id}>
                <td>#{b.final_rank}</td>
                <td>{b.striker_name}</td>
                <td>{b.final_score.toFixed(2)}</td>
                <td>{b.pressure_strike_rate.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
```

### C. Player Comparison
```tsx
import { usePlayerComparison } from '@/services/useCricketData';

export function CompareWidget({ playerIds, format }: { playerIds: number[]; format: 'T20' | 'T20I' }) {
  const { data, loading } = usePlayerComparison('Batter', playerIds, format);

  if (loading) return <div>Comparing metrics...</div>;
  if (!data) return <div>Select players to compare.</div>;

  return (
    <div>
      <h4>Head-to-Head Comparison ({format})</h4>
      {data.metric_matrix.map((row) => (
        <div key={row.metric_key} className="flex justify-between py-1">
          <span>{row.metric_label}</span>
          <span>Leader: #{row.leader_player_id}</span>
        </div>
      ))}
    </div>
  );
}
```
