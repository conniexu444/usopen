import { Badge } from "@/components/ui/badge";
import { dash, formatOdds, gsLabel, seedLabel, statusLabel } from "@/lib/utils";
import type { Player } from "@/lib/types";

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[10px] uppercase tracking-[0.14em] text-paper/45">{label}</p>
      <p className="mt-0.5 text-sm text-paper/90">{value}</p>
    </div>
  );
}

export function PlayerRow({
  player,
  rank,
  open,
  onToggle,
}: {
  player: Player;
  rank: number;
  open: boolean;
  onToggle: () => void;
}) {
  const eliminated = player.status === "eliminated";
  const titles = player.snapshot.titles.length
    ? player.snapshot.titles.join(" · ")
    : "—";

  return (
    <article
      className={`rounded-2xl border border-white/10 bg-white/[0.04] ${eliminated ? "opacity-55" : ""}`}
    >
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-start gap-3 px-3 py-3 text-left sm:px-4"
      >
        <span className="w-7 shrink-0 pt-0.5 text-xs text-paper/40">{rank}</span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-medium leading-tight">{player.name}</h3>
            <Badge>{seedLabel(player)}</Badge>
          </div>
          <p className="mt-1 text-xs text-paper/55">
            {dash(player.country)} · rank {dash(player.rank)} · age {dash(player.age)}
          </p>
          <p className="mt-1 text-xs text-paper/70">
            {statusLabel(player.status)}
            {player.nextOpponent ? ` · next: ${player.nextOpponent}` : ""}
          </p>
        </div>
        <div className="shrink-0 text-right">
          <p className="font-display text-xl font-semibold text-lime sm:text-2xl">
            {formatOdds(player.titleOdds)}
          </p>
          <p className="text-[10px] uppercase tracking-[0.12em] text-paper/40">title</p>
        </div>
      </button>
      {open ? (
        <div className="grid gap-3 border-t border-white/8 px-3 py-3 sm:grid-cols-2 sm:px-4">
          <Stat label="Last 12 months W/L" value={dash(player.snapshot.wlOverall)} />
          <Stat label="Hard-court W/L" value={dash(player.snapshot.wlHard)} />
          <Stat label="Notable titles" value={titles} />
          <Stat label="2025 US Open" value={gsLabel(player.snapshot.uso2025)} />
          <Stat label="2026 Australian Open" value={gsLabel(player.snapshot.ao2026)} />
          <Stat label="2026 Roland Garros" value={gsLabel(player.snapshot.rg2026)} />
          <Stat label="2026 Wimbledon" value={gsLabel(player.snapshot.wimbledon2026)} />
          <div className="sm:col-span-2">
            <p className="text-[10px] uppercase tracking-[0.14em] text-paper/45">Notes</p>
            <p className="mt-0.5 text-sm leading-relaxed text-paper/85">
              {player.snapshot.notes || "—"}
            </p>
          </div>
        </div>
      ) : null}
    </article>
  );
}
