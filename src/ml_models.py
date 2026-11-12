"""Chronological model comparison and final next-session model selection."""

import numpy as np
import pandas as pd

from src.i18n import t


def _lstm_sequences(features, targets, window=30):
    """Build rolling input windows ending at each corresponding target date."""
    features = np.asarray(features, dtype=float)
    targets = np.asarray(targets, dtype=float)
    if features.ndim != 2 or len(features) != len(targets):
        raise ValueError("LSTM features and targets must have aligned rows.")
    if window < 1:
        raise ValueError("The LSTM window must be a positive number of sessions.")

    target_indices = np.arange(window - 1, len(targets))
    sequences = np.asarray(
        [features[index - window + 1 : index + 1] for index in target_indices]
    )
    return target_indices, sequences, targets[target_indices]


class _NumpyScaler:
    """Small scaler used when scikit-learn is unavailable."""

    def fit(self, values):
        self.mean_ = np.mean(values, axis=0)
        self.scale_ = np.std(values, axis=0)
        self.scale_[self.scale_ == 0] = 1.0
        return self

    def transform(self, values):
        return (np.asarray(values, dtype=float) - self.mean_) / self.scale_


class _NumpyLinearRegression:
    """Minimal linear regression fallback based on least squares."""

    def fit(self, values, target):
        design = np.column_stack([np.ones(len(values)), values])
        self.coef_ = np.linalg.lstsq(design, target, rcond=None)[0]
        return self

    def predict(self, values):
        design = np.column_stack([np.ones(len(values)), values])
        return design @ self.coef_


def _metrics(actual, predicted):
    actual = np.asarray(actual)
    predicted = np.asarray(predicted)
    directional_calls = np.abs(predicted) > 1e-12

    if directional_calls.any():
        directional_accuracy = float(
            np.mean(
                np.sign(actual[directional_calls])
                == np.sign(predicted[directional_calls])
            )
            * 100
        )
    else:
        directional_accuracy = np.nan

    errors = actual - predicted
    return {
        "MAE": float(np.mean(np.abs(errors))),
        "RMSE": float(np.sqrt(np.mean(errors**2))),
        "Directional Accuracy": directional_accuracy,
    }


def _lstm_predict(scaled_features, targets, train_end, test_start, test_end):
    """Train the optional LSTM on earlier rows and predict one validation block."""
    from tensorflow.keras import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout

    window = 30
    # A target at row t is the future return from the close at t, so its input
    # window must include features through t (the same convention as inference).
    target_indices, sequences, sequence_targets = _lstm_sequences(
        scaled_features[:test_end], targets[:test_end], window
    )
    training_mask = target_indices < train_end
    testing_mask = target_indices >= test_start

    if training_mask.sum() < 30 or not testing_mask.any():
        raise ValueError("Not enough sequences for the LSTM model.")

    model = Sequential(
        [
            LSTM(32, input_shape=(window, scaled_features.shape[1])),
            Dropout(0.2),
            Dense(16, activation="relu"),
            Dense(1),
        ]
    )
    model.compile(optimizer="adam", loss="mean_squared_error")
    model.fit(
        sequences[training_mask],
        sequence_targets[training_mask],
        epochs=12,
        batch_size=32,
        verbose=0,
        shuffle=False,
    )

    return (
        target_indices[testing_mask],
        model.predict(sequences[testing_mask], verbose=0).ravel(),
    )


def _make_model_factories():
    """Build the three core estimators, or a linear fallback without sklearn."""
    try:
        from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import StandardScaler

        return StandardScaler, {
            "Régression linéaire": LinearRegression,
            "Forêt aléatoire": lambda: RandomForestRegressor(
                n_estimators=180,
                max_depth=5,
                min_samples_leaf=4,
                random_state=42,
                n_jobs=-1,
            ),
            "Gradient boosting": lambda: GradientBoostingRegressor(
                n_estimators=120,
                learning_rate=0.04,
                max_depth=2,
                min_samples_leaf=4,
                random_state=42,
            ),
        }
    except Exception:
        return _NumpyScaler, {"Régression linéaire (NumPy)": _NumpyLinearRegression}


