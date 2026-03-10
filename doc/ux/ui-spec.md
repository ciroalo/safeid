# UI Specification

## Purpose

This document defines the MVP user interface for SafeID

The goal of the UI is to provide a simple, safe, and local-first workflow for 
generating a watermarked PDF from one or two identity images.

The UI is intentionally minimal. It should expose only the controls required for the MVP and map engine errors into clear user-facing messages.

---

## UX Goals

The MVP UI should be:

- Simple to understand on first use
- Fast to complete for a single task
- Safe by default
- Clear when something fails
- Thin, with business logic delegated to the application core

---

## Primary User Flow

1. User launches the application
2. User selects 1 or 2 images
3. User enters the recipient or company name
4. User optionally edits the watermark text
5. User clicks **Generate PDF**
6. The application validates the inputs
7. The application generates the watermarked PDF locally
8. The application shows a success dialog with the output file path

---

## Error flows

### Invalid image count
- User selects fewer than 1 image or more than 2 images
- App shows an error dialog
- User returns to the main screen and corrects the selection

### Image too small
- User selects an imagesmaller than the minimum allowed size
- App shows an error dialog explaining the size requirement

### Output already exists 
- A PDF with the generated output name already exists
- App shows an error dialog and does not overwrite the file

### Export failure
- File cannot be written because of permissions or another filesystem issue
- App shows an error dialog with a short explanation

---

## Main screen

The MVP application uses a single main screen

### Layout

```text
+------------------------------------------------------+
| SafeID                                               |
| Generate a watermarked PDF from 1 or 2 ID images     |
+------------------------------------------------------+

[ Select Images ]

Selected files:
- passport_front.jpg
- passport_back.jpg

Recipient / Company
[________________________________________]

Watermark text (optional)
[________________________________________]

[ Generate Watermarked PDF ]
```

## UI Components

1. Select Images button  
    Purpose:

    - Opens the native file picker
    - Allows the user to choose 1 or 2 image files

    Behavior:

    - Accept JPG and PNG
    - After selection, display the selected filenames in the main window

2. Selected files list  
    Purpose:
    - Shows the images currently selected by the user

    Behavior:
    - Display filenames only
    - Preserve selection order

3. Recipient/Company input  
    Purpose:
    - Captures the intended recipient name
    - used in output file naming
    - used as the default watermark text if no custom watermark is provided

    Behavior:
    - Required field
    - Trim leading and trailing whitespace before submission

4. Watermark text input  
    Purpose:
    - Allows the user to override the default watermark text

    Behavior:
    - Optional field
    - If empty, use the recipient value as the watermark text

5. Generate Watermarked PDF button  
    Purpose:
    - Submits the form and triggers the PDF generation

    Behavior:
    - Enabled only when required inputs are present, or validation happens on click
    - Calls the application core through the composition root


## Validation Rules

### Required inputs
- At least 1 image and at most 2 images
- Recipient must not be empty

### Optional inputs
- Watermark text may be empty
- If watermark text is empty, recipientis used as watermark text

### Engine-level validation
The UI should rely on the application core for:
- file format validation
- image size validation
- output filename collision detection
- export failure handling


## Dialogs

### Success dialog
Message example:

**PDF created successfully**  
Saved to: `/path/to/output.pdf`

Actions: 
- OK

### Error dialog
Message structure:
- Main message: short user-friendly description
- Details: optional secondary text

Example:
**Output file already exists**  
`path/to/output.pdf`

Actions:
- OK

## Error Mapping

| Domain Error | UI Message |
| ------ | ------ |
| InvalidImageCountError | Please select 1 or 2 images. |
| UnsupportedFormatError | Unsupported file format. Please use JPG or PNG. |
| ImageTooSmallError | Image is too small. Minimum size is 600px on both sides. |
| EmptyRecipientError | Recipient cannot be empty. |
| OutputAlreadyExistsError | Output file already exists. Please choose a different recipient or folder. |
| ExportFailedError | Failed to export the PDF. |
| InvalidInputError | The provided input is not valid. |

## UI-to-Core Interaction

The UI must remain thin

Responsibilities of the UI:

- Collect user input
- Build `CreateWatermarkedRequest`
- Call `CreateWatermarkedPdfUseCase`
- Display success or error dialogs

Responsibilities of the core:
- Validate domain rules
- Decode images
- Plan layout
- Render PDF
- Export output

---

## MVP Scope

Included:
- Single main window
- Native file picker
- Recipient input
- Optional watermark text input
- Generate button
- Success and error dialog

Not included:
- Drag and drop
- Image preview
- Layout settings
- Watermark style controls
- OCR-based field detection
- Redaction controls
- Batch processing

## Future UI Enhancements

Possible future additions:
- Layout selection panel
- Watermark appearance controls
- Drag and drop image selection
- Preview of the generated page
- OCR detection and redaction selection
- Open output file / reveal in Finder action after success
