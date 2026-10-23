"""Data models for Nest x Yale locks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum, unique


@unique
class LockBoltState(StrEnum):
    """Nest x Yale Lock bolt states."""

    LOCKED = "locked"
    UNLOCKED = "unlocked"
    LOCKING = "locking"
    UNLOCKING = "unlocking"
    JAMMED = "jammed"
    UNKNOWN = "unknown"


@dataclass
class LockState:
    """Minimal lock-state model surfaced to the HA entity."""

    resource_id: str
    name: str
    serial_number: str
    bolt_state: LockBoltState
    software_version: str | None = None
    battery_level: float | None = None
    # Raw battery data the lock reports next to its own percentage. Its gauge
    # assumes one cell chemistry, so these show what the cells actually read.
    battery_voltage: float | None = None
    battery_replacement: str | None = None
    location: str | None = None
