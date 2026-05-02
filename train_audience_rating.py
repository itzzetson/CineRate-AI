import argparse
import csv
import json
import math
import os
import random
from datetime import datetime
from typing import List, Tuple, Dict, Any

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import make_scorer, mean_squared_error
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.experimental import enable_hist_gradient_boosting  # noqa: F401
from sklearn.ensemble import HistGradientBoostingRegressor


def _is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except Exception:
        return False


def _detect_feature_types(rows: List[Dict[str, str]], target: str) -> Tuple[List[str], List[str]]:
    keys = [k for k in rows[0].keys() if k != target]
    numeric = []
    categorical = []
    for k in keys:
        all_float = True
        for r in rows:
            v = r.get(k, "")
            if v == "":
                continue
            if not _is_float(v):
                all_float = False
                break
        if all_float:
            numeric.append(k)
        else:
            categorical.append(k)
    return numeric, categorical


def _rows_to_xy(rows: List[Dict[str, str]], target: str, numeric: List[str], categorical: List[str]) -> Tuple[List[List[Any]], List[float]]:
    X = []
    y = []
    for r in rows:
        row = []
        for k in numeric:
            v = r.get(k, "")
            row.append(float(v) if v != "" else None)
        for k in categorical:
            row.append(r.get(k, ""))
        tv = r.get(target, "")
        if tv == "":
            continue
        y.append(float(tv))
        X.append(row)
    return X, y


def load_csv_dataset(path: str, target: str) -> Tuple[List[List[Any]], List[float], List[str], List[str]]:
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader]
    numeric, categorical = _detect_feature_types(rows, target)
    X, y = _rows_to_xy(rows, target, numeric, categorical)
    return X, y, numeric, categorical


