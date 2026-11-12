"""Run the read-only species profile audit and write JSON, Markdown, and CSV reports."""
from __future__ import annotations

import argparse
from pathlib import Path

from pipeline.species_validator import ROOT, audit_species, write_reports


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports")
    args = parser.parse_args()
    report = audit_species(ROOT / "data" / "species", ROOT / "data" / "parameters.json")
    write_reports(report, args.output_dir)
    summary = report["summary"]
    print(f"Inspected {summary['profiles_inspected']} profiles: {summary['structurally_valid']} structurally valid, "
          f"{summary['model_compatibility_issues']} with model compatibility issues, "
          f"{summary['needs_biological_research_or_rebuild']} needing research or model rebuilding.")
    print(f"Reports written to {args.output_dir}")


if __name__ == "__main__":
    main()
