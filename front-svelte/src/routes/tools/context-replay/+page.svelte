<script lang="ts">

  import { fetchContextReplayDataForDate, convertTimeCandles, fetchCandlesForDate, fetchLatestDate } from '$lib/api/candles';
	import * as Accordion from "$lib/components/ui/accordion/index.js";
	import { createChart } from 'lightweight-charts';
	import type { Candle } from '$lib/api/candles';
	import { Toggle } from "$lib/components/ui/toggle/index.js";
	 
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { get } from 'svelte/store';


	  // 🔹 30m Open visibility state: default = visible (not hidden)
  let hide30Open = $state(false);
  // Initialize date from URL OR fallback to today
  let date = $state<string>("");
  let lastDate = "";

  // 1) Initialize from URL once
  $effect(() => {
    const urlDate = get(page).url.searchParams.get("date");
    if (!date && urlDate) {
      date = urlDate;
      lastDate = urlDate;
    }
  });



  // 2) If still no date, fetch latest from backend
  $effect(async () => {
    if (!date) {
      const latest = await fetchLatestDate();
      date = latest;
      lastDate = latest;
    }
  });

  // Sync URL when date changes (Arrow keys, inputs, etc.)
  $effect(() => {
    if (date !== lastDate) {
      goto(`?date=${date}`, {
        replaceState: true,
        keepFocus: true,
        noScroll: true
      });
      lastDate = date;
    }
  });

	let chartDivTMinusSixt: HTMLDivElement | null = null;
	let chartDiv3: HTMLDivElement | null = null;
	let chartDiv4: HTMLDivElement | null = null;
	let chartDiv5: HTMLDivElement | null = null;
	

	let charts: Record<string, ReturnType<typeof createChart>> = {};
	let series: Record<string, any> = {};


	let prev_day_metrics: any = $state(null);

	type DatasetKey =
		| "t_minus_60"
		| "prev_day_business_hours"
		| "m15"
		| "h1"
		| "all"
		| "30_min_open";

	const CHART_MAP: { key: DatasetKey; div: () => HTMLDivElement | null }[] = [
		// { key: "m15", div: () => chartDiv2 },
		{ key: "h1", div: () => chartDiv3 },
		{ key: "prev_day_business_hours", div: () => chartDiv4 },
		{ key: "t_minus_60", div: () => chartDivTMinusSixt },
		{ key: "30_min_open", div: () => chartDiv5 }
	];

	function initChart(div: HTMLDivElement) {
	// destroy old instance if needed
	const chart = createChart(div, {
			width: div.clientWidth,
			height: div.clientHeight, //|| 280
			layout: { background: { color: '#0f172a' }, textColor: '#e5e7eb' },
			grid: { vertLines: { color: '#1f2937' }, horzLines: { color: '#1f2937' } },
			timeScale: { borderColor: '#374151', timeVisible: true },
			rightPriceScale: { borderColor: '#374151' }
	});

	const ro = new ResizeObserver(entries => {
			for (const entry of entries) {
					const { width, height } = entry.contentRect;
					if (width > 0 && height > 0) {
							// 1. Resize the chart
							chart.applyOptions({ width, height });

							// 2. Make candle spacing adjust correctly
							chart.timeScale().fitContent();

							// 3. Optional: maintain look-ahead space
							chart.applyOptions({
									timeScale: { rightOffset: 2 }
							});
					}
			}
	});

	ro.observe(div);
	return chart;
	}


  // 🔹 Init all charts when their divs exist
	$effect(() => {
		for (const c of CHART_MAP) {
			const div = c.div();
			if (!div) continue;

			if (!charts[c.key]) {
				const chart = initChart(div);
				charts[c.key] = chart;
				series[c.key] = chart.addCandlestickSeries();
				chart.applyOptions({
						timeScale: {
								rightOffset: 2,
								barSpacing: 10,
								
						}
				});
			}
		}
	});

  // 🔹 Fetch + set data
	$effect(async () => {
		const response = await fetchContextReplayDataForDate(date);
		const responseThirty = await fetchCandlesForDate(date)

		const datasets = response.data;
		const dataThirty = responseThirty.data
		prev_day_metrics = response.metrics.prev_day
		console.log($state.snapshot(prev_day_metrics));

		for (const c of CHART_MAP) {
			let raw; 

			if (c.key == "30_min_open") {
				raw = dataThirty
			} else {
				raw = datasets[c.key];
			}
			
			if (!raw) continue;
		  if (!series[c.key]) continue; // 🔹 important when chart is hidden

			const converted = convertTimeCandles(raw);
			series[c.key].setData(converted);
			charts[c.key]?.timeScale().fitContent();
		}
	});


	function todayISO() {
		return new Date().toISOString().split('T')[0];
	}
	
	function shiftDate(days: number) {
		const d = new Date(date);
		d.setDate(d.getDate() + days);
		date = d.toISOString().split('T')[0];
	}

	function handleKey(e: KeyboardEvent) {
		if (e.key === 'ArrowLeft') shiftDate(-1);
		if (e.key === 'ArrowRight') shiftDate(1);
  }
	function getWeekday(dateString: string) {
		if (!dateString) return "";
		const d = new Date(dateString);
		return d.toLocaleDateString("en-US", { weekday: "short" });
	}

