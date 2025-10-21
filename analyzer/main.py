import json
import sys
import click
import logging
from rich.console import Console
from rich.table import Table

from .processor import aggregate_stats_from_files

console = Console()

@click.command()
@click.option("--source", required=True, type=click.Path(), 
              help="Path to logs folder or file")
@click.option("--output", "-o", type=click.Path(), default=None, 
              help="Write JSON report to file")
@click.option("--pretty", is_flag=True, help="Pretty-print JSON output")
@click.option("--show", type=click.Choice(["summary", "none"]), default="summary", 
              help="Show summary in terminal")
def main(source, output, pretty, show):

    logging.info(f"Starting log analysis for source: {source}")

    try:
        report = aggregate_stats_from_files(source)

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


    except PermissionError as e:
        console.print(f"[red]Permission denied: {e}[/red]")
        sys.exit(2)
    
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        logging.exception("Unexpected error occurred")
        sys.exit(99)

    # نوشتن گزارش به فایل JSON
    if output:
        try:
            with open(output, "w", encoding="utf-8") as fh:
                if pretty:
                    json.dump(report, fh, ensure_ascii=False, indent=2)
                else:
                    json.dump(report, fh, ensure_ascii=False)
            console.print(f"[green]Report written to {output}[/green]")
            logging.info(f"Report successfully written to {output}")
        except PermissionError:
            console.print(f"[red]Permission denied when writing to {output}[/red]")
            logging.error(f"Permission denied when writing to {output}")
            sys.exit(2)

    else:
        if pretty:
            console.print_json(data=report, indent=2)
        else:
            console.print(json.dumps(report, ensure_ascii=False))

    if show == "summary":
        _print_summary(report)

def _print_summary(report):
    """نمایش خلاصه‌ی خروجی در ترمینال با جدول رنگی."""
    t = Table(title="Log Summary")
    t.add_column("Metric")
    t.add_column("Value", justify="right")
    t.add_row("Processed lines", str(report["metadata"]["total_lines_processed"]))
    t.add_row("Total Errors & Criticals", str(report["overall_summary"]\
                                              ["total_errors_and_criticals"]))
    t.add_row("Total Warnings", str(report["overall_summary"]\
                                    ["total_warnings"]))
    t.add_row("Malformed lines", str(report["overall_summary"]\
                                     ["malformed_lines_count"]))
    console.print(t)

if __name__ == "__main__":
    main()