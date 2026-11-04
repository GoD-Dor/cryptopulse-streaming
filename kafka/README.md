# Kafka Streaming Architecture

This module will manage the ingestion of Binance market data into Apache Kafka.

## Planned Responsibilities
- Receive normalized events from the Binance WebSocket producer.
- Publish events to Kafka topics.
- Configure partitions and replication.
- Support reliable event delivery and consumption.

## Planned Kafka Topic
- Topic: crypto.trades.btcusdt
- Message key: BTCUSDT
- Message format: JSON
- Event time: Binance exchange timestamp (UTC)

## Status
Architecture design phase. Kafka deployment is planned for a later checkpoint.

