"""Leakage-aware holdout evaluation for next-session stock price estimates."""

import numpy as np
import pandas as pd

from src.ml_models import _NumpyLinearRegression, _NumpyScaler

MIN_TRAIN_ROWS = 60
MIN_VALIDATION_ROWS = 10
MIN_TEST_ROWS = 10


def calculate_price_metrics(actual, predicted, previous_close, mase_scale=None):
    """Calculate price error and direction metrics for aligned observations."""
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    previous_close = np.asarray(previous_close, dtype=float)
    valid = np.isfinite(actual) & np.isfinite(predicted) & np.isfinite(previous_close)
    actual, predicted, previous_close = (
        actual[valid],
        predicted[valid],
        previous_close[valid],
    )
    if not len(actual):
        raise ValueError("No valid actual/predicted price pairs are available.")

    errors = predicted - actual
    denominators = np.abs(actual)
    mape_floor = max(1e-8, float(np.median(denominators)) * 1e-6)
    mape_valid = denominators > mape_floor
    mape = (
        float(np.mean(np.abs(errors[mape_valid] / actual[mape_valid])) * 100)
        if mape_valid.any()
        else np.nan
    )
    mase = (
        float(np.mean(np.abs(errors)) / mase_scale)
        if mase_scale is not None and np.isfinite(mase_scale) and mase_scale > 0
        else np.nan
    )
    actual_direction = np.sign(actual - previous_close)
    predicted_direction = np.sign(predicted - previous_close)
    return {
        "MAE": float(np.mean(np.abs(errors))),
        "RMSE": float(np.sqrt(np.mean(errors**2))),
        "MAPE": mape,
        "MASE": mase,
        "mape_count": int(mape_valid.sum()),
        "count": int(len(actual)),
        "Directional Accuracy": float(
            np.mean(actual_direction == predicted_direction) * 100
        ),
    }


def _aligned_data(frame, prices):
    if frame is None or frame.empty or "Target" not in frame:
        raise ValueError("no_labelled_rows")
    if prices is None or "Close" not in prices:
        raise ValueError("no_closing_prices")
    rows = frame.replace([np.inf, -np.inf], np.nan).dropna().copy()
    if rows.empty:
        raise ValueError("no_feature_rows")
    close = prices["Close"].astype(float)
    previous = close.reindex(rows.index).to_numpy(dtype=float)
    actual = close.shift(-1).reindex(rows.index).to_numpy(dtype=float)
    target_dates = (
        pd.Series(prices.index, index=prices.index).shift(-1).reindex(rows.index)
    )
    returns = rows["Target"].to_numpy(dtype=float)
    mask = (
        np.isfinite(previous)
        & np.isfinite(actual)
        & (previous > 0)
        & np.isfinite(returns)
    )
    rows = rows.iloc[np.flatnonzero(mask)].copy()
    target_dates = target_dates.iloc[np.flatnonzero(mask)]
    if rows.empty:
        raise ValueError("no_aligned_prices")
    return (
        rows,
        rows.drop(columns="Target").to_numpy(dtype=float),
        rows["Target"].to_numpy(dtype=float),
        previous[mask],
        actual[mask],
        target_dates,
    )


def _validation_selection(
    factories, x, returns, previous, actual, train_end, validation_end
):
    results = {}
    for name, factory in factories.items():
        try:
            predicted_return = _fit_predict(
                factory, x[:train_end], returns[:train_end], x[train_end:validation_end]
            )
            predicted_price = previous[train_end:validation_end] * (
                1 + predicted_return
            )
            results[name] = float(
                np.mean(np.abs(predicted_price - actual[train_end:validation_end]))
            )
        except Exception:
            continue
    if not results:
        raise ValueError("no_validation_model")
    return min(results, key=results.get), results


