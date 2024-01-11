import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from reproduction import *
from succession import *
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


def generate_plots(data: pd.DataFrame, dataset: str):
    for plot_kind in [sns.stripplot, sns.boxplot]:
        for column in data.columns.drop(["accuracy", "std_dev", "min_score", "max_score"]):
            plot_kind(x=column, y="accuracy", data=data)
            plt.title(f"Wpływ hiperparametru {column}\nna zbiorze {dataset}")
            plt.savefig(f"./plots/{column}_{dataset}_{plot_kind.__name__}.png")
            plt.close()


if __name__ == "__main__":

    reproductions = ["proportional", "rank_0.05",
                     "truncation_0.8", "tournament_2"]
    successions = ["generational", "elite_2"]

    datasets = ["breast_cancer", "dry_bean", "glass", "lol", "wine"]
    official_names = {
        "breast_cancer": "breast_cancer_wisconsin_diagnostic",
        "dry_bean": "dry_bean_dataset",
        "glass": "glass_identification",
        "lol": "high_diamond_ranked_10min",
        "wine": "wine",
    }


    with open("./results/best_hyper.csv", "w") as file:
        pass

    for dataset in datasets:
        data = pd.read_csv(f"experiment_results/{dataset}.csv", names=["seed_nr", "max_depth", "reproduction", "mutation_probability",
                           "leaf_inner_swap_probability", "crossover_probability", "succession", "accuracy", "std_dev", "min_score", "max_score"])

        data = aggregate_data(data)

        data["reproduction"] = [reproductions[j] for j in data["reproduction"]]
        data["succession"] = [successions[k] for k in data["succession"]]

        data.to_csv(f"./results/{dataset}.csv", index=False)

        save_best_row(data, dataset)

        generate_plots(data, official_names[dataset])

    id3_datasets = [f"id3_{name}" for name in datasets]

    for dataset in id3_datasets:
        data = pd.read_csv(f"experiment_results/{dataset}.csv", names=["seed_nr", "max_depth", "min_samples_split",
                           "prune", "gain_ratio", "min_entropy_decrease", "repeating", "accuracy", "std_dev", "min_score", "max_score"])

        data = aggregate_data(data)

        data.to_csv(f"./results/{dataset}.csv", index=False)

        save_best_row(data, dataset)
