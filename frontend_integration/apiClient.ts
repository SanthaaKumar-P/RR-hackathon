/**
 * SupeRR Selector – Centralized API Client
 * Connects the Lovable React frontend directly to the FastAPI analytical engine.
 */

import {
  OverviewResponse,
  BatterRankingItem,
  BowlerRankingItem,
  PaginatedList,
  BatterDetailResponse,
  BowlerDetailResponse,
  PressureSummaryResponse,
  PressureCategoryItem,
  PressurePhaseItem,
  MatchItem,
  MatchPressureTimelineResponse,
  PlayerComparisonResponse,
  MethodologyResponse,
  AuditSummaryResponse,
  HealthResponse,
  MatchFormat
} from './types';

// Reads from Vite environment variable or defaults to local FastAPI server
const BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_BASE_URL)
  ? import.meta.env.VITE_API_BASE_URL
  : 'http://localhost:8000/api/v1';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  private async request<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    let url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;

    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, val]) => {
        if (val !== undefined && val !== null && val !== '') {
          searchParams.append(key, String(val));
        }
      });
      const queryString = searchParams.toString();
      if (queryString) {
        url += (url.includes('?') ? '&' : '?') + queryString;
      }
    }

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        let errorData: any;
        try {
          errorData = await response.json();
        } catch {
          errorData = { detail: response.statusText };
        }
        throw new Error(errorData.detail || errorData.message || `Request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (err: any) {
      console.error(`[ApiClient Error] ${url}:`, err.message);
      throw err;
    }
  }

  // Health
  public async getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  // Overview
  public async getOverview(): Promise<OverviewResponse> {
    return this.request<OverviewResponse>('/overview');
  }

  // Batters
  public async getBatters(params?: {
    format?: MatchFormat;
    search?: string;
    eligible?: boolean;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
    page?: number;
    limit?: number;
  }): Promise<PaginatedList<BatterRankingItem>> {
    return this.request<PaginatedList<BatterRankingItem>>('/batters', params);
  }

  public async getTop10Batters(format: MatchFormat = 'T20'): Promise<{ format: MatchFormat; count: number; items: BatterRankingItem[] }> {
    return this.request('/batters/top10', { format });
  }

  public async getBatterById(playerId: number, format?: MatchFormat): Promise<BatterDetailResponse> {
    return this.request<BatterDetailResponse>(`/batters/${playerId}`, { format });
  }

  // Bowlers
  public async getBowlers(params?: {
    format?: MatchFormat;
    search?: string;
    eligible?: boolean;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
    page?: number;
    limit?: number;
  }): Promise<PaginatedList<BowlerRankingItem>> {
    return this.request<PaginatedList<BowlerRankingItem>>('/bowlers', params);
  }

  public async getTop10Bowlers(format: MatchFormat = 'T20'): Promise<{ format: MatchFormat; count: number; items: BowlerRankingItem[] }> {
    return this.request('/bowlers/top10', { format });
  }

  public async getBowlerById(playerId: number, format?: MatchFormat): Promise<BowlerDetailResponse> {
    return this.request<BowlerDetailResponse>(`/bowlers/${playerId}`, { format });
  }

  // Pressure Analytics
  public async getPressureSummary(format?: MatchFormat): Promise<PressureSummaryResponse> {
    return this.request<PressureSummaryResponse>('/pressure/summary', { format });
  }

  public async getPressureCategories(): Promise<PressureCategoryItem[]> {
    return this.request<PressureCategoryItem[]>('/pressure/categories');
  }

  public async getPressurePhases(): Promise<PressurePhaseItem[]> {
    return this.request<PressurePhaseItem[]>('/pressure/phases');
  }

  public async getBatterPressurePerformance(params?: { search?: string; page?: number; limit?: number }) {
    return this.request('/pressure/batter-performance', params);
  }

  public async getBowlerPressurePerformance(params?: { search?: string; page?: number; limit?: number }) {
    return this.request('/pressure/bowler-performance', params);
  }

  // Matches
  public async getMatches(params?: {
    format?: MatchFormat;
    season?: string;
    stage?: string;
    team?: string;
    search?: string;
    page?: number;
    limit?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }): Promise<PaginatedList<MatchItem>> {
    return this.request<PaginatedList<MatchItem>>('/matches', params);
  }

  public async getMatchById(matchId: number): Promise<MatchItem> {
    return this.request<MatchItem>(`/matches/${matchId}`);
  }

  public async getMatchInnings(matchId: number): Promise<any[]> {
    return this.request(`/matches/${matchId}/innings`);
  }

  public async getMatchPressureTimeline(matchId: number): Promise<MatchPressureTimelineResponse> {
    return this.request<MatchPressureTimelineResponse>(`/matches/${matchId}/pressure-timeline`);
  }

  // Comparison
  public async compareBatters(playerIds: number[], format: MatchFormat = 'T20'): Promise<PlayerComparisonResponse> {
    return this.request<PlayerComparisonResponse>('/compare/batters', {
      player_ids: playerIds.join(','),
      format
    });
  }

  public async compareBowlers(playerIds: number[], format: MatchFormat = 'T20'): Promise<PlayerComparisonResponse> {
    return this.request<PlayerComparisonResponse>('/compare/bowlers', {
      player_ids: playerIds.join(','),
      format
    });
  }

  // Methodology
  public async getMethodology(): Promise<MethodologyResponse> {
    return this.request<MethodologyResponse>('/methodology');
  }

  // Scenarios
  public async getBatterScenarios(format: MatchFormat = 'T20'): Promise<any> {
    return this.request('/scenarios/batters', { format });
  }

  public async getBowlerScenarios(format: MatchFormat = 'T20'): Promise<any> {
    return this.request('/scenarios/bowlers', { format });
  }

  // Audit
  public async getAuditSummary(): Promise<AuditSummaryResponse> {
    return this.request<AuditSummaryResponse>('/audit/summary');
  }

  public async getDataQuality(): Promise<any> {
    return this.request('/audit/data-quality');
  }
}

export const apiClient = new ApiClient();
export default apiClient;
