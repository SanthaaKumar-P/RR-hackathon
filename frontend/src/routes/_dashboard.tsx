import { Link, Outlet, createFileRoute, useRouterState } from "@tanstack/react-router";
import { useEffect, useMemo, useState, createContext, useContext, type ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bell,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CircleHelp,
  GitCompareArrows,
  LayoutDashboard,
  Menu,
  Moon,
  Search,
  ShieldCheck,
  Sun,
  Target,
  Users,
  X,
  Zap,
  CheckCircle2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiBaseUrl } from "@/lib/analytics-api";

export const Route = createFileRoute("/_dashboard")({ component: DashboardLayout });

const navigation = [
  { label: "Overview", to: "/", icon: LayoutDashboard, group: "Workspace" },
  { label: "Batter intelligence", to: "/batters", icon: Target, group: "Intelligence" },
  { label: "Bowler intelligence", to: "/bowlers", icon: Activity, group: "Intelligence" },
  { label: "Pressure analytics", to: "/pressure", icon: Zap, group: "Intelligence" },
  { label: "Match insights", to: "/matches", icon: BarChart3, group: "Workspace" },
  { label: "Player comparison", to: "/comparison", icon: GitCompareArrows, group: "Workspace" },
  { label: "Ranking methodology", to: "/methodology", icon: CircleHelp, group: "Governance" },
  { label: "Scenario analysis", to: "/scenarios", icon: Activity, group: "Governance" },
  { label: "Audit & data quality", to: "/audit", icon: ShieldCheck, group: "Governance" },
] as const;

import {
  DashboardContext,
  type Format,
  SectionHeader,
  Surface,
  useDashboard,
} from "@/lib/dashboard-context";

export { SectionHeader, Surface, useDashboard };

