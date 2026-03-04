# ADR-4: Adopt Hexagonal Architecture (Port and Adapters)

**Status:** Draft (Proposed)  
**Project manager:** @Ciro Alonso  
**Last revision date:** March 4, 2026  
**Version:** 0.1

## Context
The application's MVP must:
- Run locally (no cloud processing) and avoid retaining user data.
- Produce a deterministic, professional **A4 PDF output** from 1-2 input images (JPG/PNG), with consistent layout rules (margins, centering, rotation of 90 degrees if beneficial)
- Be macOS-first, with open for open-source quality.
- Keep room for future capabilities (OCR-based attribute detection and optional redaction/blackout) without forcing major rewrites.

## Decision
Adopt a **Hexagonal Architecture (Ports & Adapters):**
- Define an **Aplication Core** containing:
    - Use cases (ex. SafeID)
    - Domain models (e.g., ImageAsset, WatermarkSpec, LayoutPlan, ExportSpec)
    - Pure planning logic (LayoutPlanner, WatermarkPlanner) with deterministic outputs

- Define ports (interfaces) owned by the core for external concerns:
    - ImageDecoderPort (JPG/PNG decode + normalization; drop metadata implications early)
    - PdfRendererPort (render A4 PDF from plans + images)
    - FileSystemPort (export “create new only”; error if exists)
    - (Future) OcrPort and RedactionPort as optional adapters

- Implement adapters outside the core:
    - GUI adapter (macOS UI)
    - Pillow-based image decoding adapter
    - PDF rendering adapter (library-specific)
    - Local filesystem adapter

Dependency rule: adapters depend on the core; the core does not depend on adapters or third-party libraries directly.

## Alternatives Considered
1. Layered architecture (UI -> services -> domain -> infrastructure)
    - Pros: simpler upfront structure; faster to implement for small apps.
    - Cons: domain/use-case logic tends to leak dependency on PDF/image libraries and filesystem; harder to swap rendering strategy or add OCR cleanly; unit testing often becomes integration-heavy.

2. Single-module / script-first MVP
    - Pros: fastest possible MVP.
    - Cons: high refactor cost as features grow; weak testability; easy to violate privacy “safe-by-default” goals via accidental logging/temp files; harder to open-source with clean boundaries.

3. Full Clean Architecture (more formal rings/entities/use cases/interface adapters/frameworks)
    - Pros: very rigorous separation.
    - Cons: risk of over-engineering at MVP scale; more boilerplate than needed given current scope.

## Consequences

Positive
- Testability: layout and watermark planning can be unit-tested without PDF/UI/filesystem dependencies, supporting deterministic behavior expectations.
- Maintainability: swapping GUI frameworks or PDF backends is localized to adapters.
- Extensibility: future OCR/redaction can be introduced as new adapters behind new ports, without rewriting the core. 
- Privacy/security control: core explicitly constrains how data flows to adapters, supporting the “no retention / local-only” intent.

Negative
- Additional upfront structure (ports, wiring) compared to a simple layered approach.
- Requires discipline to keep third-party types (e.g., PIL Image, PDF canvas objects) out of the core.
- Slightly more work to set up dependency injection/wiring in the UI adapter.

## Validation Plan
We will validate this decision by:
1. Vertical slice prototype: UI selects 1 image -> core computes plans -> renderer produces PDF bytes -> filesystem exports with “error if exists”.

2. Unit tests (core):
    - Layout invariants: margins respected, aspect ratio preserved, images centered, no overlap, rotation applied only in 90° and only if it improves fit.
    - Watermark planning invariants: watermark covers photo area; parameters are deterministic.

3. Golden/regression tests (adapters):
    - Generate PDFs from fixed fixtures; validate page size A4 and key geometry invariants (and optionally compare rendered page images).

4. Privacy checks:
    - Confirm no temp files remain on disk after export failures.
    - Confirm exported output does not carry over source EXIF and keeps PDF metadata minimal per design intent.

