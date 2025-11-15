export interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export async function fetchCandlesForDate(date: string): Promise<Candle[]> {
  const res = await fetch(`http://localhost:8000/candles?date=${date}`);
  if (!res.ok) throw new Error("Failed to load candles");
  return await res.json();
}
