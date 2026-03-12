from __future__ import annotations

from typing import Sequence

from safeid.core.domain.errors import InvalidInputError, LayoutDoesNotFitError
from safeid.core.domain.models import (
    ImageAsset,
    LayoutPlan,
    PageSpec,
    PlacedImage,
    RectPt,
    LayoutPolicy
)

A4_WIDTH_PT = 595.275590551 # 210mm * 72 / 25.4
A4_HEIGHT_PT = 841.88976378 # 297mm * 72 / 25.4

def mm_to_pt(mm: float) -> float:
    return mm * 72.0 / 25.4


def plan_a4_vertical_stack(
    *,
    page: PageSpec,
    images: Sequence[ImageAsset],
    policy: LayoutPolicy = LayoutPolicy()
) -> LayoutPlan:
    """Plan placement for 1-2 images on an A4 page with margins, stacked vertically."""
    if len(images) not in (1, 2):
        raise InvalidInputError(user_message="Layoutplanner requires 1 or 2 images")
    
    margin_pt = mm_to_pt(page.margin_mm)
    gap_pt = mm_to_pt(policy.min_gap_mm)
    
    page_w = A4_WIDTH_PT
    page_h = A4_HEIGHT_PT
    
    avail_w = page_w - 2 * margin_pt
    avail_h = page_h - 2 * margin_pt
    
    if len(images) == 1:
        placed = _place_single(images[0], avail_w, avail_h, margin_pt, allow_rotation=policy.allow_rotation, allow_scaling=policy.allow_scaling)
        photo_area = placed.rect
        return LayoutPlan(page=page, placed_images=[placed], photo_area=photo_area)
    
    placed_top, placed_bottom = _place_two(
        images[0],
        images[1],
        avail_w,
        avail_h,
        margin_pt,
        gap_pt,
        allow_rotation=policy.allow_rotation,
        allow_scaling=policy.allow_scaling
    )
    photo_area = _union_rects(placed_top.rect, placed_bottom.rect)
    return LayoutPlan(page=page, placed_images=[placed_top, placed_bottom], photo_area=photo_area)
    
# --- ONE IMAGE ---  
    
def _place_single(
    image: ImageAsset, 
    avail_w: float, 
    avail_h: float, 
    margin_pt: float, 
    *,
    allow_rotation: bool,
    allow_scaling: bool
) -> PlacedImage:
    """Place a single image, trying 0 degrees or 90 degrees rotation
    and choosing the better fit.
    """
    original_w = image.size_px.width
    original_h = image.size_px.height
    
    candidates: list[tuple[int, float, float, float]] = []
    rotations = (0, 1) if allow_rotation else (0, )
    # tuple = (rotate_90, fitted_w, fitted_h, area)
    for rotate_90 in rotations:
        if rotate_90 == 0:
            w_px, h_px = original_w, original_h
        else:
            w_px, h_px = original_h, original_w
        
        fitted = _fit_single_candidate(w_px, h_px, avail_w, avail_h, allow_scaling=allow_scaling)
        if fitted is None:
            continue
        
        fitted_w, fitted_h, area = fitted
        candidates.append((rotate_90, fitted_w, fitted_h, area))
        
    if not candidates:
        raise LayoutDoesNotFitError.for_policy(
            detail=(
                f"Single image does not fit. "
                f"Image size={original_w}x{original_h}px, "
                f"available area={avail_w:.2f}x{avail_h:.2f}pt, "
                f"allow_rotation={allow_rotation}, "
                f"allow_scaling={allow_scaling}."
            )
        )
        
    best_rotate, best_w, best_h, _ = max(candidates, key=lambda candidate: (candidate[3], -candidate[0]))
    
    x = margin_pt + (avail_w - best_w) / 2.0
    y = margin_pt + (avail_h - best_h) / 2.0
    
    return PlacedImage(
        source_index=0,
        rect=RectPt(x=x, y=y, width=best_w, height=best_h),
        rotate_90=best_rotate
    )
    

def _fit_single_candidate(
    w_px: int, 
    h_px: int,
    avail_w: float,
    avail_h: float,
    *,
    allow_scaling: bool
) -> tuple[float, float, float] | None:
    # Could be good to add a type alias
    # SingleFitResult = tuple[float, float, float]
    """Fit one orientation candidate into the available area.
    
    Returns:
        tuple[fitted_w, fitted_h, area] if the candidate is valid,
        otherwise None when scaling is disabled and it does not fit.
    """
    if allow_scaling:
        scale = min(avail_w / w_px, avail_h, h_px)
        fitted_w = w_px * scale
        fitted_h = h_px * scale
    else:
        fitted_w = float(w_px)
        fitted_h = float(h_px)
        
        if fitted_w > avail_w or fitted_h > avail_h:
            return None
    
    area = fitted_w * fitted_h
    return fitted_w, fitted_h, area
    
# -- TWO IMAGES --- 

