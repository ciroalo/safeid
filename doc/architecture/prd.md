# Requirements
**Project name:** Document Watermarker  
**Project manager:** @Ciro Alonso  
**Last revision date:** February 18, 2026  
**Version:** 0.1

Legend:  
[P0] = MVP  
[P1] = First version. Possibly ﬁnal.  
[P2] = Second version (optional). OCR plugin.  
[P3] = Third version (optional). Preview plugin.


## Functional Requirements (FR)
### Input & Validation  
[P0] FR-1 – Import 1-2 images (JPG/JPEG/PNG only)
- User may select exactly 1 or 2 ﬁles.
- Allowed formats: .jpg, .jpeg and .png.
- 0 or >2 selected ﬁles shows an error messages and does not crash.

[P0] FR-2 – Validate image readability, basic integrity and size
- Corrupt ﬁles do produces an error message and does not crash.
- If size is too small to upscale it produces an error message and does not continue. If any of the images has width or height of <600px, it will be rejected.

### Watermark conﬁguration

[P0] FR-3 – Required watermark text (recipient/company)
- Watermark text ﬁeld must be non-empty after trimming.
- Watermark text must appear in the exported document.

[P0] FR-4 – Basic styling options (font-size + line spacing/density)
- User can control font size and line spacing / tiling density.
- Output reﬂects conﬁguration.

[P0] FR-5 – Tiled watermark covering entire page including photo area
- Watermark always overlays photo(s).
- Repeated pattern covers the entire A4 page.

[P0] FR-6 – Use system default font
- Use macOS system default font.
- No bundled fonts in MVP.

[P1] FR-7 – Advanced watermark controls (opacity, angle, presets)
- User can control opacity and angle.
- Presets, gives already a default value instead of zero.
Layout & PDF export

[P0] FR-8 – Export to single-page A4 PDF only
- Exported ﬁle is a PDF on A4 page size.
- Opens correctly in macOS Preview.

[P0] FR-9 – Fixed minimum sized margins (19 mm) on all sizes
- Layout must respect 19mm on top, bottom, left and right sides.

[P0] FR-10 – Image placement (stacked vertically, centered)
- If 1 image:
o Centered within usable content area (A4 minus 19mm margins).
o Aspect ratio preserved.
o No distortion.
- If 2 images:
o Stacked vertically (one on top of the other).
o Both images centered horizontally.
o Combined layout vertically centered within content area.
o Proportional spacing between images, minimum of 12mm.
o Aspect ratios preserved.

[P0] FR-11 – Image rotation allowed for better ﬁt
- Images may be rotated (90 degrees increments) to better ﬁt landscape layout.
- Rotation must improve ﬁt inside content area.
- No arbitrary angle rotation.

[P0] FR-12 – Deterministic scaling rules
- Same inputs + same settings = same layout.
- No cropping in MVP.

[P0] FR-13 – Output naming convention
- Output ﬁlename format: <ﬁle_name>_<recipient>_watermarked.pdf
- <ﬁle_name> is the name of the ﬁle of the ﬁrst image selected.
- Saved in the directory of the ﬁrst selected image (MVP).

[P0] FR-14 – No overwrite. Quit after dialog error closes
- If a ﬁle with that name already exists show error dialog and quit after dialog closes. Privacy & Security

[P0] FR-15 – Olline only processing
- App functions without network.
- No telemetry or external API calls.

[P0] FR-16 – Strip EXIF metadata from output
- Input data not preserved in PDF.
- PDF metadata minimized.

[P0] FR-17 – No persistent or storage or history
- No saved sessions, nor recent ﬁles list.
- No logs containing sensitive data.

[P0] FR-18 – Minimal temp ﬁle usage
- Prefer in-memory processing.
- If temp ﬁles are required, clean them after execution.

### Error Handling
[P0] FR-19 – Clear, actionable error messages
- Must cover: Unsupported format, corrupt image, cancel ﬁle selection and output ﬁle
exists.

### Optional Future Phases
[P2] FR-20 – OCR plugin (olline, packaged model)  
[P2] FR-21 – User-selected redaction regions  
[P3] FR-22 – Preview window plugin 

## Non-Functional Requirements (NFR)
[P0] NFR-1 – Performance
- Export completes in <1s.

[P0] NFR-2 – Reliability
- No crashes or invalid input.
- Deterministic layout rules.

[P0] NFR-3 – Privacy-ﬁrst architecture
- No network dependency.
- No sensitive logging.
- In-memory processing preferred.

[P0] NFR-4 – Usability
- Happy path under 30 seconds.

[P0] NFR-5 – macOS packaging ready

[P0] NFR-6 – Open-source quality
- Clean repository structure.
- Pinned dependencies.
- Quality readme.