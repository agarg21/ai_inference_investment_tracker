from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from ai_power_validation.config import Settings
from ai_power_validation.constants import SIGNAL_TIER_BY_VARIANT
from ai_power_validation.db import get_connection, init_db
from ai_power_validation.strategy import build_strategy_windows


def _save_chart(series: pd.Series, path: Path, title: str, xlabel: str) -> None:
    if series.empty:
        return
    plt.figure(figsize=(10, 5))
    series.sort_values(ascending=False).plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def export_outputs(settings: Settings) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    init_db(settings)
    with get_connection(settings) as connection:
        events_df = pd.read_sql_query("SELECT * FROM events ORDER BY trade_date DESC, issuer", connection)
        price_windows_df = pd.read_sql_query(
            "SELECT * FROM price_windows ORDER BY horizon, event_id",
            connection,
        )
        trade_cards_df = pd.read_sql_query(
            "SELECT * FROM trade_cards ORDER BY median_abnormal_return DESC, hit_rate DESC",
            connection,
        )

    events_df.to_csv(settings.outputs_dir / "events.csv", index=False)
    price_windows_df.to_csv(settings.outputs_dir / "event_study.csv", index=False)
    trade_cards_df.to_csv(settings.outputs_dir / "trade_cards.csv", index=False)
    return events_df, price_windows_df, trade_cards_df


def build_strategy_variant_summary(events_df: pd.DataFrame, price_windows_df: pd.DataFrame) -> pd.DataFrame:
    if events_df.empty or price_windows_df.empty:
        return pd.DataFrame(
            columns=[
                "signal_variant",
                "signal_tier",
                "horizon",
                "sample_count",
                "hit_rate",
                "median_abnormal_return",
                "mean_abnormal_return",
            ]
        )

    merged = build_strategy_windows(events_df, price_windows_df)
    merged = merged[merged["signal_variant"].notna()].copy()
    if merged.empty:
        return pd.DataFrame(
            columns=[
                "signal_variant",
                "signal_tier",
                "horizon",
                "sample_count",
                "hit_rate",
                "median_abnormal_return",
                "mean_abnormal_return",
            ]
        )

    summary = (
        merged.groupby(["signal_variant", "horizon"], dropna=False)["strategy_abnormal_return"]
        .agg(
            sample_count="count",
            hit_rate=lambda values: (values > 0).mean(),
            median_abnormal_return="median",
            mean_abnormal_return="mean",
        )
        .reset_index()
    )
    summary["signal_tier"] = summary["signal_variant"].map(SIGNAL_TIER_BY_VARIANT).fillna("unknown")
    return summary.sort_values(
        ["median_abnormal_return", "hit_rate", "sample_count"],
        ascending=[False, False, False],
    )


def build_issuer_signal_summary(events_df: pd.DataFrame, price_windows_df: pd.DataFrame) -> pd.DataFrame:
    if events_df.empty or price_windows_df.empty:
        return pd.DataFrame(
            columns=[
                "issuer",
                "sample_count",
                "hit_rate",
                "median_abnormal_return",
                "mean_abnormal_return",
                "signal_variants",
            ]
        )

    merged = build_strategy_windows(events_df, price_windows_df)
    merged = merged[(merged["horizon"] == 20) & (merged["signal_variant"].notna())].copy()
    if merged.empty:
        return pd.DataFrame(
            columns=[
                "issuer",
                "sample_count",
                "hit_rate",
                "median_abnormal_return",
                "mean_abnormal_return",
                "signal_variants",
            ]
        )

    merged["signal_tier"] = merged["signal_variant"].map(SIGNAL_TIER_BY_VARIANT).fillna("unknown")
    merged = merged[merged["signal_tier"] != "low"].copy()
    if merged.empty:
        return pd.DataFrame(
            columns=[
                "issuer",
                "sample_count",
                "hit_rate",
                "median_abnormal_return",
                "mean_abnormal_return",
                "signal_variants",
            ]
        )

    summary = (
        merged.groupby("issuer", dropna=False)["strategy_abnormal_return"]
        .agg(
            sample_count="count",
            hit_rate=lambda values: (values > 0).mean(),
            median_abnormal_return="median",
            mean_abnormal_return="mean",
        )
        .reset_index()
    )
    variants = (
        merged.groupby("issuer", dropna=False)["signal_variant"]
        .agg(lambda values: ", ".join(sorted(set(values))))
        .reset_index(name="signal_variants")
    )
    summary = summary.merge(variants, on="issuer", how="left")
    return summary.sort_values(
        ["median_abnormal_return", "hit_rate", "sample_count"],
        ascending=[False, False, False],
    )


