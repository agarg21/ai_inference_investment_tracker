# AI Power Bottleneck Validation Report

## Summary

- Corpus size: **28** canonical events
- Issuers represented: **7**
- Qualified trade card event types: **1**
- Qualified 20-day signal variants: **4**
- Recommendation: **narrow scope**
- Conclusion: **partial signal exists, but v1 thresholds were not fully met.**

## Charts

- Corpus by event type: `/Users/apoorvagarg/Documents/Playground/ai_power_validation/data/charts/corpus_by_event_type.png`
- Corpus by issuer: `/Users/apoorvagarg/Documents/Playground/ai_power_validation/data/charts/corpus_by_issuer.png`
- Trading spec: `/Users/apoorvagarg/Documents/Playground/ai_power_validation/data/outputs/trading_spec.md`
- Issuer summary: `/Users/apoorvagarg/Documents/Playground/ai_power_validation/data/outputs/issuer_signal_summary.csv`
- Historical setups: `/Users/apoorvagarg/Documents/Playground/ai_power_validation/data/outputs/historical_setups.csv`
- Recommendation book: `/Users/apoorvagarg/Documents/Playground/ai_power_validation/data/outputs/recommendation_book.csv`

## Strongest Buckets

- `signed_large_load_contract` / `positive` / `+60`: median strategy abnormal return `3.20%`
- `transmission_or_interconnection_approval` / `positive` / `+60`: median strategy abnormal return `3.03%`
- `signed_large_load_contract` / `positive` / `+20`: median strategy abnormal return `1.59%`
- `transmission_or_interconnection_approval` / `positive` / `+20`: median strategy abnormal return `1.30%`
- `pipeline_mw_increase` / `positive` / `+20`: median strategy abnormal return `1.15%`

## Weakest Buckets

- `tariff_or_special_rate_approval` / `positive` / `+60`: median strategy abnormal return `-4.04%`
- `tariff_or_special_rate_approval` / `positive` / `+5`: median strategy abnormal return `-0.83%`
- `pipeline_mw_increase` / `positive` / `+5`: median strategy abnormal return `-0.81%`
- `pipeline_mw_increase` / `positive` / `+1`: median strategy abnormal return `-0.32%`
- `signed_large_load_contract` / `positive` / `+1`: median strategy abnormal return `-0.17%`

## Trade Cards

- `pipeline_mw_increase` `long` `+20`: hit rate `71.4%`, median abnormal `1.15%`, sample `14`

## Signal Variants

- `pipeline_capacity_expansion` (`high` tier): hit rate `100.0%`, median abnormal `2.34%`, sample `2`
- `named_large_load_contract` (`high` tier): hit rate `75.0%`, median abnormal `1.59%`, sample `4`
- `contracted_load_backlog` (`high` tier): hit rate `100.0%`, median abnormal `1.47%`, sample `2`
- `transmission_capex_growth` (`high` tier): hit rate `75.0%`, median abnormal `1.30%`, sample `4`

## Exploratory Variants

- `regional_grid_readthrough` (`low` tier): hit rate `100.0%`, median abnormal `1.53%`, sample `2`

## Issuer Focus

- `FE`: hit rate `66.7%`, median abnormal `2.15%`, sample `3`
- `ETR`: hit rate `80.0%`, median abnormal `1.94%`, sample `5`
- `IDA`: hit rate `100.0%`, median abnormal `1.55%`, sample `2`
- `AEP`: hit rate `75.0%`, median abnormal `1.08%`, sample `4`
- `PNW`: hit rate `100.0%`, median abnormal `0.58%`, sample `2`

## Recommendations

- `high` `FE` on `transmission_capex_growth`: hit rate `100.0%`, median abnormal `2.90%`, sample `2`
- `high` `ETR` on `named_large_load_contract`: hit rate `100.0%`, median abnormal `2.67%`, sample `3`
- `high` `AEP` on `contracted_load_backlog`: hit rate `100.0%`, median abnormal `1.47%`, sample `2`
- `medium` `PNW` on `company_load_forecast`: hit rate `100.0%`, median abnormal `0.58%`, sample `2`

## Avoid List

- `ETR` on `transmission_capex_growth`: median abnormal `-0.18%`, sample `1`
- `PNW` on `proposed_rate_design`: median abnormal `-1.35%`, sample `1`
- `POR` on `company_load_forecast`: median abnormal `-2.10%`, sample `3`
- `BKH` on `named_large_load_contract`: median abnormal `-3.56%`, sample `1`
- `FE` on `early_pipeline_signal`: median abnormal `-4.83%`, sample `1`

## Example Events

- `ETR` `signed_large_load_contract` on `2026-03-05`: Entergy announced approximately $5 billion in total savings for 2.3 million customers because of data center customer agreements in Arkansas, Louisiana, and Mississippi.
- `FE` `transmission_or_interconnection_approval` on `2026-03-02`: FirstEnergy said PJM awarded projects expected to drive more than $950 million of investment by 2029, including over 200 miles of new 765-kV lines to address rising demand from data centers and electrification.
- `FE` `transmission_or_interconnection_approval` on `2026-02-17`: FirstEnergy said regulators approved a major central Ohio transmission project that includes more than 300 miles of new 765-kV lines, new substations and upgrades to support data center development.

## Historical Setup Grades

- `2025-02-06` `BKH` `pipeline_capacity_expansion` `preferred` grade `A`: `+20` abnormal `2.74%`
- `2025-10-03` `ETR` `named_large_load_contract` `preferred` grade `A`: `+20` abnormal `0.52%`
- `2024-12-05` `ETR` `named_large_load_contract` `preferred` grade `A`: `+20` abnormal `2.67%`
- `2026-02-13` `AEP` `contracted_load_backlog` `preferred` grade `A`: `+20` abnormal `1.61%`
- `2025-10-30` `AEP` `contracted_load_backlog` `preferred` grade `A`: `+20` abnormal `1.33%`

## Thesis Risks

- Corpus has only 28 canonical events; target is at least 40.
- Only 1 event types qualified for trade cards; target is at least 2.
