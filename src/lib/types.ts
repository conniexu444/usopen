export type PlayerStatus = "still_in" | "eliminated" | "not_yet_played";
export type EntryCode = "Q" | "WC" | "LL" | "PR";

export interface PlayerSnapshot {
  wlOverall: string | null;
  wlHard: string | null;
  titles: string[];
  uso2025: string | null;
  ao2026: string | null;
  rg2026: string | null;
  wimbledon2026: string | null;
  notes: string;
}

export interface Player {
  id: string;
  name: string;
  country: string | null;
  countryCode: string | null;
  seed: number | null;
  entry: EntryCode | null;
  age: number | null;
  rank: number | null;
  rankPoints: number | null;
  status: PlayerStatus;
  nextOpponent: string | null;
  r1Opponent: string | null;
  slot: number;
  titleOdds: number;
  snapshot: PlayerSnapshot;
}

export interface DrawCatalog {
  draw: "men" | "women";
  event: string;
  generatedAt: string;
  rankingsDate: string;
  modelNote: string;
  sources: string[];
  players: Player[];
}
