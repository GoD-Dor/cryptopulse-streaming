# Grafana Dashboard KPI Specification — CryptoPulse

## 1. Objective

This document defines the planned KPIs and visualizations for the CryptoPulse monitoring dashboard.

The dashboard will provide an overview of:

- Bitcoin market activity.
- Market volatility and machine learning predictions.
- Data collection and streaming pipeline health.

**Important:** This document specifies the dashboard design. Grafana deployment and data-source integration are planned for a later project phase.

## 2. Dashboard Structure

The dashboard is organized into three sections.

### Section A — Market Overview

| KPI                   | Definition                                               | Unit       | Visualization |
| --------------------- | -------------------------------------------------------- | ---------- | ------------- |
| Latest BTC/USDT Price | Most recent observed trade price                         | USDT       | Stat          |
| Trading Volume        | Total traded quantity over the selected interval         | BTC        | Time series   |
| Trade Count           | Number of aggregate trades per minute                    | Trades/min | Time series   |
| One-Minute Return     | Logarithmic return between consecutive minute prices     | %          | Time series   |
| Realized Volatility   | Rolling realized volatility over the latest five minutes | Decimal    | Time series   |

**Purpose:** understand recent market activity and identify changes in trading intensity and volatility.

### Section B — Machine Learning Performance

| KPI                  | Definition                                                | Unit    | Visualization      |
| -------------------- | --------------------------------------------------------- | ------- | ------------------ |
| Predicted Volatility | Forecast realized volatility over the next five minutes   | Decimal | Stat / Time series |
| Actual Volatility    | Realized volatility calculated after the forecast horizon | Decimal | Time series        |
| Prediction Error     | Difference between predicted and actual volatility        | Decimal | Time series        |
| Rolling MAE          | Rolling mean absolute prediction error                    | Decimal | Stat / Time series |
| Rolling RMSE         | Rolling root mean squared prediction error                | Decimal | Stat / Time series |
| Model Version        | Identifier of the model currently used for inference      | Text    | Stat               |

**Important:** actual volatility and prediction errors are available only after the five-minute target horizon has elapsed.

**Purpose:** monitor forecast behavior and evaluate model performance over time.

### Section C — Pipeline Health

| KPI                      | Definition                                              | Unit         | Visualization      |
| ------------------------ | ------------------------------------------------------- | ------------ | ------------------ |
| Producer Status          | Whether the market-data producer is operating           | Status       | Stat               |
| Producer Reconnects      | Number of WebSocket reconnections                       | Count        | Time series        |
| Incoming Event Rate      | Number of received trade events per second              | Events/sec   | Time series        |
| Kafka Consumer Lag       | Difference between latest produced and consumed offsets | Messages     | Time series        |
| Spark Processing Latency | Time required to process streaming data                 | ms / seconds | Time series        |
| Spark Throughput         | Number of records processed over time                   | Records/sec  | Time series        |
| Data Gaps                | Missing or delayed market-data intervals                | Count        | Stat / Time series |
| HDFS Storage Status      | Availability of the historical data storage layer       | Status       | Stat               |

**Purpose:** identify collection, ingestion, processing, and storage problems.

## 3. Data Sources and Implementation Dependencies

The following table distinguishes currently available or reported components from future integrations.

| Component                               | Expected Source                              | Dependency / Status                                                         |
| --------------------------------------- | -------------------------------------------- | --------------------------------------------------------------------------- |
| Market price and trade activity         | Raw Binance trade events / producer output   | Producer collection reported by Member 1; metric aggregation still required |
| Producer status and reconnects          | Producer logs or exported metrics            | Requires metric exposure                                                    |
| Kafka consumer lag                      | Kafka consumer-group metrics                 | Requires Kafka integration by Member 2                                      |
| Spark latency and throughput            | Spark streaming metrics                      | Requires Spark processing and metric exposure                               |
| ML predictions                          | Spark MLlib inference output                 | Requires model training and inference                                       |
| Actual volatility and prediction errors | Prediction records joined with future labels | Requires completed target horizons                                          |
| HDFS storage status                     | HDFS metrics                                 | Requires storage integration                                                |

The exact metrics backend and Grafana data source have not yet been selected.

## 4. Dashboard Layout

Proposed layout:

1. **Top row:** latest BTC/USDT price, producer status, predicted volatility, model version.
2. **Market overview:** price evolution, trading volume, trade count, and realized volatility.
3. **ML performance:** predicted versus actual volatility, rolling MAE, and rolling RMSE.
4. **Pipeline health:** incoming event rate, Kafka lag, Spark latency, throughput, data gaps, and HDFS status.

## 5. Time Ranges and Refresh Intervals

Proposed dashboard time ranges:

- Last 15 minutes: real-time operational monitoring.
- Last 1 hour: short-term market and pipeline analysis.
- Last 24 hours: broader activity and performance analysis.

Proposed refresh intervals:

- Market and producer metrics: 5 seconds.
- Kafka and Spark metrics: 5–15 seconds.
- ML performance metrics: 15–30 seconds.

These intervals are design proposals and may be adjusted according to infrastructure capacity and metric availability.

## 6. Potential Alerts

The following alert conditions may be configured after the monitoring infrastructure is available:

- Producer disconnected.
- No incoming market events for a defined period.
- Kafka consumer lag exceeds an agreed threshold.
- Spark processing latency remains abnormally high.
- Missing or delayed data exceeds an agreed threshold.
- Prediction errors show sustained deterioration.

Alert thresholds must be determined from observed system behavior rather than assumed in advance.

## 7. Current Status

| Component                        | Status    |
| -------------------------------- | --------- |
| Dashboard structure              | Specified |
| Market KPIs                      | Specified |
| ML KPIs                          | Specified |
| Pipeline health KPIs             | Specified |
| Data-source integration          | Planned   |
| Grafana dashboard implementation | Planned   |
| Alert configuration              | Planned   |

**Current project phase:** dashboard design and KPI specification. No deployed Grafana dashboard or integrated metrics backend is claimed at this stage.
