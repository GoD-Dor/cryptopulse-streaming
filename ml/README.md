# Machine Learning — CryptoPulse

## Objective
Predict Bitcoin market volatility over the next 5 minutes using real-time Binance trading data.

## Planned ML Pipeline
1. Collect historical BTC/USDT trade data.
2. Aggregate trades into time-based windows using Apache Spark.
3. Extract features from price and volume movements.
4. Train a regression model using Spark MLlib.
5. Evaluate the model using chronological validation.
6. Apply predictions to incoming market data.

## Candidate Features
- Historical price returns
- Trading volume
- Number of trades per minute
- Rolling volatility
- Buy/sell trade imbalance

## Target
Realized volatility over the next 5 minutes.

## Evaluation
- Baseline: previous-window volatility
- Metrics: MAE and RMSE
- Train/test split: chronological to avoid data leakage

## Status
ML design phase. Model training and deployment are planned for later checkpoints.

