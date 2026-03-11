from __future__ import annotations

from dataclasses import dataclass

from safeid.core.domain.errors import *


@dataclass(frozen=True)
class ErrorDialogModel:
    title: str
    message: str
    detail: str
    

def map_error_to_dialog(error: SafeIdError) -> ErrorDialogModel:
    if isinstance(error, InvalidImageCountError):
        return ErrorDialogModel(
            title="Invalid Selection",
            message="Please select 1 or 2 images.",
            detail=error.detail,
        )

    if isinstance(error, UnsupportedFormatError):
        return ErrorDialogModel(
            title="Unsupported Format",
            message="Unsupported file format. Please use JPG or PNG.",
            detail=error.detail,
        )

    if isinstance(error, ImageTooSmallError):
        return ErrorDialogModel(
            title="Image Too Small",
            message="Image is too small. Minimum size is 600px on both sides.",
            detail=error.detail,
        )

    if isinstance(error, EmptyRecipientError):
        return ErrorDialogModel(
            title="Missing Recipient",
            message="Recipient cannot be empty.",
            detail=error.detail,
        )

    if isinstance(error, OutputAlreadyExistsError):
        return ErrorDialogModel(
            title="Output Already Exists",
            message="A file with this name already exists.",
            detail=error.detail,
        )

    if isinstance(error, ExportFailedError):
        return ErrorDialogModel(
            title="Export Failed",
            message="Failed to export the PDF.",
            detail=error.detail,
        )

    if isinstance(error, LayoutDoesNotFitError):
        return ErrorDialogModel(
            title="Layout Error",
            message="The selected images do not fit on the page with the current layout settings.",
            detail=error.detail,
        )

    if isinstance(error, InvalidInputError):
        return ErrorDialogModel(
            title="Invalid Input",
            message=error.user_message,
            detail=error.detail,
        )

    return ErrorDialogModel(
        title="Error",
        message=error.user_message,
        detail=error.detail,
    )