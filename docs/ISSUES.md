# Ranked issues

| rank | issue | impact |
|---:|---|---|
| 1 | Timeout handling was missing in the agent loop. | Hurts the automated grader by causing tests to hang indefinitely. |
| 2 | Tool call restrictions were not fully categorized. | Hurts strict contract compliance checks. |
| 3 | Trace logging was limited to basic outputs. | Limits deep debugging capabilities. |

## Rank 1, in progress
- The fix: Added a ThreadPoolExecutor with a 30-second timeout in agent.py.
- The regression test: tests/test_contract.py
- Before and after: see EVAL_REPORT.md.