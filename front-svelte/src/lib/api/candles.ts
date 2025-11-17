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

export async function fetchCandlesForDate(date: string): Promise<CandleResponse> {
  const res = await fetch(`http://localhost:8000/candles?date=${date}`);
  if (!res.ok) throw new Error("Failed to load candles");
  return await res.json() as CandleResponse;
}
