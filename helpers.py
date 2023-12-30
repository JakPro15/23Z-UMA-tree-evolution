from evo_tree import EvoTree
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
import statistics

RANDOM_STATE = 42


def cross_validate(model: EvoTree, x: pd.DataFrame, y: pd.Series, k=5) -> tuple[float, float, float, float]:
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
