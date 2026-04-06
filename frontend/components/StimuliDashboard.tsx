"use client";

import { useDeferredValue, useState, useTransition } from "react";

export interface DashboardCollection {
  id: string;
  name: string;
  cardCount: number;
  subject?: string;
}

export interface PreviewCard {
  id?: string | number;
  prompt: string;
  insight: string;
}

interface StimuliDashboardProps {
  collections: DashboardCollection[];
  cards: PreviewCard[];
  isLoading?: boolean;
  initialText?: string;
  selectedCollectionId?: string;
  onCollectionSelect?: (collectionId: string) => void;
  onGenerate?: (text: string) => void;
}

export function StimuliDashboard({
  collections,
  cards,
  isLoading = false,
  initialText = "",
  selectedCollectionId,
  onCollectionSelect,
  onGenerate,
}: StimuliDashboardProps) {
  const [text, setText] = useState(initialText);
  const [isPending, startTransition] = useTransition();
  const deferredCards = useDeferredValue(cards);
  const busy = isLoading || isPending;

  return (
    <section className="min-h-screen bg-stone-950 px-4 py-6 text-stone-100 sm:px-6 lg:px-8">
      <div className="mx-auto grid max-w-7xl gap-4 lg:grid-cols-[280px_minmax(0,1fr)_420px]">
        <aside className="overflow-hidden rounded-[28px] border border-white/10 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.12),_transparent_45%),linear-gradient(180deg,#0f172a_0%,#111827_100%)] shadow-[0_30px_90px_rgba(2,8,23,0.45)]">
          <div className="border-b border-white/10 px-6 py-6">
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-sky-300/80">
              stimul.li
            </p>
            <h2 className="mt-3 text-2xl font-semibold text-white">My Collections</h2>
            <p className="mt-2 text-sm leading-6 text-slate-300">
              Organize teaching materials by course, unit, or grade level.
            </p>
          </div>

          <div className="space-y-3 p-4">
            {collections.map((collection) => {
              const selected = selectedCollectionId === collection.id;

              return (
                <button
                  key={collection.id}
                  type="button"
                  onClick={() => onCollectionSelect?.(collection.id)}
                  className={`w-full rounded-2xl border px-4 py-4 text-left transition ${
                    selected
                      ? "border-sky-400/50 bg-sky-400/10 shadow-[0_10px_30px_rgba(56,189,248,0.12)]"
                      : "border-white/8 bg-white/[0.03] hover:border-white/15 hover:bg-white/[0.05]"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="text-sm font-semibold text-white">{collection.name}</h3>
                      <p className="mt-1 text-xs uppercase tracking-[0.2em] text-slate-400">
                        {collection.subject ?? "General"}
                      </p>
                    </div>
                    <span className="rounded-full border border-white/10 bg-black/20 px-2.5 py-1 text-xs text-slate-300">
                      {collection.cardCount}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </aside>

        <main className="overflow-hidden rounded-[28px] border border-slate-200/70 bg-[linear-gradient(180deg,#fcfcfb_0%,#f4f1ea_100%)] text-slate-900 shadow-[0_30px_90px_rgba(15,23,42,0.12)]">
          <div className="border-b border-slate-200/80 px-6 py-6 sm:px-8">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-sky-800/70">
                  Input
                </p>
                <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">
                  Micro-Learning Studio
                </h1>
              </div>

              <button
                type="button"
                onClick={() => startTransition(() => onGenerate?.(text))}
                className="rounded-full bg-sky-800 px-5 py-3 text-sm font-semibold text-white shadow-[0_14px_30px_rgba(26,82,118,0.28)] transition hover:bg-sky-900 disabled:cursor-wait disabled:opacity-70"
                disabled={busy || !text.trim()}
              >
                {busy ? "Generating..." : "Generate Stimuli"}
              </button>
            </div>
          </div>

          <div className="px-6 py-6 sm:px-8">
            <label htmlFor="stimuli-input" className="mb-3 block text-sm font-semibold text-slate-700">
              Paste chapter text, lecture notes, or source material
            </label>
            <textarea
              id="stimuli-input"
              value={text}
              onChange={(event) => setText(event.target.value)}
              placeholder="Paste the lesson content here. stimul.li will extract high-signal prompts and insights for classroom review."
              className="min-h-[420px] w-full rounded-[24px] border border-slate-200 bg-white/90 px-5 py-4 text-base leading-7 text-slate-900 shadow-inner outline-none ring-0 placeholder:text-slate-400 focus:border-sky-400 focus:outline-none focus:ring-4 focus:ring-sky-100"
            />

            <div className="mt-4 flex flex-wrap gap-3 text-sm text-slate-500">
              <span className="rounded-full border border-slate-200 bg-white/80 px-3 py-1.5">
                Character count: {text.length.toLocaleString()}
              </span>
              <span className="rounded-full border border-slate-200 bg-white/80 px-3 py-1.5">
                Recommended: one lesson or one chapter section at a time
              </span>
            </div>
          </div>
        </main>

        <aside className="overflow-hidden rounded-[28px] border border-white/10 bg-[linear-gradient(180deg,#0b1120_0%,#111827_100%)] shadow-[0_30px_90px_rgba(2,8,23,0.45)]">
          <div className="border-b border-white/10 px-6 py-6">
            <p className="text-xs font-semibold uppercase tracking-[0.32em] text-emerald-300/80">
              Live Preview
            </p>
            <h2 className="mt-3 text-2xl font-semibold text-white">Generated Cards</h2>
            <p className="mt-2 text-sm leading-6 text-slate-300">
              Preview how the AI output will appear before saving it to a collection.
            </p>
          </div>

          <div className="space-y-4 p-5">
            {busy ? (
              <DashboardSkeleton />
            ) : deferredCards.length > 0 ? (
              deferredCards.map((card) => (
                <article
                  key={card.id ?? `${card.prompt}-${card.insight}`}
                  className="rounded-[24px] border border-white/10 bg-white/[0.04] p-5 shadow-[0_18px_50px_rgba(15,23,42,0.22)] backdrop-blur"
                >
                  <span className="inline-flex rounded-full border border-sky-300/20 bg-sky-300/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.25em] text-sky-200">
                    Prompt
                  </span>
                  <h3 className="mt-4 text-lg font-semibold leading-7 text-white">{card.prompt}</h3>

                  <div className="mt-5 h-px bg-gradient-to-r from-transparent via-white/15 to-transparent" />

                  <span className="mt-5 inline-flex rounded-full border border-emerald-300/20 bg-emerald-300/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.25em] text-emerald-200">
                    Insight
                  </span>
                  <p className="mt-4 text-sm leading-7 text-slate-300">{card.insight}</p>
                </article>
              ))
            ) : (
              <div className="rounded-[24px] border border-dashed border-white/12 bg-white/[0.03] p-8 text-center">
                <p className="text-sm uppercase tracking-[0.28em] text-slate-500">Waiting For Input</p>
                <p className="mt-4 text-base leading-7 text-slate-300">
                  Generated micro-learning cards will appear here in real time once the backend begins processing.
                </p>
              </div>
            )}
          </div>
        </aside>
      </div>
    </section>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-4">
      {[0, 1, 2].map((index) => (
        <div
          key={index}
          className="overflow-hidden rounded-[24px] border border-white/10 bg-white/[0.04] p-5"
        >
          <div className="animate-pulse">
            <div className="h-6 w-28 rounded-full bg-sky-200/10" />
            <div className="mt-4 h-5 w-11/12 rounded-full bg-white/10" />
            <div className="mt-3 h-5 w-4/5 rounded-full bg-white/10" />
            <div className="mt-6 h-px bg-white/10" />
            <div className="mt-6 h-6 w-24 rounded-full bg-emerald-200/10" />
            <div className="mt-4 h-4 w-full rounded-full bg-white/10" />
            <div className="mt-3 h-4 w-5/6 rounded-full bg-white/10" />
            <div className="mt-3 h-4 w-3/4 rounded-full bg-white/10" />
          </div>
        </div>
      ))}
    </div>
  );
}
