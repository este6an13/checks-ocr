from src.utils import calculate_iou

import pytest

@pytest.mark.parametrize(
    ("box1", "box2", "expected"),
    [
        ((0.1, 0.1, 0.5, 0.5), (0.1, 0.1, 0.5, 0.5), 1.0,),
        ((0.1, 0.1, 0.0, 0.0), (0.1, 0.1, 0.5, 0.5), 0.0,),
        ((0.2, 0.2, 0.0, 0.0), (0.2, 0.2, 0.1, 0.0), 1/3,),
    ],
)
def test_calculate_iou(box1: tuple, box2: tuple, expected: float) -> None:
    iou = calculate_iou(box1, box2)
    assert iou >= 0 and iou <= 1
    assert pytest.approx(iou) == expected