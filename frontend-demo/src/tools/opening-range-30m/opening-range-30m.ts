import './style.css'

import * as LightweightCharts from 'lightweight-charts';

const API_BASE_URL = "http://localhost:8000";

// DOM elements
const dateInput = document.getElementById("date") as HTMLInputElement | null;
const chartContainer = document.getElementById("chart") as HTMLDivElement;

interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// Initialize date
const today = new Date().toISOString().slice(0, 10);

function requestCandlesForCurrentDate(): void {
  if (!dateInput?.value) return;
  loadCandles(dateInput.value);
}

if (dateInput) {
  dateInput.value = today;
  dateInput.addEventListener("change", requestCandlesForCurrentDate);
  requestCandlesForCurrentDate();
}

// Create chart
const chart = LightweightCharts.createChart(chartContainer, {
  width: chartContainer.clientWidth || 800,
  height: chartContainer.clientHeight || 600,
  layout: { background: { color: "#0f172a" }, textColor: "#e5e7eb" },
  grid: { vertLines: { color: "#1f2937" }, horzLines: { color: "#1f2937" } },
  timeScale: { borderColor: "#374151", timeVisible: true, secondsVisible: false },
  rightPriceScale: { borderColor: "#374151" },
});

const candleSeries = (chart as any).addCandlestickSeries({
  priceFormat: { type: "price", precision: 1 },
});

async function loadCandles(date: string): Promise<void> {
  try {
    const url = new URL(`${API_BASE_URL}/candles`);
    console.log(url)
    url.searchParams.set("date", date);
    const res = await fetch(url);
    console.log(res)
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    
    const raw = await res.json();
    console.log(raw)

    const data: Candle[] = raw.map((row: any) => ({
      time: Math.floor(new Date(row.time).getTime() / 1000),
      open: Number(row.open),
      high: Number(row.high),
      low: Number(row.low),
      close: Number(row.close),
      volume: Number(row.volume ?? 0),
    }));
    const setData = data.sort((a, b) => a.time - b.time);
    console.log(setData)
    candleSeries.setData(setData);
    chart.timeScale().fitContent();
  } catch (err) {
    console.error("Failed to load candles:", err);
  }
}

function changeDateByDays(days: number): void {
  if (!dateInput) return;
  const current = new Date(dateInput.value);
  current.setDate(current.getDate() + days);
  dateInput.value = current.toISOString().slice(0, 10);
  requestCandlesForCurrentDate();
}

chart.timeScale().fitContent();
window.addEventListener("resize", () => {
  chart.applyOptions({ width: chartContainer.clientWidth, height: chartContainer.clientHeight });
});

window.addEventListener("keydown", (event) => {
  if (!["ArrowLeft", "ArrowRight"].includes(event.key)) return;
  if ((event.target as HTMLElement)?.tagName?.match(/^(INPUT|TEXTAREA|SELECT)$/)) return;
  event.preventDefault();
  changeDateByDays(event.key === "ArrowLeft" ? -1 : 1);
});
