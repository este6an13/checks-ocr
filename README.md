<h1 align="center"> Checks OCR + RAG  </h1>

<div align="center">
  <img src="fig/logo-2.png" width="150">

  Software to extract key information from printed and handwritten text on bank checks, using object detection techniques, cloud ML services and Retrieval Augmented Generation (RAG). The solution provides enhanced transparency by reporting confidence levels in the OCR results.

  [![codecov](https://codecov.io/gh/este6an13/checks-ocr/graph/badge.svg?token=3TE5I10NPT)](https://codecov.io/gh/este6an13/checks-ocr)

</div>

## How it works?

The program includes annotations indicating the locations of details to extract from checks, organized by bank. It employs `Amazon Textract` to extract text from checks, followed by an Intersection over Union (IoU) algorithm to retrieve specific details from the `Amazon Textract` results. These results are cached to prevent redundant costs if a check is placed in the `unprocessed` category again. The confidence scores provided by `Amazon Textract` help visualize the generated data, highlighting potentially inaccurate results—commonly occurring when check details are misplaced or when the check is not horizontally aligned during scanning.

If utilizing the LLM feature, the program utilizes Retrieval Augmented Generation (RAG) with `LangChain`, `Chroma DB` (which uses a user-updatable context) and the `GPT-3.5 Turbo` model by default (users can specify another OpenAI model). This enhances result accuracy by correcting potential errors.

It's important to note that the current annotations specifically cover a subset of banks in Ecuador (see the at the end of this document). Additionally, as of now, the program exclusively supports OpenAI models. This is the list of supported banks:


## Prerequisites

- Docker installed in your system
- AWS Credentials for Amazon Textract
- OPENAI Credentials if you want to use the LLM feature

If you don't have Docker installed, you would need:

- A recent version of Python installed in your system.
- A Python package manager installed in your system (like `pip` or `conda`).

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

If you want to use the LLM feature, add your OpenAI credentials as well. For the program to work, use this name for your environment variable:

```
OPENAI_API_KEY
```

>[!WARNING]
>When using Docker, the `docker run` command passes your credentials, and they will be visible to any user who can inspect your container. This will be addressed in a future release.

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

To use the LLM feature add the `--llm` option when running the script:

```sh
bash checks-ocr/run.sh --llm
```

You can manually add the `client_names.txt` and `account_names.txt` files to the folder `checks-ocr/data/data` and populate it with the list of clients and accounts of your organization. This will help the LLM to generate better results. You can modify the `checks-ocr/data/data/territories.txt` file too if needed.

After you modify any of these files you can tell the program to update its internal vector databases to start using the new context in the RAG chain. To do so, pass the `--update` option to the script like this:

```sh
bash checks-ocr/run.sh --llm --update client_names --update account_names --update territories
```

You only need the pass the `--update` option for the files that you modified.

You can also switch the LLM model you want to use by using the `--model-name` option.

```sh
bash checks-ocr/run.sh --llm --model-name gpt-4-0125-preview
```

The program will use the `gpt-3.5-turbo-0125` model by default.

> [!NOTE]  
> Without the `--llm` option, the `--update` and `--model-name` options won't take effect.

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

If running the program this way, pass the arguments in the following format:

```sh
py main.py --llm --update=client_names --update=account_names --update=territories --model-name=gpt-4-0125-preview
```

Note the equal symbol between the option and its value.

After starting the program, wait for the program to complete the processing

> [!NOTE]  
>It takes around `8 seconds` to process a new check. If using the LLM feature, it may take `10 seconds` per new check.

Check the results in the created `data.xlsx` file. Click on the ID of each row to see the check and fix any mistake or bad formatting if you need to.


## Remember

- The processed checks are moved to the `processed` folder automatically.
- Images of the checks are generated and saved in the `checks-ocr/images` folder.

- If you move the images from that folder, you won't be able to see them from the `data.xlsx` file when clicking their `ID`.

- The cache folder stores the responses received from Amazon Textract, so if you move a check to the `unprocessed` folder and removes its row from the `data.xlsx` folder, it will re-process the image but won't
make any call to Amazon Textract. This is useful in case you want to manually adjust the `BOXES` of a given bank in `checks-ocr/src/constants/__init__.py` file if you need it, and re-run the processing for a given set of checks.

- The generated `data.xlsx` file cells are painted based on the confidence reported by Amazon Textract. Cells in red color indicated a confidence lower than `90`. Violet cells are cells that seem to have some inconsistencies in their content suggesting that the `BOXES` coordinates seemed to not haven't captured the contents precisely. This happens when the checks details are not in the place they use to be or they cross with other details in the check.

- You can update the context that the LLM uses to generate results by adding and updating the `client_names.txt`, `account_names.txt`, and `territories.txt` files located in the `checks-ocr/data/data` folder. This way, users have complete control over the context used by the program and can make updates as needed. To apply these changes to the internal vector databases, run the program with the `--update` option, as explained earlier. You only need to do this once after making any changes to the files.

- Remember to close the `data.xlsx` file when running the script, otherwise the program won't be able to write the collected data and you will have to run it again.

## Supported Banks

**Ecuador**

- Banco Internacional
- Banco Pichincha
- Banco Guayaquil
- Banco del Austro
- BanEcuador
- Produbanco

## Direct Dependencies

- `boto3`
- `coverage`
- `chromadb`
- `langchain`
- `langchain-openai`
- `openpyxl`
- `pandas`
- `pillow`
- `pymupdf`
- `pytest`
- `unidecode`

For a comprehensive list that includes both direct and transitive dependencies, please refer to the `requirements.txt` file.
