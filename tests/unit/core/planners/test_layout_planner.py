import pytest

from safeid.core.planners.layout_planner import (
    plan_a4_vertical_stack,
    mm_to_pt,
)
from safeid.core.domain.models import (
    SizePx,
    PageSpec,
    ImageAsset,
    LayoutPolicy,
    PlacedImage,
    LayoutPlan,
)
from safeid.core.domain.errors import LayoutDoesNotFitError

def make_image(width: int, height: int) -> ImageAsset:
    return ImageAsset(
        size_px=SizePx(width=width, height=height),
        mode="RGB",
        pixel_bytes=b"", # not used by planner
    )


# --- ONE IMAGE --- 

def test_single_image_respects_margins():
    page = PageSpec(size="A4", margin_mm=19.0)
    
    img = make_image(1200, 800)
    
    layout = plan_a4_vertical_stack(page=page, images=[img])
    
    placed = layout.placed_images[0]
    
    margin = mm_to_pt(page.margin_mm)
    
    assert placed.rect.x >= margin
    assert placed.rect.y >= margin


def test_single_image_does_not_rotate_when_rotation_disabled():
    page = PageSpec()
    
    img = make_image(300, 1200)
    
    layout = plan_a4_vertical_stack(page=page, images=[img], policy=LayoutPolicy(allow_rotation=False))
    
    placed = layout.placed_images[0]
    
    assert placed.rotate_90 == 0


def test_single_image_aspect_ratio_preserved_without_rotation():
    page = PageSpec()
    
    img_w, img_h = 1600, 800
    img = make_image(img_w, img_h) # ratio 2:1
    
    layout = plan_a4_vertical_stack(page=page, images=[img], policy=LayoutPolicy(allow_rotation=False))
    
    rect = layout.placed_images[0].rect
    
    ratio_original = img_w / img_h
    ratio_rect = rect.width / rect.height
    
    assert abs(ratio_original - ratio_rect) < 1e-6
    

def test_single_image_aspect_ratio_preserved():
    page = PageSpec()
    
    img_w, img_h = 1600, 800
    img = make_image(img_w, img_h) # ratio 2:1
    
    layout = plan_a4_vertical_stack(page=page, images=[img], policy=LayoutPolicy(allow_rotation=False))
    
    placed = layout.placed_images[0]
    rect = placed.rect
    
    original_ratio = img_w / img_h
    rotated_ratio = img_h / img_w
    
    actual_ratio = rect.width / rect.height
    expected_ratio = original_ratio if placed.rotate_90 == 0 else rotated_ratio
    
    assert abs(expected_ratio - actual_ratio) < 1e-6
    
    
def test_single_image_raises_when_scaling_disabled_and_image_does_not_fit():
    page = PageSpec()
    img = make_image(2000, 2000)
    
    with pytest.raises(LayoutDoesNotFitError):
        plan_a4_vertical_stack(
            page=page,
            images=[img],
            policy=LayoutPolicy(
                allow_rotation=False,
                allow_scaling=False
            )
        )
    
# --- TWO IMAGES --- 
    
def test_two_images_do_not_overlap():
    page = PageSpec()
    
    img1 = make_image(1000, 800)
    img2 = make_image(900, 700)
    
    layout = plan_a4_vertical_stack(page=page, images=[img1, img2])
    
    top = layout.placed_images[0].rect
    bottom = layout.placed_images[1].rect

    assert top.y >= bottom.y + bottom.height
    

def test_gap_between_images_respected():
    page = PageSpec()
    
    img1 = make_image(1000, 800)
    img2 = make_image(900, 700)
    
    policy = LayoutPolicy(min_gap_mm=12)
    layout = plan_a4_vertical_stack(page=page, images=[img1, img2], policy=policy)
    
    gap_pt = mm_to_pt(policy.min_gap_mm)
    
    top = layout.placed_images[0].rect
    bottom = layout.placed_images[1].rect
    
    real_gap = top.y - (bottom.y + bottom.height)
    
    assert real_gap - gap_pt <= 0.01
    
    
def test_photo_area_encloses_images():
    page = PageSpec()
    
    img1 = make_image(1000, 800)
    img2 = make_image(900, 700)
    
    layout = plan_a4_vertical_stack(page=page, images=[img1, img2])
    
    top = layout.placed_images[0].rect
    bottom = layout.placed_images[1].rect
    
    area = layout.photo_area
    
    for placed in layout.placed_images:
        r = placed.rect
        
        assert r.x >= area.x
        assert r.y >= area.y
        assert r.x + r.width <= area.x + area.width
        assert r.y + r.height <= area.y + area.height
        
        
def test_two_images_keep_original_sizes_when_scaling_disabled():
    page = PageSpec()
    img1 = make_image(200, 150)
    img2 = make_image(180, 120)
    
    layout = plan_a4_vertical_stack(
        page=page,
        images=[img1, img2],
        policy=LayoutPolicy(
            allow_rotation=False,
            allow_scaling=False,
            min_gap_mm=12.0
        )
    )
    
    top = layout.placed_images[0].rect
    bottom = layout.placed_images[1].rect
    
    assert top.width == 200
    assert top.height == 150
    assert bottom.width == 180
    assert bottom.height == 120
    
    
def test_two_images_raise_when_scaling_disabled_and_stack_does_not_fit():
    page = PageSpec()
    img1 = make_image(700, 500)
    img2 = make_image(700, 500)
    
    with pytest.raises(LayoutDoesNotFitError):
        plan_a4_vertical_stack(
            page=page,
            images=[img1, img2], 
            policy=LayoutPolicy(
                allow_rotation=False,
                allow_scaling=False,
                min_gap_mm=12.0
            )
        )