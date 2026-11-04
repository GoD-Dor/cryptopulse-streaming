import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import websockets

STREAM_URL = "wss://data-stream.binance.vision/ws/btcusdt@aggTrade"

OUTPUT_DIR = Path("data/raw")
MAX_STORAGE_BYTES = 2 * 1024 * 1024 * 1024
RECONNECT_DELAY = 5
LOG_EVERY = 1000


def get_storage_usage():
    return sum(
        file.stat().st_size
        for file in OUTPUT_DIR.glob("*.jsonl")
    )


def get_last_trade_id():
    files = sorted(OUTPUT_DIR.glob("btcusdt_*.jsonl"))

    for file in reversed(files):
        with file.open("rb") as f:
            f.seek(0, 2)
            size = f.tell()

            if size == 0:
                continue

            f.seek(max(0, size - 8192))
            lines = f.read().splitlines()

        for line in reversed(lines):
            try:
                return int(json.loads(line)["trade_id"])
            except (ValueError, KeyError, TypeError):
                continue

    return None


async def collect_trades():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    storage_used = get_storage_usage()
    last_trade_id = get_last_trade_id()
    total_events = 0

    print("===== CryptoPulse Collector =====", flush=True)
    print(f"Storage used: {storage_used / 1024**2:.2f} MB", flush=True)
    print(f"Last trade ID: {last_trade_id}", flush=True)
    print("Press Ctrl+C to stop.", flush=True)

    while storage_used < MAX_STORAGE_BYTES:
        try:
            print("Connecting to Binance...", flush=True)

            async with websockets.connect(
                STREAM_URL,
                open_timeout=15,
                ping_interval=20,
                ping_timeout=20,
                max_size=2**20,
            ) as websocket:

                print("Connected!", flush=True)

                async for message in websocket:
                    trade = json.loads(message)

                    trade_id = int(trade["a"])

                    if (
                        last_trade_id is not None
                        and trade_id <= last_trade_id
                    ):
                        continue

                    event_time = datetime.fromtimestamp(
                        trade["E"] / 1000,
                        tz=timezone.utc
                    )

                    event = {
                        "event_type": trade["e"],
                        "symbol": trade["s"],
                        "trade_id": trade_id,
                        "event_time": trade["E"],
                        "event_time_utc": event_time.isoformat(),
                        "price": trade["p"],
                        "quantity": trade["q"],
                        "first_trade_id": trade["f"],
                        "last_trade_id": trade["l"],
                        "trade_time": trade["T"],
                        "buyer_is_maker": trade["m"],
                    }

                    output_file = OUTPUT_DIR / (
                        f"btcusdt_{event_time:%Y-%m-%d}.jsonl"
                    )

                    encoded = (
                        json.dumps(event, separators=(",", ":")) + "\n"
                    ).encode("utf-8")

                    if storage_used + len(encoded) > MAX_STORAGE_BYTES:
                        print("Storage limit reached. Stopping.", flush=True)
                        return

                    with output_file.open("ab") as f:
                        f.write(encoded)

                    storage_used += len(encoded)
                    last_trade_id = trade_id
                    total_events += 1

                    if total_events % LOG_EVERY == 0:
                        print(
                            f"Events this run: {total_events} | "
                            f"Storage: {storage_used / 1024**2:.2f} MB",
                            flush=True,
                        )

        except (
            OSError,
            TimeoutError,
            websockets.exceptions.ConnectionClosed,
        ) as error:
            print(f"Connection issue: {error}", flush=True)

        except (ValueError, KeyError, TypeError) as error:
            print(f"Data error: {error}", flush=True)

        print(
            f"Reconnecting in {RECONNECT_DELAY} seconds...",
            flush=True,
        )
        await asyncio.sleep(RECONNECT_DELAY)

    print("Storage limit reached. Collection stopped.", flush=True)


if __name__ == "__main__":
    try:
        asyncio.run(collect_trades())
    except KeyboardInterrupt:
        print("\nCollector stopped by user.", flush=True)
