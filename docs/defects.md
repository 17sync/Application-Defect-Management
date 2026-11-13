# Defect log

All expected results below come from FR-01, FR-03, FR-04, FR-08, and FR-13 in `REQUIREMENTS.md`. Reproduction tests were run against the unmodified starter before source fixes.

| ID | Requirement | Reproduction | Expected | Starter actual | Failed test ID | Status |
|---|---|---|---|---|---|---|
| D-01 | FR-01 | `check_credit_limit(15, 3)` | `True` at exactly 18 credits | `False` | `BVA-TOTAL-18` | Fixed on `fixes`; [Issue #5](https://github.com/17sync/Application-Defect-Management/issues/5) |
| D-02 | FR-03 / FR-06 | `prerequisites_satisfied({'CS101'}, {'CS101','MATH101'})` | `False`; registration is `PREREQUISITES_MISSING` | `True` because any intersection suffices | `ECP-PR-SOME` | Fixed on `fixes`; [Issue #2](https://github.com/17sync/Application-Defect-Management/issues/2) |
| D-03 | FR-04 / FR-09 | decision for dues Rs. 1, all else eligible | `DUES_BLOCK` | `REGISTERED` | `BVA-DUES-1` | Fixed on `fixes`; [Issue #3](https://github.com/17sync/Application-Defect-Management/issues/3) |
| D-04 | FR-08 | eligible student, `enrolled == capacity` | `WAITLISTED` | `REGISTERED`; the over-capacity check can never be reached with valid input | `BVA-CAPACITY-FULL` | Fixed on `fixes`; [Issue #1](https://github.com/17sync/Application-Defect-Management/issues/1) |
| D-05 | FR-13 | withdraw registered course with `enrolled=1` | credits decrease and `enrolled` becomes 0 | student changes; enrollment remains 1 | `STATE-WITHDRAW` | Fixed on `fixes`; [Issue #4](https://github.com/17sync/Application-Defect-Management/issues/4) |

## GitHub issue records

The records map one-to-one to GitHub Issues #1 through #5 in this repository. The links above are the created issue records.
