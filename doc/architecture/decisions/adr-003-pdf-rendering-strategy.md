# ADR-003: PDF Rendering Strategy

Status: Accepted

## Context

The system must generate a PDF document containing:

- one A4 page
- one or two images
- a repeated watermark overlay

The renderer must:

- operate entirely in memory
- avoid temporary files
- produce deterministic output

---

## Decision

User **ReportLab** to render the final PDF.

---

## Alternatives Considered

### PyFPDF

Pros:
- simple API

Cons:
- limited flexibility
- fewer drawing features

---

### HTML to PDF engines

Pros:
- easier layout authoring

Cons:
- heavy dependencies
- unpredictable rendering behavior

---

## Consequences

Pros:
- mature PDF generation library
- fine control over geometry
- good integration with Python

Cons:
- lower-level drawing API