def _place_two(
    img_a: ImageAsset, 
    img_b: ImageAsset, 
    avail_w: float, 
    avail_h: float, 
    margin_pt: float, 
    gap_pt: float,
    *,
    allow_rotation: bool,
    allow_scaling: bool
) -> tuple[PlacedImage, PlacedImage]:
    # If you'd like, I can also show you how senior engineers simplify the two-image scaling math, 
    # because there is a neat trick that avoids complex iterative solving.
    """Place two images stacked vertically, choosing the best orientation combo"""
    rotations = (0, 1) if allow_rotation else (0,)
    
    candidates: list[
        tuple[
            float,  # total area
            int,    # total rotations
            PlacedImage,
            PlacedImage
        ]
    ] = []
    
    for rot_a in rotations:
        for rot_b in rotations:
            if rot_a == 0:
                w_a_px, h_a_px = img_a.size_px.width, img_a.size_px.height
            else:
                w_a_px, h_a_px = img_a.size_px.height, img_a.size_px.width

            if rot_b == 0:
                w_b_px, h_b_px = img_b.size_px.width, img_b.size_px.height
            else:
                w_b_px, h_b_px = img_b.size_px.height, img_b.size_px.width
                
            fitted = _fit_two_stack_candidate(
                w_a_px,
                h_a_px,
                w_b_px,
                h_b_px,
                avail_w,
                avail_h,
                gap_pt,
                allow_scaling=allow_scaling
            )
            
            if fitted is None:
                continue
        
            w_a, h_a, w_b, h_b, total_area = fitted
            
            total_height = h_a + gap_pt + h_b
            start_y = margin_pt + (avail_h - total_height) / 2.0

            b_x = margin_pt + (avail_w - w_b) / 2.0
            b_y = start_y

            a_x = margin_pt + (avail_w - w_a) / 2.0
            a_y = start_y + h_b + gap_pt

            placed_a = PlacedImage(
                source_index=0,
                rect=RectPt(
                    x=a_x,
                    y=a_y,
                    width=w_a,
                    height=h_a,
                ),
                rotate_90=rot_a,
            )

            placed_b = PlacedImage(
                source_index=1,
                rect=RectPt(
                    x=b_x,
                    y=b_y,
                    width=w_b,
                    height=h_b,
                ),
                rotate_90=rot_b,
            )

            total_rotations = rot_a + rot_b
            candidates.append((total_area, -total_rotations, placed_a, placed_b))

    if not candidates:
        raise LayoutDoesNotFitError.for_policy(
            detail=(
                f"Two-image stack does not fit. "
                f"Image A={img_a.size_px.width}x{img_a.size_px.height}px, "
                f"Image B={img_b.size_px.width}x{img_b.size_px.height}px, "
                f"available area={avail_w:.2f}x{avail_h:.2f}pt, "
                f"gap={gap_pt:.2f}pt, "
                f"allow_rotation={allow_rotation}, "
                f"allow_scaling={allow_scaling}."
            )
        )

    _, _, best_a, best_b = max(candidates, key=lambda c: (c[0], c[1]))
    return best_a, best_b
    
    
def _fit_two_stack_candidate(
    w_a_px: int,
    h_a_px: int,
    w_b_px: int,
    h_b_px: int,
    avail_w: float,
    avail_h: float,
    gap_pt: float,
    *,
    allow_scaling: bool
) -> tuple[float, float, float, float, float] | None:
    """Fit two vertically stacked image candidates into the available area.
    
    Returns:
        tuple[w_a_px, h_a_px, w_b_px, h_b_px, total_area] if the candidate fits,
        otherwise None
    """
    if allow_scaling:
        # First, scale each image to full available width
        scale_a_full = avail_w / w_a_px
        scale_b_full = avail_w / w_b_px
        
        h_a_full = h_a_px * scale_a_full
        h_b_full = h_b_px * scale_b_full
        
        total_full_height = h_a_full + gap_pt + h_b_full
        if total_full_height <= avail_h:
            w_a = avail_w
            h_a = h_a_full
            w_b = avail_w
            h_b = h_b_full
        else:
            available_image_height = avail_h - gap_pt
            if available_image_height <= 0:
                # will never happen currently
                return None
            
            stack_scale = available_image_height/ (h_a_full + h_b_full)
            
            w_a = avail_w * stack_scale
            h_a = h_a_full * stack_scale
            w_b = avail_w * stack_scale
            h_b = h_b_full * stack_scale
    
    else:
        w_a = float(w_a_px)
        h_a = float(h_a_px)
        w_b = float(w_b_px)
        h_b = float(h_b_px)
        
        if w_a > avail_w or w_b > avail_w:
            return None
        
        if h_a > avail_h or h_b > avail_h:
            return None
        
    total_area = (w_a * h_a) + (w_b * h_b)
    return w_a, h_a, w_b, h_b, total_area
        

def _union_rects(a: RectPt, b: RectPt) -> RectPt:
    x0 = min(a.x, b.x)
    y0 = min(a.y, b.y)
    x1 = max(a.x + a.width, b.x + b.width)
    y1 = max(a.y + a.height, b.y + b.height)
    
    return RectPt(x=x0, y=y0, width=(x1 - x0), height=(y1 - y0))