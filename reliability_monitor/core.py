"""Storage, validation, aggregation, and regression detection."""

import csv
import sqlite3
from collections.abc import Mapping
from contextlib import closing
from pathlib import Path


SEVERITIES = ("light", "medium", "heavy")
METRIC_TYPE = "rain_instance_agreement"
METRIC_FIELDS = (
    "mean_miou",
    "median_miou",
    "std_miou",
    "min_miou",
    "max_miou",
)


class ValidationError(ValueError):
    """Raised when an evaluation run does not match the monitor schema."""


def initialize_database(database_path):
    """Create the monitor database and return its normalized path."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS evaluation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                segmentor TEXT NOT NULL,
                treatment TEXT NOT NULL,
                severity TEXT NOT NULL,
                variant TEXT NOT NULL,
                sample_count INTEGER NOT NULL CHECK (sample_count > 0),
                mean_miou REAL NOT NULL CHECK (mean_miou BETWEEN 0 AND 1),
                median_miou REAL NOT NULL CHECK (median_miou BETWEEN 0 AND 1),
                std_miou REAL NOT NULL CHECK (std_miou BETWEEN 0 AND 1),
                min_miou REAL NOT NULL CHECK (min_miou BETWEEN 0 AND 1),
                max_miou REAL NOT NULL CHECK (max_miou BETWEEN 0 AND 1),
                source TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (segmentor, treatment, severity, variant)
            )
            """
        )
        connection.commit()
    return path


def _required_text(record, field):
    value = str(record.get(field, "")).strip().lower()
    if not value:
        raise ValidationError(f"{field} must not be empty")
    return value


def normalize_run(record, source="api"):
    """Validate and normalize one run from CSV or JSON input."""
    if not isinstance(record, Mapping):
        raise ValidationError("each run must be a JSON object or CSV row")
    metric_type = str(record.get("metric_type", METRIC_TYPE)).strip().lower()
    if metric_type != METRIC_TYPE:
        raise ValidationError(
            f"this monitor accepts only {METRIC_TYPE}; other metrics need a separate schema"
        )
    treatment_value = record.get("treatment", record.get("derainer", ""))
    normalized = {
        "segmentor": _required_text(record, "segmentor"),
        "treatment": str(treatment_value).strip().lower(),
        "severity": _required_text(record, "severity"),
        "variant": str(record.get("variant", record.get("version", ""))).strip().lower(),
        "source": str(record.get("source", source)).strip() or source,
    }
    if not normalized["treatment"]:
        raise ValidationError("treatment must not be empty")
    if not normalized["variant"]:
        raise ValidationError("variant must not be empty")
    if normalized["severity"] not in SEVERITIES:
        raise ValidationError(
            f"severity must be one of {', '.join(SEVERITIES)}"
        )

    try:
        normalized["sample_count"] = int(record.get("sample_count", record.get("n")))
    except (TypeError, ValueError) as exc:
        raise ValidationError("sample_count must be a positive integer") from exc
    if normalized["sample_count"] <= 0:
        raise ValidationError("sample_count must be a positive integer")

    for field in METRIC_FIELDS:
        try:
            value = float(record[field])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValidationError(f"{field} must be a number between 0 and 1") from exc
        if not 0 <= value <= 1:
            raise ValidationError(f"{field} must be between 0 and 1")
        normalized[field] = value

    if normalized["min_miou"] > normalized["max_miou"]:
        raise ValidationError("min_miou must not exceed max_miou")
    return normalized


def insert_run(database_path, record, source="api"):
    """Insert or update a run using its model/condition identity."""
    path = initialize_database(database_path)
    run = normalize_run(record, source=source)
    columns = (
        "segmentor",
        "treatment",
        "severity",
        "variant",
        "sample_count",
        *METRIC_FIELDS,
        "source",
    )
    placeholders = ", ".join("?" for _ in columns)
    updates = ", ".join(
        f"{column}=excluded.{column}"
        for column in columns
        if column not in {"segmentor", "treatment", "severity", "variant"}
    )
    values = tuple(run[column] for column in columns)
    with closing(sqlite3.connect(path)) as connection:
        connection.execute(
            f"""
            INSERT INTO evaluation_runs ({', '.join(columns)})
            VALUES ({placeholders})
            ON CONFLICT (segmentor, treatment, severity, variant)
            DO UPDATE SET {updates}, updated_at=CURRENT_TIMESTAMP
            """,
            values,
        )
        connection.commit()
    return run


def import_csv(database_path, csv_path):
    """Upsert all evaluation rows from a compatible CSV file."""
    source_path = Path(csv_path)
    count = 0
    with source_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            insert_run(database_path, row, source=str(source_path))
            count += 1
    return count


