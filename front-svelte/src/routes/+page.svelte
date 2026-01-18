<svelte:head>
	<title>Jeremy Vu | Quant Research Workspace</title>
</svelte:head>

<main class="bg-slate-950 text-slate-100">
	<section class="relative overflow-hidden">
		<div class="pointer-events-none absolute inset-0">
			<div class="absolute -left-24 top-24 h-72 w-72 rounded-full bg-emerald-500/20 blur-3xl"></div>
			<div class="absolute -right-24 top-10 h-72 w-72 rounded-full bg-blue-500/20 blur-3xl"></div>
		</div>
		<div class="relative mx-auto flex max-w-6xl flex-col gap-12 px-6 py-16 lg:flex-row lg:items-center lg:py-24">
			<div class="flex-1 space-y-6">
				<span class="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.2em] text-slate-300">
					Live analytics · research driven
				</span>
				<h1 class="text-4xl font-semibold leading-tight text-white md:text-5xl">
					Market intelligence built for precision, speed, and clarity.
				</h1>
				<p class="max-w-2xl text-base text-slate-300 md:text-lg">
					Explore a curated workspace for quantitative research, execution tooling, and market
					context replay. Designed to turn raw data into actionable insight with less noise and more
					focus.
				</p>
				<div class="flex flex-wrap gap-3">
					<a
						href="/tools/opening-range-30m"
						class="rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-900 shadow-lg shadow-white/20 transition hover:-translate-y-0.5 hover:shadow-white/30"
					>
						Explore tools
					</a>
					<a
						href="/tools/context-replay"
						class="rounded-full border border-white/20 px-6 py-3 text-sm font-semibold text-white transition hover:border-white/40 hover:text-white"
					>
						View context replay
					</a>
				</div>
			</div>
			<div class="flex-1">
				<div class="grid gap-4 sm:grid-cols-2">
					<div class="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/20">
						<p class="text-xs uppercase tracking-[0.2em] text-emerald-200">Signal</p>
						<h3 class="mt-3 text-xl font-semibold text-white">Real-time decision support</h3>
						<p class="mt-2 text-sm text-slate-300">
							Streamlined analytics for quick directional reads, volatility shifts, and market tempo.
						</p>
					</div>
					<div class="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/20">
						<p class="text-xs uppercase tracking-[0.2em] text-blue-200">Research</p>
						<h3 class="mt-3 text-xl font-semibold text-white">Backtest-ready pipelines</h3>
						<p class="mt-2 text-sm text-slate-300">
							Reusable workflows and feature libraries built for iteration and scale.
						</p>
					</div>
					<div class="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/20">
						<p class="text-xs uppercase tracking-[0.2em] text-purple-200">Execution</p>
						<h3 class="mt-3 text-xl font-semibold text-white">Risk-aware tooling</h3>
						<p class="mt-2 text-sm text-slate-300">
							Designed to keep sizing, exposure, and downside controls visible at a glance.
						</p>
					</div>
					<div class="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-lg shadow-black/20">
						<p class="text-xs uppercase tracking-[0.2em] text-amber-200">Workflow</p>
						<h3 class="mt-3 text-xl font-semibold text-white">Context-rich replay</h3>
						<p class="mt-2 text-sm text-slate-300">
							Replay sessions with narrative notes and contextual overlays for faster reviews.
						</p>
					</div>
				</div>
			</div>
		</div>
	</section>

	<section class="border-t border-white/10 bg-slate-950 py-16">
		<div class="mx-auto grid max-w-6xl gap-6 px-6 md:grid-cols-3">
			<div class="rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/0 p-6">
				<p class="text-sm font-semibold text-white">Focused analytics</p>
				<p class="mt-2 text-sm text-slate-300">
					Monitor volatility, liquidity, and structure shifts without clutter.
				</p>
			</div>
			<div class="rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/0 p-6">
				<p class="text-sm font-semibold text-white">Curated toolchain</p>
				<p class="mt-2 text-sm text-slate-300">
					Jump from research to execution with consistent metrics and shared context.
				</p>
			</div>
			<div class="rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-white/0 p-6">
				<p class="text-sm font-semibold text-white">Session-ready reports</p>
				<p class="mt-2 text-sm text-slate-300">
					Automated exports to support post-trade reviews and daily briefings.
				</p>
			</div>
		</div>
	</section>

	<section class="bg-slate-950 py-16">
		<div class="mx-auto flex max-w-6xl flex-col gap-10 px-6">
			<div class="flex items-end justify-between gap-6 flex-wrap">
				<div>
					<p class="text-xs uppercase tracking-[0.2em] text-slate-400">Featured tools</p>
					<h2 class="mt-3 text-2xl font-semibold text-white">Stay in sync with live context.</h2>
				</div>
				<a
					href="/tools/context-replay"
					class="text-sm font-semibold text-emerald-200 hover:text-emerald-100"
				>
					Open replay →
				</a>
			</div>
			<div class="grid gap-6 md:grid-cols-2">
				<div class="rounded-3xl border border-white/10 bg-white/5 p-7">
					<h3 class="text-lg font-semibold text-white">30-minute opening range</h3>
					<p class="mt-2 text-sm text-slate-300">
						Breakdown of early-session range, directional bias, and follow-through signal tracking.
					</p>
					<a
						href="/tools/opening-range-30m"
						class="mt-4 inline-flex items-center text-sm font-semibold text-emerald-200 hover:text-emerald-100"
					>
						Launch tool →
					</a>
				</div>
				<div class="rounded-3xl border border-white/10 bg-white/5 p-7">
					<h3 class="text-lg font-semibold text-white">Context replay</h3>
					<p class="mt-2 text-sm text-slate-300">
						Review sessions with layered notes, key timestamps, and contextual overlays.
					</p>
					<a
						href="/tools/context-replay"
						class="mt-4 inline-flex items-center text-sm font-semibold text-emerald-200 hover:text-emerald-100"
					>
						Open replay →
					</a>
				</div>
			</div>
		</div>
	</section>

	<section class="border-t border-white/10 bg-slate-950 py-16">
		<div class="mx-auto grid max-w-6xl gap-8 px-6 lg:grid-cols-3">
			<div>
				<p class="text-xs uppercase tracking-[0.2em] text-slate-400">Workflow</p>
				<h2 class="mt-3 text-2xl font-semibold text-white">From raw data to live insight.</h2>
				<p class="mt-3 text-sm text-slate-300">
					Keep research, context, and execution notes stitched together in one place.
				</p>
			</div>
			<div class="rounded-3xl border border-white/10 bg-white/5 p-6">
				<p class="text-sm font-semibold text-white">1. Ingest</p>
				<p class="mt-2 text-sm text-slate-300">
					Sync market data and analytics into the shared DuckDB pipeline.
				</p>
			</div>
			<div class="rounded-3xl border border-white/10 bg-white/5 p-6">
				<p class="text-sm font-semibold text-white">2. Evaluate</p>
				<p class="mt-2 text-sm text-slate-300">
					Surface signals, validate edges, and generate scenario notes.
				</p>
			</div>
			<div class="rounded-3xl border border-white/10 bg-white/5 p-6 lg:col-start-2">
				<p class="text-sm font-semibold text-white">3. Execute</p>
				<p class="mt-2 text-sm text-slate-300">
					Deploy with live dashboards and context-aware decision support.
				</p>
			</div>
		</div>
	</section>

	<footer class="border-t border-white/10 bg-slate-950 py-10">
		<div class="mx-auto flex max-w-6xl flex-col gap-4 px-6 text-sm text-slate-400 md:flex-row md:items-center md:justify-between">
			<p>Quant research workspace for systematic trading.</p>
			<p>Built with SvelteKit and DuckDB pipelines.</p>
		</div>
	</footer>
</main>
