import { useEffect, useMemo, useState } from "react";
import { AboutPanel } from "@/components/AboutPanel";
import { FavoritesStrip } from "@/components/FavoritesStrip";
import { PlayerRow } from "@/components/PlayerRow";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { DrawCatalog, Player } from "@/lib/types";

type DrawTab = "men" | "women";

async function loadDraw(tab: DrawTab): Promise<DrawCatalog> {
  const res = await fetch(`/data/${tab}.json`);
  if (!res.ok) throw new Error(`Could not load ${tab} catalog`);
  return res.json() as Promise<DrawCatalog>;
}

export default function App() {
  const [tab, setTab] = useState<DrawTab>("men");
  const [query, setQuery] = useState("");
  const [catalog, setCatalog] = useState<DrawCatalog | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [openId, setOpenId] = useState<string | null>(null);
  const [showAbout, setShowAbout] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    loadDraw(tab)
      .then((data) => {
        if (!cancelled) setCatalog(data);
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Load failed");
      });
    return () => {
      cancelled = true;
    };
  }, [tab]);

  const filtered: Player[] = useMemo(() => {
    if (!catalog) return [];
    const q = query.trim().toLowerCase();
    if (!q) return catalog.players;
    return catalog.players.filter((p) => p.name.toLowerCase().includes(q));
  }, [catalog, query]);

  return (
    <div className="desk-grid min-h-dvh">
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-5 px-4 py-6 sm:py-8">
        <header>
          <p className="text-[11px] uppercase tracking-[0.22em] text-lime">
            Connie Xu · Flushing Meadows
          </p>
          <h1 className="mt-2 font-display text-4xl leading-none text-paper sm:text-5xl">
            US Open 2026 desk
          </h1>
          <p className="mt-3 max-w-xl text-sm text-paper/70">
            Men’s and women’s singles, all 128. Sorted by title-win percent. Form-weighted, last
            12 months, hard-court bump, not betting odds.
          </p>
        </header>

        <Tabs>
          <div className="flex flex-wrap items-center gap-3">
            <TabsList>
              <TabsTrigger active={tab === "men"} onClick={() => setTab("men")}>
                Men’s singles
              </TabsTrigger>
              <TabsTrigger active={tab === "women"} onClick={() => setTab("women")}>
                Women’s singles
              </TabsTrigger>
            </TabsList>
            <Button variant="ghost" size="sm" onClick={() => setShowAbout((v) => !v)}>
              {showAbout ? "Hide about" : "About the model"}
            </Button>
          </div>
        </Tabs>

        {catalog ? (
          <>
            <FavoritesStrip players={catalog.players} />
            {showAbout ? <AboutPanel catalog={catalog} /> : null}
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by name"
              aria-label="Search by name"
            />
            <p className="text-xs text-paper/45">
              {filtered.length} of 128 · rankings of Mon Aug 24, 2026 · {catalog.modelNote}
            </p>
            <div className="flex flex-col gap-2">
              {filtered.map((player, i) => (
                <PlayerRow
                  key={player.id}
                  player={player}
                  rank={query ? i + 1 : catalog.players.indexOf(player) + 1}
                  open={openId === player.id}
                  onToggle={() => setOpenId((id) => (id === player.id ? null : player.id))}
                />
              ))}
            </div>
          </>
        ) : (
          <p className="text-sm text-paper/60">{error ?? "Loading the draw…"}</p>
        )}
      </div>
    </div>
  );
}
