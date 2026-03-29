# AI Inference Investment Trading Spec

## Core Rule

- Base expression: long utility / power-infrastructure beneficiaries on issuer-specific positive disclosures.
- Base holding period: 20 trading days.
- Primary benchmark: XLU-relative abnormal return.
- Do not treat 1-day or 5-day reactions as the signal horizon.
- Treat this as a medium-horizon event strategy, not an intraday news-reaction system.

## Validated Edge

- The cleanest current family is `pipeline_capacity_expansion` at `+20`, with sample `2`, hit rate `100.0%`, and median abnormal `2.34%`.
- The broader event-type signal still points to `pipeline_mw_increase` as the only fully qualified v1 trade-card family.
- Inference from the sample: issuer-specific load-growth and backlog disclosures are the best current lead; read-through macro commentary is not.

## Preferred Variants

- `pipeline_capacity_expansion` (`high` tier) at `+20`: sample `2`, hit rate `100.0%`, median abnormal `2.34%`.
- `named_large_load_contract` (`high` tier) at `+20`: sample `4`, hit rate `75.0%`, median abnormal `1.59%`.
- `contracted_load_backlog` (`high` tier) at `+20`: sample `2`, hit rate `100.0%`, median abnormal `1.47%`.
- `transmission_capex_growth` (`high` tier) at `+20`: sample `4`, hit rate `75.0%`, median abnormal `1.30%`.

## Exploratory Only

- `regional_grid_readthrough` (`low` tier) at `+20`: sample `2`, hit rate `100.0%`, median abnormal `1.53%`.

## Watchlist

- `approved_infrastructure_incentive` (`medium` tier) at `+20`: single-sample median abnormal `1.16%`.
- `approved_tariff_with_minimums` (`high` tier) at `+20`: single-sample median abnormal `0.83%`.

## Avoid Or Downweight

- `proposed_rate_design` at `+20`: sample `1`, median abnormal `-1.35%`.
- `early_pipeline_signal` at `+20`: sample `1`, median abnormal `-4.83%`.

## Entry Checklist

- Require an issuer-specific disclosure from the company, its utility commission, or a directly linked grid/operator source.
- Require a `high` or `medium` tier variant unless the setup is explicitly marked exploratory.
- Prefer events with at least one concrete proof point: named MW, contracted load, minimum-bill terms, cost recovery, or capital-spending support.
- Require a setup score of `B` or better for live experimentation; treat `A` setups as highest priority.
- Skip pure regional read-throughs and proposed tariffs without approval or signed economics.

## Execution Template

- Direction: long only in v1.
- Entry: act on the normalized event trade date used by the study; if multiple signals hit the same issuer on one day, keep the highest-scoring setup.
- Hold: target `20` trading days by default.
- Benchmark: manage performance versus `XLU`, not just absolute return.
- Revisit sooner only if a regulatory delay or customer rollback directly invalidates the disclosed load thesis.

## Practical Filters

- Prefer disclosures with named MW, signed agreements, or explicit capital/contract backing.
- Prefer issuer-specific disclosures over regional read-throughs.
- Downweight proposed tariffs without approval and broad macro commentary without company economics.
- Use source confidence and analyst confidence to break ties when multiple setups land the same day.

## Issuer Focus

- `FE`: sample `3`, hit rate `66.7%`, median abnormal `2.15%`, variants `early_pipeline_signal, transmission_capex_growth`.
- `ETR`: sample `5`, hit rate `80.0%`, median abnormal `1.94%`, variants `named_large_load_contract, pipeline_capacity_expansion, transmission_capex_growth`.
- `IDA`: sample `2`, hit rate `100.0%`, median abnormal `1.55%`, variants `approved_infrastructure_incentive, company_load_forecast`.
- `AEP`: sample `4`, hit rate `75.0%`, median abnormal `1.08%`, variants `approved_tariff_with_minimums, company_load_forecast, contracted_load_backlog`.
- `PNW`: sample `2`, hit rate `100.0%`, median abnormal `0.58%`, variants `company_load_forecast`.

## Recommendation Book

- `high` `FE` on `transmission_capex_growth`: sample `2`, hit rate `100.0%`, median abnormal `2.90%`. Long FE on issuer-specific transmission_capex_growth disclosures and hold 20 trading days versus XLU.
- `high` `ETR` on `named_large_load_contract`: sample `3`, hit rate `100.0%`, median abnormal `2.67%`. Long ETR on issuer-specific named_large_load_contract disclosures and hold 20 trading days versus XLU.
- `high` `AEP` on `contracted_load_backlog`: sample `2`, hit rate `100.0%`, median abnormal `1.47%`. Long AEP on issuer-specific contracted_load_backlog disclosures and hold 20 trading days versus XLU.
- `medium` `PNW` on `company_load_forecast`: sample `2`, hit rate `100.0%`, median abnormal `0.58%`. Long PNW on issuer-specific company_load_forecast disclosures and hold 20 trading days versus XLU.

## Avoid Book

- `ETR` on `transmission_capex_growth`: sample `1`, median abnormal `-0.18%`. Avoid initiating ETR on transmission_capex_growth disclosures.
- `PNW` on `proposed_rate_design`: sample `1`, median abnormal `-1.35%`. Avoid initiating PNW on proposed_rate_design disclosures.
- `POR` on `company_load_forecast`: sample `3`, median abnormal `-2.10%`. Avoid initiating POR on company_load_forecast disclosures.
- `BKH` on `named_large_load_contract`: sample `1`, median abnormal `-3.56%`. Avoid initiating BKH on named_large_load_contract disclosures.
- `FE` on `early_pipeline_signal`: sample `1`, median abnormal `-4.83%`. Avoid initiating FE on early_pipeline_signal disclosures.

## Historical Preferred Setups

- `2025-02-06` `BKH` `pipeline_capacity_expansion` (grade `A`, score `9`): `2.74%` abnormal vs `XLU` at `+20`.
- `2025-10-03` `ETR` `named_large_load_contract` (grade `A`, score `9`): `0.52%` abnormal vs `XLU` at `+20`.
- `2024-12-05` `ETR` `named_large_load_contract` (grade `A`, score `9`): `2.67%` abnormal vs `XLU` at `+20`.
- `2026-02-13` `AEP` `contracted_load_backlog` (grade `A`, score `9`): `1.61%` abnormal vs `XLU` at `+20`.
- `2025-10-30` `AEP` `contracted_load_backlog` (grade `A`, score `9`): `1.33%` abnormal vs `XLU` at `+20`.

## Historical Watchlist Setups

- `2025-07-31` `AEP` `approved_tariff_with_minimums` (grade `A`, score `8`): `0.83%` abnormal vs `XLU` at `+20`.
- `2025-02-21` `IDA` `company_load_forecast` (grade `B`, score `5`): `1.93%` abnormal vs `XLU` at `+20`.
- `2025-01-15` `IDA` `approved_infrastructure_incentive` (grade `C`, score `4`): `1.16%` abnormal vs `XLU` at `+20`.
- `2025-11-03` `PNW` `company_load_forecast` (grade `C`, score `4`): `0.41%` abnormal vs `XLU` at `+20`.
- `2025-07-25` `POR` `company_load_forecast` (grade `C`, score `4`): `2.26%` abnormal vs `XLU` at `+20`.

## Historical Avoid Setups

- `2024-10-29` `FE` `early_pipeline_signal` (grade `C`, score `3`): `-4.83%` abnormal vs `XLU` at `+20`.
