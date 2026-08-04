from pathlib import Path


def solve(values):
    source = Path("input.csv")
    with open(source, "r", encoding="utf-8") as stream:
        sample = stream.read()
    return {"values": values, "sample": sample}