def _event_setup_score(row: pd.Series) -> int:
    score = 0
    score += {"high": 3, "medium": 2, "low": 0}.get(str(row.get("signal_tier") or "unknown"), 1)
    score += 1 if pd.notna(row.get("mw_value")) else 0
    score += 1 if pd.notna(row.get("contract_term_years")) or pd.notna(row.get("take_or_pay_pct")) else 0
    score += 1 if any(
        value not in (None, "", "nan")
        for value in [
            row.get("tariff_type"),
            row.get("cost_recovery"),
            row.get("capex_mention"),
        ]
    ) else 0
    score += 1 if float(row.get("source_confidence") or 0) >= 3 else 0
    score += 1 if float(row.get("analyst_confidence") or 0) >= 2 else 0
    return score


def _event_setup_grade(score: int) -> str:
    if score >= 7:
        return "A"
    if score >= 5:
        return "B"
    return "C"


def build_historical_setup_summary(
    events_df: pd.DataFrame,
    price_windows_df: pd.DataFrame,
    variant_summary_df: pd.DataFrame,
) -> pd.DataFrame:
    if events_df.empty or price_windows_df.empty:
        return pd.DataFrame(
            columns=[
                "trade_date",
                "issuer",
                "signal_variant",
                "signal_tier",
                "family_bucket",
                "setup_score",
                "setup_grade",
                "variant_sample_count",
                "variant_hit_rate",
                "variant_median_abnormal_return",
                "strategy_abnormal_return",
                "mw_value",
                "evidence_snippet",
            ]
        )

    merged = build_strategy_windows(events_df, price_windows_df)
    merged = merged[merged["horizon"] == 20].copy()
    if merged.empty:
        return pd.DataFrame(
            columns=[
                "trade_date",
                "issuer",
                "signal_variant",
                "signal_tier",
                "family_bucket",
                "setup_score",
                "setup_grade",
                "variant_sample_count",
                "variant_hit_rate",
                "variant_median_abnormal_return",
                "strategy_abnormal_return",
                "mw_value",
                "evidence_snippet",
            ]
        )

    merged["signal_tier"] = merged["signal_variant"].map(SIGNAL_TIER_BY_VARIANT).fillna("unknown")
    summary_lookup = (
        variant_summary_df[variant_summary_df["horizon"] == 20]
        .set_index("signal_variant")[["sample_count", "hit_rate", "median_abnormal_return"]]
        .to_dict("index")
        if not variant_summary_df.empty
        else {}
    )

    def classify_family(row: pd.Series) -> str:
        signal_tier = row["signal_tier"]
        stats = summary_lookup.get(row["signal_variant"], {})
        sample_count = int(stats.get("sample_count", 0) or 0)
        hit_rate = float(stats.get("hit_rate", 0.0) or 0.0)
        median_abnormal = float(stats.get("median_abnormal_return", 0.0) or 0.0)
        if signal_tier == "low":
            return "exploratory"
        if sample_count >= 2 and hit_rate >= 0.60 and median_abnormal > 0:
            return "preferred"
        if median_abnormal > 0:
            return "watchlist"
        return "avoid"

    merged["variant_sample_count"] = merged["signal_variant"].map(
        lambda value: summary_lookup.get(value, {}).get("sample_count", 0)
    )
    merged["variant_hit_rate"] = merged["signal_variant"].map(
        lambda value: summary_lookup.get(value, {}).get("hit_rate", 0.0)
    )
    merged["variant_median_abnormal_return"] = merged["signal_variant"].map(
        lambda value: summary_lookup.get(value, {}).get("median_abnormal_return", 0.0)
    )
    merged["family_bucket"] = merged.apply(classify_family, axis=1)
    merged["setup_score"] = merged.apply(_event_setup_score, axis=1)
    merged["setup_score"] += (merged["family_bucket"] == "preferred").astype(int)
    merged["setup_score"] += (merged["variant_sample_count"] >= 2).astype(int)
    merged["setup_grade"] = merged["setup_score"].map(_event_setup_grade)
    family_rank = {"preferred": 0, "watchlist": 1, "exploratory": 2, "avoid": 3}
    merged["family_rank"] = merged["family_bucket"].map(family_rank).fillna(9)

    columns = [
        "trade_date",
        "issuer",
        "event_type",
        "signal_variant",
        "signal_tier",
        "family_bucket",
        "setup_score",
        "setup_grade",
        "variant_sample_count",
        "variant_hit_rate",
        "variant_median_abnormal_return",
        "strategy_abnormal_return",
        "mw_value",
        "contract_term_years",
        "take_or_pay_pct",
        "tariff_type",
        "cost_recovery",
        "capex_mention",
        "source_confidence",
        "analyst_confidence",
        "evidence_snippet",
    ]
    summary = merged.sort_values(
        ["family_rank", "setup_score", "variant_median_abnormal_return", "trade_date"],
        ascending=[True, False, False, False],
    )[columns]
    return summary