def _connect(database_path):
    path = initialize_database(database_path)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def get_overview(database_path):
    """Return condition-level and treatment-level aggregate metrics."""
    with closing(_connect(database_path)) as connection:
        run_count = connection.execute(
            "SELECT COUNT(*) FROM evaluation_runs"
        ).fetchone()[0]
        group_rows = connection.execute(
            """
            SELECT segmentor, treatment, severity,
                   COUNT(*) AS run_count,
                   SUM(sample_count) AS evaluated_images,
                   AVG(mean_miou) AS mean_miou,
                   AVG(std_miou) AS mean_std_miou
            FROM evaluation_runs
            GROUP BY segmentor, treatment, severity
            ORDER BY segmentor, treatment,
                     CASE severity
                       WHEN 'light' THEN 1
                       WHEN 'medium' THEN 2
                       WHEN 'heavy' THEN 3
                     END
            """
        ).fetchall()
        treatment_rows = connection.execute(
            """
            SELECT segmentor, treatment, COUNT(*) AS run_count,
                   AVG(mean_miou) AS mean_miou
            FROM evaluation_runs
            GROUP BY segmentor, treatment
            ORDER BY mean_miou DESC
            """
        ).fetchall()

    return {
        "metric_type": METRIC_TYPE,
        "metric": "pairwise mask mIoU across rain realizations",
        "metric_scope": (
            "Rain-instance agreement, not clean-reference agreement or ground-truth accuracy."
        ),
        "run_count": run_count,
        "groups": [dict(row) for row in group_rows],
        "treatments": [dict(row) for row in treatment_rows],
    }


def get_alerts(database_path, minimum_mean=0.70, maximum_severity_drop=0.12):
    """Flag weak conditions and large light-to-heavy degradation."""
    if not 0 <= minimum_mean <= 1:
        raise ValidationError("minimum_mean must be between 0 and 1")
    if not 0 <= maximum_severity_drop <= 1:
        raise ValidationError("maximum_severity_drop must be between 0 and 1")
    overview = get_overview(database_path)
    alerts = []
    grouped = {}
    for row in overview["groups"]:
        key = (row["segmentor"], row["treatment"])
        grouped.setdefault(key, {})[row["severity"]] = row["mean_miou"]
        if row["mean_miou"] < minimum_mean:
            alerts.append(
                {
                    "type": "condition_below_threshold",
                    "level": "warning",
                    "segmentor": row["segmentor"],
                    "treatment": row["treatment"],
                    "severity": row["severity"],
                    "observed": row["mean_miou"],
                    "threshold": minimum_mean,
                    "message": (
                        f"{row['treatment']} falls below the rain-instance agreement threshold "
                        f"under {row['severity']} rain."
                    ),
                }
            )

    for (segmentor, treatment), values in grouped.items():
        if "light" not in values or "heavy" not in values:
            continue
        drop = values["light"] - values["heavy"]
        if drop > maximum_severity_drop:
            alerts.append(
                {
                    "type": "severity_degradation",
                    "level": "warning",
                    "segmentor": segmentor,
                    "treatment": treatment,
                    "observed_drop": drop,
                    "threshold": maximum_severity_drop,
                    "message": (
                        f"{treatment} drops {drop:.3f} rain-instance mIoU from light to heavy rain."
                    ),
                }
            )
    return {
        "minimum_mean": minimum_mean,
        "maximum_severity_drop": maximum_severity_drop,
        "alert_count": len(alerts),
        "alerts": alerts,
    }


def compare_treatments(database_path, baseline, candidate, segmentor="mseg"):
    """Compare two restoration treatments across matching severities."""
    baseline = baseline.strip().lower()
    candidate = candidate.strip().lower()
    segmentor = segmentor.strip().lower()
    with closing(_connect(database_path)) as connection:
        rows = connection.execute(
            """
            SELECT treatment, severity, AVG(mean_miou) AS mean_miou
            FROM evaluation_runs
            WHERE segmentor = ? AND treatment IN (?, ?)
            GROUP BY treatment, severity
            """,
            (segmentor, baseline, candidate),
        ).fetchall()

    by_treatment = {baseline: {}, candidate: {}}
    for row in rows:
        by_treatment[row["treatment"]][row["severity"]] = row["mean_miou"]
    if not by_treatment[baseline]:
        raise ValidationError(f"unknown baseline treatment: {baseline}")
    if not by_treatment[candidate]:
        raise ValidationError(f"unknown candidate treatment: {candidate}")

    comparisons = []
    for severity in SEVERITIES:
        if severity not in by_treatment[baseline] or severity not in by_treatment[candidate]:
            continue
        baseline_mean = by_treatment[baseline][severity]
        candidate_mean = by_treatment[candidate][severity]
        comparisons.append(
            {
                "severity": severity,
                "baseline_mean": baseline_mean,
                "candidate_mean": candidate_mean,
                "delta": candidate_mean - baseline_mean,
            }
        )
    if not comparisons:
        raise ValidationError("baseline and candidate have no matching rain severities")
    overall_delta = sum(row["delta"] for row in comparisons) / len(comparisons)
    return {
        "segmentor": segmentor,
        "baseline": baseline,
        "candidate": candidate,
        "overall_delta": overall_delta,
        "regression": overall_delta < 0,
        "conditions": comparisons,
    }
