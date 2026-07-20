from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Diagnostic:
    severity: str
    identifier: str
    location: str
    message: str

    def render(self) -> str:
        return f"{self.severity} {self.identifier} {self.location}: {self.message}"


def error(identifier: str, location: str, message: str) -> Diagnostic:
    return Diagnostic("ERROR", identifier, location, message)


def warning(identifier: str, location: str, message: str) -> Diagnostic:
    return Diagnostic("WARNING", identifier, location, message)


def exit_code(diagnostics: list[Diagnostic]) -> int:
    if any(item.identifier == "LITE-TOOL-001" for item in diagnostics):
        return 2
    if any(item.severity == "ERROR" for item in diagnostics):
        return 1
    return 0


def render(diagnostics: list[Diagnostic]) -> list[str]:
    lines = [item.render() for item in diagnostics]
    errors = sum(item.severity == "ERROR" for item in diagnostics)
    warnings = sum(item.severity == "WARNING" for item in diagnostics)
    lines.append(f"SUMMARY errors={errors} warnings={warnings}")
    return lines