def build_recommendation_book(events_df: pd.DataFrame, price_windows_df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "issuer",
        "signal_variant",
        "signal_tier",
        "sample_count",
        "hit_rate",
        "median_abnormal_return",
        "mean_abnormal_return",
        "confidence",
        "action",
        "notes",
    ]
    if events_df.empty or price_windows_df.empty:
        return pd.DataFrame(columns=columns)

    merged = build_strategy_windows(events_df, price_windows_df)
    merged = merged[(merged["horizon"] == 20) & (merged["signal_variant"].notna())].copy()
    if merged.empty:
        return pd.DataFrame(columns=columns)

    merged["signal_tier"] = merged["signal_variant"].map(SIGNAL_TIER_BY_VARIANT).fillna("unknown")
    summary = (
        merged.groupby(["issuer", "signal_variant", "signal_tier"], dropna=False)["strategy_abnormal_return"]
        .agg(
            sample_count="count",
            hit_rate=lambda values: (values > 0).mean(),
            median_abnormal_return="median",
            mean_abnormal_return="mean",
        )
        .reset_index()
    )

    def classify_confidence(row: pd.Series) -> str:
        if row["median_abnormal_return"] <= 0:
            return "avoid"
        if row["sample_count"] >= 2 and row["signal_tier"] == "high" and row["hit_rate"] >= 0.75 and row[
            "median_abnormal_return"
        ] >= 0.012:
            return "high"
        if row["sample_count"] >= 2 and row["hit_rate"] >= 0.60 and row["median_abnormal_return"] > 0:
            return "medium"
        return "watchlist"

    def build_action(row: pd.Series) -> str:
        if row["confidence"] == "avoid":
            return f"Avoid initiating {row['issuer']} on {row['signal_variant']} disclosures."
        return (
            f"Long {row['issuer']} on issuer-specific {row['signal_variant']} disclosures and hold 20 trading days "
            "versus XLU."
        )

    def build_notes(row: pd.Series) -> str:
        if row["confidence"] == "avoid":
            return "Current sample has non-positive median abnormal return."
        if row["sample_count"] == 1:
            return "Positive single-sample setup; useful for watchlisting, not position sizing."
        return "Validated on the current 20-day event-study sample."

    summary["confidence"] = summary.apply(classify_confidence, axis=1)
    summary["action"] = summary.apply(build_action, axis=1)
    summary["notes"] = summary.apply(build_notes, axis=1)
    confidence_rank = {"high": 0, "medium": 1, "watchlist": 2, "avoid": 3}
    summary["confidence_rank"] = summary["confidence"].map(confidence_rank).fillna(9)
    return summary.sort_values(
        ["confidence_rank", "median_abnormal_return", "hit_rate", "sample_count"],
        ascending=[True, False, False, False],
    ).drop(columns=["confidence_rank"])


