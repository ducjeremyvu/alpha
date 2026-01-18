<script lang="ts">
	import * as Menubar from '$lib/components/ui/menubar/index.js';

	// later you can pass routes, user info, etc.
</script>

<header class="sticky top-0 z-20 border-b border-white/10 bg-slate-950/80 backdrop-blur">
	<div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
		<div class="flex items-center gap-3">
			<div
				class="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-400 via-cyan-400 to-blue-500 text-sm font-semibold text-slate-950"
			>
				JV
			</div>
			<div>
				<p class="text-sm font-semibold text-white">Duc Jeremy Vu</p>
				<p class="text-xs text-slate-400">Quant research workspace</p>
			</div>
		</div>
		<Menubar.Root class="border-none bg-transparent shadow-none">
			<Menubar.Menu>
				<Menubar.Trigger class="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white hover:bg-white/10">
					Navigate
				</Menubar.Trigger>

				<Menubar.Content class="w-56">
					<Menubar.Item>
						<a href="/">Home</a>
					</Menubar.Item>

					<Menubar.Separator />

					<Menubar.Item>
						<a href="/tools/opening-range-30m">30 Min Open</a>
					</Menubar.Item>

					<Menubar.Separator />

					<Menubar.Item>
						<a href="/tools/context-replay">Context Replay</a>
					</Menubar.Item>
				</Menubar.Content>
			</Menubar.Menu>
		</Menubar.Root>
	</div>
</header>
