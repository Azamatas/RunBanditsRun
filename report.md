# RunBanditsRun Code Review Report

**Project:** Strava Clone (Activity Tracking + Social Feed)  
**Stack:** FastAPI + React + PostgreSQL  
**Date:** 2024  
**Total Findings:** 32 (Critical: 7, High: 7, Medium: 10, Low: 8)

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| Critical | 7 | Security vulnerabilities, data integrity risks |
| High | 7 | Performance bottlenecks, missing validation |
| Medium | 10 | Code duplication, maintainability issues |
| Low | 8 | Style inconsistencies, minor improvements |

---

## Critical Issues (7)

### C1: SQL Injection Risk in Raw Queries
- **File:** `backend/models/user.py:45-48`
- **Issue:** Raw SQL with string formatting for user queries
- **Risk:** Malicious input can execute arbitrary SQL
- **Fix:** Use SQLAlchemy ORM or parameterized queries

### C2: Password Hashing Without Salt
- **File:** `backend/services/auth_service.py:18-22`
- **Issue:** bcrypt.hashpw() called without explicit salt generation
- **Risk:** Rainbow table attacks if salt reuse occurs
- **Fix:** Use `bcrypt.gensalt()` and pass to hashpw

### C3: No Rate Limiting on Auth Endpoints
- **File:** `backend/routers/auth.py`
- **Issue:** Login/register endpoints have no rate protection
- **Risk:** Brute force attacks on user credentials
- **Fix:** Implement FastAPI rate limiting (e.g., slowapi)

### C4: JWT Secret Hardcoded
- **File:** `backend/config.py:8-10`
- **Issue:** SECRET_KEY defined as plain string in source
- **Risk:** Compromised secrets if repo is exposed
- **Fix:** Load from environment variables

### C5: No Input Sanitization on Activity Creation
- **File:** `backend/routers/activity.py:32-38`
- **Issue:** Activity title/description accepted without sanitization
- **Risk:** XSS attacks when rendered in frontend
- **Fix:** Sanitize HTML input, use DOMPurify on frontend

### C6: Direct File Upload Without Validation
- **File:** `backend/routers/upload.py:20-25`
- **Issue:** Profile picture uploads not validated for file type/size
- **Risk:** Malicious file upload, DoS via large files
- **Fix:** Validate MIME types, set size limits, scan for malware

### C7: No HTTPS Enforcement
- **File:** `backend/main.py:5-10`
- **Issue:** No middleware to redirect HTTP->HTTPS or set HSTS headers
- **Risk:** MITM attacks, session hijacking
- **Fix:** Add HTTPSRedirectMiddleware, set secure cookie flags

---

## High Priority Issues (7)

### H1: ~Duplicated Token Type Validation Logic~
- **File:** `backend/routers/auth.py:30-33`, `backend/routers/deps.py:15-20`
- **Issue:** Token type ("access" vs "refresh") checked manually in multiple endpoints
- **Impact:** Code duplication, inconsistent error handling
- **Fix:** ✅ **FIXED** - Centralized `decode_access_token()` and `decode_refresh_token()` in `auth_service.py`

### H2: N+1 Query Problem in Activity Feed
- **File:** `backend/services/activity_service.py`, `backend/services/feed_service.py`
- **Issue:** Each activity fetches owner and kudos separately in a loop via `enrich_activity()`
- **Impact:** O(n) queries for feed of n activities (1 + n + n queries)
- **Fix:** ✅ **FIXED** - Added `selectinload(Activity.owner)` and `selectinload(Activity.kudos)` to all activity queries in `list_activities()`, `get_feed()`, `get_activity()`, and `update_activity()`

### H3: No Pagination on Activities Endpoint
- **File:** `backend/routers/activity.py:40-50`
- **Issue:** `/activities` returns all records without pagination
- **Impact:** Performance degradation, large payloads, DoS risk
- **Fix:** Add FastAPI Paginator or manual offset/limit

### H4: Missing Validation on Segment Creation
- **File:** `backend/routers/segment.py:25-35`
- **Issue:** No validation that segment belongs to activity owner
- **Risk:** Users can create segments on others' activities
- **Fix:** Add ownership check in segment_service.create()

### H5: No Database Index on Frequently Queried Columns
- **File:** `backend/models/activity.py:10-15`
- **Issue:** No indexes on `user_id`, `created_at`, `is_public`
- **Impact:** Slow queries on user feeds, public activity lists
- **Fix:** Add `index=True` to SQLAlchemy Column definitions

### H6: Race Condition in Kudos Toggle
- **File:** `backend/services/activity_service.py:80-90`
- **Issue:** Check-then-act pattern: verify kudos exists, then delete/insert
- **Risk:** Duplicate kudos or failed deletion under concurrent requests
- **Fix:** Use database transaction with SELECT FOR UPDATE or unique constraint

### H7: No Input Length Limits
- **File:** `backend/schemas/user.py:10-25`
- **Issue:** Username, email fields have no max length validation
- **Impact:** Database errors, UI breaking, potential DoS
- **Fix:** Add `max_length` to Pydantic models matching DB schema

---

## Medium Priority Issues (10)

### M1: Hardcoded JWT Expiry in Multiple Files
- **File:** `backend/services/auth_service.py:12-14`, `backend/config.py:15-17`
- **Issue:** ACCESS_TOKEN_EXPIRE_MINUTES defined in two places
- **Fix:** Centralize in config.py, import elsewhere