def generate_synthetic_dataset(path: str, n: int = 2000, seed: int = 42) -> None:
    random.seed(seed)
    genres = ["Action", "Comedy", "Drama", "Horror", "SciFi", "Romance", "Animation"]
    years = list(range(1995, 2026))
    fieldnames = [
        "genre",
        "director_popularity",
        "budget_musd",
        "runtime_min",
        "release_year",
        "social_buzz",
        "critic_score",
        "star_power",
        "audience_rating",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for _ in range(n):
            genre = random.choice(genres)
            director_popularity = max(0.0, min(1.0, random.gauss(0.5, 0.2)))
            budget_musd = max(0.5, random.gauss(30, 15))
            runtime_min = max(70, int(random.gauss(110, 15)))
            release_year = random.choice(years)
            social_buzz = max(0.0, min(1.0, random.gauss(0.5, 0.25)))
            critic_score = max(0.0, min(100.0, random.gauss(65, 15)))
            star_power = max(0.0, min(1.0, random.gauss(0.5, 0.25)))
            base = 4.0
            g_boost = {
                "Action": 0.4,
                "Comedy": 0.3,
                "Drama": 0.5,
                "Horror": -0.2,
                "SciFi": 0.2,
                "Romance": 0.1,
                "Animation": 0.6,
            }[genre]
            year_trend = (release_year - 2000) * 0.01
            popularity_term = director_popularity * 1.2 + star_power * 1.0
            buzz_term = social_buzz * 1.5
            critic_term = critic_score * 0.02
            budget_term = math.log(budget_musd) * 0.3
            runtime_term = -abs(runtime_min - 110) * 0.01
            noise = random.gauss(0, 0.6)
            rating = max(0.0, min(10.0, base + g_boost + year_trend + popularity_term + buzz_term + critic_term + budget_term + runtime_term + noise))
            writer.writerow(
                {
                    "genre": genre,
                    "director_popularity": round(director_popularity, 3),
                    "budget_musd": round(budget_musd, 3),
                    "runtime_min": runtime_min,
                    "release_year": release_year,
                    "social_buzz": round(social_buzz, 3),
                    "critic_score": round(critic_score, 3),
                    "star_power": round(star_power, 3),
                    "audience_rating": round(rating, 3),
                }
            )


def build_preprocessor(numeric: List[str], categorical: List[str]) -> ColumnTransformer:
    num_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    cat_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    transformer = ColumnTransformer(
        transformers=[
            ("num", num_pipe, list(range(len(numeric)))),
            ("cat", cat_pipe, list(range(len(numeric), len(numeric) + len(categorical)))),
        ]
    )
    return transformer


def build_models(preprocessor: ColumnTransformer) -> List[Tuple[str, Pipeline]]:
    models = []
    models.append(("ridge", Pipeline(steps=[("prep", preprocessor), ("est", Ridge(alpha=1.0))])))
    models.append(("svr", Pipeline(steps=[("prep", preprocessor), ("est", SVR(C=2.0, epsilon=0.1, kernel="rbf"))])))
    models.append(("rf", Pipeline(steps=[("prep", preprocessor), ("est", RandomForestRegressor(n_estimators=300, max_depth=None, n_jobs=-1, random_state=42))])))
    models.append(("gbr", Pipeline(steps=[("prep", preprocessor), ("est", GradientBoostingRegressor(random_state=42))])))
    models.append(("hgb", Pipeline(steps=[("prep", preprocessor), ("est", HistGradientBoostingRegressor(max_depth=None, learning_rate=0.06, random_state=42))])))
    return models


def rmse_scorer():
    def rmse(y_true, y_pred):
        return math.sqrt(mean_squared_error(y_true, y_pred))
    return make_scorer(rmse, greater_is_better=False)


def select_best_model(models: List[Tuple[str, Pipeline]], X: List[List[Any]], y: List[float], cv_splits: int) -> Tuple[str, Pipeline, Dict[str, Any]]:
    cv = KFold(n_splits=cv_splits, shuffle=True, random_state=42)
    scoring = rmse_scorer()
    best_name = ""
    best_pipe = None
    best_rmse = float("inf")
    metrics: Dict[str, Any] = {}
    for name, pipe in models:
        scores = cross_val_score(pipe, X, y, scoring=scoring, cv=cv, n_jobs=None)
        rmse = -float(sum(scores)) / float(len(scores))
        metrics[name] = {"cv_rmse": rmse}
        if rmse < best_rmse:
            best_rmse = rmse
            best_name = name
            best_pipe = pipe
    return best_name, best_pipe, {"models": metrics, "best_name": best_name, "best_cv_rmse": best_rmse}


def train_and_save(best_name: str, pipe: Pipeline, X: List[List[Any]], y: List[float], out_dir: str, metrics: Dict[str, Any]) -> str:
    os.makedirs(out_dir, exist_ok=True)
    pipe.fit(X, y)
    model_path = os.path.join(out_dir, "audience_rating_model.joblib")
    joblib.dump({"name": best_name, "pipeline": pipe}, model_path)
    metrics_path = os.path.join(out_dir, "audience_rating_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump({"created_at": datetime.utcnow().isoformat() + "Z", **metrics}, f, indent=2)
    return model_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default="", help="Path to CSV dataset")
    parser.add_argument("--target", type=str, default="audience_rating", help="Target column name")
    parser.add_argument("--cv", type=int, default=5, help="Cross-validation splits")
    parser.add_argument("--output", type=str, default="c:\\Users\\Asus\\Desktop\\Zoho AI\\models", help="Model output directory")
    parser.add_argument("--synth", action="store_true", help="Generate synthetic dataset and use it")
    parser.add_argument("--synth_out", type=str, default="c:\\Users\\Asus\\Desktop\\Zoho AI\\data\\audience_ratings_synth.csv")
    args = parser.parse_args()

    data_path = args.data
    if args.synth or not data_path:
        generate_synthetic_dataset(args.synth_out, n=3000, seed=42)
        data_path = args.synth_out
    X, y, numeric, categorical = load_csv_dataset(data_path, args.target)
    preprocessor = build_preprocessor(numeric, categorical)
    models = build_models(preprocessor)
    best_name, best_pipe, metrics = select_best_model(models, X, y, cv_splits=args.cv)
    model_path = train_and_save(best_name, best_pipe, X, y, args.output, metrics)
    print(json.dumps({"best_model": best_name, "model_path": model_path, "metrics": metrics}, indent=2))


if __name__ == "__main__":
    main()
