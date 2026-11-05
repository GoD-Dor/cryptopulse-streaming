# Kafka Streaming Architecture

This module defines the planned Kafka streaming layer for CryptoPulse.

## Responsibilities

- Receive normalized Binance market-data events from the producer.
- Publish normalized events to Kafka.
- Define Kafka topic, message key, partitions, and replication.
- Provide durable buffering between the producer and Spark Structured Streaming.
- Support reliable event delivery and downstream consumption.

## Planned Kafka Topic

- Topic: `crypto.trades.btcusdt`
- Message key: `BTCUSDT`
- Message format: JSON
- Planned partitions: 1
- Planned replication factor: 3 if three Kafka brokers are available
- Event time: Binance exchange timestamp in UTC

The current project uses one BTCUSDT stream, so one partition is sufficient for the planned initial architecture. If multiple symbols are added later, partitioning by symbol can be considered.

## Message Schema

Kafka messages will contain the normalized Binance aggregated-trade event defined in:

`kafka/message_schema.json`

The schema contains 11 required fields and uses JSON Schema Draft 2020-12.

## Spark Integration

Spark Structured Streaming is planned as the Kafka consumer.

- Consumer group: `cryptopulse-spark`
- Event-time processing will be used for time-based windows.
- Watermarking will be used to handle late-arriving events.
- Spark checkpoints will support streaming recovery.

## Status

Kafka deployment and topic creation are planned for a later implementation stage.

Currently implemented:

- Kafka message schema
- Kafka streaming architecture documentation

Not yet implemented:

- Kafka brokers
- Kafka topic deployment
- Kafka producer integration
- Spark Structured Streaming consumer
