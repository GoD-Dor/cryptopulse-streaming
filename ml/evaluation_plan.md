# ML Model Evaluation Plan — CryptoPulse

## 1. Objective

This document defines the evaluation strategy for the CryptoPulse machine learning model.

The objective is to evaluate the model's ability to forecast BTC/USDT realized volatility over the next five minutes.

The evaluation will focus on prediction accuracy, generalization to unseen market data, and comparison against a simple baseline.

## 2. Evaluation Strategy

A chronological data split will be used to preserve the time order of market observations.

The dataset will be divided into:

- **Training set:** used to train the candidate models.
- **Validation set:** used for model selection and hyperparameter tuning.
- **Test set:** used for the final unbiased evaluation.

Random shuffling will not be used because it could introduce temporal data leakage.

Since the target uses future five-minute returns, observations around dataset split boundaries must be excluded or handled with an appropriate time gap. This prevents information from the future from leaking into training or validation.

All preprocessing parameters must be fitted using training data only.

## 3. Baseline Model

A persistence baseline will be implemented before evaluating more complex models.

The baseline will predict the next five-minute realized volatility using the most recent available trailing volatility estimate.

This provides a simple reference to determine whether machine learning models bring measurable improvements.

## 4. Evaluation Metrics

The following metrics will be used:

| Metric        | Purpose                                                                   |
| ------------- | ------------------------------------------------------------------------- |
| MAE           | Measures the average absolute prediction error.                           |
| RMSE          | Penalizes large prediction errors more strongly.                          |
| R² (optional) | Measures explained variance, with caution for non-stationary time series. |

All candidate models must be evaluated using the same held-out test period and target definition.

## 5. Model Comparison

The following models are planned for comparison:

1. Persistence baseline.
2. Linear Regression.
3. Random Forest Regressor.
4. Gradient-Boosted Tree Regressor.

Model selection will be based primarily on validation performance.

The final test set must not be used for hyperparameter tuning.

The implementation will use Spark MLlib, subject to compatibility with the Spark version selected by the project.

## 6. Robustness Checks

Additional analyses are planned to assess model reliability:

- Compare performance across different market periods.
- Examine prediction errors during periods of high and low volatility.
- Check the impact of missing or delayed market events.
- Verify that features are available at prediction time.
- Consider walk-forward validation in a later project iteration.

## 7. Monitoring Strategy

When streaming inference is implemented, the following information should be monitored:

- Predicted five-minute realized volatility.
- Actual realized volatility once the five-minute target horizon is complete.
- Rolling MAE and RMSE once actual labels become available.
- Model version and prediction timestamp.
- Missing features and data-quality issues.

Prediction errors cannot be calculated immediately because the actual future volatility is not known at prediction time.

Monitoring thresholds will be defined after collecting sufficient baseline observations.

## 8. Current Status

| Component              | Status     |
| ---------------------- | ---------- |
| Evaluation strategy    | Specified  |
| Baseline definition    | Specified  |
| Evaluation metrics     | Specified  |
| Candidate models       | Identified |
| Model training         | Planned    |
| Model comparison       | Planned    |
| Streaming evaluation   | Planned    |
| Performance monitoring | Planned    |

**Current project phase:** ML design and evaluation planning. No trained or deployed model is claimed at this stage.
