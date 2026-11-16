import { useState, useEffect, useCallback } from 'react';
import apiClient from './apiClient';
import {
  OverviewResponse,
  BatterRankingItem,
  BowlerRankingItem,
  PaginatedList,
  MatchFormat,
  MatchPressureTimelineResponse,
  PlayerComparisonResponse
} from './types';

// State interface
export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  isEmpty: boolean;
  refetch: () => void;
}

/** Hook for Overview Dashboard statistics */
export function useOverview(): AsyncState<OverviewResponse> {
  const [data, setData] = useState<OverviewResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOverview = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.getOverview();
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch overview analytics');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOverview();
  }, [fetchOverview]);

  return {
    data,
    loading,
    error,
    isEmpty: !loading && !error && data === null,
    refetch: fetchOverview
  };
}

/** Hook for Batter Rankings with search, sort, pagination */
export function useBatters(params: {
  format?: MatchFormat;
  search?: string;
  eligible?: boolean;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}): AsyncState<PaginatedList<BatterRankingItem>> {
  const [data, setData] = useState<PaginatedList<BatterRankingItem> | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBatters = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.getBatters(params);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch batters');
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => {
    fetchBatters();
  }, [fetchBatters]);

  return {
    data,
    loading,
    error,
    isEmpty: !loading && !error && (!data || data.items.length === 0),
    refetch: fetchBatters
  };
}

/** Hook for Top 10 Batters (switches seamlessly between T20 and T20I) */
export function useTop10Batters(format: MatchFormat = 'T20'): AsyncState<BatterRankingItem[]> {
  const [data, setData] = useState<BatterRankingItem[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTop10 = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.getTop10Batters(format);
      setData(res.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load top 10 batters');
    } finally {
      setLoading(false);
    }
  }, [format]);

  useEffect(() => {
    fetchTop10();
  }, [fetchTop10]);

  return {
    data,
    loading,
    error,
    isEmpty: !loading && !error && (!data || data.length === 0),
    refetch: fetchTop10
  };
}

/** Hook for Bowler Rankings with search, sort, pagination */
export function useBowlers(params: {
  format?: MatchFormat;
  search?: string;
  eligible?: boolean;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}): AsyncState<PaginatedList<BowlerRankingItem>> {
  const [data, setData] = useState<PaginatedList<BowlerRankingItem> | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBowlers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.getBowlers(params);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch bowlers');
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => {
    fetchBowlers();
  }, [fetchBowlers]);

  return {
    data,
    loading,
    error,
    isEmpty: !loading && !error && (!data || data.items.length === 0),
    refetch: fetchBowlers
  };
}

/** Hook for Top 10 Bowlers */
export function useTop10Bowlers(format: MatchFormat = 'T20'): AsyncState<BowlerRankingItem[]> {
  const [data, setData] = useState<BowlerRankingItem[] | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTop10 = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.getTop10Bowlers(format);
      setData(res.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load top 10 bowlers');
    } finally {
      setLoading(false);
    }
  }, [format]);

  useEffect(() => {
    fetchTop10();
  }, [fetchTop10]);

  return {
    data,
    loading,
    error,
    isEmpty: !loading && !error && (!data || data.length === 0),
    refetch: fetchTop10
  };
}

/** Hook for Player Comparison */
export function usePlayerComparison(
  playerType: 'Batter' | 'Bowler',
  playerIds: number[],
  format: MatchFormat = 'T20'
): AsyncState<PlayerComparisonResponse> {
  const [data, setData] = useState<PlayerComparisonResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchComparison = useCallback(async () => {
    if (!playerIds || playerIds.length === 0) {
      setData(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = (playerType === 'Batter')
        ? await apiClient.compareBatters(playerIds, format)
        : await apiClient.compareBowlers(playerIds, format);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Comparison failed');
    } finally {
      setLoading(false);
    }
  }, [playerType, playerIds.join(','), format]);

  useEffect(() => {
    fetchComparison();
  }, [fetchComparison]);

  return {
    data,
    loading,
    error,
    isEmpty: !loading && !error && (!data || data.players.length === 0),
    refetch: fetchComparison
  };
}

/** Hook for Match Pressure Timeline */
export function usePressureTimeline(matchId: number): AsyncState<MatchPressureTimelineResponse> {
  const [data, setData] = useState<MatchPressureTimelineResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTimeline = useCallback(async () => {
    if (!matchId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.getMatchPressureTimeline(matchId);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load match pressure timeline');
    } finally {
      setLoading(false);
    }
  }, [matchId]);

  useEffect(() => {
    fetchTimeline();
  }, [fetchTimeline]);

  return {
    data,
    loading,
    error,
    isEmpty: !loading && !error && data === null,
    refetch: fetchTimeline
  };
}
