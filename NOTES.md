# Lab 03 — Task 2: Existing Failures

## (a) GET /students/NOPE

**Command:**
```powershell
curl.exe -i http://localhost:8000/students/NOPE
```

**Actual result:** HTTP 200 OK

**Response:**
```json
{"error": "not found"}
```

**Observation:** The service returns an error message but uses HTTP 200 instead of the expected HTTP 404 status code.

## (b) POST /students with body `5`

**Command:**
```powershell
curl.exe -i -X POST http://localhost:8000/students -H "Content-Type: application/json" -d "5"
```

**Actual result:** No HTTP response. `curl` reported error 52: Empty reply from server.

**Observation:** The service did not return a proper HTTP response for this invalid request. Check the server terminal for the corresponding exception.

### (c) POST /marks with invalid score

**Setup:** Created assessment A1 successfully.

**Command:** Sent a POST request to `/marks` using `requests/mark.json`, containing `"score": "abc"`.

**Actual result:** HTTP 200 OK with response `{"ok": true}`.

**Observation:** The service accepted a mark with a non-numeric score instead of rejecting invalid input.

### (d) POST /assessments with zero total

**Command:** POST request to `/assessments` using `requests/zero-assessment.json`.

**Actual result:** HTTP 200 OK.

**Response:** The service returned the created assessment with `"total": "0"`.

**Observation:** The service accepted a zero assessment total instead of rejecting the invalid value.

### (e) POST /marks with nonexistent assessment

**Command:** POST request to `/marks` using `requests/missing-assessment-mark.json`.

**Actual result:** HTTP 200 OK with response `{"ok": true}`.

**Observation:** The service accepted a mark referencing assessment `NOPE`, which does not exist.

### Ruff check results

**Command:** `ruff check .`

**Actual result:** 8 errors reported.

**Findings:**
- `I001`: Import block is unsorted.
- `F401`: Unused `os` import.
- `SIM115`: Two file-opening operations should use context managers.
- `E722`: Three bare `except:` statements.
- `S110`: An exception is silently ignored using `except: pass`.

**Bare except locations:**
- `gradebook.py:19`
- `gradebook.py:28`
- `gradebook.py:84`

**Observation:** The existing code contains linting issues and overly broad exception handling. These findings will be addressed in the relevant later tasks.


## Task 8 — Repeat Task 2 Requests

Repeated the Task 2 HTTP requests using `curl.exe` and the JSON files in the `requests/` directory.

| Request | Actual HTTP status | Actual response |
|---|---:|---|
| POST `/assessments` — `assessment.json` | 409 Conflict | `assessment already exists` |
| POST `/marks` — `mark.json` | 400 Bad Request | `score must be a finite number` |
| POST `/marks` — `missing-assessment-mark.json` | 404 Not Found | `assessment not found` |
| POST `/assessments` — `zero-assessment.json` | 400 Bad Request | `total must be greater than 0` |

The service returned structured JSON error responses for the duplicate assessment, invalid score, missing assessment, and zero assessment total.

## Lab 04 — Task 8: Mutation Testing and Test Doubles

### (a) Mutation testing

Temporarily changed the percentage calculation in `gradebook.py` from division to multiplication:

```python
got += score * weight * assessment_total
```

**Command:** `pytest -v`

**Actual result:** 3 failed, 24 passed.

**Failures observed:**
- `one-mark`: expected `7.5`, but got `3000.0`.
- `full-mark`: expected `10.0`, but got `4000.0`.
- `two-marks`: expected `31.5`, but got `63000.0`.

**Observation:** The percentage tests detected the incorrect calculation. The zero-mark and no-marks cases still passed, demonstrating why multiple test cases are important.

Restored the correct calculation:

```python
got += score * weight / assessment_total
```

**Verification command:** `pytest -v`

**Final result:** 27 passed.

### (b) Test doubles

A **stub** provides predefined responses to a dependency so a test can control its behavior.

A **fake** is a simplified working implementation of a dependency, suitable for testing but not intended for production use.

A **mock** is a test double that can be used to verify interactions with a dependency, such as whether a function was called.

### (c) Why mocks were not needed for percentage and storage tests

**Percentage tests:** The tests use controlled gradebook state through fixtures and check the returned percentage. Mocking is unnecessary because the calculation can be tested directly using known input data.

**Storage tests:** The tests use temporary files through `tmp_path` and redirect the data-file path using `monkeypatch`. This tests actual JSON file reading and writing without mocking the file operations.

# Lab 05 Notes

## Task 1 — Initial Coverage

- **Total coverage:** 48%
- **File with the lowest coverage:** `gradebook.py` — 37%

## Task 2 — TDD Cycles

### Cycle 1
- Test: `([], 50)` fits.
- Red failure: `ModuleNotFoundError: No module named 'rules'`
- Green: `1 passed`.

### Cycle 2
- Test: `([60], 50)` raises `ValidationError` with `"100"` in the message.
- Red failure: Not recorded.
- Green: `2 passed`.

### Cycle 3
- Test: `([60], 40)` fits.
- Red failure: None; the test passed on the first run.
- Green: `3 passed`.

### Cycle 4
- Test: `([9.3, 27.3, 33.7], 29.7)` fits.
- Red failure: `errors.ValidationError: Total weight cannot exceed 100`
- Red result: `1 failed, 3 passed`.
- Green: `4 passed`.