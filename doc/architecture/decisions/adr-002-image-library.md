# ADR-002: Image Processing Library

Status: Accepted

## Context

The application needs to decode user-supplied images and normalized them for processing.

Requirements:

- support JPG and PNG
- normalize EXIF orientation
- convert to a predictable pixel format
- work locally with no external services

---

## Decision

Use the **Pillow** library for image decoding and normalization.

---

## Alternatives Considered

### OpenCV

Pros:
- powerful image processing capabilities

Cons:
- heavy dependency
- unnecessary complexity for simple decoding

---

### ImageIO

Pros:
- simple API

Cons:
- less mature ecosystem
- fewer image handling utilities

---

## Consequences 

Pros:

- widely used Python image library
- reliably format support
- easy EXIF normalization

Cons:

- introduces dependency on Pillow