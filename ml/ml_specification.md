# CryptoPulse — Machine Learning Specification

**Project:** Real-Time Cryptocurrency Volatility Prediction  
**Data source:** Binance BTCUSDT Aggregate Trade Stream (`aggTrade`)  
**Technology:** Apache Spark / Spark MLlib  
**Status:** Design phase — Checkpoint 1

---

## 1. Objective and Scope

The objective of CryptoPulse is to forecast short-term Bitcoin market volatility for the BTC/USDT trading pair over a five-minute horizon.

This is a supervised regression and time-series forecasting problem. The model will use historical trading information collected from Binance to estimate the realized volatility expected during the next five minutes.

The system is designed around the following workflow:

1. Collect real-time BTCUSDT aggregate trade events from Binance.
2. Process and aggregate trading events into one-minute observations using Apache Spark.
3. Extract historical price, volume, and trading activity features.
4. Train regression models using Apache Spark MLlib.
5. Evaluate predictions against a chronological baseline.
6. Apply the selected model to newly generated market features.

The forecast is intended for market analysis and volatility monitoring. It does not aim to predict exact future prices or guarantee profitable trading decisions.

**Forecast origin:** The end of minute `t`, once the observations for that minute are available and aggregated.

**Forecast horizon:** The following five one-minute intervals, covering minutes `t+1` through `t+5`.

## 2. Target Definition

### 2.1 One-minute price observations

The raw data comes from Binance's public BTCUSDT aggregate trade WebSocket stream:

`wss://data-stream.binance.vision/ws/btcusdt@aggTrade`

Each event provides information such as:

- Event timestamp.
- Trade timestamp.
- Trade price.
- Trade quantity.
- Aggregate trade ID.
- Buyer-is-maker indicator.

Price and quantity are initially represented as strings and must be converted into appropriate numeric types during processing.

For each UTC minute, the reference price is defined as the price of the last observed aggregate trade within that minute, ordered by trade timestamp and aggregate trade ID.

Let \(P_t\) denote the resulting reference price for minute \(t\).

### 2.2 One-minute logarithmic returns

The one-minute logarithmic return is calculated as:

\[
r*t = \ln\left(\frac{P_t}{P*{t-1}}\right)
\]

Where:

- \(P_t\) is the last observed price during minute \(t\).
- \(P\_{t-1}\) is the reference price from the preceding minute.
- \(r_t\) represents the relative price movement between consecutive minute observations.

Logarithmic returns provide a consistent representation of price movements and are suitable for calculating realized volatility.

### 2.3 Five-minute forward realized volatility

The prediction target is defined as the realized volatility over the next five one-minute intervals:

\[
RV*{t,t+5} =
\sqrt{\sum*{k=1}^{5} r\_{t+k}^{2}}
\]

This target measures the accumulated magnitude of price movements during the five minutes following the forecast origin.

The target is:

- Non-negative.
- Expressed in decimal return units.
- Not annualized.
- Based on five one-minute logarithmic returns.

A larger value indicates greater price variability during the forecast horizon.

**Important:** This target uses future returns. It is therefore a label available only after the five-minute forecast horizon has elapsed. It must never be included in the input features used to generate the prediction at time `t`.

A valid target requires five consecutive valid future one-minute returns. Labels crossing missing observations or significant data gaps should be excluded according to the data-quality policy.

## 3. Input Features

The model will use features computed exclusively from information available at or before the forecast origin.

Candidate features are grouped into the following categories.

### 3.1 Historical price features

- Recent one-minute logarithmic returns.
- Lagged returns at 1, 2, 3, 5, and 10 minutes.
- Mean, minimum, maximum, and last observed price per minute.

These features describe recent price movements and market direction.

### 3.2 Historical volatility features

Rolling realized volatility will be calculated over historical windows:

- Previous 5 minutes.
- Previous 15 minutes.
- Previous 30 minutes.

For a window of length \(W\), trailing realized volatility is defined as:

\[
RV*{t-W+1,t} =
\sqrt{\sum*{i=t-W+1}^{t} r_i^2}
\]

These features provide information about recent market volatility and help the model identify changing volatility regimes.

### 3.3 Trading activity features

The following features will be extracted from the aggregate trade events:

- Number of aggregate trade events per minute.
- Total traded quantity per minute.
- Quote volume (price multiplied by quantity).
- Average trade size.

These indicators describe trading intensity and market activity.

### 3.4 Buy/sell imbalance

The `buyer_is_maker` field can be used to derive an aggressor-side proxy.

Under Binance's field semantics:

- `buyer_is_maker = true`: the buyer is the maker, so the seller is the aggressor.
- `buyer_is_maker = false`: the buyer is the aggressor.

A signed traded-quantity imbalance can therefore be defined as:

\[
Imbalance*t =
\frac{Q*{buy,t}-Q*{sell,t}}
{Q*{buy,t}+Q\_{sell,t}}
\]

Where:

- \(Q\_{buy,t}\) is the quantity associated with buyer-aggressor trades.
- \(Q\_{sell,t}\) is the quantity associated with seller-aggressor trades.

The resulting value ranges from -1 to +1 when total traded quantity is positive.

This feature is a proxy for trade-side pressure, not a direct measurement of order-book imbalance.

### 3.5 Time-based features