def build_trading_spec(settings: Settings, events_df: pd.DataFrame, price_windows_df: pd.DataFrame) -> Path:
    summary = build_strategy_variant_summary(events_df, price_windows_df)
    issuer_summary = build_issuer_signal_summary(events_df, price_windows_df)
    setup_summary = build_historical_setup_summary(events_df, price_windows_df, summary)
    recommendation_book = build_recommendation_book(events_df, price_windows_df)
    summary.to_csv(settings.outputs_dir / "strategy_variant_summary.csv", index=False)
    issuer_summary.to_csv(settings.outputs_dir / "issuer_signal_summary.csv", index=False)
    setup_summary.to_csv(settings.outputs_dir / "historical_setups.csv", index=False)
    recommendation_book.to_csv(settings.outputs_dir / "recommendation_book.csv", index=False)

    qualified = summary[
        (summary["horizon"] == 20)
        & (summary["sample_count"] >= 2)
        & (summary["hit_rate"] >= 0.60)
        & (summary["median_abnormal_return"] > 0)
        & (summary["signal_tier"] != "low")
    ].copy()
    exploratory = summary[
        (summary["horizon"] == 20)
        & (summary["sample_count"] >= 2)
        & (summary["hit_rate"] >= 0.60)
        & (summary["median_abnormal_return"] > 0)
        & (summary["signal_tier"] == "low")
    ].copy()
    watchlist = summary[
        (summary["horizon"] == 20)
        & (summary["sample_count"] == 1)
        & (summary["median_abnormal_return"] > 0)
        & (summary["signal_tier"].isin(["high", "medium"]))
    ].copy()
    avoid = summary[
        (summary["horizon"] == 20)
        & (summary["sample_count"] >= 1)
        & (summary["median_abnormal_return"] <= 0)
    ].copy()
    preferred_examples = setup_summary[
        (setup_summary["family_bucket"] == "preferred") & (setup_summary["strategy_abnormal_return"] > 0)
    ].head(5)
    watchlist_examples = setup_summary[
        (setup_summary["family_bucket"] == "watchlist") & (setup_summary["strategy_abnormal_return"] > 0)
    ].head(5)
    avoid_examples = setup_summary[
        (setup_summary["family_bucket"] == "avoid") & (setup_summary["strategy_abnormal_return"] <= 0)
    ].head(5)
    issuer_focus = issuer_summary.head(5)
    top_recommendations = recommendation_book[recommendation_book["confidence"].isin(["high", "medium"])].head(5)
    avoid_recommendations = recommendation_book[recommendation_book["confidence"] == "avoid"].head(5)

    lines = [
        "# AI Power Bottleneck Trading Spec",
        "",
        "## Core Rule",
        "",
        "- Base expression: long utility / power-infrastructure beneficiaries on issuer-specific positive disclosures.",
        "- Base holding period: 20 trading days.",
        "- Primary benchmark: XLU-relative abnormal return.",
        "- Do not treat 1-day or 5-day reactions as the signal horizon.",
        "- Treat this as a medium-horizon event strategy, not an intraday news-reaction system.",
        "",
        "## Validated Edge",
        "",
    ]
    if qualified.empty:
        lines.append("- No signal variants cleared the tighter trading-spec thresholds yet.")
    else:
        best_row = qualified.iloc[0]
        lines.append(
            f"- The cleanest current family is `{best_row['signal_variant']}` at `+20`, with sample "
            f"`{int(best_row['sample_count'])}`, hit rate `{best_row['hit_rate']:.1%}`, and median abnormal "
            f"`{best_row['median_abnormal_return']:.2%}`."
        )
    lines.extend(
        [
            "- The broader event-type signal still points to `pipeline_mw_increase` as the only fully qualified v1 trade-card family.",
            "- Inference from the sample: issuer-specific load-growth and backlog disclosures are the best current lead; read-through macro commentary is not.",
            "",
            "## Preferred Variants",
            "",
        ]
    )
    if qualified.empty:
        lines.append("- No signal variants cleared the tighter trading-spec thresholds yet.")
    else:
        for row in qualified.itertuples(index=False):
            lines.append(
                f"- `{row.signal_variant}` (`{row.signal_tier}` tier) at `+{int(row.horizon)}`: "
                f"sample `{int(row.sample_count)}`, hit rate `{row.hit_rate:.1%}`, "
                f"median abnormal `{row.median_abnormal_return:.2%}`."
            )

    lines.extend(["", "## Exploratory Only", ""])
    if exploratory.empty:
        lines.append("- No low-tier read-through variants met the exploratory threshold.")
    else:
        for row in exploratory.itertuples(index=False):
            lines.append(
                f"- `{row.signal_variant}` (`{row.signal_tier}` tier) at `+{int(row.horizon)}`: "
                f"sample `{int(row.sample_count)}`, hit rate `{row.hit_rate:.1%}`, "
                f"median abnormal `{row.median_abnormal_return:.2%}`."
            )

    lines.extend(["", "## Watchlist", ""])
    if watchlist.empty:
        lines.append("- No under-sampled but promising variants yet.")
    else:
        for row in watchlist.itertuples(index=False):
            lines.append(
                f"- `{row.signal_variant}` (`{row.signal_tier}` tier) at `+{int(row.horizon)}`: "
                f"single-sample median abnormal `{row.median_abnormal_return:.2%}`."
            )

    lines.extend(["", "## Avoid Or Downweight", ""])
    if avoid.empty:
        lines.append("- No 20-day variants with current sample have negative median abnormal return.")
    else:
        for row in avoid.itertuples(index=False):
            lines.append(
                f"- `{row.signal_variant}` at `+{int(row.horizon)}`: sample `{int(row.sample_count)}`, "
                f"median abnormal `{row.median_abnormal_return:.2%}`."
            )

    lines.extend(
        [
            "",
            "## Entry Checklist",
            "",
            "- Require an issuer-specific disclosure from the company, its utility commission, or a directly linked grid/operator source.",
            "- Require a `high` or `medium` tier variant unless the setup is explicitly marked exploratory.",
            "- Prefer events with at least one concrete proof point: named MW, contracted load, minimum-bill terms, cost recovery, or capital-spending support.",
            "- Require a setup score of `B` or better for live experimentation; treat `A` setups as highest priority.",
            "- Skip pure regional read-throughs and proposed tariffs without approval or signed economics.",
            "",
            "## Execution Template",
            "",
            "- Direction: long only in v1.",
            "- Entry: act on the normalized event trade date used by the study; if multiple signals hit the same issuer on one day, keep the highest-scoring setup.",
            "- Hold: target `20` trading days by default.",
            "- Benchmark: manage performance versus `XLU`, not just absolute return.",
            "- Revisit sooner only if a regulatory delay or customer rollback directly invalidates the disclosed load thesis.",
            "",
            "## Practical Filters",
            "",
            "- Prefer disclosures with named MW, signed agreements, or explicit capital/contract backing.",
            "- Prefer issuer-specific disclosures over regional read-throughs.",
            "- Downweight proposed tariffs without approval and broad macro commentary without company economics.",
            "- Use source confidence and analyst confidence to break ties when multiple setups land the same day.",
            "",
        ]
    )
    lines.extend(["## Issuer Focus", ""])
    if issuer_focus.empty:
        lines.append("- No issuer-level focus list yet.")
    else:
        for row in issuer_focus.itertuples(index=False):
            lines.append(
                f"- `{row.issuer}`: sample `{int(row.sample_count)}`, hit rate `{row.hit_rate:.1%}`, "
                f"median abnormal `{row.median_abnormal_return:.2%}`, variants `{row.signal_variants}`."
            )

    lines.extend(["", "## Recommendation Book", ""])
    if top_recommendations.empty:
        lines.append("- No issuer-level recommendations cleared the medium-confidence threshold yet.")
    else:
        for row in top_recommendations.itertuples(index=False):
            lines.append(
                f"- `{row.confidence}` `{row.issuer}` on `{row.signal_variant}`: sample `{int(row.sample_count)}`, "
                f"hit rate `{row.hit_rate:.1%}`, median abnormal `{row.median_abnormal_return:.2%}`. {row.action}"
            )

    lines.extend(["", "## Avoid Book", ""])
    if avoid_recommendations.empty:
        lines.append("- No issuer-level avoid list yet.")
    else:
        for row in avoid_recommendations.itertuples(index=False):
            lines.append(
                f"- `{row.issuer}` on `{row.signal_variant}`: sample `{int(row.sample_count)}`, "
                f"median abnormal `{row.median_abnormal_return:.2%}`. {row.action}"
            )

    lines.extend(["", "## Historical Preferred Setups", ""])
    if preferred_examples.empty:
        lines.append("- No preferred historical setups yet.")
    else:
        for row in preferred_examples.itertuples(index=False):
            lines.append(
                f"- `{row.trade_date}` `{row.issuer}` `{row.signal_variant}` "
                f"(grade `{row.setup_grade}`, score `{int(row.setup_score)}`): "
                f"`{row.strategy_abnormal_return:.2%}` abnormal vs `XLU` at `+20`."
            )

    lines.extend(["", "## Historical Watchlist Setups", ""])
    if watchlist_examples.empty:
        lines.append("- No watchlist setups yet.")
    else:
        for row in watchlist_examples.itertuples(index=False):
            lines.append(
                f"- `{row.trade_date}` `{row.issuer}` `{row.signal_variant}` "
                f"(grade `{row.setup_grade}`, score `{int(row.setup_score)}`): "
                f"`{row.strategy_abnormal_return:.2%}` abnormal vs `XLU` at `+20`."
            )

    lines.extend(["", "## Historical Avoid Setups", ""])
    if avoid_examples.empty:
        lines.append("- No avoid setups yet.")
    else:
        for row in avoid_examples.itertuples(index=False):
            lines.append(
                f"- `{row.trade_date}` `{row.issuer}` `{row.signal_variant}` "
                f"(grade `{row.setup_grade}`, score `{int(row.setup_score)}`): "
                f"`{row.strategy_abnormal_return:.2%}` abnormal vs `XLU` at `+20`."
            )

    path = settings.outputs_dir / "trading_spec.md"
    path.write_text("\n".join(lines) + "\n")
    return path