def compare_models(frame, lang="fr"):
    """Select a model from expanding chronological validation windows."""
    features = frame.drop(columns="Target").to_numpy(dtype=float)
    targets = frame["Target"].to_numpy(dtype=float)
    row_count = len(frame)
    horizon = max(1, int(frame.attrs.get("horizon", 1)))

    if row_count < 75:
        # Smaller pillar-history samples can be used experimentally, while
        # retaining a minimum training window after purging future labels.
        min_train = max(8 + horizon, int(row_count * 0.50))
    else:
        min_train = max(60, int(row_count * 0.50), 8 + horizon)
    fold_count = min(5, (row_count - min_train) // 5)
    if fold_count < 2:
        raise ValueError(
            "Historique trop court pour une validation temporelle fiable. "
            "Choisissez une période plus longue ou un horizon plus court."
        )

    fold_size = (row_count - min_train) // fold_count
    scaler_factory, model_factories = _make_model_factories()
    # The inference sequence for longer horizons would need dated pillar values
    # for every intervening session. Keep LSTM on the next-session horizon only.
    lstm_available = horizon == 1 and _has_tensorflow()

    model_names = list(model_factories)
    if lstm_available:
        model_names.append("LSTM")

    baseline_name = "Référence sans variation"
    out_of_fold = {name: [] for name in [baseline_name, *model_names]}
    actual_parts = []
    date_parts = []
    fold_bounds = []

    for fold in range(fold_count):
        train_end = min_train + fold * fold_size
        # Purge training labels whose future close overlaps the validation period.
        train_label_end = train_end - horizon
        test_end = min(row_count, train_end + fold_size)
        test_size = test_end - train_end
        if test_size < 5 or train_label_end < 8:
            continue

        scaler = scaler_factory().fit(features[:train_label_end])
        scaled_features = scaler.transform(features[:test_end])
        actual_parts.extend(targets[train_end:test_end])
        date_parts.extend(frame.index[train_end:test_end])
        out_of_fold[baseline_name].extend(np.zeros(test_size))
        fold_bounds.append((train_end, test_end))

        for name, factory in model_factories.items():
            model = factory().fit(
                scaled_features[:train_label_end], targets[:train_label_end]
            )
            out_of_fold[name].extend(model.predict(scaled_features[train_end:test_end]))

        if lstm_available:
            try:
                _, predictions = _lstm_predict(
                    scaled_features, targets, train_label_end, train_end, test_end
                )
                if len(predictions) == test_size:
                    out_of_fold["LSTM"].extend(predictions)
                else:
                    lstm_available = False
                    out_of_fold.pop("LSTM", None)
            except Exception:
                lstm_available = False
                out_of_fold.pop("LSTM", None)

    if len(fold_bounds) < 3:
        raise ValueError(t(lang, "horizon_history_error"))

    actual = np.asarray(actual_parts, dtype=float)
    dates = np.asarray(date_parts)
    valid_names = [
        name
        for name in model_names
        if name in out_of_fold and len(out_of_fold[name]) == len(actual)
    ]
    if not valid_names:
        raise ValueError(
            "Aucun modèle n’a pu être évalué sur les fenêtres temporelles."
        )

    predictions = {
        name: np.asarray(out_of_fold[name], dtype=float)
        for name in [baseline_name, *valid_names]
    }
    model_metrics = {
        name: _metrics(actual, values) for name, values in predictions.items()
    }

    baseline_mae = model_metrics[baseline_name]["MAE"]
    # Always show the strongest trained candidate's estimate. Keep the baseline
    # comparison explicit so a weaker model is never presented as a validated win.
    best_name = min(valid_names, key=lambda name: model_metrics[name]["MAE"])
    baseline_beaten = model_metrics[best_name]["MAE"] < baseline_mae
    best_predictions = predictions[best_name]

    # Fit the selected model on labelled history; keep the newest row for inference.
    scaler = scaler_factory().fit(features)
    scaled_history = scaler.transform(features)
    best_model = None
    if best_name not in (baseline_name, "LSTM"):
        best_model = model_factories[best_name]().fit(scaled_history, targets)

    current_features = frame.attrs.get("current_features")
    if current_features is not None:
        last_features = scaler.transform(
            np.asarray(current_features, dtype=float).reshape(1, -1)
        )
    else:
        last_features = scaled_history[-1:]

    feature_effects = []
    if best_model is not None:
        try:
            # Local one-standard-deviation perturbations provide a lightweight,
            # model-agnostic explanation around the current observation.
            names = list(frame.drop(columns="Target").columns)
            baseline_prediction = float(best_model.predict(last_features)[0])
            for index, name in enumerate(names):
                plus, minus = last_features.copy(), last_features.copy()
                plus[0, index] += 0.5
                minus[0, index] -= 0.5
                effect = (
                    float(best_model.predict(plus)[0])
                    - float(best_model.predict(minus)[0])
                ) / 2
                feature_effects.append(
                    {
                        "feature": name,
                        "effect": effect,
                        "direction": (
                            "up"
                            if effect > 1e-10
                            else "down" if effect < -1e-10 else "neutral"
                        ),
                    }
                )
            feature_effects.sort(key=lambda item: abs(item["effect"]), reverse=True)
        except Exception:
            feature_effects = []

    display_names = {
        baseline_name: t(lang, "zero_baseline"),
        "Régression linéaire": t(lang, "linear"),
        "Régression linéaire (NumPy)": t(lang, "linear_numpy"),
        "Forêt aléatoire": t(lang, "forest"),
        "Gradient boosting": t(lang, "boosting"),
        "LSTM": t(lang, "lstm"),
    }
    table_rows = []
    for name, values in model_metrics.items():
        accuracy = values["Directional Accuracy"]
        table_rows.append(
            {
                t(lang, "table_model"): display_names[name],
                t(lang, "metric_mae"): f"{values['MAE']:.4f}",
                t(lang, "metric_rmse"): f"{values['RMSE']:.4f}",
                t(lang, "metric_direction"): (
                    f"{accuracy:.1f}%"
                    if np.isfinite(accuracy)
                    else t(lang, "not_available")
                ),
            }
        )

    residuals = actual - best_predictions
    absolute_residuals = np.sort(np.abs(residuals))

    def conformal_radius(coverage):
        if not len(absolute_residuals):
            return 0.0
        # Finite-sample split-conformal order statistic. Walk-forward residuals
        # are dependent in time, so coverage remains approximate in markets.
        rank = min(
            len(absolute_residuals),
            max(1, int(np.ceil((len(absolute_residuals) + 1) * coverage))),
        )
        return float(absolute_residuals[rank - 1])

    radius_50 = conformal_radius(0.50)
    radius_90 = conformal_radius(0.90)
    error_band = radius_90

    return {
        "metrics": pd.DataFrame(table_rows),
        "best_name": best_name,
        "display_model_name": display_names[best_name],
        "best_model": best_model,
        "scaler": scaler,
        "actual": actual,
        "predicted": best_predictions,
        "dates": dates,
        "last_x": last_features,
        "fold_count": len(fold_bounds),
        "validated_rows": len(actual),
        "error_band": error_band,
        "residuals": residuals,
        "interval_50": radius_50,
        "interval_90": radius_90,
        "feature_effects": feature_effects[:8],
        "benchmark_mae": baseline_mae,
        "baseline_beaten": baseline_beaten,
        "uses_lstm": best_name == "LSTM",
        "lstm_available": lstm_available,
        "horizon": horizon,
    }


def _has_tensorflow():
    """Check whether the optional LSTM dependency is available."""
    try:
        import tensorflow  # noqa: F401

        return True
    except Exception:
        return False
