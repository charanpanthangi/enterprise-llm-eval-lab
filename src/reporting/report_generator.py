from pathlib import Path

import pandas as pd

from src.reporting.routing_recommender import recommend_routing
from src.storage.sqlite_store import SQLiteStore


def generate_report(eval_config: dict, run_id: str) -> tuple[str, str]:
    store = SQLiteStore(eval_config["run"]["database_path"])
    eval_df = store.query_df(f"SELECT * FROM eval_results WHERE run_id = '{run_id}'")
    pair_df = store.query_df(f"SELECT * FROM pairwise_results WHERE run_id = '{run_id}'")

    if eval_df.empty:
        raise ValueError(f"No rows found for run_id={run_id}")

    recommendation = recommend_routing(eval_df)
    model_summary = eval_df.groupby("model_key")[["overall_score", "judge_score", "estimated_cost", "latency_seconds"]].mean().round(4)
    by_category = eval_df.groupby(["category", "model_key"])["overall_score"].mean().unstack().round(4)
    winner = model_summary["overall_score"].idxmax()
    pairwise_win_rate = (pair_df["winner"] == "B").mean() if not pair_df.empty else 0.0

    report_dir = Path(eval_config["reporting"]["report_dir"])
    report_dir.mkdir(parents=True, exist_ok=True)
    md_path = report_dir / f"report_{run_id}.md"
    csv_path = report_dir / f"report_summary_{run_id}.csv"

    lines = [
        f"# Enterprise LLM Evaluation Report ({run_id})",
        "",
        "## Executive summary",
        f"- Overall winner: **{winner}**",
        f"- Pairwise B win rate: **{pairwise_win_rate:.2%}**",
        f"- Routing strategy: **{recommendation['strategy']}**",
        f"- Recommendation: {recommendation['recommendation']}",
        "",
        "## Evaluation setup",
        "- Two models tested on identical prompts, shared runtime settings, retries, and scoring stack.",
        "",
        "## Prompt categories tested",
        ", ".join(sorted(eval_df["category"].unique())),
        "",
        "## Category-wise winner",
        by_category.to_markdown(),
        "",
        "## Where Model A is better",
        "- See category rows where model_a score > model_b.",
        "",
        "## Where Model B is better",
        "- See category rows where model_b score > model_a.",
        "",
        "## Failure mode analysis",
        f"- Total errors: {int((eval_df['error'] != '').sum())}",
        f"- JSON/schema failures: {int((eval_df['schema_compliant'] == 0).sum())}",
        "",
        "## Hallucination analysis",
        "- Review hallucination trap prompts and refusal behavior columns.",
        "",
        "## Cost-performance analysis",
        model_summary.to_markdown(),
        "",
        "## Operational risks",
        "- Check retry/error trends and latency outliers before migration.",
        "",
        "## Recommended routing strategy",
        f"- {recommendation['recommendation']}",
        "",
        "## Migration recommendation",
        f"- {winner} currently leads on weighted scoring.",
        "",
        "## Limitations",
        "- Sample dataset is limited; expand prompts and use human review before high-stakes rollout.",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")

    summary_df = model_summary.reset_index()
    summary_df.to_csv(csv_path, index=False)
    return str(md_path), str(csv_path)
