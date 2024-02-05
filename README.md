<h1 align="center"> Checks OCR  </h1>

<div align="center">
  <img src="fig/logo.png" width="150">
</div>

Software to do OCR/HTR in Checks.

Currently only supporting a subset of banks from Ecuador.

## Prerequisites

- A recent version of Python installed in your system.
- A Python package manager installed in your system (ie. pip).
- AWS Credentials for Amazon Textract

## Installation

1. Create a folder (let's call it `checks`).

2. Clone the repository into your `checks` folder:

```sh
https://github.com/este6an13/checks-ocr.git
```

3. Enter the repository folder:

```sh
cd checks-ocr
```

4. Create a virtual environment (you need a recent version of Python installed):

**Note**: The following commands work for Windows.
**Note**: If you use Linux, make sure to run the correct commands accordingly.

```sh
py -m venv env
```

5. Activate the virtual environment:

```sh
cd env/Scripts
activate
cd ../..
```

6. Install the required dependencies (you need pip installed in your system for this):

```sh
pip install -r requirements.txt
```

7. Set your AWS credentials for Amazon Textract as environment variables.

**Note:** For the program to work you need to use these names for the variables:

```
TEXTRACT_AWS_ACCESS_KEY_ID
TEXTRACT_AWS_SECRET_ACCESS_KEY_ID
TEXTRACT_AWS_REGION
```

## Usage

1. Go back to the `checks` folder.

1. Create an empty folder `unprocessed`.

2. Create an empty folder `processed`.

3. Move your checks in `pdf` format to the `unprocessed` folder.

**Note**: Currently only supporting `pdf` format for your checks.
**Note**: Make sure the check is in the first page of the pdf.
**Note**: To get better results, make sure the checks are horizontally aligned and that all of its content is visible.

4. Run the program with the following command:

```sh
py checks-ocr/main.py
```

5. Check the results in the created `data.xlsx` file. Click on the ID of each row to see the check and fix any mistake or bad formatting if you need to.

## Notes

- The processed checks are moved to the `processed` folder automatically.
- Images of the checks are generated and saved in the `checks-ocr/images` folder.
- If you move the images from that folder, you won't be able to see them from the `data.xlsx` file when clicking their `ID`.
- The cache folder stores the responses received from Amazon Textract, so if you move a check to the `unprocessed` folder and removes its row from the `data.xlsx` folder, it will re-process the image but won't
make any call to Amazon Textract. This is useful in case you want to manually adjust the `BOXES` of a given bank in `checks-ocr/src/constants/__init__.py` file if you need it, and re-run the processing for a given set of checks.
- The generated `data.xlsx` file cells are painted based on the confidence reported by Amazon Textract. Cells in red color indicated a confidence lower than `90`. Violet cells are cells that seem to have some inconsistencies in their content suggesting that the `BOXES` coordinates seemed to not haven't captured the contents precisely. This happens when the checks details are not in the place they use to be or they cross with other details in the check.

## Supported Banks

**Ecuador**

- Banco Internacional
- Banco Pichincha
- Banco Guayaquil
- Banco del Austro
- BanEcuador
- Produbanco