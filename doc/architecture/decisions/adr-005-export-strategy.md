# ADR-005: Export Strategy

Status: Accepted

## Context 

Exporting the generated PDF must follow strict safety rules:

- never overwrite existing files
- avoid partial file writes
- provide clear error messages

---

## Decision

Use exclusive file creation(`xb` mode) when writing the output file.

The system:

1. Checks if the file exists
2. Attempts exclusive write
3. Maps filesystem errors to domain errors

---

## Consequences

Pros:
- prevents accidental overwrite
- protects against race conditions
- ensures consistent error handling

Cons:
- requires explicit error handling logic