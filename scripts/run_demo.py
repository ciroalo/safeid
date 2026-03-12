from __future__ import annotations

import argparse
import sys
from pathlib import Path

from safeid.app.container import build_create_watermarked_pdf_use_case
from safeid.core.domain.models import (
    CreateWatermarkedPdfRequest,
    ImageSource,
    WatermarkSpec
)
from safeid.core.domain.errors import SafeIdError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a watermarked PDF from 1 or 2 images"
    )
    parser.add_argument(
        "images",
        nargs="+",
        type=Path,
        help="Path to 1 or 2 input images (PNG/JPG)"
    )
    parser.add_argument(
        "--recipient",
        required=True,
        help="Recipient/company used in the output file"
    )
    parser.add_argument(
        "--watermark",
        help="Watermark text to draw over the photo area. Defaults to recipient"
    )
    
    return parser
    
    
def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    
    image_paths = args.images
    if len(image_paths) not in (1, 2):
        parser.error("Please provide exactly 1 or 2 images")
        
    watermark_text = args.watermark if args.watermark else args.recipient
    
    request = CreateWatermarkedPdfRequest(
        images=[ImageSource(path=path) for path in image_paths],
        recipient=args.recipient,
        watermark=WatermarkSpec(text=watermark_text)
    )
    
    use_case = build_create_watermarked_pdf_use_case()
    
    try:
        result = use_case.execute(request=request)
    except SafeIdError as exc:
        print(f"Error: {exc.user_message}", file=sys.stderr)
        if exc.detail:
            print(f"Detail: {exc.detail}", file=sys.stderr)
        
        return 1
    
    print(f"PDF created succesfully: {result.output_path}")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
