# Retention policy

STORED: preferences and the last N episodes
WHY: to provide context-aware research assistance
CORRECTED BY: user clearing or overriding session memory
EXPIRES: 30 days
WE REFUSE TO REMEMBER: passwords, authentication keys, and sensitive personal data

## How the code enforces it
name: retention-check
description: verified by tests/test_contract.py ensuring caps and resets work correctly.