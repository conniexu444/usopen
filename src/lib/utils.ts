import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { Player } from "./types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function dash(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  return String(value);
}

export function seedLabel(player: Player): string {
  if (player.seed != null) return String(player.seed);
  if (player.entry) return player.entry;
  return "—";
}

export function statusLabel(status: Player["status"]): string {
  if (status === "still_in") return "Still in";
  if (status === "eliminated") return "Eliminated";
  return "Not yet played";
}

export function formatOdds(pct: number): string {
  if (pct === 0) return "0%";
  if (pct < 0.05) return "<0.05%";
  if (pct < 1) return `${pct.toFixed(2)}%`;
  return `${pct.toFixed(2)}%`;
}

export function gsLabel(code: string | null): string {
  return code ?? "—";
}