def _prediction_rows(
    dates, actual, previous, predicted_return, mean_return, selected_model, fold=None
):
    predicted = previous * (1 + predicted_return)
    mean_predicted = previous * (1 + mean_return)
    actual_return = actual / previous - 1
    predicted_return_error = (predicted_return - actual_return) * 100
    data = {
        "Date": dates,
        "Actual close": actual,
        "Predicted close": predicted,
        "Last-close baseline": previous,
        "Mean-return baseline": mean_predicted,
        "Predicted return (fraction)": predicted_return,
        "Actual return (%)": actual_return * 100,
        "Predicted return (%)": predicted_return * 100,
        "Return error (percentage points)": predicted_return_error,
        "Error": predicted - actual,
        "Absolute error": np.abs(predicted - actual),
        "Percentage error": np.where(
            np.abs(actual) > 1e-8, (predicted - actual) / actual * 100, np.nan
        ),
        "Direction correct": np.sign(predicted_return) == np.sign(actual_return),
        "Selected model": [selected_model] * len(actual),
    }
    if fold is not None:
        data["Fold"] = [fold] * len(actual)
    return pd.DataFrame(data)


def _benchmark_returns(previous_close, start, end):
    """Create causal always-up and 20-session price-average forecasts."""
    previous_close = np.asarray(previous_close, dtype=float)
    always_up = []
    moving_average = []
    for index in range(start, end):
        history = previous_close[max(0, index - 20) : index + 1]
        returns = (
            np.diff(history) / history[:-1] if len(history) > 1 else np.asarray([])
        )
        magnitude = float(np.median(np.abs(returns))) if len(returns) else 0.0
        always_up.append(magnitude)
        moving_average.append(
            float(np.mean(history[-20:]) / history[-1] - 1) if len(history) else 0.0
        )
    return np.asarray(always_up), np.asarray(moving_average)


def _backtest_metrics(predicted_return, actual_return, fee_bps=10, slippage_bps=5):
    """Long-or-cash daily strategy with entry/exit costs and slippage."""
    predicted_return = np.asarray(predicted_return, dtype=float)
    actual_return = np.asarray(actual_return, dtype=float)
    position = (predicted_return > 0).astype(float)
    turnover = np.abs(np.diff(np.r_[0.0, position]))
    # Close any open position at the end of each out-of-sample test stream.
    if len(turnover):
        turnover[-1] += position[-1]
    cost = turnover * ((fee_bps + slippage_bps) / 10000)
    net = position * actual_return - cost
    equity = np.cumprod(1 + net)
    peaks = np.maximum.accumulate(np.r_[1.0, equity])[1:]
    drawdown = equity / peaks - 1 if len(equity) else np.asarray([])
    sharpe = (
        float(np.mean(net) / np.std(net, ddof=1) * np.sqrt(252))
        if len(net) > 1 and np.std(net, ddof=1) > 0
        else np.nan
    )
    active = position > 0
    return {
        "Sharpe": sharpe,
        "Max Drawdown": float(np.min(drawdown)) if len(drawdown) else np.nan,
        "Win Rate": float(np.mean(net[active] > 0) * 100) if active.any() else np.nan,
        "Net Return": float((equity[-1] - 1) * 100) if len(equity) else 0.0,
        "Trades": int(turnover.sum()),
        "Fees bps": fee_bps,
        "Slippage bps": slippage_bps,
    }


