"""Summarize recorded MSeg rain-instance agreement, not clean-reference accuracy."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path


SEVERITIES = ("light", "medium", "heavy")


def load_variant_means(csv_path):
    grouped = defaultdict(list)
    with Path(csv_path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            grouped[(row["derainer"], row["severity"])].append(
                float(row["mean_miou"])
            )
    return grouped


def aggregate_means(grouped):
    derainers = sorted({derainer for derainer, _ in grouped})
    summary = {}

    for derainer in derainers:
        severity_means = {}
        all_values = []
        for severity in SEVERITIES:
            values = grouped[(derainer, severity)]
            if not values:
                raise ValueError(f"Missing values for {derainer}/{severity}")
            severity_means[severity] = sum(values) / len(values)
            all_values.extend(values)

        severity_means["overall"] = sum(all_values) / len(all_values)
        summary[derainer] = severity_means

    return summary


def render_markdown(summary):
    lines = [
        "| Derainer | Light | Medium | Heavy | Overall |",
        "|---|---:|---:|---:|---:|",
    ]
    for derainer, values in summary.items():
        lines.append(
            f"| {derainer} | {values['light']:.3f} | {values['medium']:.3f} "
            f"| {values['heavy']:.3f} | {values['overall']:.3f} |"
        )
    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "csv_path",
        nargs="?",
        type=Path,
        default=Path("results/tables/mseg_rain_instance_miou_summary.csv"),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    grouped = load_variant_means(args.csv_path)
    print("MSeg pairwise mask mIoU across synthetic rain realizations")
    print(render_markdown(aggregate_means(grouped)))


if __name__ == "__main__":
    main()
