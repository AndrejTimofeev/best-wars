import pandas as pd
import matplotlib.pyplot as plt


baseline = pd.read_csv(
    "experiments/results/random_pair_generation/random_baseline.csv"
)

inverse = pd.read_csv(
    "experiments/results/random_pair_generation/inverse_voices.csv"
)

# Нормируем spread относительно среднего количества голосов
baseline["relative_spread"] = baseline["spread"] / baseline["mean"]
inverse["relative_spread"] = inverse["spread"] / inverse["mean"]


fig, axes = plt.subplots(2, 1, figsize=(12, 9))

metrics = [
    ("cv", "Coefficient of variation"),
    ("relative_spread", "Relative spread"),
]

for ax, (metric, title) in zip(axes, metrics):
    ax.plot(
        baseline["votes"],
        baseline[metric],
        label="Random baseline"
    )

    ax.plot(
        inverse["votes"],
        inverse[metric],
        label="Inverse voting"
    )

    ax.set_title(title)
    ax.set_xlabel("Number of votes")
    ax.set_ylabel("Normalized value")
    ax.legend()
    ax.grid()

plt.tight_layout()
# plt.show()
plt.savefig("experiments/results/random_pair_generation/10000")