export function StimuliLandingPage() {
  const features = [
    {
      title: "Turn Chapters Into Review Cards",
      description:
        "Paste long-form readings, lecture notes, or source passages and turn them into clear, classroom-ready micro-learning cards in minutes.",
    },
    {
      title: "Built For Teacher Workflow",
      description:
        "Generate vocabulary prompts, quick checks, and retrieval-practice cards without manually rewriting every lesson by hand.",
    },
    {
      title: "API-First For EdTech Teams",
      description:
        "Integrate stimul.li into curriculum tools, district platforms, and LMS workflows with structured outputs and export-ready formats.",
    },
    {
      title: "Safe Testing With Sandbox Mode",
      description:
        "Developers can test integrations against realistic mock responses before they ever spend on production AI generation.",
    },
    {
      title: "Collections For Every Course",
      description:
        "Organize generated cards into reusable collections by unit, subject, teacher, or school so materials stay easy to find.",
    },
    {
      title: "Operationally Ready",
      description:
        "Metered billing, audit-friendly logging, secure deployment patterns, and background processing make it production-capable from day one.",
    },
  ];

  const pricing = [
    {
      name: "Free",
      price: "$0",
      note: "Best for testing and small classroom pilots",
      cta: "Start Free",
      featured: false,
      items: [
        "Sandbox mode for safe integration testing",
        "5 requests per minute",
        "100 stimuli per month",
        "Basic export support",
      ],
    },
    {
      name: "Pro",
      price: "$29",
      note: "For independent teachers and tutoring businesses",
      cta: "Upgrade To Pro",
      featured: true,
      items: [
        "Production API access",
        "Higher usage limits and priority processing",
        "Collections, exports, and billing visibility",
        "Email support for deployment and onboarding",
      ],
    },
    {
      name: "School District",
      price: "Custom",
      note: "For multi-teacher rollouts and district procurement",
      cta: "Contact Sales",
      featured: false,
      items: [
        "Multi-school provisioning",
        "Shared governance and admin review workflows",
        "Contract billing and onboarding support",
        "Custom retention, security, and compliance review",
      ],
    },
  ];

  return (
    <main className="bg-white text-slate-900">
      <section className="relative overflow-hidden">
        <div className="absolute inset-x-0 top-0 h-[540px] bg-[radial-gradient(circle_at_top,_rgba(26,82,118,0.12),_transparent_48%),linear-gradient(180deg,#ffffff_0%,#f7fbfd_100%)]" />
        <div className="relative mx-auto flex min-h-[88vh] max-w-7xl flex-col justify-center px-6 py-20 sm:px-8 lg:px-10">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.34em] text-sky-800/70">
              stimul.li for teachers
            </p>
            <h1 className="mt-6 max-w-4xl font-serif text-5xl leading-[0.95] tracking-tight text-slate-950 sm:text-6xl lg:text-7xl">
              Turn dense lesson content into fast, memorable micro-learning.
            </h1>
            <p className="mt-8 max-w-2xl text-lg leading-8 text-slate-600 sm:text-xl">
              stimul.li helps teachers transform chapters, lecture notes, and instructional text into
              high-signal cards students can actually review, retain, and revisit.
            </p>

            <div className="mt-10 flex flex-col gap-4 sm:flex-row">
              <a
                href="#pricing"
                className="inline-flex items-center justify-center rounded-full bg-[#1A5276] px-7 py-3.5 text-sm font-semibold text-white shadow-[0_18px_40px_rgba(26,82,118,0.22)] transition hover:bg-[#154360]"
              >
                View Pricing
              </a>
              <a
                href="#features"
                className="inline-flex items-center justify-center rounded-full border border-slate-200 px-7 py-3.5 text-sm font-semibold text-slate-800 transition hover:border-slate-300 hover:bg-slate-50"
              >
                Explore Features
              </a>
            </div>
          </div>

          <div className="mt-16 grid gap-4 md:grid-cols-3">
            <div className="rounded-[28px] border border-slate-200 bg-white/80 p-6 shadow-[0_24px_60px_rgba(15,23,42,0.08)] backdrop-blur">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-800/70">
                Classroom speed
              </p>
              <p className="mt-4 text-3xl font-semibold text-slate-950">Minutes</p>
              <p className="mt-3 text-sm leading-7 text-slate-600">
                Go from full chapter text to review-ready prompts without rewriting material manually.
              </p>
            </div>
            <div className="rounded-[28px] border border-slate-200 bg-white/80 p-6 shadow-[0_24px_60px_rgba(15,23,42,0.08)] backdrop-blur">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-800/70">
                Better retention
              </p>
              <p className="mt-4 text-3xl font-semibold text-slate-950">Higher recall</p>
              <p className="mt-3 text-sm leading-7 text-slate-600">
                Reinforce vocabulary, concepts, and retrieval practice with compact, repeatable study cards.
              </p>
            </div>
            <div className="rounded-[28px] border border-slate-200 bg-white/80 p-6 shadow-[0_24px_60px_rgba(15,23,42,0.08)] backdrop-blur">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-800/70">
                Ready to scale
              </p>
              <p className="mt-4 text-3xl font-semibold text-slate-950">API-first</p>
              <p className="mt-3 text-sm leading-7 text-slate-600">
                Ideal for educators, tutoring platforms, and school systems that want structured AI output.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="mx-auto max-w-7xl px-6 py-24 sm:px-8 lg:px-10">
        <div className="max-w-2xl">
          <p className="text-sm font-semibold uppercase tracking-[0.34em] text-sky-800/70">
            Features
          </p>
          <h2 className="mt-5 font-serif text-4xl leading-tight text-slate-950 sm:text-5xl">
            Built for modern teaching teams, not generic AI demos.
          </h2>
          <p className="mt-6 text-lg leading-8 text-slate-600">
            Every part of stimul.li is designed to help teachers create useful review material faster and
            help education teams integrate AI without sacrificing structure.
          </p>
        </div>

        <div className="mt-14 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {features.map((feature) => (
            <article
              key={feature.title}
              className="rounded-[30px] border border-slate-200 bg-white p-8 shadow-[0_20px_50px_rgba(15,23,42,0.06)]"
            >
              <div className="h-11 w-11 rounded-2xl bg-[linear-gradient(135deg,#1A5276_0%,#4ea7ce_100%)]" />
              <h3 className="mt-6 text-2xl font-semibold tracking-tight text-slate-950">
                {feature.title}
              </h3>
              <p className="mt-4 text-base leading-8 text-slate-600">{feature.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="pricing" className="border-t border-slate-200 bg-slate-50/70">
        <div className="mx-auto max-w-7xl px-6 py-24 sm:px-8 lg:px-10">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.34em] text-sky-800/70">
              Pricing
            </p>
            <h2 className="mt-5 font-serif text-4xl leading-tight text-slate-950 sm:text-5xl">
              Start small, upgrade when your classroom or district is ready.
            </h2>
          </div>

          <div className="mt-14 grid gap-6 lg:grid-cols-3">
            {pricing.map((tier) => (
              <article
                key={tier.name}
                className={`rounded-[32px] border p-8 shadow-[0_24px_60px_rgba(15,23,42,0.08)] ${
                  tier.featured
                    ? "border-[#1A5276] bg-white ring-1 ring-[#1A5276]/15"
                    : "border-slate-200 bg-white"
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="text-2xl font-semibold text-slate-950">{tier.name}</h3>
                    <p className="mt-3 text-sm leading-7 text-slate-600">{tier.note}</p>
                  </div>
                  {tier.featured ? (
                    <span className="rounded-full bg-[#1A5276] px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-white">
                      Most Popular
                    </span>
                  ) : null}
                </div>

                <div className="mt-8 flex items-end gap-2">
                  <span className="text-5xl font-semibold tracking-tight text-slate-950">{tier.price}</span>
                  {tier.price !== "Custom" ? (
                    <span className="pb-2 text-sm text-slate-500">/month</span>
                  ) : null}
                </div>

                <ul className="mt-8 space-y-4">
                  {tier.items.map((item) => (
                    <li key={item} className="flex items-start gap-3 text-sm leading-7 text-slate-600">
                      <span className="mt-2 h-2.5 w-2.5 rounded-full bg-[#1A5276]" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>

                <a
                  href="#"
                  className={`mt-10 inline-flex w-full items-center justify-center rounded-full px-5 py-3.5 text-sm font-semibold transition ${
                    tier.featured
                      ? "bg-[#1A5276] text-white hover:bg-[#154360]"
                      : "border border-slate-200 bg-white text-slate-900 hover:bg-slate-100"
                  }`}
                >
                  {tier.cta}
                </a>
              </article>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
