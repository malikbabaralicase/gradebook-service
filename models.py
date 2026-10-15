import math
from dataclasses import dataclass

from errors import ValidationError


@dataclass(frozen=True)
class Student:
    id: str
    name: str

    def __post_init__(self) -> None:
        if not self.id:
            raise ValidationError("id must not be empty")
        if not self.name:
            raise ValidationError("name must not be empty")


@dataclass(frozen=True)
class Assessment:
    id: str
    title: str
    weight: float
    total: float

    def __post_init__(self) -> None:
        if not self.id:
            raise ValidationError("id must not be empty")
        if not self.title:
            raise ValidationError("title must not be empty")
        if not 0 <= self.weight <= 100:
            raise ValidationError("weight must be between 0 and 100")
        if self.total <= 0:
            raise ValidationError("total must be greater than 0")


@dataclass(frozen=True)
class Mark:
    student: str
    assessment: str
    score: float

    def __post_init__(self) -> None:
        if not self.score >= 0:
            raise ValidationError("score must not be negative")


def parse_number(raw: object, field: str) -> float:
    if isinstance(raw, bool) or not isinstance(raw, (int, float, str)):
        raise ValidationError(f"{field} must be a finite number")

    try:
        value = float(raw)
    except ValueError:
        raise ValidationError(
            f"{field} must be a finite number"
        ) from None

    if not math.isfinite(value):
        raise ValidationError(f"{field} must be a finite number")

    return value


def parse_text(raw: object, field: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise ValidationError(f"{field} must be a non-blank string")

    return raw.strip()


def parse_student(payload: object) -> Student:
    if not isinstance(payload, dict):
        raise ValidationError("payload must be a dict")

    if "id" not in payload:
        raise ValidationError("id is required")
    if "name" not in payload:
        raise ValidationError("name is required")

    return Student(
        id=parse_text(payload["id"], "id"),
        name=parse_text(payload["name"], "name"),
    )


def parse_assessment(payload: object) -> Assessment:
    if not isinstance(payload, dict):
        raise ValidationError("payload must be a dict")

    for field in ("id", "title", "weight", "total"):
        if field not in payload:
            raise ValidationError(f"{field} is required")

    return Assessment(
        id=parse_text(payload["id"], "id"),
        title=parse_text(payload["title"], "title"),
        weight=parse_number(payload["weight"], "weight"),
        total=parse_number(payload["total"], "total"),
    )


def parse_mark(payload: object) -> Mark:
    if not isinstance(payload, dict):
        raise ValidationError("payload must be a dict")

    for field in ("student", "assessment", "score"):
        if field not in payload:
            raise ValidationError(f"{field} is required")

    return Mark(
        student=parse_text(payload["student"], "student"),
        assessment=parse_text(payload["assessment"], "assessment"),
        score=parse_number(payload["score"], "score"),
    )