</script>

<div class="mx-auto w-full max-w-3xl px-4 py-3">
	<h1 class="mb-1 text-center text-3xl font-bold">Context Replay Dashboard</h1>
</div>

<div class="mb-3 flex items-center justify-center gap-3">
	<span>Symbol:</span>
	<select id="symbol">
		<option value="US500">US500</option>
		<option value="NAS100">NAS100</option>
	</select>

	<span>Date:</span>
	<input type="date" bind:value={date} />
	<span class="px-2 py-1 rounded bg-neutral-800 text-neutral-300 text-sm">
			{getWeekday(date)}
	</span>
</div>

<div class="flex w-full">
	<div class="w-3/4 grid grid-cols-2 gap-4 mt-0 min-w-0 p-6">
		<div class="flex flex-col">
			<h2 class="p-2 text-center flex-none leading-tight">T-60 PM</h2>
			<div bind:this={chartDivTMinusSixt} class="bg-neutral-900 rounded-lg  overflow-hidden h-[300px]"></div>
		</div>
		<div class="flex flex-col">
			<div class="flex items-center justify-between px-2">
				<h2 class="flex-1 text-center leading-tight p-2">30 Open</h2>
				<Toggle 
					bind:pressed={hide30Open}
					class="w-15 h-7 rounded-md border border-neutral-700 flex items-center justify-center"
				>Hide</Toggle>
			</div>
			{#if !hide30Open}
				<div bind:this={chartDiv5} class="bg-neutral-900 rounded-lg  overflow-hidden h-[300px]"></div>
			{/if}
		</div>
		
		<div class="flex flex-col">
			<h2 class="p-2 text-center flex-none leading-tight">Prev Day</h2>
			<div bind:this={chartDiv4} class="bg-neutral-900 rounded-lg  overflow-hidden h-[300px]"></div>
		</div>
		
		<div class="flex flex-col">
			<h2 class="p-2 text-center flex-none leading-tight">H1</h2>
			<div bind:this={chartDiv3} class="bg-neutral-900 rounded-lg  overflow-hidden h-[300px]"></div>
		</div>
	</div >
	<div class="w-1/4 min-w-0">		
		<Accordion.Root type="single" class="w-full sm:max-w-[70%]" value="item-1">
		<Accordion.Item value="item-1">
			<Accordion.Trigger>Previous Day</Accordion.Trigger>
			<Accordion.Content class="flex flex-col gap-4 text-balance">
				<div class="p-4 space-y-4">
						<h2 class="text-lg font-semibold text-center">Prev Day Metrics</h2>

						<div class="grid grid-cols-2 gap-x-3 gap-y-2 text-sm">
							{#if prev_day_metrics}
								<div class="text-neutral-400">Open</div>
								<div class="text-right font-medium">{prev_day_metrics.prev_day_open}</div>

								<div class="text-neutral-400">High</div>
								<div class="text-right font-medium">{prev_day_metrics.prev_day_high}</div>

								<div class="text-neutral-400">Low</div>
								<div class="text-right font-medium">{prev_day_metrics.prev_day_low}</div>

								<div class="text-neutral-400">Close</div>
								<div class="text-right font-medium">{prev_day_metrics.prev_day_close}</div>

								<div class="text-neutral-400">Change</div>
								<div class="text-right font-medium">
										{prev_day_metrics.prev_day_change}
								</div>

								<div class="text-neutral-400">% Change</div>
								<div class="text-right font-medium">
										{prev_day_metrics.prev_day_change_perc}%
								</div>

								<div class="text-neutral-400">Range</div>
								<div class="text-right font-medium">
										{prev_day_metrics.prev_day_range}
								</div>

								<div class="text-neutral-400">Change / Range</div>
								<div class="text-right font-medium">
										{prev_day_metrics.prev_day_change_to_range}
								</div>
							{/if}
						</div>
				</div>
			</Accordion.Content>
		</Accordion.Item>
		<Accordion.Item value="item-2">
			<Accordion.Trigger>Pre Market</Accordion.Trigger>
			<Accordion.Content class="flex flex-col gap-4 text-balance">
					<div class="p-4 space-y-4">
						<h2 class="text-lg font-semibold text-center">Premarket Metrics</h2>
					</div>
			</Accordion.Content>
		</Accordion.Item>
		<Accordion.Item value="item-3">
			<Accordion.Trigger>30 Min Open</Accordion.Trigger>
			<Accordion.Content class="flex flex-col gap-4 text-balance">
				<div class="p-4 space-y-4">
					<h2 class="text-lg font-semibold text-center">30 Min Open Metrics</h2>
				</div>
			</Accordion.Content>
		</Accordion.Item>
		</Accordion.Root>
	</div>
</div>

<svelte:window on:keydown={handleKey} />
