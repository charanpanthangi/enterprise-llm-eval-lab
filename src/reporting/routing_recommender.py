import pandas as pd


def recommend_routing(eval_df: pd.DataFrame) -> dict:
    grouped = eval_df.groupby("model_key").agg(
        overall=("overall_score", "mean"),
        cost=("estimated_cost", "mean"),
        latency=("latency_seconds", "mean"),
        reliability=("error", lambda x: (x == "").mean()),
    )
    if grouped.empty:
        return {"strategy": "No data", "recommendation": "Run evaluation first."}

    a, b = grouped.loc["model_a"], grouped.loc["model_b"]
    if b["overall"] > a["overall"] + 0.05 and b["cost"] <= a["cost"] * 1.2:
        return {"strategy": "Case C", "recommendation": "Model B strong winner. Recommend full migration."}
    if b["overall"] > a["overall"] and b["cost"] > a["cost"] * 1.5:
        return {"strategy": "Case A", "recommendation": "Model A default; route complex/premium tasks to Model B."}
    if b["overall"] > a["overall"] and b["reliability"] > a["reliability"]:
        return {"strategy": "Case B", "recommendation": "Use Model B for agentic/tool workflows only."}
    return {"strategy": "Case D", "recommendation": "Route by task type; keep Model A for simple summarization."}
