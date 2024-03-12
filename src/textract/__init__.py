import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError
import logging as logger
import os

from utils import calculate_iou


class TextractWrapper:
    """Encapsulates Textract functions."""

    def __init__(self, textract_client, s3_resource, sqs_resource):
        """
        :param textract_client: A Boto3 Textract client.
        :param s3_resource: A Boto3 Amazon S3 resource.
        :param sqs_resource: A Boto3 Amazon SQS resource.
        """
        self.textract_client = textract_client
        self.s3_resource = s3_resource
        self.sqs_resource = sqs_resource

    def detect_file_text(
        self, *, document_file_name=None, document_bytes=None
    ):
        """
        Detects text elements in a local image file or from in-memory byte data.
        The image must be in PNG or JPG format.

        :param document_file_name: The name of a document image file.
        :param document_bytes: In-memory byte data of a document image.
        :return: The response from Amazon Textract, including a list of blocks
                 that describe elements detected in the image.
        """
        if document_file_name is not None:
            with open(document_file_name, "rb") as document_file:
                document_bytes = document_file.read()
        try:
            response = self.textract_client.detect_document_text(
                Document={"Bytes": document_bytes}
            )
            logger.info("Detected %s blocks.", len(response["Blocks"]))
        except ClientError:
            logger.exception("Couldn't detect text.")
            raise
        else:
            return response


def initialize_textract(credentials, region):
    """
    Initialize TextractWrapper with provided AWS credentials and region.

    :param credentials: A dictionary containing 'aws_access_key_id' and 'aws_secret_access_key'.
    :param region: The AWS region.
    :return: An instance of TextractWrapper.
    """
    try:
        textract_client = boto3.client(
            "textract",
            region_name=region,
            aws_access_key_id=credentials["aws_access_key_id"],
            aws_secret_access_key=credentials["aws_secret_access_key"],
        )
        s3_resource = boto3.resource(
            "s3",
            region_name=region,
            aws_access_key_id=credentials["aws_access_key_id"],
            aws_secret_access_key=credentials["aws_secret_access_key"],
        )
        sqs_resource = boto3.resource(
            "sqs",
            region_name=region,
            aws_access_key_id=credentials["aws_access_key_id"],
            aws_secret_access_key=credentials["aws_secret_access_key"],
        )

        textract_wrapper = TextractWrapper(
            textract_client, s3_resource, sqs_resource
        )
        return textract_wrapper
    except NoCredentialsError:
        print("Credentials not available.")
        return None


def process_image(textract_wrapper, image_path):
    """
    Process the image using the provided TextractWrapper instance.

    :param textract_wrapper: An instance of TextractWrapper.
    :param image_path: The path to the image file.
    :return: The result from TextractWrapper's detect_file_text method.
    """
    try:
        result = textract_wrapper.detect_file_text(
            document_file_name=image_path
        )
        return result
    except NoCredentialsError:
        print("Credentials not available.")
        return None


def setup_textract():
    AWS_CREDENTIALS = {
        "aws_access_key_id": os.environ.get("TEXTRACT_AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.environ.get(
            "TEXTRACT_AWS_SECRET_ACCESS_KEY_ID"
        ),
    }

    AWS_REGION = os.environ.get("TEXTRACT_AWS_REGION")

    textract = initialize_textract(AWS_CREDENTIALS, AWS_REGION)

    return textract


def in_top_left_corner(block):
    if (
        block["Geometry"]["BoundingBox"]["Top"] < 0.5
        and block["Geometry"]["BoundingBox"]["Left"] < 0.5
    ):
        return True
    return False


def extract_detail(box, blocks, max_boxes=1, sep=" "):
    """
    Extract details from blocks that best match the given box.

    :param box: Tuple (W, H, L, T) representing the target bounding box.
    :param blocks: List of objects with Geometry property containing BoundingBox.
    :param max_boxes: Maximum number of top matching blocks to consider.
    :return: Tuple (text, confidence) of the best matching block(s).
    """
    # Initialize lists to store top matching blocks
    top_blocks = []
    top_iou_scores = []

    for block in blocks:
        bounding_box = block.get("Geometry", {}).get("BoundingBox", {})
        block_box = (
            bounding_box.get("Width", 0),
            bounding_box.get("Height", 0),
            bounding_box.get("Left", 0),
            bounding_box.get("Top", 0),
        )

        iou_score = calculate_iou(box, block_box)

        # Check if the block should be included in the top blocks
        if len(top_blocks) < max_boxes or iou_score > min(top_iou_scores):
            top_blocks.append(block)
            top_iou_scores.append(iou_score)

            # Keep only the top max_boxes blocks
            if len(top_blocks) > max_boxes:
                min_iou_index = top_iou_scores.index(min(top_iou_scores))
                top_blocks.pop(min_iou_index)
                top_iou_scores.pop(min_iou_index)

    # Concatenate text and calculate minimum confidence
    if top_blocks:
        # Sort top_blocks based on Left and Top coordinates
        top_blocks.sort(
            key=lambda block: (
                block["Geometry"]["BoundingBox"]["Top"],
                block["Geometry"]["BoundingBox"]["Left"],
            )
        )

        # Concatenate text and calculate minimum confidence
        concatenated_text = sep.join(
            [
                block.get("Text", "")
                for block in top_blocks
                if block is not None
            ]
        )
        min_confidence = min(
            [
                block.get("Confidence", 0.0)
                for block in top_blocks
                if block is not None
            ]
        )
        return (
            concatenated_text,
            min_confidence,
            min(top_iou_scores),
        )  # min to be pessimistic
    else:
        return None, 0.0, 0.0
