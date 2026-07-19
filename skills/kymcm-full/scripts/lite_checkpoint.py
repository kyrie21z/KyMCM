#!/usr/bin/env python3
"""Deprecated compatibility wrapper for :mod:`full_checkpoint`."""

from full_checkpoint import main


if __name__ == "__main__":
    raise SystemExit(main())
