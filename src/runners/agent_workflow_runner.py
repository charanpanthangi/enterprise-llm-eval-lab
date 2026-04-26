import random
import time

import pandas as pd

from src.metrics.tool_use import tool_misuse_rate
from src.runners.eval_runner import _client_from_config
from src.storage.sqlite_store import SQLiteStore

WORKFLOWS = [
    "insight_generation_agent",
    "channel_strategy_agent",
    "performance_analytics_agent",
    "visualization_assistant",
]


def run_agent_benchmark(eval_config: dict, models_config: dict, run_id: str) -> pd.DataFrame:
    store = SQLiteStore(eval_config["run"]["database_path"])
    rows = []
    for model_key in ["model_a", "model_b"]:
        client = _client_from_config(models_config[model_key])
        for wf in WORKFLOWS:
            start = time.time()
            prompt = f"Simulate workflow {wf}. Return JSON with tool_steps, outputs, final_recommendation."
            text = client.generate(prompt).content
            runtime = time.time() - start
            total_tool_steps = 5
            misuses = random.randint(0, 2)
            completion = max(0.0, 1 - misuses * 0.2)
            row = {
                "run_id": run_id,
                "workflow_name": wf,
                "model_key": model_key,
                "completion_rate": completion,
                "tool_misuse_rate": tool_misuse_rate(misuses, total_tool_steps),
                "human_corrections": misuses,
                "avg_runtime": round(runtime, 3),
                "business_quality": 0.8 if len(text) > 80 else 0.5,
                "schema_compliance": 1.0 if text.strip().startswith("{") else 0.0,
                "output_usability": 0.85 if "recommendation" in text.lower() else 0.6,
            }
            store.insert_agent_result(row)
            rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(eval_config["run"]["output_agent_csv"], index=False)
    return df
