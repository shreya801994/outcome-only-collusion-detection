import pandas as pd

from detectors import deviation_response_score


auditor = pd.read_csv(
    "data/dynamic_auditor_trajectories.csv"
)

results = []

for run_id, group in auditor.groupby("run_id"):
    group = group.sort_values("period").reset_index(drop=True)

    results.append({
        "run_id": run_id,
        "b3_score": deviation_response_score(group),
    })

result_df = pd.DataFrame(results)

print(result_df)

print("\nOverall mean B3:")
print(result_df["b3_score"].mean())