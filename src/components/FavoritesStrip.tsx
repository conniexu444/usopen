import { Badge } from "@/components/ui/badge";
import { formatOdds, seedLabel } from "@/lib/utils";
import type { Player } from "@/lib/types";

export function FavoritesStrip({ players }: { players: Player[] }) {
  const favorites = players
    .filter((p) => p.status !== "eliminated")
    .slice(0, 6);

  return (
    <section className="overflow-x-auto">
      <div className="flex min-w-max gap-2 pb-1">
        {favorites.map((player, i) => (
          <article
            key={player.id}
            className="w-[148px] shrink-0 rounded-2xl border border-white/10 bg-white/5 p-3"
          >
            <div className="flex items-center justify-between gap-2">
              <Badge>#{i + 1}</Badge>
              <span className="font-display text-lg font-semibold text-lime">
                {formatOdds(player.titleOdds)}
              </span>
            </div>
            <p className="mt-2 truncate text-sm font-medium">{player.name}</p>
            <p className="truncate text-xs text-paper/55">
              {seedLabel(player)} · {player.country ?? "—"}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
