import uuid
import re
import os
import fitz
from PIL import Image


def calculate_iou(box1, box2):
    """
    Calculate Intersection over Union (IoU) between two bounding boxes.

    :param box1: Tuple (W, H, L, T) representing the first bounding box.
    :param box2: Tuple (W, H, L, T) representing the second bounding box.
    :return: IoU score.
    """
    # Extract box coordinates
    w1, h1, l1, t1 = box1
    w2, h2, l2, t2 = box2

    # Calculate coordinates of intersection rectangle
    intersection_left = max(l1, l2)
    intersection_top = max(t1, t2)
    intersection_right = min(l1 + w1, l2 + w2)
    intersection_bottom = min(t1 + h1, t2 + h2)

    # Calculate area of intersection
    intersection_area = max(0, intersection_right - intersection_left) * max(0, intersection_bottom - intersection_top)

    # Calculate area of union
    union_area = w1 * h1 + w2 * h2 - intersection_area

    # Calculate IoU
    iou = intersection_area / union_area if union_area > 0 else 0.0

    return iou

def pdf_to_img(pdf_path, folder, resolution=300):
    file_path = os.path.join(folder, f"{pdf_path}")
    file_handle = fitz.open(file_path)

    # Get the first page
    page = file_handle[0]

    # Set resolution (DPI) for the image
    zoom_factor = resolution / 72.0  # 72 DPI is the default resolution in get_pixmap
    matrix = fitz.Matrix(zoom_factor, zoom_factor)

    # Get the pixmap of the page with higher resolution
    pixmap = page.get_pixmap(matrix=matrix)

    # Convert the pixmap to a PIL Image
    img = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)

    return img


def generate_id():
  id = str(uuid.uuid4())
  return id

def contains_number(s):
    """
    Check if a string contains a number.

    :param s: The input string.
    :return: True if the string contains a number, False otherwise.
    """
    return bool(re.search(r'\d', s))

def get_id(filename):
    """
    Extract the ID from a filename (without the extension).

    :param filename: The full filename including extension.
    :return: The ID extracted from the filename.
    """
    return os.path.splitext(os.path.basename(filename))[0]
