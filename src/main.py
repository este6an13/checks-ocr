import pandas as pd
from constants import BANK_CODES, BANK_NAMES, BOXES, COLUMNS_MAP, COLUMNS
import textract
import confidence
import data
import handler
import utils
import extractor
import cache
import llm

import argparse


def main(
    llm_enabled=False, vectordb_updates=[], model_name="gpt-3.5-turbo-0125"
):
    df = handler.load_data(file_path="../../data.xlsx", columns=COLUMNS)

    data.setup_data()

    llm_client = None
    if llm_enabled:
        llm_client = llm.LLMClient(vectordb_updates, model_name)

    confidence_df = handler.load_data(
        file_path="confidence/confidence.xlsx", columns=COLUMNS
    )
    confidence_df = confidence.filter_confidence_df(confidence_df, df)

    unprocessed_filenames = handler.get_unprocessed_filenames(
        folder_path="../../unprocessed"
    )

    TERRITORIES = data.load_territories()

    for pdf_filename in unprocessed_filenames:
        res = {}
        id = utils.get_id(pdf_filename)

        processed = handler.check_if_processed(df, pdf_filename)
        if processed:
            handler.move_file(
                pdf_filename,
                id,
                source_folder="../../unprocessed",
                destination_folder="../../processed",
            )
            continue

        cached = cache.check_if_cached(pdf_filename, cache_folder="../cache")
        if cached:
            res = cache.read_cache(pdf_filename, cache_folder="../cache")

        # Processing
        else:
            img = utils.pdf_to_img(pdf_filename, folder="../../unprocessed")
            id = utils.generate_id()
            img_filename = handler.save_image(
                img, id, images_folder="../images"
            )
            t = textract.setup_textract()
            res = textract.process_image(t, img_filename)
            cache.write_to_cache(res, id, cache_folder="../cache")

        blocks = [b for b in res["Blocks"] if b["BlockType"] == "LINE"]
        bank_code = extractor.get_bank_code(BANK_CODES, blocks)

        if bank_code is None:
            continue

        handler.move_file(
            pdf_filename,
            id,
            source_folder="../../unprocessed",
            destination_folder="../../processed",
        )

        boxes = BOXES[bank_code]

        row = {
            "FECHA": "",
            "BANCO": BANK_NAMES[bank_code],
            "NUMERO-CUENTA": "",
            "NOMBRE-CUENTA": "",
            "BENEFICIARIO": "",
            "CHEQUE": "",
            "VALOR": "",
            "CIUDAD": "",
            "ID": id,
        }
        confidence_row = {
            "FECHA": 0,
            "BANCO": BANK_NAMES[bank_code],
            "NUMERO-CUENTA": 0,
            "NOMBRE-CUENTA": 0,
            "BENEFICIARIO": 0,
            "CHEQUE": 0,
            "VALOR": 0,
            "CIUDAD": 0,
            "ID": id,
        }

        for box_name in boxes:
            max_boxes = (
                2
                if box_name == "ACCOUNT_NAME"
                and bank_code not in ["austro", "guayaquil"]
                else 1
            )
            text, conf, _ = textract.extract_detail(
                boxes[box_name], blocks, max_boxes=max_boxes
            )

            # Extraction and Formatting
            if box_name in ["ACCOUNT_NUMBER", "CHECK_NUMBER"]:
                row[COLUMNS_MAP[box_name]] = str(
                    extractor.extract_numbers(text)
                )
            if box_name == "AMOUNT":
                row[COLUMNS_MAP[box_name]] = extractor.extract_float_numbers(
                    text
                )
            if box_name in ["ACCOUNT_NAME"]:
                account_name = extractor.clean_and_uppercase(text)
                row[COLUMNS_MAP[box_name]] = (
                    llm_client.rag.query("ACCOUNT_NAME", id, account_name)
                    if llm_client
                    else account_name
                )
            if box_name in ["CLIENT_NAME"]:
                client_name = extractor.clean_and_uppercase(text)
                row[COLUMNS_MAP[box_name]] = (
                    llm_client.rag.query("CLIENT_NAME", id, client_name)
                    if llm_client
                    else client_name
                )
            if box_name == "PLACE_AND_DATE":
                date, city = extractor.get_city_and_date(text)
                row["FECHA"] = (
                    llm_client.rag.query("DATE", id, text)
                    if llm_client
                    else date
                )
                row["CIUDAD"] = (
                    llm_client.rag.query("CITY", id, city)
                    if llm_client
                    else city
                )

            # Confidences Assignment
            if box_name != "PLACE_AND_DATE":
                cell_value = row[COLUMNS_MAP[box_name]]
                confidence_row[COLUMNS_MAP[box_name]] = conf
                if box_name == "CHECK_NUMBER":  # account number already set
                    if len(cell_value) == len(row["NUMERO-CUENTA"]):
                        confidence_row["CHEQUE"] = -1
                        if len(row["NUMERO-CUENTA"]) in range(1, 10):
                            confidence_row["NUMERO-CUENTA"] = -1
                if box_name == "CLIENT_NAME":
                    if utils.contains_number(cell_value):
                        confidence_row["BENEFICIARIO"] = -1
                if box_name == "AMOUNT":
                    if cell_value == 0:
                        confidence_row["VALOR"] = -1
            else:
                confidence_row["FECHA"] = conf
                if data.is_in_territories(row["CIUDAD"], TERRITORIES):
                    conf = 99
                if utils.contains_number(row["CIUDAD"]):
                    conf = -1
                confidence_row["CIUDAD"] = conf

        df = pd.concat(
            [df, pd.DataFrame([row], columns=df.columns)], ignore_index=True
        )
        print(row)
        confidence_df = pd.concat(
            [
                confidence_df,
                pd.DataFrame([confidence_row], columns=df.columns),
            ],
            ignore_index=True,
        )

    handler.write_data(
        df,
        confidence_df,
        data_path="../../data.xlsx",
        images_path="checks-ocr/images",
    )
    handler.write_confidence(
        confidence_df, filename="confidence/confidence.xlsx"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--llm", action="store_true", help="Enable the llm feature"
    )
    parser.add_argument(
        "--update", action="append", help="Specify files to update"
    )
    parser.add_argument(
        "--model-name", type=str, help="Specify the model name"
    )
    args = parser.parse_args()
    if args.llm:
        print("- LLM feature enabled!")
        # if not llm, these arguments will be received but not used
        if args.update:
            for vector_db in args.update:
                print(f"- '{vector_db}' vector database will be updated.")
        if args.model_name:
            print(f"- Using '{args.model_name}' model.")
        else:
            print(f"- Using default 'gpt-3.5-turbo-0125' model.")

    main(
        llm_enabled=args.llm,
        vectordb_updates=args.update if args.update else [],
        model_name=args.model_name
        if args.model_name
        else "gpt-3.5-turbo-0125",
    )