function DashboardLayout() {
  const currentPath = useRouterState({ select: (state) => state.location.pathname });
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [format, setFormat] = useState<Format>("T20");
  const [search, setSearch] = useState("");
  const [dark, setDark] = useState(false);
  const [notice, setNotice] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [backendConnected, setBackendConnected] = useState(true);
  const active = navigation.find((item) => item.to === currentPath) ?? navigation[0];

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  // Ping backend health
  useEffect(() => {
    let isMounted = true;
    fetch(`${apiBaseUrl.replace(/\/+$/, "")}/health`)
      .then((res) => res.json())
      .then((data) => {
        if (isMounted) setBackendConnected(data.status === "ok");
      })
      .catch(() => {
        if (isMounted) setBackendConnected(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const groups = useMemo(() => [...new Set(navigation.map((item) => item.group))], []);

  const aside = (
    <aside
      className={`flex h-full min-h-0 flex-col bg-sidebar text-sidebar-foreground transition-[width,transform] duration-200 ${collapsed ? "w-[76px]" : "w-[254px]"}`}
    >
      <div className="flex h-[72px] shrink-0 items-center gap-3 border-b border-sidebar-border px-5">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-rr-pink text-rr-pink-foreground shadow-sm shadow-rr-pink/30">
          <Zap className="h-[19px] w-[19px]" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="truncate text-[14px] font-extrabold tracking-[0.02em]">
              SupeRR <span className="text-rr-pink">Selector</span>
            </p>
            <p className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.08em] text-sidebar-foreground/50">
              Cricket Intelligence
            </p>
          </div>
        )}
        <Button
          className="ml-auto md:hidden"
          variant="ghost"
          size="icon"
          aria-label="Close navigation"
          onClick={() => setMobileOpen(false)}
        >
          <X />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-5">
        {groups.map((group) => (
          <div key={group} className="mb-6">
            {!collapsed && (
              <p className="mb-2 px-3 text-[10px] font-bold uppercase tracking-[0.12em] text-sidebar-foreground/45">
                {group}
              </p>
            )}
            <nav aria-label={group} className="space-y-1">
              {navigation
                .filter((item) => item.group === group)
                .map((item) => {
                  const Icon = item.icon;
                  const selected = active.to === item.to;
                  return (
                    <Link
                      key={item.to}
                      to={item.to}
                      onClick={() => setMobileOpen(false)}
                      title={collapsed ? item.label : undefined}
                      aria-current={selected ? "page" : undefined}
                      className={`group flex h-10 items-center gap-3 rounded-md px-3 text-[12px] font-semibold transition-colors ${selected ? "bg-sidebar-accent text-sidebar-accent-foreground shadow-sm" : "text-sidebar-foreground/65 hover:bg-sidebar-accent/70 hover:text-sidebar-foreground"}`}
                    >
                      <Icon
                        className={`h-[17px] w-[17px] shrink-0 ${selected ? "text-rr-pink" : ""}`}
                        strokeWidth={1.8}
                      />
                      {!collapsed && <span className="truncate">{item.label}</span>}
                      {!collapsed && selected && (
                        <span className="ml-auto h-1.5 w-1.5 rounded-full bg-rr-pink" />
                      )}
                    </Link>
                  );
                })}
            </nav>
          </div>
        ))}
      </div>

      {!collapsed && (
        <div className="m-3 rounded-md border border-sidebar-border bg-sidebar-accent/60 p-3">
          <div className="flex items-center gap-2">
            <span
              className={`h-2 w-2 rounded-full ${backendConnected ? "bg-success animate-pulse" : "bg-amber"}`}
            />
            <span className="text-[11px] font-semibold">
              {backendConnected ? "Live Analytics Active" : "Backend Connecting"}
            </span>
          </div>
          <p className="mt-1.5 pl-4 text-[10px] leading-relaxed text-sidebar-foreground/65">
            {backendConnected
              ? "853 matches · 103,976 pressure balls"
              : "Connecting to port 8000..."}
          </p>
        </div>
      )}

      <div className="flex h-14 shrink-0 items-center justify-between border-t border-sidebar-border px-3">
        {!collapsed && (
          <span className="px-2 text-[10px] font-semibold tracking-wider text-sidebar-foreground/45">
            SEASON 2 · ROUND 1
          </span>
        )}
        <Button
          aria-label={collapsed ? "Expand navigation" : "Collapse navigation"}
          title={collapsed ? "Expand navigation" : "Collapse navigation"}
          onClick={() => setCollapsed(!collapsed)}
          variant="ghost"
          size="icon"
          className="text-sidebar-foreground/70 hover:text-sidebar-foreground"
        >
          <ChevronLeft
            className={`h-4 w-4 transition-transform ${collapsed ? "rotate-180" : ""}`}
          />
        </Button>
      </div>
    </aside>
  );

  return (
    <DashboardContext.Provider value={{ format, setFormat, search, setSearch, backendConnected }}>
      <div className="min-h-screen bg-background text-foreground font-sans">
        <div className="fixed inset-y-0 left-0 z-30 hidden md:block">{aside}</div>
        {mobileOpen && (
          <div
            className="fixed inset-0 z-40 bg-foreground/30 md:hidden"
            onClick={() => setMobileOpen(false)}
          >
            <div
              className="h-full w-[min(82vw,280px)]"
              onClick={(event) => event.stopPropagation()}
            >
              {aside}
            </div>
          </div>
        )}
        <div
          className={`min-h-screen transition-[padding] duration-200 ${collapsed ? "md:pl-[76px]" : "md:pl-[254px]"}`}
        >
          <header className="sticky top-0 z-20 flex h-[68px] items-center gap-3 border-b border-border bg-card/95 px-4 backdrop-blur-sm sm:px-6 lg:px-8">
            <Button
              aria-label="Open navigation"
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setMobileOpen(true)}
            >
              <Menu />
            </Button>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                <span className="font-semibold text-rr-pink">Rajasthan Royals</span>
                <ChevronRight className="h-3 w-3" />
                <span className="truncate font-semibold text-foreground">{active.label}</span>
              </div>
              <div className="mt-0.5 hidden text-[10px] text-muted-foreground sm:block">
                SupeRR Selector <span className="mx-1">/</span> Season 2{" "}
                <span className="mx-1">/</span> Round 1
              </div>
            </div>

            {/* Quick Search */}
            <div className="relative hidden w-[clamp(160px,22vw,280px)] lg:block">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                aria-label="Search players and matches"
                placeholder="Search players, matches…"
                className="h-9 border-border bg-background pl-9 pr-8 text-[12px]"
              />
              {search && (
                <button
                  onClick={() => setSearch("")}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-muted-foreground hover:text-foreground"
                >
                  ✕
                </button>
              )}
            </div>

            {/* Format Switcher */}
            <div
              aria-label="Select cricket format"
              className="flex h-9 shrink-0 items-center rounded-lg border border-border bg-background p-0.5 shadow-xs"
            >
              {(["T20", "T20I"] as const).map((item) => (
                <Button
                  key={item}
                  aria-pressed={format === item}
                  variant="ghost"
                  onClick={() => setFormat(item)}
                  className={`h-7 rounded-md px-3 text-[11px] font-extrabold tracking-wide transition-all ${format === item ? "bg-primary text-primary-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"}`}
                >
                  {item === "T20" ? "T20 (IPL)" : "T20I"}
                </Button>
              ))}
            </div>

            {/* Theme Toggle */}
            <Button
              aria-label={dark ? "Switch to light theme" : "Switch to dark theme"}
              title={dark ? "Light theme" : "Dark theme"}
              variant="ghost"
              size="icon"
              className="hidden shrink-0 sm:inline-flex"
              onClick={() => setDark(!dark)}
            >
              {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>

            {/* Notification Bell */}
            <div className="relative">
              <Button
                aria-label="Notifications"
                title="Notifications"
                variant="ghost"
                size="icon"
                onClick={() => setNotice(!notice)}
              >
                <Bell className="h-4 w-4" />
                <span className="absolute right-2 top-1.5 h-1.5 w-1.5 rounded-full bg-rr-pink" />
              </Button>
              {notice && (
                <div className="absolute right-0 top-11 z-50 w-72 rounded-lg border border-border bg-card p-4 shadow-xl">
                  <p className="text-[12px] font-bold">Workspace Status</p>
                  <p className="mt-2 text-[11px] leading-relaxed text-muted-foreground">
                    Analytical backend running on{" "}
                    <code className="text-primary font-mono">{apiBaseUrl}</code>. All 853 matches
                    and 103,976 pressure deliveries verified.
                  </p>
                </div>
              )}
            </div>

            {/* Analyst Profile */}
            <div className="relative">
              <Button
                variant="ghost"
                className="h-9 gap-2 px-2"
                aria-label="Analyst profile"
                onClick={() => setProfileOpen(!profileOpen)}
              >
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-rr-pink/15 text-[11px] font-black text-rr-pink">
                  RR
                </span>
                <span className="hidden text-[11px] font-bold sm:inline">Lead Analyst</span>
                <ChevronDown className="hidden h-3.5 w-3.5 sm:block opacity-60" />
              </Button>
              {profileOpen && (
                <div className="absolute right-0 top-11 z-50 w-52 rounded-lg border border-border bg-card p-3 shadow-xl">
                  <div className="px-2 py-1 text-[11px] font-bold">Rajasthan Royals Analytics</div>
                  <div className="px-2 py-1 text-[10px] text-muted-foreground">
                    SupeRR Selector · Round 1
                  </div>
                  <div className="mt-2 border-t border-border pt-2 px-2 text-[10px] text-muted-foreground">
                    Target Format: <strong className="text-foreground">{format}</strong>
                  </div>
                </div>
              )}
            </div>
          </header>

          <main className="mx-auto w-full max-w-[1560px] p-4 sm:p-6 lg:p-8">
            <Outlet />
          </main>

          <footer className="border-t border-border px-6 py-4 text-center text-[10px] font-medium text-muted-foreground">
            SUPERR SELECTOR <span className="mx-2">·</span> Season 2 · Round 1{" "}
            <span className="mx-2">·</span> Rajasthan Royals Analytical Intelligence Platform
          </footer>
        </div>
      </div>
    </DashboardContext.Provider>
  );
}
