# Document Watermarker – Project Charter
**Project name:** Document Watermarker  
**Project manager:** @Ciro Alonso  
**Last revision date:** February 18, 2026  
**Version:** 0.1

## 1. Problem Statement
People often need to **share sensitive ID images (passport/ID card) with companies or individuals**. If those images leak, they can be abused. Users need a simple, online tool that converts 1-2 ID photos into a clean PDF page and overlays a visible, repeated watermark to discourage misuse.

## 2. Goals
- Generate a single-page PDF (or predictable multi-page if 2 photos) containing 1-2
images centered on a blank page.
- Apply conﬁgurable watermarks (recipient/company name) in a safe-by-default way.
- Ensure online-only processing with no persistent retention.
- Strip sensitive metadata (EXIF) from outputs.
- Provide a simple macOS GUI suitable for personal use and later sharing.

## 3. Non-Goals
- Cloud upload/sharing features.
- Accounts system, history, recent ﬁles list.
- Batch processing or many images.

## 4. Users-stakeholders
- Primary: individual users sending ID photos to a recipient.

## 5. Scope
MVP: macOS GUI -> load 1-2 images -> set watermark text + basic styling -> export PDF. Future (v2+): optional OCR-based ﬁeld detection and user-selected redaction regions (oAline), improved templated/layout options. Later (v3+): show provisional output on how it would look with the current style selected.

## 6. Success Metrics
- Typical export completes in <1s for 1-2 photos.
- Zero network access required.
- No leftover temp ﬁles: no output unless user exports.
- Users can reliably produce a PDF that meets a “send to company” workﬂow.

## 7. Risk & Mitigations
- Privacy leakage via metadata/temp ﬁles: process in-memory, strip EXIF, minimize
logging.
- PDF quality / scaling issues: golden-image tests + ﬁxed layout rules, render veriﬁcation.
- GUI packaging complexity on macOS: choose a framework with a clear packaging story;
keep architecture modular.

## 8. Milestones
- MVP (v0.1): UI + watermark + PDF export + EXIF strip + error-on-existing-ﬁle.
- v1.0: presets, better typography controls, accessibility polish, robust tests, signed
macOS app packaging.
- v2.0: oAline OCR plugin + redaction UI + audit-friendly privacy mode.
- v3.0: small preview window on how the document would look.