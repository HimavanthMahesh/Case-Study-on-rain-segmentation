# Vision Reliability Monitor

The Vision Reliability Monitor turns the recorded evaluation table into a small operational ML system. It stores evaluation runs, aggregates performance by condition, compares candidate treatments with a baseline, and flags threshold breaches through a JSON API and browser dashboard.

The monitor is part of this repository rather than a separate project because it is an operational extension of the rain-robustness study.

## What the MVP demonstrates

- Schema validation for incoming evaluation records
- Idempotent ingestion into SQLite
- Condition-level and treatment-level aggregation
- Configurable consistency and severity-degradation alerts
- Baseline-versus-candidate comparison
- A dependency-free HTTP API and responsive dashboard
- Unit and HTTP integration tests

The current data measures mIoU against each segmentor's clean-image prediction. The dashboard therefore monitors prediction consistency, not accuracy against Cityscapes ground-truth labels.

## Run locally

From the repository root:

```bash
python -m reliability_monitor --database data/monitor/reliability.db seed
python -m reliability_monitor --database data/monitor/reliability.db serve
```

Open `http://127.0.0.1:8081`.

For a one-command demo that refreshes the seed data first:

```bash
python -m reliability_monitor --database data/monitor/reliability.db serve --seed
```

The monitor uses only Python's standard library. It does not download model weights, require a GPU, or add a large environment to the local computer.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Service health |
| `GET` | `/api/overview` | Aggregated run and treatment metrics |
| `GET` | `/api/alerts` | Threshold and severity-drop alerts |
| `GET` | `/api/compare?baseline=idt&candidate=nerdrain` | Matched treatment comparison |
| `POST` | `/api/runs` | Validate and upsert one run or a JSON array of runs |

Alert thresholds are configurable through query parameters:

```text
/api/alerts?minimum_mean=0.72&maximum_severity_drop=0.10
```

The POST endpoint accepts the same fields as the recorded MSeg CSV. `treatment` can be used in place of `derainer`, and `sample_count` can be used in place of `n`.

## Using the GPU server later

The A100/H200 server is best used as an evaluation worker rather than as a requirement for the dashboard. A later phase can run new segmentation and restoration checkpoints on the server, calculate ground-truth and consistency metrics, and POST the resulting records to this monitor.

Recommended server-side sequence:

1. Package each segmentor and derainer in a reproducible environment.
2. Run an evaluation manifest through a scheduled or queued GPU job.
3. Calculate both ground-truth mIoU and clean-prediction consistency.
4. Submit summarized runs to the API with model and dataset version metadata.
5. Keep the dashboard/API process on a CPU node; reserve A100/H200 capacity for inference.

## Production backlog

- Extend the schema with model, dataset, code, and checkpoint versions
- Add ground-truth Cityscapes metrics and per-class regressions
- Move from SQLite to PostgreSQL when multiple workers write concurrently
- Add authentication before exposing write endpoints outside a trusted network
- Add a GPU job queue, run status, and artifact links
- Record latency, GPU memory, throughput, and approximate compute cost
- Export Prometheus metrics and send alerts to an external notification system
- Containerize the service after the deployment target is selected
