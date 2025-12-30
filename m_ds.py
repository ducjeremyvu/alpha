from datetime import datetime, timezone

from ib_insync import IB, Stock, util


def fetch_spy_1m(
    host: str = "127.0.0.1",
    port: int = 4002,
    client_id: int = 1,
    output_csv: str = "spy_1m.csv",
):
    ib = IB()
    ib.connect(host, port, clientId=client_id)

    # SPY is a liquid ETF proxy for US equity index exposure.
    contract = Stock("SPY", "ARCA", "USD")
    ib.qualifyContracts(contract)

    bars = ib.reqHistoricalData(
        contract,
        endDateTime="",
        durationStr="1 D",
        barSizeSetting="1 min",
        whatToShow="TRADES",
        useRTH=True,
        formatDate=1,
    )

    if not bars:
        print("No bars returned.")
        ib.disconnect()
        return

    df = util.df(bars)
    df["fetched_at_utc"] = datetime.now(timezone.utc).isoformat()
    df.to_csv(output_csv, index=False)
    print(f"Saved {len(df)} bars to {output_csv}")

    ib.disconnect()


if __name__ == "__main__":
    fetch_spy_1m()
