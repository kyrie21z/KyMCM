from pathlib import Path


def solve(values):
    Path("result.csv").write_text("value\n", encoding="utf-8")
    return values
