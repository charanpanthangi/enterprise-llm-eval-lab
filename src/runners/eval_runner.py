import random
import time
import uuid
from datetime import datetime

import pandas as pd

from src.metrics.cost import estimate_cost
from src.metrics.hallucination import hallucination_risk_score
from src.metrics.schema_validation import is_valid_json
from src.model_clients.litellm_client import LiteLLMClient
from src.model_clients.openai_client import OpenAIModelClient
from src.scoring.golden_answer_scorer import score_golden
from src.scoring.llm_judge import JUDGE_DIMENSIONS, judge_output
from src.scoring.pairwise_judge import judge_pairwise
from src.scoring.rule_based_scorer import score_rule_based
from src.scoring.score_aggregator import weighted_score
from src.storage.sqlite_store import SQLiteStore
from src.utils.logger import get_logger
from src.utils.retry import with_retry

logger = get_logger(__name__)


def _client_from_config(config: dict):
    provider = config.get("provider", "openai").lower()
    if provider == "litellm":
        return LiteLLMClient(config)
    return OpenAIModelClient(config)


def _detect_refusal(text: str) -> bool:
    markers = ["i can't", "i cannot", "unable to", "not enough information"]
    lowered = text.lower()
    return any(m in lowered for m in markers)


def run_eval(eval_config: dict, models_config: dict, weights: dict, output_csv: str | None = None) -> str:
    run_id = f"{eval_config['run'].get('run_name', 'run')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    random.seed(eval_config["run"].get("random_seed", 42))

    prompts = pd.read_csv(eval_config["run"]["prompt_csv"])
    golden = pd.read_csv(eval_config["run"]["golden_csv"])
    prompts = prompts.merge(golden, on="prompt_id", how="left", suffixes=("", "_golden"))

    store = SQLiteStore(eval_config["run"]["database_path"])

    model_clients = {k: _client_from_config(v) for k, v in [("model_a", models_config["model_a"]), ("model_b", models_config["model_b"])]}
    judge_client = _client_from_config(models_config.get("judge_model", models_config["model_a"]))

    result_rows = []
    pairwise_rows = []

    for _, prompt_row in prompts.iterrows():
        outputs = {}
        for model_key in ["model_a", "model_b"]:
            mcfg = models_config[model_key]
            client = model_clients[model_key]
            start = time.time()
            error = ""
            retries_used = 0

            def _call_model():
                return client.generate(prompt_row["prompt"])

            try:
                response, retries_used = with_retry(_call_model, retries=mcfg.get("retry_count", 1))
                text = response.content
                in_toks, out_toks = response.input_tokens, response.output_tokens
            except Exception as exc:  # noqa: BLE001
                text = ""
                in_toks, out_toks = 0, 0
                error = str(exc)

            latency = time.time() - start
            cost = estimate_cost(in_toks, out_toks, mcfg.get("input_token_cost", 0), mcfg.get("output_token_cost", 0))
            json_valid = is_valid_json(text) if bool(prompt_row["requires_json"]) else None
            schema_ok = 1 if (json_valid is True or json_valid is None) else 0
            refusal = _detect_refusal(text)

            rule = score_rule_based(text, str(prompt_row["expected_format"]), bool(prompt_row["requires_json"]), str(prompt_row.get("evaluation_notes", "")))
            golden_score = score_golden(text, str(prompt_row.get("golden_answer_golden", "") or prompt_row.get("golden_answer", "")))
            judge = judge_output(judge_client, prompt_row["prompt"], text) if eval_config["scoring"].get("judge_enabled", True) else {k: 3 for k in JUDGE_DIMENSIONS}
            judge_score = sum(float(judge.get(k, 3)) for k in JUDGE_DIMENSIONS) / (5 * len(JUDGE_DIMENSIONS))

            metric_bundle = {
                "quality": judge_score,
                "accuracy": golden_score["golden_score"],
                "latency": max(0.0, 1 - min(latency / 15, 1)),
                "cost": max(0.0, 1 - min(cost / 0.2, 1)),
                "reliability": 0.0 if error else 1.0,
            }
            overall = weighted_score(metric_bundle, weights["default"])

            row = {
                "run_id": run_id,
                "prompt_id": prompt_row["prompt_id"],
                "category": prompt_row["category"],
                "task_type": prompt_row["task_type"],
                "model_key": model_key,
                "model_label": mcfg.get("label", model_key),
                "response_text": text,
                "latency_seconds": round(latency, 3),
                "input_tokens": in_toks,
                "output_tokens": out_toks,
                "estimated_cost": round(cost, 6),
                "retries": retries_used,
                "error": error,
                "requires_json": int(bool(prompt_row["requires_json"])),
                "json_valid": int(json_valid) if json_valid is not None else None,
                "schema_compliant": schema_ok,
                "refusal_detected": int(refusal),
                "rule_score": rule["rule_score"],
                "golden_score": golden_score["golden_score"],
                "judge_score": round(judge_score, 3),
                "overall_score": overall,
            }
            outputs[model_key] = text
            store.insert_eval_result(row)
            result_rows.append(row)

        if eval_config["scoring"].get("pairwise_enabled", True):
            pairwise = judge_pairwise(judge_client, prompt_row["prompt"], outputs["model_a"], outputs["model_b"])
            pair_row = {
                "run_id": run_id,
                "prompt_id": prompt_row["prompt_id"],
                "winner": pairwise.get("winner", "Tie"),
                "reason": pairwise.get("reason", ""),
                "confidence": str(pairwise.get("confidence", "medium")),
                "raw_json": pairwise,
            }
            store.insert_pairwise_result(pair_row)
            pairwise_rows.append(pair_row)

    result_df = pd.DataFrame(result_rows)
    pairwise_df = pd.DataFrame(pairwise_rows)
    out_csv = output_csv or eval_config["run"]["output_results_csv"]
    result_df.to_csv(out_csv, index=False)
    pairwise_df.to_csv(eval_config["run"]["output_pairwise_csv"], index=False)
    logger.info("Completed run_id=%s with %s rows", run_id, len(result_df))
    logger.info("Hallucination avg risk=%.3f", result_df["response_text"].map(hallucination_risk_score).mean())
    return run_id
