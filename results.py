import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from reproduction import *
from succesion import *
from numpy import sqrt


def get_std_dev(accuracy: pd.Series, accuracy_square: pd.Series, std_dev_square: pd.Series):
    first_part = 4 * std_dev_square
    second_part = 125 * (accuracy ** 2)
    third_part = 5 * accuracy_square
    return sqrt((first_part - second_part + third_part) / 124)


def aggregate_data(data: pd.DataFrame) -> pd.DataFrame:
    data["accuracy_square"] = data["accuracy"].apply(lambda x: x ** 2)
    data["std_dev_square"] = data["std_dev"].apply(lambda x: x ** 2)

    data = data.drop(columns="std_dev")

    data = data.groupby(list(data.drop(columns=["seed_nr", "accuracy", "min_score", "max_score", "accuracy_square", "std_dev_square"]).columns)).agg({
        "accuracy": "mean",
        "min_score": "min",
        "max_score": "max",
        "accuracy_square": "sum",
        "std_dev_square": "sum"
    }).reset_index()

    data["std_dev"] = get_std_dev(
        data["accuracy"], data["accuracy_square"], data["std_dev_square"])

    data = data.drop(columns=["accuracy_square", "std_dev_square"])

    return data


def save_best_row(data: pd.DataFrame, dataset: str):
    best_row = data[data['accuracy'] == data['accuracy'].max()]

    with open("./results/best_hyper.csv", "a+") as file:
        for field in best_row.columns:
            file.write(f"{best_row[field].iloc[0]},")
        file.write(f"{dataset}\n")


def generate_plots(data: pd.DataFrame):
    for plot_kind in [sns.stripplot, sns.boxplot]:
        for column in data.columns.drop(["accuracy", "std_dev", "min_score", "max_score"]):
            plot_kind(x=column, y="accuracy", data=data)
            plt.title(f"Accuracy for: {column}")
            plt.savefig(f"./plots/{dataset}_{column}_{plot_kind.__name__}.png")
            plt.close()


if __name__ == "__main__":

    reproductions = ["proportional", "rank_0.05",
                     "truncation_0.8", "tournament_2"]
    succesions = ["generational", "elite_2"]

    datasets = ["breast_cancer", "dry_bean", "glass", "lol", "wine"]

    for dataset in datasets:
        data = pd.read_csv(f"experiment_results/{dataset}.csv", names=["seed_nr", "max_depth", "reproduction", "mutation_probability",
                           "leaf_inner_swap_probabilty", "crossover_probability", "succesion", "accuracy", "std_dev", "min_score", "max_score"])

        data = aggregate_data(data)

        data["reproduction"] = [reproductions[j] for j in data["reproduction"]]
        data["succesion"] = [succesions[k] for k in data["succesion"]]

        data.to_csv(f"./results/{dataset}.csv", index=False)

        save_best_row(data, dataset)

        generate_plots(data)

    id3_datasets = [f"id3_{name}" for name in datasets]

    for dataset in id3_datasets:
        data = pd.read_csv(f"experiment_results/{dataset}.csv", names=["seed_nr", "max_depth", "min_samples_split",
                           "prune", "gain_ratio", "min_entropy_decrease", "repeating", "accuracy", "std_dev", "min_score", "max_score"])

        data = aggregate_data(data)

        data.to_csv(f"./results/{dataset}.csv", index=False)

        save_best_row(data, dataset)

        generate_plots(data)
