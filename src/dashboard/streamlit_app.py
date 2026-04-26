import pandas as pd
import streamlit as st

from src.reporting.routing_recommender import recommend_routing
from src.storage.sqlite_store import SQLiteStore

st.set_page_config(page_title="Enterprise LLM Eval Lab", layout="wide")
st.title("Enterprise LLM Evaluation Dashboard")

db_path = st.sidebar.text_input("SQLite DB Path", "outputs/results/eval_results.db")
run_id = st.sidebar.text_input("Run ID")

if run_id:
    store = SQLiteStore(db_path)
    eval_df = store.query_df(f"SELECT * FROM eval_results WHERE run_id='{run_id}'")
    pair_df = store.query_df(f"SELECT * FROM pairwise_results WHERE run_id='{run_id}'")

    if eval_df.empty:
        st.warning("No data for this run_id.")
    else:
        st.subheader("Overall winner")
        model_scores = eval_df.groupby("model_key")["overall_score"].mean().sort_values(ascending=False)
        st.metric("Winner", model_scores.index[0], f"Score {model_scores.iloc[0]:.3f}")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Pairwise B win rate", f"{((pair_df['winner'] == 'B').mean() if not pair_df.empty else 0):.1%}")
        with c2:
            st.metric("JSON/schema failures", int((eval_df["schema_compliant"] == 0).sum()))
        with c3:
            st.metric("Avg latency (s)", f"{eval_df['latency_seconds'].mean():.2f}")

        st.subheader("Score comparison by category")
        st.dataframe(eval_df.pivot_table(index="category", columns="model_key", values="overall_score", aggfunc="mean"))

        st.subheader("Task type comparison")
        st.dataframe(eval_df.pivot_table(index="task_type", columns="model_key", values="overall_score", aggfunc="mean"))

        st.subheader("Operational metrics")
        st.dataframe(eval_df.groupby("model_key")[["latency_seconds", "input_tokens", "output_tokens", "estimated_cost", "retries"]].mean())

        st.subheader("Prompt-level drilldown")
        prompt_id = st.selectbox("Prompt ID", sorted(eval_df["prompt_id"].unique()))
        subset = eval_df[eval_df["prompt_id"] == prompt_id]
        cols = st.columns(2)
        for i, model_key in enumerate(["model_a", "model_b"]):
            with cols[i]:
                row = subset[subset["model_key"] == model_key].iloc[0]
                st.markdown(f"### {model_key}")
                st.write(row["response_text"])

        rec = recommend_routing(eval_df)
        st.subheader("Routing recommendation")
        st.info(f"{rec['strategy']}: {rec['recommendation']}")
else:
    st.info("Enter a run_id to load results.")
