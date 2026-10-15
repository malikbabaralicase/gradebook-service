# gradebook.py -- the department gradebook service

import datetime
import http.server
import json
import logging
import sys

from errors import ConflictError, NotFoundError, ValidationError
from models import parse_assessment, parse_mark, parse_student

DATA = "gradebook.json"
STATE = {}


def load():
    global STATE
    try:
        with open(DATA) as f:
            STATE = json.load(f)
    except FileNotFoundError:
        STATE = {"students": {}, "assessments": {}, "marks": []}


def save():
    with open(DATA, "w") as f:
        json.dump(STATE, f)



def pct(sid):
    total = 0.0
    got = 0.0

    for m in STATE["marks"]:
        if m["student"] == sid:
            a = STATE["assessments"].get(m["assessment"])
            if a:
                try:
                    score = float(m["score"])
                    weight = float(a["weight"])
                    assessment_total = float(a["total"])
                except (TypeError, ValueError):
                    continue

                if assessment_total <= 0:
                    continue

                got += score * weight / assessment_total
                total += weight

    if total == 0:
        return "0"

    return str(round(got, 2))



class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logging.info("%s - %s", self.address_string(), format % args)

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _error_boundary(self, operation):
        try:
            status, body = operation()
        except ValidationError as exc:
            status, body = 400, {"error": str(exc)}
        except NotFoundError as exc:
            status, body = 404, {"error": str(exc)}
        except ConflictError as exc:
            status, body = 409, {"error": str(exc)}
        except Exception:
            logging.exception("Unexpected error handling %s %s", self.command, self.path)
            status, body = 500, {"error": "internal error"}

        self._send(status, body)

    def do_GET(self):
        self._error_boundary(self._get)

    def _get(self):
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

    def do_POST(self):
        self._error_boundary(self._post)

    def _post(self):
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

            if assessment.id in STATE["assessments"]:
                raise ConflictError("assessment already exists")

            record = {
                "id": assessment.id,
                "title": assessment.title,
                "weight": data["weight"],
                "total": data["total"],
            }

            STATE["assessments"][assessment.id] = record
            save()
            return 200, record

        if self.path == "/marks":
            mark = parse_mark(data)

            if mark.student not in STATE["students"]:
                raise NotFoundError("student not found")

            if mark.assessment not in STATE["assessments"]:
                raise NotFoundError("assessment not found")

            assessment = STATE["assessments"][mark.assessment]
            if mark.score > float(assessment["total"]):
                raise ValidationError("score must not exceed total")

            record = {
                "student": mark.student,
                "assessment": mark.assessment,
                "score": data["score"],
                "at": str(datetime.datetime.now()),
            }

            STATE["marks"].append(record)
            save()

            logging.info(
                "Recorded mark for %s with score %s",
                mark.student,
                mark.score,
            )
            return 200, {"ok": True}

        raise NotFoundError("unknown route")


def main(argv=sys.argv):
    logging.basicConfig(level=logging.INFO)
    load()
    port = 8000
    if len(argv) > 1:
        port = int(argv[1])

    logging.info("gradebook on %s", port)
    http.server.HTTPServer(("", port), Handler).serve_forever()


if __name__ == "__main__":
    main()