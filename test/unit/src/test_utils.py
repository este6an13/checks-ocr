from src.utils import (
    calculate_iou,
    pdf_to_img,
)
from PIL import Image
import fitz
import os
import pytest
import shutil

@pytest.mark.parametrize(
    ("box1", "box2", "expected"),
    [
        ((0.1, 0.1, 0.5, 0.5), (0.1, 0.1, 0.5, 0.5), 1.0,),
        ((0.1, 0.1, 0.0, 0.0), (0.1, 0.1, 0.5, 0.5), 0.0,),
        ((0.2, 0.2, 0.0, 0.0), (0.2, 0.2, 0.1, 0.0), 1/3,),
    ],
)
def test_calculate_iou(box1: tuple[float], box2: tuple[float], expected: float) -> None:
    iou = calculate_iou(box1, box2)
    assert iou >= 0 and iou <= 1
    assert pytest.approx(iou) == expected


def _create_sample_pdf(pdf_path: str) -> None:
    doc = fitz.open()
    doc.insert_page(0)
    doc.save(str(pdf_path))


@pytest.mark.parametrize(
    ("resolution", "expected_width", "expected_height", "expected_format"),
    [
        (300, 2480, 3508, "RGB"),
        (150, 1240, 1754, "RGB"),
    ],
)
def test_pdf_to_img(resolution: int, expected_width: int, expected_height: int, expected_format: str) -> None:
    folder = r"./test/unit/temp/"
    
    # Create the output folder if it doesn't exist
    os.makedirs(folder, exist_ok=True)

    file_name = "sample.pdf"

    pdf_path = os.path.join(folder, file_name)

    _create_sample_pdf(pdf_path)

    img = pdf_to_img(file_name, folder, resolution)

    # Check if the output image is an instance of PIL Image
    assert isinstance(img, Image.Image)

    # Check image dimensions
    assert pytest.approx(img.size, rel=1.0) == (expected_width, expected_height)

    # Check image format
    assert img.mode == expected_format

    # Clean up: Remove the temporary folder and its contents
    shutil.rmtree(folder)
