"""Create the next-session estimate and an empirical error range."""

import numpy as np


def _predict_lstm_return(frame, results):
    """Retrain the selected LSTM on available history and predict one step ahead."""
    from tensorflow.keras import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout

    features = frame.drop(columns="Target").to_numpy(dtype=float)
    targets = frame["Target"].to_numpy(dtype=float)
    scaled_features = results["scaler"].transform(features)
    window = 30

    sequences = np.asarray(
        [scaled_features[index - window : index] for index in range(window, len(features))]
    )
    sequence_targets = targets[window:]

    model = Sequential(
        [
            LSTM(32, input_shape=(window, features.shape[1])),
            Dropout(0.2),
            Dense(16, activation="relu"),
            Dense(1),
        ]
    )
    model.compile(optimizer="adam", loss="mean_squared_error")
    model.fit(
        sequences,
        sequence_targets,
        epochs=12,
        batch_size=32,
        verbose=0,
        shuffle=False,
    )

    inference_features = frame.attrs.get("inference_sequence_features")
    if inference_features is None or len(inference_features) < window:
        current_features = results["last_x"]
        recent_sequence = np.concatenate(
            [scaled_features[-(window - 1) :], current_features], axis=0
        )
    else:
        recent_sequence = results["scaler"].transform(
            np.asarray(inference_features[-window:], dtype=float)
        )
    return float(model.predict(recent_sequence[None, ...], verbose=0)[0, 0])


def forecast_next_close(frame, results):
    """Return an indicative horizon close and validation-based error range."""
    model_name = results["best_name"]

    if model_name == "Référence sans variation":
        predicted_return = 0.0
    elif model_name == "LSTM":
        predicted_return = _predict_lstm_return(frame, results)
    else:
        predicted_return = float(results["best_model"].predict(results["last_x"])[0])

    current_close = float(frame.attrs.get("current_close", frame["Close"].iloc[-1]))
    predicted_price = current_close * (1 + predicted_return)
    residuals = np.asarray(results.get("residuals", []), dtype=float)
    residuals = residuals[np.isfinite(residuals)]
    band_50 = float(results.get("interval_50", results.get("error_band", 0.0)))
    band_90 = float(results.get("interval_90", results.get("error_band", 0.0)))
    lower_50, upper_50 = predicted_return - band_50, predicted_return + band_50
    lower_90, upper_90 = predicted_return - band_90, predicted_return + band_90
    probability_up = float(np.mean(predicted_return + residuals > 0)) if len(residuals) else 0.5

    return {
        "return": predicted_return,
        "price": current_close * (1 + predicted_return),
        "current_price": current_close,
        "price_change": predicted_price - current_close,
        "change": predicted_return * 100,
        "horizon": int(results.get("horizon", frame.attrs.get("horizon", 1))),
        "model": results["display_model_name"],
        "model_key": model_name,
        "error_band": band_90,
        "lower_price": max(0.0, current_close * (1 + lower_90)),
        "upper_price": max(0.0, current_close * (1 + upper_90)),
        "interval_50_low": max(0.0, current_close * (1 + lower_50)),
        "interval_50_high": max(0.0, current_close * (1 + upper_50)),
        "interval_90_low": max(0.0, current_close * (1 + lower_90)),
        "interval_90_high": max(0.0, current_close * (1 + upper_90)),
        "probability_up": probability_up,
        "probability_down": 1 - probability_up,
        "feature_effects": results.get("feature_effects", []),
        "interval_note": "Finite-sample conformal order-statistic radii calibrated on walk-forward residuals; temporal dependence makes coverage approximate.",
    }
