import argparse

from src.reporting.report_generator import generate_report
from src.runners.agent_workflow_runner import run_agent_benchmark
from src.runners.eval_runner import run_eval
from src.runners.multi_turn_runner import run_multiturn
from src.utils.config_loader import load_env, load_yaml
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _load_all(config_path: str) -> tuple[dict, dict, dict]:
    eval_config = load_yaml(config_path)
    models_config = load_yaml("config/models.yaml")
    scoring_weights = load_yaml(eval_config["scoring"]["weights_file"])
    return eval_config, models_config, scoring_weights


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Enterprise LLM Evaluation Lab")
    sub = parser.add_subparsers(dest="command", required=True)

    run_eval_parser = sub.add_parser("run-eval")
    run_eval_parser.add_argument("--config", required=True)

    run_multiturn_parser = sub.add_parser("run-multiturn")
    run_multiturn_parser.add_argument("--config", required=True)

    run_agent_parser = sub.add_parser("run-agent-benchmark")
    run_agent_parser.add_argument("--config", required=True)

    report_parser = sub.add_parser("generate-report")
    report_parser.add_argument("--config", default="config/eval_config.yaml")
    report_parser.add_argument("--run-id", required=True)

    args = parser.parse_args()

    if args.command == "run-eval":
        eval_config, models_config, scoring_weights = _load_all(args.config)
        run_id = run_eval(eval_config, models_config, scoring_weights)
        logger.info("run_id=%s", run_id)

    elif args.command == "run-multiturn":
        eval_config, models_config, _ = _load_all(args.config)
        rows = run_multiturn(eval_config, models_config)
        logger.info("multiturn_rows=%s", len(rows))

    elif args.command == "run-agent-benchmark":
        eval_config, models_config, scoring_weights = _load_all(args.config)
        run_id = run_eval(eval_config, models_config, scoring_weights)
        df = run_agent_benchmark(eval_config, models_config, run_id)
        logger.info("agent_rows=%s", len(df))

    elif args.command == "generate-report":
        eval_config, _, _ = _load_all(args.config)
        md_path, csv_path = generate_report(eval_config, args.run_id)
        logger.info("report=%s summary=%s", md_path, csv_path)


if __name__ == "__main__":
    main()
