import { createContext, useContext, type ReactNode } from "react";
import type { LucideIcon } from "lucide-react";

export type Format = "T20" | "T20I";

export type DashboardContextValue = {
  format: Format;
  setFormat: (format: Format) => void;
  search: string;
  setSearch: (search: string) => void;
  backendConnected: boolean;
};

export const defaultDashboardContext: DashboardContextValue = {
  format: "T20",
  setFormat: () => {},
  search: "",
  setSearch: () => {},
  backendConnected: true,
};

export const DashboardContext = createContext<DashboardContextValue>(defaultDashboardContext);

export function useDashboard(): DashboardContextValue {
  const context = useContext(DashboardContext);
  return context ?? defaultDashboardContext;
}

export function SectionHeader({
  eyebrow,
  title,
  description,
  icon: Icon,
}: {
  eyebrow: string;
  title: string;
  description: string;
  icon: LucideIcon;
}) {
  const { backendConnected } = useDashboard();
  return (
    <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
      <div>
        <div className="mb-2 flex items-center gap-2 text-[10px] font-extrabold uppercase tracking-[0.14em] text-rr-pink">
          <Icon className="h-3.5 w-3.5" />
          {eyebrow}
        </div>
        <h1 className="text-[26px] font-black leading-tight tracking-tight sm:text-[30px]">
          {title}
        </h1>
        <p className="mt-1.5 max-w-2xl text-[12px] leading-relaxed text-muted-foreground">
          {description}
        </p>
      </div>
      <div className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 shadow-xs">
        <span
          className={`h-2 w-2 rounded-full ${backendConnected ? "bg-success animate-pulse" : "bg-amber"}`}
        />
        <span className="text-[10px] font-bold text-foreground">
          {backendConnected ? "Verified Intelligence · Live" : "Connecting Backend"}
        </span>
      </div>
    </div>
  );
}

export function Surface({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <section
      className={`rounded-xl border border-border bg-card shadow-xs transition-shadow duration-200 hover:shadow-sm ${className}`}
    >
      {children}
    </section>
  );
}
