"""Synthetic formal entrypoint: build and run the submitted C++ search."""
import argparse
import configparser
import csv
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--steps", type=int)
    parser.add_argument("--candidate", type=Path)
    args = parser.parse_args()
    config = configparser.ConfigParser()
    if not config.read(args.config):
        raise FileNotFoundError(args.config)
    with args.input.open(newline="") as stream:
        target = sum(int(row["value"]) for row in csv.DictReader(stream))
    target += config.getint("model", "offset")
    steps = args.steps if args.steps is not None else config.getint("model", "steps")
    if steps <= 0:
        raise ValueError("positive search budget required")
    args.output.mkdir(parents=True, exist_ok=False)
    binary = args.output.resolve() / "search"
    subprocess.run(
        [args.compiler, "-std=c++17", "-O0", str(Path(__file__).with_name("search.cpp")),
         "-o", str(binary)], check=True, timeout=20,
    )
    command = [str(binary), str(target), str(steps)]
    if args.candidate is not None:
        command.append(args.candidate.read_text().strip())
    result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=5)
    candidate, objective = (int(value) for value in result.stdout.split())
    with (args.output / "result.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["candidate", "objective"])
        writer.writerow([candidate, objective])
    print("built-from-source")
    print("fixed-candidate-recalculation" if args.candidate else (
        "short-search" if args.steps is not None else "full-search"
    ))


if __name__ == "__main__":
    main()
