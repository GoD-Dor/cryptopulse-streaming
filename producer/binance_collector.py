
import asyncio
import json
import signal
from datetime import datetime, timezone
from pathlib import Path

import websockets

STREAM_URL = "wss://data-stream.binance.vision/ws/btcusdt@aggTrade"
OUTPUT_DIR = Path("data/raw")
RECONNECT_DELAY = 5
MAX_EVENTS = 1000


async def collect_trades():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_events = 0

    while total_events < MAX_EVENTS:
        try:
            print("Connecting to Binance...")

            async with websockets.connect(
                STREAM_URL,
                open_timeout=15,
                ping_interval=20,
            ) as websocket:

                print("Connected to Binance WebSocket!")

                async for message in websocket:
                    trade = json.loads(message)

                    event = {
                        "event_type": trade["e"],
                        "symbol": trade["s"],
                        "trade_id": trade["a"],
                        "event_time": trade["E"],
                        "event_time_utc": datetime.fromtimestamp(
                            trade["E"] / 1000,
                            tz=timezone.utc
                        ).isoformat(),
                        "price": trade["p"],
                        "quantity": trade["q"],
                        "first_trade_id": trade["f"],
                        "last_trade_id": trade["l"],
                        "trade_time": trade["T"],
                        "buyer_is_maker": trade["m"]
                    }

                    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                    output_file = OUTPUT_DIR / f"btcusdt_{date}.jsonl"

                    with output_file.open("a", encoding="utf-8") as file:
                        file.write(json.dumps(event) + "\n")

                    total_events += 1

                    if total_events % 100 == 0:
                        print(f"Collected {total_events} events")

                    if total_events >= MAX_EVENTS:
                        break

        except (OSError, websockets.exceptions.ConnectionClosed) as error:
            print(f"Connection lost: {error}")
            print(f"Reconnecting in {RECONNECT_DELAY} seconds...")
            await asyncio.sleep(RECONNECT_DELAY)

    print(f"Collection finished: {total_events} events saved")


if __name__ == "__main__":
    try:
        asyncio.run(collect_trades())
    except KeyboardInterrupt:
        print("\nCollector stopped by user.")
