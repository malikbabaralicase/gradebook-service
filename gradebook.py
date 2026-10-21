# gradebook.py -- the department gradebook service
import datetime
import http.server
import json
import logging
import sys
from collections.abc import Callable
from typing import Any

from errors import ConflictError, NotFoundError, ValidationError
from models import Mark, parse_assessment, parse_mark, parse_student
from rules import ensure_weight_fits

DATA: str = "gradebook.json"
STATE: dict[str, Any] = {
    "students": {},
    "assessments": {},
    "marks": [],
}

logger = logging.getLogger(__name__)


def load() -> None:
    global STATE

    try:
        with open(DATA) as file:
            STATE = json.load(file)
    except FileNotFoundError:
        STATE = {"students": {}, "assessments": {}, "marks": []}


def save() -> None:
    with open(DATA, "w") as file:
        json.dump(STATE, file)


def pct(sid: str) -> str:
    total = 0.0
    got = 0.0

    for mark in STATE["marks"]:
        if mark["student"] == sid:
            assessment = STATE["assessments"].get(mark["assessment"])

            if assessment:
                try:
                    score = float(mark["score"])
                    weight = float(assessment["weight"])
                    assessment_total = float(assessment["total"])
                except (TypeError, ValueError):
                    continue

                if assessment_total <= 0:
                    continue

                got += score * weight / assessment_total
                total += weight

    if total == 0:
        return "0"

    return str(round(got, 2))

def now() -> str:
    return str(datetime.datetime.now())


def add_mark(
    state: dict[str, Any],
    mark: Mark,
    now: Callable[[], str],
    save: Callable[[], None],
) -> None:
    if mark.student not in state["students"]:
        raise NotFoundError("student not found")

    assessment = state["assessments"].get(mark.assessment)
    if assessment is None:
        raise NotFoundError("assessment not found")

    if mark.score > float(assessment["total"]):
        raise ValidationError("score must not exceed total")

    record = {
        "student": mark.student,
        "assessment": mark.assessment,
        "score": mark.score,
        "at": now(),
    }

    state["marks"].append(record)
    save()


def add_assessment(
    state: dict[str, Any],
    assessment: dict[str, Any],
    save: Callable[[], None],
) -> None:
    """Validate, store, and save an assessment."""
    assessment_id = assessment["id"]

    if assessment_id in state["assessments"]:
        raise ConflictError("assessment already exists")

    ensure_weight_fits(
        [
            item["weight"]
            for item in state["assessments"].values()
        ],
        assessment["weight"],
    )

    state["assessments"][assessment_id] = assessment
    save()

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        logger.info("%s - %s", self.address_string(), format % args)

    def _send(self, code: int, obj: object) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _error_boundary(
        self,
        operation: Callable[[], tuple[int, object]],
    ) -> None:
        try:
            status, body = operation()
        except ValidationError as exc:
            status, body = 400, {"error": str(exc)}
        except NotFoundError as exc:
            status, body = 404, {"error": str(exc)}
        except ConflictError as exc:
            status, body = 409, {"error": str(exc)}
        except Exception:
            logger.exception(
                "Unexpected error handling %s %s",
                self.command,
                self.path,
            )
            status, body = 500, {"error": "internal error"}

        self._send(status, body)

    def do_GET(self) -> None:
        self._error_boundary(self._get)

    def _get(self) -> tuple[int, object]:
        if self.path == "/students":
            return 200, list(STATE["students"].values())

        if self.path.startswith("/students/"):
            parts = self.path.split("/")

            if len(parts) != 3 or not parts[2]:
                raise NotFoundError("student not found")

            sid = parts[2]

            if sid not in STATE["students"]:
                raise NotFoundError("student not found")

            student = dict(STATE["students"][sid])
            student["percentage"] = pct(sid)
            return 200, student

        if self.path == "/assessments":
            return 200, list(STATE["assessments"].values())

        if self.path == "/report":
            report = []

            for sid in STATE["students"]:
                report.append(
                    {
                        "id": sid,
                        "name": STATE["students"][sid]["name"],
                        "pct": pct(sid),
                    }
                )

            return 200, report

        raise NotFoundError("unknown route")

    def do_POST(self) -> None:
        self._error_boundary(self._post)

    def _post(self) -> tuple[int, object]:
        content_length = self.headers.get("Content-Length")

        if content_length is None or not content_length.isdigit():
            raise ValidationError("Content-Length must be a number")

        length = int(content_length)
        raw = self.rfile.read(length)

        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValidationError("body must be valid JSON") from None

        if not isinstance(data, dict):
            raise ValidationError("body must be a JSON object")

        if self.path == "/students":
            student = parse_student(data)

            if student.id in STATE["students"]:
                raise ConflictError("student already exists")

            record = {
                "id": student.id,
                "name": student.name,
                "joined": str(datetime.datetime.now()),
            }

            STATE["students"][student.id] = record
            save()
            return 200, record

        
        if self.path == "/assessments":
            assessment = parse_assessment(data)

            record = {
                "id": assessment.id,
                "title": assessment.title,
                "weight": data["weight"],
                "total": data["total"],
            }

            add_assessment(STATE, record, save)
            return 200, record


        
        if self.path == "/marks":
            mark = parse_mark(data)
            add_mark(STATE, mark, now, save)
            logger.info(
                "Recorded mark for %s with score %s",
                mark.student,
                mark.score,
            )
            return 200, {"ok": True}
        raise NotFoundError("unknown route")


def main(argv: list[str] = sys.argv) -> None:
    logging.basicConfig(level=logging.INFO)
    load()

    port = 8000

    if len(argv) > 1:
        port_text = argv[1]

        if not port_text.isdigit():
            raise SystemExit("port must be a whole number from 1 to 65535")

        port = int(port_text)

        if not 1 <= port <= 65535:
            raise SystemExit("port must be a whole number from 1 to 65535")

    logger.info("gradebook on %s", port)
    http.server.HTTPServer(("", port), Handler).serve_forever()


if __name__ == "__main__":
    main()