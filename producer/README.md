# Binance Data Producer

This module collects real-time BTC/USDT market data from the Binance WebSocket API.

## Responsibilities
- Connect to the Binance WebSocket feed.
- Receive and parse trade events.
- Save raw events for historical analysis.
- Prepare events for future Kafka integration.

## Status
WebSocket connectivity has been successfully tested on the Azure master VM. Persistent data collection is not yet deployed.
