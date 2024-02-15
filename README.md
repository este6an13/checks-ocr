<h1 align="center"> Checks OCR  </h1>

<div align="center">
  <img src="fig/logo.png" width="150">
</div>

Software to extract key information from printed and handwritten text on bank checks, using object detection techniques and cloud ML services. The solution provides enhanced transparency by reporting confidence levels in the OCR results.

Currently only supporting a subset of banks from Ecuador.

## Prerequisites

- Docker installed in your system
- AWS Credentials for Amazon Textract

If you don't have Docker installed, you would need:

- A recent version of Python installed in your system.
- A Python package manager installed in your system (ie. pip).

## Setup

1. Create a folder (let's call it `checks`).

2. Create an empty folder `unprocessed`.

3. Create an empty folder `processed`.

4. Clone the repository into your `checks` folder:

```sh
git clone https://github.com/este6an13/checks-ocr.git
```

6. Set your AWS credentials for Amazon Textract as environment variables.

For the program to work you need to use these names for the variables:

```
TEXTRACT_AWS_ACCESS_KEY_ID
TEXTRACT_AWS_SECRET_ACCESS_KEY_ID
TEXTRACT_AWS_REGION
```

If you don't have Docker installed in your system, follow these extra steps:

7. Enter the repository folder:

```sh
cd checks-ocr
```

8. Create a virtual environment (you need a recent version of Python installed):

- The following commands work for Windows.
- If you use Linux, make sure to run the correct commands accordingly.

```sh
py -m venv env
```

9. Activate the virtual environment:

```sh
cd env/Scripts
activate
cd ../..
```

10. Install the required dependencies (you need pip installed in your system for this):

```sh
pip install -r requirements.txt
```

## Usage

1. Move your checks in `pdf` format to the `unprocessed` folder.

- Currently only supporting `pdf` format for your checks.
- Make sure the check is in the first page of the pdf.
- To get better results, make sure the checks are horizontally aligned and that all of its content is visible.

If you have Docker installed in your system:

2. Build the Docker image running the following script from the `checks` folder:

```sh
bash checks-ocr/build.sh
```

3. Start the application by running the following script from the `checks` folder:

```sh
bash checks-ocr/run.sh 
```

If you don't have Docker installed in your system, follow steps 4 and 5:

4. Navigate to the `src` folder:

```sh
cd checks-ocr
cd src
```

5. Run the program with the following command:

```sh
py main.py
```


Wait for the program to complete the processing

**Note**: It takes around `8 seconds` to process a new check.

Check the results in the created `data.xlsx` file. Click on the ID of each row to see the check and fix any mistake or bad formatting if you need to.


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