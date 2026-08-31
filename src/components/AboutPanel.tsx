import type { DrawCatalog } from "@/lib/types";

export function AboutPanel({ catalog }: { catalog: DrawCatalog }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.04] p-5 text-sm leading-relaxed text-paper/80">
      <h2 className="font-display text-2xl text-paper">How this desk works</h2>
      <p className="mt-3">
        Title-win percents are a <strong className="font-medium text-paper">form-weighted model</strong>,
        not betting odds and not ATP/WTA Elo. Each player starts from the ranking points published
        Monday 24 August 2026 — the list used to seed the US Open draws. Last-12-month Grand Slam
        results are layered on top, with a hard-court bump for the 2025 US Open and 2026 Australian
        Open. Roland Garros and Wimbledon count, but less. Recent fitness flags (Alcaraz’s wrist
        layoff, Rybakina’s Cincinnati retirement) trim the rating. The model then walks the actual
        128-player bracket.
      </p>
      <p className="mt-3">
        Eliminated players sit at <strong className="font-medium text-paper">0%</strong>. Remaining
        mass is renormalized so each singles draw sums to 100%. Missing W/L records and other
        unpublished stats show an em dash rather than a guess.
      </p>
      <p className="mt-3">
        One-line model note: <span className="text-lime">{catalog.modelNote}</span>
      </p>
      <p className="mt-3 text-xs text-paper/50">
        Rankings date {catalog.rankingsDate}. Snapshot generated {catalog.generatedAt}. Women’s
        final 12 September; men’s final 13 September. Jannik Sinner withdrew with a right-knee
        injury and is not in the men’s draw.
      </p>
      <ul className="mt-3 list-disc space-y-1 pl-5 text-xs text-paper/50">
        {catalog.sources.map((source) => (
          <li key={source}>{source}</li>
        ))}
      </ul>
    </section>
  );
}