### M2: No Error Handling for Database Failures
- **File:** `backend/services/*.py`
- **Issue:** SQLAlchemy operations not wrapped in try/except
- **Impact:** 500 errors on DB issues, no graceful degradation
- **Fix:** Add try/except blocks, return meaningful errors

### M3: Duplicate Code in Activity Enrichment
- **File:** `backend/services/activity_service.py:45-60`, `backend/services/feed_service.py:30-45`
- **Issue:** `enrich_activity()` logic duplicated in feed service
- **Fix:** Extract to shared utility function

### M4: No Logging for Important Events
- **File:** `backend/services/auth_service.py`
- **Issue:** No logging for login attempts, password resets, token refreshes
- **Impact:** Difficult debugging, audit trail missing
- **Fix:** Add structured logging (e.g., loguru, python-json-logger)

### M5: Inconsistent Response Formats
- **File:** `backend/routers/*.py`
- **Issue:** Some endpoints return `{"data": ...}`, others return bare objects
- **Impact:** Frontend needs conditional handling
- **Fix:** Standardize on `{"data": ..., "message": ...}` format

### M6: No OpenAPI Tags for Routers
- **File:** `backend/routers/*.py`
- **Issue:** API endpoints not grouped with tags
- **Impact:** Poor API documentation organization
- **Fix:** Add `tags=["auth"]` to router decorators

### M7: Magic Strings for Token Types
- **File:** `backend/services/auth_service.py:25-30`
- **Issue:** Hardcoded `"access"` and `"refresh"` strings
- **Fix:** Define constants `TOKEN_TYPE_ACCESS = "access"`

### M8: No Type Hints in Some Service Functions
- **File:** `backend/services/activity_service.py:10-20`
- **Issue:** Missing return type hints
- **Impact:** Poor IDE support, harder refactoring
- **Fix:** Add `-> ReturnType` annotations

### M9: Frontend No TypeScript
- **File:** `frontend/src/**/*.js`
- **Issue:** JavaScript instead of TypeScript
- **Impact:** No compile-time type checking, harder maintenance
- **Fix:** Migrate to TypeScript (incremental with `.tsx`)

### M10: No API Versioning
- **File:** `backend/main.py`
- **Issue:** All endpoints at root path
- **Impact:** Breaking changes harder to manage
- **Fix:** Add `/api/v1/` prefix to all routes

---

## Low Priority Issues (8)

### L1: Inconsistent Import Order
- **File:** `backend/routers/*.py`
- **Issue:** Imports not grouped (standard lib, third-party, local)
- **Fix:** Use isort or enforce order via linter

### L2: Missing Docstrings
- **File:** `backend/services/*.py`
- **Issue:** Functions lack docstrings
- **Fix:** Add Google-style docstrings

### L3: Line Length Exceeds 88 Characters
- **File:** Multiple files
- **Issue:** Lines exceed PEP8 recommended length
- **Fix:** Break long lines, use parenthesis for implied continuation

### L4: Inconsistent Naming (snake_case vs camelCase)
- **File:** `backend/schemas/*.py` vs `frontend/src/*.js`
- **Issue:** Backend uses snake_case, frontend uses camelCase
- **Fix:** Standardize on camelCase for API responses (or use alias)

### L5: No Pre-commit Hooks
- **File:** `.pre-commit-config.yaml` missing
- **Issue:** No automated linting before commits
- **Fix:** Add pre-commit with black, isort, flake8, mypy

### L6: Docker Compose Only for DB
- **File:** `docker-compose.yml`
- **Issue:** Only PostgreSQL containerized, not backend/frontend
- **Fix:** Add services for backend and frontend

### L7: No .gitignore for IDE Files
- **File:** `.gitignore`
- **Issue:** Missing patterns for `.vscode/`, `.idea/`, `*.swp`
- **Fix:** Update .gitignore with common patterns

### L8: Frontend No CSS Methodology
- **File:** `frontend/src/**/*.css`
- **Issue:** Inline styles and ad-hoc CSS classes
- **Fix:** Adopt BEM, Tailwind, or CSS Modules

---

## Quick Wins (Can Fix in <30 min)

1. **C4:** Move SECRET_KEY to environment variables
2. **H7:** Add input length limits to Pydantic schemas
3. **M7:** Define token type constants
4. **L3:** Run autopep8/black on entire codebase
5. **L7:** Update .gitignore

---

## Recommended Implementation Order

1. **Week 1:** Critical security (C1-C7)
2. **Week 2:** High priority performance (H2, H3, H5, H6)
3. **Week 3:** High priority validation (H4, H7) + Medium code quality (M1-M10)
4. **Week 4:** Low priority cleanup (L1-L8)

---

## Notes

- ✅ **H1 (Token Type Validation):** FIXED - Centralized decode functions in auth_service.py
- ⚠️ **H1 Correction:** Original finding description was inaccurate. The real issue was duplicated validation logic, not tokens being accepted incorrectly. Each endpoint manually checked `payload.get("type")` after decoding. Now resolved with `decode_access_token()` and `decode_refresh_token()`.
- ⚠️ **Behavioral Change:** New strict validation only accepts exact token types ("access" or "refresh"). Previously deps.py accepted `None` as well. Verify this matches intended behavior.
- ✅ **H2 (N+1 Query Problem):** FIXED - Added `selectinload()` to eager-load `Activity.owner` and `Activity.kudos` in all activity queries, reducing feed endpoint from O(n) queries to O(1) (3 queries total regardless of activity count).
