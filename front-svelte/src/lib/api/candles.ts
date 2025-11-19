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

export interface ContextReplayResponse {
  symbol: string;
  data: {
    all: Record<string, any>;
    t_minus_60: Record<string, any>;
    prev_day_business_hours: Record<string, any>;
    m15: Record<string, any>;
    h1: Record<string, any>;
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
  if (!res.ok) throw new Error("Failed to laod candles");
  return await res.json() as ContextReplayResponse;
}