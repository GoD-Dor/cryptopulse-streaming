# CryptoPulse - Streaming Architecture

## 1. Overview

CryptoPulse is designed as a real-time cryptocurrency data pipeline for BTCUSDT market data.

The planned streaming architecture is:

Binance WebSocket
-> Python Binance Collector
-> Apache Kafka
-> Spark Structured Streaming
-> HDFS / Parquet
-> Machine Learning pipeline


## 2. Data Producer

The Binance WebSocket producer receives aggregated trade events from the public BTCUSDT market-data stream.

The existing Python collector:

- Connects to the Binance BTCUSDT `aggTrade` WebSocket.
- Normalizes Binance events into a consistent JSON structure.
- Preserves Binance trade identifiers and timestamps.
- Stores normalized events as JSON Lines during the current ingestion stage.
- Reconnects after connection failures.
- Filters previously processed trade IDs after reconnection.

The normalized event contains 11 fields defined in `kafka/message_schema.json`.

## 3. Kafka Layer

-> Spark Structured Streaming

### Planned Kafka Topic

- Topic: `crypto.trades.btcusdt`
- Message key: `BTCUSDT`
- Message format: JSON
- Current planned partitions: 1
- Replication factor: 3 if three Kafka brokers are available
- Event timestamp: Binance exchange event time in UTC

The single planned partition is appropriate for the current BTCUSDT-only stream because it provides a simple ordered stream. If multiple trading symbols are added later, partitioning by symbol can be considered.

Replication and broker configuration will be finalized after the available Kafka infrastructure is confirmed.

## 4. Message Contract

Each Kafka message will contain one normalized Binance aggregated trade event.

The message contract is defined in:

`kafka/message_schema.json`

Required fields include:

- `event_type`
- `symbol`
- `trade_id`
- `event_time`
- `event_time_utc`
- `price`
- `quantity`
- `first_trade_id`
- `last_trade_id`
- `trade_time`
- `buyer_is_maker`

The schema uses JSON Schema Draft 2020-12.

-> Spark Structured Streaming

-> Spark Structured Streaming

The planned Spark pipeline is:

Kafka
???????? read JSON messages
???????? apply the message schema
???????? validate records
???????? convert timestamps
???????? handle duplicates
???????? handle late events
???????? aggregate trades into one-minute windows
???????? write processed data to HDFS/Parquet

The Spark application will use a dedicated consumer group:

`cryptopulse-spark`

Spark checkpoints will be used to maintain streaming progress and support recovery after application failures.

## 6. Event Time and Late Data

CryptoPulse will use the Binance exchange timestamp as the primary event time.

The pipeline must distinguish between:

- Event time: when the trade occurred according to Binance.
- Processing time: when the event is processed by the streaming application.

Because network delays and reconnections can cause events to arrive late or out of order, the Spark pipeline will use event-time windows with watermarking.

The exact watermark duration will be selected during implementation based on observed stream behavior rather than assumed in advance.

## 7. Delivery and Fault Tolerance

Kafka will provide durable buffering between the producer and Spark.

The planned architecture will use Kafka acknowledgements and replication to reduce the risk of losing messages when brokers fail.

Spark checkpointing will allow the streaming application to recover its processing state.

The project will not claim exactly-once end-to-end delivery unless this behavior is verified in the implemented pipeline.

## 8. Data Flow Summary

The complete planned flow is:

Binance WebSocket
???????? Python normalization
???????? Kafka `crypto.trades.btcusdt`
-> Spark Structured Streaming
???????? validation and timestamp processing
???????? one-minute aggregation
-> HDFS / Parquet
???????? ML feature generation and prediction

## 9. Current Status

### Implemented

- Binance BTCUSDT WebSocket connection
- Python event collector
- Event normalization
- Trade ID filtering
- JSONL local storage
- Data-source documentation
- Kafka message schema

### Planned

- Kafka broker deployment
- Kafka topic creation
- Kafka producer integration
-> Spark Structured Streaming
- Spark validation and transformation
- Watermarking and late-event handling
- One-minute aggregation
- HDFS/Parquet streaming sink
- ML integration



