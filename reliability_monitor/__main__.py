"""Command-line interface for the Vision Reliability Monitor."""

import argparse
import json
from pathlib import Path

from .core import compare_treatments, get_alerts, get_overview, import_csv
from .server import serve


DEFAULT_DATABASE = Path("data/monitor/reliability.db")
DEFAULT_RESULTS = Path("results/tables/mseg_rain_instance_miou_summary.csv")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed_parser = subparsers.add_parser("seed", help="Import recorded CSV results")
    seed_parser.add_argument("--csv", type=Path, default=DEFAULT_RESULTS)

    subparsers.add_parser("summary", help="Print aggregate results as JSON")

    alert_parser = subparsers.add_parser("alerts", help="Print reliability alerts")
    alert_parser.add_argument("--minimum-mean", type=float, default=0.70)
    alert_parser.add_argument("--maximum-severity-drop", type=float, default=0.12)

    compare_parser = subparsers.add_parser("compare", help="Compare two treatments")
    compare_parser.add_argument("baseline")
    compare_parser.add_argument("candidate")
    compare_parser.add_argument("--segmentor", default="mseg")

    serve_parser = subparsers.add_parser("serve", help="Run the API and dashboard")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8081)
    serve_parser.add_argument(
        "--seed",
        action="store_true",
        help="Import the recorded CSV before starting",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.command == "seed":
        count = import_csv(args.database, args.csv)
        print(f"Imported {count} runs into {args.database}")
    elif args.command == "summary":
        print(json.dumps(get_overview(args.database), indent=2))
    elif args.command == "alerts":
        print(
            json.dumps(
                get_alerts(
                    args.database,
                    minimum_mean=args.minimum_mean,
                    maximum_severity_drop=args.maximum_severity_drop,
                ),
                indent=2,
            )
        )
    elif args.command == "compare":
        print(
            json.dumps(
                compare_treatments(
                    args.database,
                    args.baseline,
                    args.candidate,
                    segmentor=args.segmentor,
                ),
                indent=2,
            )
        )
    elif args.command == "serve":
        if args.seed:
            count = import_csv(args.database, DEFAULT_RESULTS)
            print(f"Imported {count} runs into {args.database}")
        serve(args.database, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