def build_report(settings: Settings) -> Path:
    events_df, price_windows_df, trade_cards_df = export_outputs(settings)
    strategy_spec_path = build_trading_spec(settings, events_df, price_windows_df)
    variant_summary_df = build_strategy_variant_summary(events_df, price_windows_df)
    issuer_summary_df = build_issuer_signal_summary(events_df, price_windows_df)
    setup_summary_df = build_historical_setup_summary(events_df, price_windows_df, variant_summary_df)
    recommendation_book_df = build_recommendation_book(events_df, price_windows_df)

    chart_event_type = settings.charts_dir / "corpus_by_event_type.png"
    chart_issuer = settings.charts_dir / "corpus_by_issuer.png"
    _save_chart(events_df["event_type"].value_counts(), chart_event_type, "Corpus by Event Type", "Event Type")
    _save_chart(events_df["issuer"].value_counts(), chart_issuer, "Corpus by Issuer", "Issuer")

    corpus_size = len(events_df)
    issuer_count = events_df["issuer"].nunique() if not events_df.empty else 0
    qualifying_event_types = trade_cards_df["event_type"].nunique() if not trade_cards_df.empty else 0
    qualifying_signal_variants = (
        variant_summary_df[
            (variant_summary_df["horizon"] == 20)
            & (variant_summary_df["sample_count"] >= 2)
            & (variant_summary_df["hit_rate"] >= 0.60)
            & (variant_summary_df["median_abnormal_return"] > 0)
            & (variant_summary_df["signal_tier"] != "low")
        ]["signal_variant"].nunique()
        if not variant_summary_df.empty
        else 0
    )

    merged = build_strategy_windows(events_df, price_windows_df)

    strongest = (
        merged.groupby(["event_type", "directional_label", "horizon"])["strategy_abnormal_return"]
        .median()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
        if not merged.empty
        else pd.DataFrame(columns=["event_type", "directional_label", "horizon", "strategy_abnormal_return"])
    )
    weakest = (
        merged.groupby(["event_type", "directional_label", "horizon"])["strategy_abnormal_return"]
        .median()
        .sort_values(ascending=True)
        .head(5)
        .reset_index()
        if not merged.empty
        else pd.DataFrame(columns=["event_type", "directional_label", "horizon", "strategy_abnormal_return"])
    )

    examples = events_df.head(3).copy()
    if not examples.empty:
        examples["evidence_snippet"] = examples["evidence_snippet"].str.slice(0, 220)

    failure_reasons: list[str] = []
    if corpus_size < 40:
        failure_reasons.append(f"Corpus has only {corpus_size} canonical events; target is at least 40.")
    if issuer_count < 5:
        failure_reasons.append(f"Only {issuer_count} issuers are represented; target is at least 5.")
    if qualifying_event_types < 2:
        failure_reasons.append(
            f"Only {qualifying_event_types} event types qualified for trade cards; target is at least 2."
        )
    if events_df.empty:
        failure_reasons.append("No events were ingested from the manual annotation sheet.")

    if not failure_reasons:
        recommendation = "proceed"
        conclusion = "v1 validation thresholds passed; a recommendation engine is justified."
    elif corpus_size >= 15 and issuer_count >= 5 and (qualifying_event_types >= 1 or qualifying_signal_variants >= 1):
        recommendation = "narrow scope"
        conclusion = "partial signal exists, but v1 thresholds were not fully met."
    else:
        recommendation = "stop"
        conclusion = "no validated signal in v1 scope"

    report_lines = [
        "# AI Power Bottleneck Validation Report",
        "",
        "## Summary",
        "",
        f"- Corpus size: **{corpus_size}** canonical events",
        f"- Issuers represented: **{issuer_count}**",
        f"- Qualified trade card event types: **{qualifying_event_types}**",
        f"- Qualified 20-day signal variants: **{qualifying_signal_variants}**",
        f"- Recommendation: **{recommendation}**",
        f"- Conclusion: **{conclusion}**",
        "",
        "## Charts",
        "",
        f"- Corpus by event type: `{chart_event_type}`",
        f"- Corpus by issuer: `{chart_issuer}`",
        f"- Trading spec: `{strategy_spec_path}`",
        f"- Issuer summary: `{settings.outputs_dir / 'issuer_signal_summary.csv'}`",
        f"- Historical setups: `{settings.outputs_dir / 'historical_setups.csv'}`",
        f"- Recommendation book: `{settings.outputs_dir / 'recommendation_book.csv'}`",
        "",
        "## Strongest Buckets",
        "",
    ]

    if strongest.empty:
        report_lines.append("- None yet.")
    else:
        report_lines.extend(
            f"- `{row.event_type}` / `{row.directional_label}` / `+{int(row.horizon)}`: median strategy abnormal return `{row.strategy_abnormal_return:.2%}`"
            for row in strongest.itertuples(index=False)
        )

    report_lines.extend(["", "## Weakest Buckets", ""])
    if weakest.empty:
        report_lines.append("- None yet.")
    else:
        report_lines.extend(
            f"- `{row.event_type}` / `{row.directional_label}` / `+{int(row.horizon)}`: median strategy abnormal return `{row.strategy_abnormal_return:.2%}`"
            for row in weakest.itertuples(index=False)
        )

    report_lines.extend(["", "## Trade Cards", ""])
    if trade_cards_df.empty:
        report_lines.append("- No trade templates qualified in v1.")
    else:
        report_lines.extend(
            f"- `{row.event_type}` `{row.direction}` `+{int(row.horizon)}`: hit rate `{row.hit_rate:.1%}`, median abnormal `{row.median_abnormal_return:.2%}`, sample `{int(row.sample_count)}`"
            for row in trade_cards_df.itertuples(index=False)
        )

    report_lines.extend(["", "## Signal Variants", ""])
    qualified_variants = variant_summary_df[
        (variant_summary_df["horizon"] == 20)
        & (variant_summary_df["sample_count"] >= 2)
        & (variant_summary_df["hit_rate"] >= 0.60)
        & (variant_summary_df["median_abnormal_return"] > 0)
        & (variant_summary_df["signal_tier"] != "low")
    ]
    if qualified_variants.empty:
        report_lines.append("- No 20-day signal variants cleared the tighter strategy thresholds yet.")
    else:
        report_lines.extend(
            f"- `{row.signal_variant}` (`{row.signal_tier}` tier): hit rate `{row.hit_rate:.1%}`, median abnormal `{row.median_abnormal_return:.2%}`, sample `{int(row.sample_count)}`"
            for row in qualified_variants.itertuples(index=False)
        )

    exploratory_variants = variant_summary_df[
        (variant_summary_df["horizon"] == 20)
        & (variant_summary_df["sample_count"] >= 2)
        & (variant_summary_df["hit_rate"] >= 0.60)
        & (variant_summary_df["median_abnormal_return"] > 0)
        & (variant_summary_df["signal_tier"] == "low")
    ]
    report_lines.extend(["", "## Exploratory Variants", ""])
    if exploratory_variants.empty:
        report_lines.append("- No low-tier exploratory variants met the threshold.")
    else:
        report_lines.extend(
            f"- `{row.signal_variant}` (`{row.signal_tier}` tier): hit rate `{row.hit_rate:.1%}`, median abnormal `{row.median_abnormal_return:.2%}`, sample `{int(row.sample_count)}`"
            for row in exploratory_variants.itertuples(index=False)
        )

    report_lines.extend(["", "## Issuer Focus", ""])
    issuer_focus = issuer_summary_df.head(5)
    if issuer_focus.empty:
        report_lines.append("- No issuer-level summary yet.")
    else:
        report_lines.extend(
            f"- `{row.issuer}`: hit rate `{row.hit_rate:.1%}`, median abnormal `{row.median_abnormal_return:.2%}`, sample `{int(row.sample_count)}`"
            for row in issuer_focus.itertuples(index=False)
        )

    report_lines.extend(["", "## Recommendations", ""])
    recommendation_focus = recommendation_book_df[recommendation_book_df["confidence"].isin(["high", "medium"])].head(5)
    if recommendation_focus.empty:
        report_lines.append("- No issuer-level recommendations cleared the medium-confidence threshold yet.")
    else:
        report_lines.extend(
            f"- `{row.confidence}` `{row.issuer}` on `{row.signal_variant}`: hit rate `{row.hit_rate:.1%}`, median abnormal `{row.median_abnormal_return:.2%}`, sample `{int(row.sample_count)}`"
            for row in recommendation_focus.itertuples(index=False)
        )

    report_lines.extend(["", "## Avoid List", ""])
    avoid_focus = recommendation_book_df[recommendation_book_df["confidence"] == "avoid"].head(5)
    if avoid_focus.empty:
        report_lines.append("- No issuer-level avoid list yet.")
    else:
        report_lines.extend(
            f"- `{row.issuer}` on `{row.signal_variant}`: median abnormal `{row.median_abnormal_return:.2%}`, sample `{int(row.sample_count)}`"
            for row in avoid_focus.itertuples(index=False)
        )

    report_lines.extend(["", "## Example Events", ""])
    if examples.empty:
        report_lines.append("- No examples available.")
    else:
        report_lines.extend(
            f"- `{row.issuer}` `{row.event_type}` on `{row.trade_date}`: {row.evidence_snippet}"
            for row in examples.itertuples(index=False)
        )

    report_lines.extend(["", "## Historical Setup Grades", ""])
    setup_focus = setup_summary_df[setup_summary_df["strategy_abnormal_return"] > 0].head(5)
    if setup_focus.empty:
        report_lines.append("- No historical setup grades yet.")
    else:
        report_lines.extend(
            f"- `{row.trade_date}` `{row.issuer}` `{row.signal_variant}` `{row.family_bucket}` grade `{row.setup_grade}`: `+20` abnormal `{row.strategy_abnormal_return:.2%}`"
            for row in setup_focus.itertuples(index=False)
        )

    report_lines.extend(["", "## Thesis Risks", ""])
    if failure_reasons:
        report_lines.extend(f"- {reason}" for reason in failure_reasons)
    else:
        report_lines.append("- No gating failures in v1 scope.")

    report_path = settings.outputs_dir / "validation_report.md"
    report_path.write_text("\n".join(report_lines) + "\n")
    return report_path
