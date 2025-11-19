<script lang="ts">

  import { fetchContextReplayDataForDate } from '$lib/api/candles';
	import { createChart } from 'lightweight-charts';
	import type { Candle } from '$lib/api/candles';

	// import ContextReplayResponse from '$lib/api/candles';
	let candleSeriesTMinusSixty: any = null;
	let chartTMinusSixty: ReturnType<typeof createChart> | null = null;
	let chartDivTMinusSixt: HTMLDivElement | null = null;
	let chart2: ReturnType<typeof createChart> | null = null;
	let chartDiv2: HTMLDivElement | null = null;
	let chart3: ReturnType<typeof createChart> | null = null;
	let chartDiv3: HTMLDivElement | null = null;
	let chart4: ReturnType<typeof createChart> | null = null;
	let chartDiv4: HTMLDivElement | null = null;

	$effect(() => {
		if (!chartDivTMinusSixt) return;

		chartTMinusSixty = createChart(chartDivTMinusSixt, {
			width: chartDivTMinusSixt.clientWidth,
			height: 300,
			layout: { background: { color: '#0f172a' }, textColor: '#e5e7eb' },
			grid: { vertLines: { color: '#1f2937' }, horzLines: { color: '#1f2937' } },
			timeScale: { borderColor: '#374151', timeVisible: true, secondsVisible: false },
			rightPriceScale: { borderColor: '#374151' }
		});

		candleSeriesTMinusSixty = chartTMinusSixty.addCandlestickSeries();
	});

	$effect(async () => {
		const response = await fetchContextReplayDataForDate("2025-11-06")
		const data_raw = response.data.t_minus_60
		console.log(data_raw)
		const data_t_minux_sixty: Candle[] = data_raw.map((row: any) => ({
			time: Math.floor(new Date(row.time).getTime() / 1000),
			open: Number(row.open),
			high: Number(row.high),
			low: Number(row.low),
			close: Number(row.close),
			volume: Number(row.volume ?? 0)
		}));
		console.log("DATA FOR CHART:", data_t_minux_sixty);
		candleSeriesTMinusSixty.setData(data_t_minux_sixty);
		chartTMinusSixty?.timeScale().fitContent();
	})

	let date = $state(todayISO());

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
</script>

<div class="mx-auto w-full max-w-screen-md px-4 py-3">
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
</div>

<div class="grid grid-cols-2 gap-4 mt-7">
	<div bind:this={chartDiv2} class="bg-neutral-900 rounded-lg p-2"></div>
	<div bind:this={chartDiv3} class="bg-neutral-900 rounded-lg p-2"></div>
	<div bind:this={chartDiv4} class="bg-neutral-900 rounded-lg p-2"></div>
	<div>
		<h2 class="flex p-2 item-center justify-center">T Minus 60</h2>
		<div bind:this={chartDivTMinusSixt} class="bg-neutral-900 rounded-lg p-2"></div>
	</div>
</div>

<svelte:window on:keydown={handleKey} />