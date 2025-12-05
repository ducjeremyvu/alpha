export interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface CandleMetrics {
  [key: string]: number | string | null | undefined; 
  // or define explicit metric fields once you know them
}

export interface CandleResponse {
  data: Candle[];
  metrics: CandleMetrics;
}

export type TimeCandleCollection = Record<string, TimeCandleRow>;

export interface ContextReplayResponse {
  symbol: string;
  data: {
    all: TimeCandleCollection;
    t_minus_60: TimeCandleCollection;
    prev_day_business_hours: TimeCandleCollection;
    m15: TimeCandleCollection;
    h1: TimeCandleCollection;
  };
  metrics: {
    prev_day: PrevDayMetrics;
  };
}

export interface PrevDayMetrics {
  prev_day_open: number;
  prev_day_high: number;
  prev_day_low: number;
  prev_day_close: number;
  prev_day_change: number;
  prev_day_change_perc: number;
  prev_day_range: number;
  prev_day_change_to_range: number;
  // prev_day_avg_candle_size?: number; // if you add later
}


export async function fetchCandlesForDate(date: string): Promise<CandleResponse> {
  const res = await fetch(`http://localhost:8000/candles?date=${date}`);
  if (!res.ok) throw new Error("Failed to load candles");
  return await res.json() as CandleResponse;
}

export async function fetchContextReplayDataForDate(date: string): Promise<ContextReplayResponse> {
  const res = await fetch(`http://localhost:8000/context_replay?date=${date}`);
  if (!res.ok) throw new Error("Failed to load candles");
  return await res.json() as ContextReplayResponse;
}

export async function fetchLatestDate(): Promise<string> {
  const res = await fetch(`http://localhost:8000/utils/latest_date`);
  if (!res.ok) throw new Error("Failed to load candles");
  return await res.json() as string;
}

export interface TimeCandleRow {
  time: string | number;
  open: string | number;
  high: string | number;
  low: string | number;
  close: string | number;
  volume?: string | number;
}

export type TimeCandlesInput = TimeCandleRow[] | TimeCandleCollection;

export function convertTimeCandles(data: TimeCandlesInput): Candle[] {
  const rows = Array.isArray(data) ? data : Object.values(data);
  return rows.map((row) => ({
    time: Math.floor(new Date(row.time).getTime() / 1000),
    open: Number(row.open),
    high: Number(row.high),
    low: Number(row.low),
    close: Number(row.close),
    volume: Number(row.volume ?? 0)
  }));
}
