<h1>Candlestick Chart</h1>

<header class="centered">
  <span>Date:</span>
  <input type="date" bind:value={date} />
</header>

<Chart {...options}>
    <CandlestickSeries
        data={data}
        upColor="rgba(255, 144, 0, 1)"
        downColor="#000"
        borderDownColor="rgba(255, 144, 0, 1)"
        borderUpColor="rgba(255, 144, 0, 1)"
        wickDownColor="rgba(255, 144, 0, 1)"
        wickUpColor="rgba(255, 144, 0, 1)"
    />
</Chart>

<svelte:window on:keydown={handleKey} />

<script>
    import {ColorType, CrosshairMode} from 'lightweight-charts';
    import {Chart, CandlestickSeries} from 'svelte-lightweight-charts';
    import { onMount } from "svelte";
    import { fetchCandlesForDate } from '$lib/api/candles';

    let date = $state(todayISO());


    function todayISO() {
      return new Date().toISOString().split("T")[0];
    }
    
    const options = {
        width: 600,
        height: 300,
        layout: {
            background: {
                type: ColorType.Solid,
                color: '#000000',
            },
            textColor: 'rgba(255, 255, 255, 0.9)',
        },
        grid: {
            vertLines: {
                color: 'rgba(197, 203, 206, 0.5)',
            },
            horzLines: {
                color: 'rgba(197, 203, 206, 0.5)',
            },
        },
        crosshair: {
            mode: CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: 'rgba(197, 203, 206, 0.8)',
        },
        timeScale: {
            borderColor: 'rgba(197, 203, 206, 0.8)',
        },
    }


  function shiftDate(days) {
    const d = new Date(date);
    d.setDate(d.getDate() + days);
    date = d.toISOString().split("T")[0];
  }


  function handleKey(e) {
    if (e.key === "ArrowLeft") shiftDate(-1);
    if (e.key === "ArrowRight") shiftDate(1);
  }

  onMount(() => {
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  });
</script>

<!-- <script lang="ts">
  import { createChart } from 'lightweight-charts';
  import { fetchCandlesForDate } from '$lib/api/candles';

  let chart: ReturnType<typeof createChart> | null = null;
  let candleSeries: any = null;
  let chartDiv: HTMLDivElement | null = null;

  let date = $state(todayISO());

  function todayISO() {
    return new Date().toISOString().split("T")[0];
  }
  interface Candle {
    time: number;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }

  // 1. Setup chart
  $effect(() => {
    if (!chartDiv) return;

    chart = createChart(chartDiv, {
      width: chartDiv.clientWidth || 800,
      height: chartDiv.clientHeight || 600,
      layout: { background: { color: "#0f172a" }, textColor: "#e5e7eb" },
      grid: { vertLines: { color: "#1f2937" }, horzLines: { color: "#1f2937" } },
      timeScale: { borderColor: "#374151", timeVisible: true, secondsVisible: false },
      rightPriceScale: { borderColor: "#374151" },
    });

    candleSeries = chart.addCandlestickSeries();
  });

  // 2. Load candles whenever date changes (but only after series exists)
  $effect(async () => {
    if (!candleSeries) return;
    const raw = await fetchCandlesForDate(date);
    const data: Candle[] = raw.map((row: any) => ({
      time: Math.floor(new Date(row.time).getTime() / 1000),
      open: Number(row.open),
      high: Number(row.high),
      low: Number(row.low),
      close: Number(row.close),
      volume: Number(row.volume ?? 0),
    }));
    console.log(data)
    candleSeries.setData(data);
    chart?.timeScale().fitContent();
  });

  function shiftDate(days: number) {
    const d = new Date(date);
    d.setDate(d.getDate() + days);
    date = d.toISOString().split("T")[0];
  }

  function handleKey(e: KeyboardEvent) {
    if (e.key === "ArrowLeft") shiftDate(-1);
    if (e.key === "ArrowRight") shiftDate(1);
  }
</script> -->

<!-- 
<h1 class="centered">30 Min US500</h1>

<header class="centered">
  <span>Symbol:</span>
  <select id="symbol">
    <option value="US500">US500</option>
    <option value="NAS100">NAS100</option>
  </select>

  <span>Date:</span>
  <input type="date" bind:value={date} />
</header>

<div id="chart-container" class="charts">
  <div bind:this={chartDiv} id="chart"></div>
</div>

<svelte:window on:keydown={handleKey} />

<div>
  <a href="/">Home</a>
</div>

<style>
  h1 {
    align-content: center;
  }

  .charts {
    align-items: center;
    display: flex;
    padding: 2em;

  }
</style> -->