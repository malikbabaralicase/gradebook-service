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