def _candidate_models():
    try:
        from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
        from sklearn.linear_model import LinearRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler

        return {
            "Régression linéaire": lambda: make_pipeline(
                StandardScaler(), LinearRegression()
            ),
            "Forêt aléatoire": lambda: make_pipeline(
                StandardScaler(),
                RandomForestRegressor(
                    n_estimators=180,
                    max_depth=5,
                    min_samples_leaf=4,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
            "Gradient boosting": lambda: make_pipeline(
                StandardScaler(),
                GradientBoostingRegressor(
                    n_estimators=120,
                    learning_rate=0.04,
                    max_depth=2,
                    min_samples_leaf=4,
                    random_state=42,
                ),
            ),
        }
    except Exception:
        # Keep the evaluation usable in the same restricted environments supported
        # by the existing forecasting module.
        return {
            "Régression linéaire (NumPy)": lambda: (
                _NumpyScaler(),
                _NumpyLinearRegression(),
            )
        }


def _fit_predict(factory, train_x, train_y, predict_x):
    model = factory()
    if isinstance(model, tuple):
        scaler, estimator = model
        scaler.fit(train_x)
        estimator.fit(scaler.transform(train_x), train_y)
        return estimator.predict(scaler.transform(predict_x))
    model.fit(train_x, train_y)
    return model.predict(predict_x)


def evaluate_holdout(frame, prices):
    """Select on chronological validation, then score once on a later holdout.

    Features at date t predict the close at t+1. Scaling and model fitting use
    only training data; validation selects the model; the final test stays unseen.
    """
    rows, x, returns, previous_close, next_close, next_dates = _aligned_data(
        frame, prices
    )
    n = len(rows)
    train_end = int(n * 0.65)
    test_start = int(n * 0.80)
    if (
        train_end < MIN_TRAIN_ROWS
        or test_start - train_end < MIN_VALIDATION_ROWS
        or n - test_start < MIN_TEST_ROWS
    ):
        raise ValueError("not_enough_history")

    factories = _candidate_models()
    selected_name, validation_results = _validation_selection(
        factories, x, returns, previous_close, next_close, train_end, test_start
    )
    baseline_validation = previous_close[train_end:test_start]
    validation_actual = next_close[train_end:test_start]
    benchmark_validation_mae = float(
        np.mean(np.abs(baseline_validation - validation_actual))
    )
    test_previous = previous_close[test_start:]
    test_actual = next_close[test_start:]
    test_return = _fit_predict(
        factories[selected_name], x[:test_start], returns[:test_start], x[test_start:]
    )
    mean_return = float(np.mean(returns[:test_start]))
    training_naive_scale = float(
        np.mean(np.abs(next_close[:train_end] - previous_close[:train_end]))
    )
    test_dates = next_dates.iloc[test_start:].to_numpy()
    always_up, sma_return = _benchmark_returns(previous_close, test_start, len(rows))
    output = _prediction_rows(
        test_dates, test_actual, test_previous, test_return, mean_return, selected_name
    )
    output["Always-up baseline"] = test_previous * (1 + always_up)
    output["Moving-average baseline"] = test_previous * (1 + sma_return)
    model_metrics = calculate_price_metrics(
        test_actual, output["Predicted close"], test_previous, training_naive_scale
    )
    baseline_metrics = calculate_price_metrics(
        test_actual, test_previous, test_previous, training_naive_scale
    )
    mean_baseline_metrics = calculate_price_metrics(
        test_actual, output["Mean-return baseline"], test_previous, training_naive_scale
    )
    always_up_metrics = calculate_price_metrics(
        test_actual, output["Always-up baseline"], test_previous, training_naive_scale
    )
    sma_metrics = calculate_price_metrics(
        test_actual,
        output["Moving-average baseline"],
        test_previous,
        training_naive_scale,
    )
    mean_validation_return = float(np.mean(returns[:train_end]))
    mean_validation_predicted = previous_close[train_end:test_start] * (
        1 + mean_validation_return
    )
    mean_validation_mae = float(
        np.mean(np.abs(mean_validation_predicted - validation_actual))
    )
    return {
        "model_key": selected_name,
        "rows": output,
        "metrics": model_metrics,
        "baseline_metrics": baseline_metrics,
        "mean_baseline_metrics": mean_baseline_metrics,
        "always_up_metrics": always_up_metrics,
        "sma_metrics": sma_metrics,
        "backtest": _backtest_metrics(
            test_return, actual_return=test_actual / test_previous - 1
        ),
        "validation_model_mae": validation_results.get(selected_name),
        "validation_baseline_mae": benchmark_validation_mae,
        "validation_mean_return_mae": mean_validation_mae,
        "train_count": int(train_end),
        "validation_count": int(test_start - train_end),
        "test_count": int(len(output)),
        "period_start": output["Date"].iloc[0],
        "period_end": output["Date"].iloc[-1],
    }


def evaluate_walk_forward(frame, prices, requested_folds=4):
    """Produce non-overlapping out-of-sample blocks with expanding training data.

    Each block's model is selected on a validation slice immediately before that
    block, then refit on all observations available before its test dates.
    """
    rows, x, returns, previous, actual, target_dates = _aligned_data(frame, prices)
    n = len(rows)
    first_test_start = max(int(n * 0.50), MIN_TRAIN_ROWS + MIN_VALIDATION_ROWS)
    remaining = n - first_test_start
    fold_count = min(requested_folds, remaining // MIN_TEST_ROWS)
    if fold_count < 3:
        raise ValueError("not_enough_walk_forward_history")
    block_size = remaining // fold_count
    factories = _candidate_models()
    output_parts = []
    mase_scales = []
    for fold in range(fold_count):
        test_start = first_test_start + fold * block_size
        test_end = n if fold == fold_count - 1 else min(n, test_start + block_size)
        validation_size = max(MIN_VALIDATION_ROWS, int(test_start * 0.15))
        train_end = test_start - validation_size
        if train_end < MIN_TRAIN_ROWS or test_end - test_start < MIN_TEST_ROWS:
            continue
        selected_name, _ = _validation_selection(
            factories, x, returns, previous, actual, train_end, test_start
        )
        predicted_return = _fit_predict(
            factories[selected_name],
            x[:test_start],
            returns[:test_start],
            x[test_start:test_end],
        )
        mean_return = float(np.mean(returns[:test_start]))
        scale = float(np.mean(np.abs(actual[:train_end] - previous[:train_end])))
        mase_scales.append((scale, test_end - test_start))
        output = _prediction_rows(
            target_dates.iloc[test_start:test_end].to_numpy(),
            actual[test_start:test_end],
            previous[test_start:test_end],
            predicted_return,
            mean_return,
            selected_name,
            fold + 1,
        )
        always_up, sma_return = _benchmark_returns(previous, test_start, test_end)
        output["Always-up baseline"] = previous[test_start:test_end] * (1 + always_up)
        output["Moving-average baseline"] = previous[test_start:test_end] * (
            1 + sma_return
        )
        output_parts.append(output)
    if len(output_parts) < 3:
        raise ValueError("not_enough_walk_forward_history")
    output = pd.concat(output_parts, ignore_index=True)
    actual_oof = output["Actual close"].to_numpy(dtype=float)
    previous_oof = output["Last-close baseline"].to_numpy(dtype=float)
    weighted_scale = float(
        np.average(
            [item[0] for item in mase_scales], weights=[item[1] for item in mase_scales]
        )
    )
    model_metrics = calculate_price_metrics(
        actual_oof, output["Predicted close"], previous_oof, weighted_scale
    )
    last_close_metrics = calculate_price_metrics(
        actual_oof, output["Last-close baseline"], previous_oof, weighted_scale
    )
    mean_return_metrics = calculate_price_metrics(
        actual_oof, output["Mean-return baseline"], previous_oof, weighted_scale
    )
    always_up_metrics = calculate_price_metrics(
        actual_oof, output["Always-up baseline"], previous_oof, weighted_scale
    )
    sma_metrics = calculate_price_metrics(
        actual_oof, output["Moving-average baseline"], previous_oof, weighted_scale
    )
    backtest = _backtest_metrics(
        output["Predicted return (fraction)"], actual_oof / previous_oof - 1
    )
    return {
        "rows": output,
        "metrics": model_metrics,
        "baseline_metrics": last_close_metrics,
        "mean_baseline_metrics": mean_return_metrics,
        "fold_count": int(output["Fold"].nunique()),
        "always_up_metrics": always_up_metrics,
        "sma_metrics": sma_metrics,
        "backtest": backtest,
        "test_count": int(len(output)),
        "period_start": output["Date"].iloc[0],
        "period_end": output["Date"].iloc[-1],
    }