UTC time-of-day features may also be considered to capture recurring intraday activity patterns.

All features must be generated using historical observations only. No future aggregates, future returns, or target-derived information may enter the feature vector.

## 4. Data Preparation

The preparation pipeline will transform raw Binance events into a structured dataset suitable for Spark MLlib.

The planned processing stages are:

1. Read historical aggregate trade events from the collected JSONL files.
2. Parse timestamps and convert them consistently to UTC.
3. Convert price and quantity strings into suitable numeric representations.
4. Order events using their trade timestamps and aggregate trade IDs.
5. Detect and handle duplicate aggregate trade IDs.
6. Aggregate events into one-minute UTC windows.
7. Calculate minute-level prices, returns, volumes, and trade counts.
8. Generate historical rolling features and lagged variables.
9. Construct the five-minute forward realized-volatility target.
10. Validate the resulting feature and label dataset.

### Data quality considerations

The processing pipeline must account for:

- Missing or invalid prices and quantities.
- Duplicate aggregate trade IDs.
- Empty one-minute intervals.
- WebSocket disconnections and data gaps.
- Out-of-order events.
- Insufficient historical observations for rolling features.
- Insufficient future observations for target calculation.

Empty minutes must not automatically be treated as genuine zero-return periods.

Forward-filling prices may introduce artificial zero returns and distort realized volatility. Any imputation strategy must therefore be explicitly justified.

Observations with insufficient historical or future data should be excluded where necessary.

The resulting dataset must contain valid chronological observations with clearly defined feature timestamps and forecast targets.

## 5. Candidate Machine Learning Models

The project will evaluate several regression approaches using Apache Spark MLlib.

### 5.1 Baseline model: Persistence

The baseline will predict future realized volatility using the most recent available trailing realized-volatility estimate.

For example:

\[
\widehat{RV}_{t,t+5}^{baseline}
=
RV_{t-4,t}
\]

This baseline provides a simple reference against which more advanced regression models can be evaluated.

### 5.2 Linear Regression

Spark MLlib Linear Regression will be considered as an initial machine learning model.

It provides a relatively simple and interpretable approach for understanding relationships between historical market features and future realized volatility.

### 5.3 Random Forest Regressor

Random Forest Regression will be considered to capture nonlinear relationships between trading activity, historical returns, and volatility.

It can model more complex interactions without requiring a strictly linear relationship between input features and the target.

### 5.4 Gradient-Boosted Tree Regressor

Gradient-Boosted Tree Regression will also be evaluated as a candidate for capturing nonlinear patterns and improving predictive performance.

The final selection will depend on experimental results, computational constraints, and compatibility with the Spark version used by the project.

No model has been trained or selected at this checkpoint.

## 6. Training and Inference Design

### 6.1 Historical training

Model training is planned using curated historical market data stored in HDFS.

Apache Spark will be responsible for:

- Loading historical observations.
- Generating minute-level features and labels.
- Preparing MLlib feature vectors.
- Training candidate regression models.
- Evaluating model performance using chronological validation.

The training process must be reproducible and based on documented data and feature definitions.

### 6.2 Model versioning

Each trained model should be associated with:

- Model version.
- Training period.
- Feature schema version.
- Target definition version.
- Model parameters.
- Evaluation results.

This information will support reproducibility and facilitate future model comparisons.

### 6.3 Real-time inference

After model training and validation, the selected model is intended to generate five-minute volatility forecasts from newly available market features.

The future inference pipeline will consume feature observations produced by the streaming architecture and generate predictions for downstream monitoring.

Integration with Spark Structured Streaming and Kafka will be coordinated with Member 2.

Predictions should include their forecast timestamp and model version so that they can be monitored and evaluated later.

**Current status:** Historical training, model deployment, and real-time inference are planned activities. They are not considered operational at Checkpoint 1.

## 7. Limitations

Several limitations must be considered when interpreting the model's results:

- **Single trading pair:** The current scope focuses exclusively on BTCUSDT.
- **Limited historical period:** A short collection period may not capture all market conditions.
- **Market non-stationarity:** Cryptocurrency volatility patterns can change significantly over time.
- **Data interruptions:** Missing observations and exchange connection failures may affect feature quality and target construction.
- **Model generalization:** Good historical performance does not guarantee reliable future predictions.
- **Computational constraints:** Model complexity must be adapted to the available cluster resources.

The model is intended as a research and monitoring component of CryptoPulse rather than a guaranteed predictor of future market behavior.

---

## 8. Checkpoint 1 Implementation Status

At Checkpoint 1, the ML component is in the design and documentation phase.

| Component                                | Status                             |
| ---------------------------------------- | ---------------------------------- |
| Binance BTCUSDT data collection          | Implemented by Member 1 (reported) |
| Historical data preparation with Spark   | Planned                            |
| Minute-level feature engineering         | Planned                            |
| Five-minute volatility target generation | Specified                          |
| Spark MLlib model training               | Planned                            |
| Model evaluation                         | Methodology specified              |
| Real-time inference                      | Planned                            |
| Kafka/Spark integration                  | Planned with Member 2              |
| Model monitoring                         | Future implementation              |

This specification establishes the technical methodology for the future Machine Learning component of CryptoPulse without claiming that training, inference, or deployment has already been completed.
