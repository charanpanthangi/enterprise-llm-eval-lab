from src.runners.eval_runner import run_eval


def run_batch(eval_config: dict, models_config: dict, weights: dict, iterations: int = 2) -> list[str]:
    run_ids = []
    for _ in range(iterations):
        run_ids.append(run_eval(eval_config, models_config, weights))
    return run_ids
