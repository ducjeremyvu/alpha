<script lang="ts">
	import { createChart } from 'lightweight-charts';
	import { fetchCandlesForDate } from '$lib/api/candles';
	import type { Candle } from '$lib/api/candles';

	let chart: ReturnType<typeof createChart> | null = null;
	let candleSeries: any = null;
	let chartDiv: HTMLDivElement | null = null;

	let date = $state(todayISO());

	function todayISO() {
		return new Date().toISOString().split('T')[0];
	}

	// 1. Setup chart
	$effect(() => {
		if (!chartDiv) return;

		chart = createChart(chartDiv, {
			width: chartDiv.clientWidth || 800,
			height: chartDiv.clientHeight || 600,
			layout: { background: { color: '#0f172a' }, textColor: '#e5e7eb' },
			grid: { vertLines: { color: '#1f2937' }, horzLines: { color: '#1f2937' } },
			timeScale: { borderColor: '#374151', timeVisible: true, secondsVisible: false },
			rightPriceScale: { borderColor: '#374151' }
		});

		candleSeries = chart.addCandlestickSeries();
	});

	// 2. Load candles whenever date changes (but only after series exists)
	$effect(async () => {
		if (!candleSeries) return;
		const raw = await fetchCandlesForDate(date);
		const data_raw = raw.data;
		const data: Candle[] = data_raw.map((row: any) => ({
			time: Math.floor(new Date(row.time).getTime() / 1000),
			open: Number(row.open),
			high: Number(row.high),
			low: Number(row.low),
			close: Number(row.close),
			volume: Number(row.volume ?? 0)
		}));
		console.log(data);
		candleSeries.setData(data);
		chart?.timeScale().fitContent();
	});

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

<div class="mx-auto w-full max-w-screen-md px-4 py-6">
	<h1 class="mb-6 text-center text-3xl font-bold">30 Min US500</h1>
</div>

<div class="mb-6 flex items-center justify-center gap-4">
	<span>Symbol:</span>
	<select id="symbol">
		<option value="US500">US500</option>
		<option value="NAS100">NAS100</option>
	</select>

	<span>Date:</span>
	<input type="date" bind:value={date} />
</div>

<div id="chart-container" class="charts flex justify-center">
	<div bind:this={chartDiv} id="chart"></div>
</div>

<svelte:window on:keydown={handleKey} />
