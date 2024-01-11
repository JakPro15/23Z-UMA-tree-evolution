from evo_tree import EvoTree
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
import statistics
from typing import Any
from ucimlrepo import fetch_ucirepo, dotdict
from sklearn.model_selection import train_test_split

RANDOM_STATE = 42

def extract_data_uciml(data: dotdict):
    target = data.targets.squeeze()
    attrs = data.features

    x, x_test, y, y_test = train_test_split(
        attrs, target, test_size=0.2, random_state=RANDOM_STATE)

    return (x, y, x_test, y_test)


def prepare_datasets() -> dict[str, tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]]:
    datasets = {}

    datasets["breast_cancer"] = extract_data_uciml(fetch_ucirepo(id=17).data)
    datasets["dry_bean"] = extract_data_uciml(fetch_ucirepo(id=602).data)
    datasets["glass"] = extract_data_uciml(fetch_ucirepo(id=42).data)
    datasets["wine"] = extract_data_uciml(fetch_ucirepo(id=109).data)

    data = pd.read_csv('./datasets/high_diamond_ranked_10min.csv')
    target = data['blueWins']
    attrs = data.drop(columns=['gameId', 'blueWins'])
    x, x_test, y, y_test = train_test_split(
        attrs, target, test_size=0.2, random_state=RANDOM_STATE)
    datasets["lol"] = (x, y, x_test, y_test)

    return datasets

def cross_validate(model: Any, x: pd.DataFrame, y: pd.Series, k=5) -> tuple[float, float, float, float]:
    kf = KFold(n_splits=k)
    scores = []

    for train_index, test_index in kf.split(x):
        x_train, x_test = x.iloc[train_index], x.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        model.fit(x_train, y_train)

        prediction = model.predict(x_test)

        score = accuracy_score(y_test, prediction)
        scores.append(score)

    average_score = statistics.mean(scores)
    std_deviation = statistics.stdev(scores)
    min_score = min(scores)
    max_score = max(scores)

    return average_score, std_deviation, min_score, max_score
