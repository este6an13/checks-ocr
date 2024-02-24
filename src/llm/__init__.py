import os
import json
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
import pandas as pd
import shutil
import chromadb

class LLMCache:
    def __init__(self, cache_file_path="llm/cache/cache.json"):
        self.cache_file_path = cache_file_path

    def write(self, id, key, value):
        try:
            # Load existing data from the cache file
            with open(self.cache_file_path, "r") as file:
                cache_data = json.load(file)
        except FileNotFoundError:
            # If the file doesn't exist, create an empty dictionary
            cache_data = {}

        # Check if the id already exists in the cache
        if id in cache_data:
            # If the id exists, add the inner key and its value
            cache_data[id][key] = value
        else:
            # If the id doesn't exist, create the id entry and its inner object
            cache_data[id] = {key: value}

        # Write the updated data back to the cache file
        with open(self.cache_file_path, "w") as file:
            json.dump(cache_data, file)

    def read(self, id, key):
        try:
            # Load existing data from the cache file
            with open(self.cache_file_path, "r") as file:
                cache_data = json.load(file)

            # Check if the id exists in the cache
            if id in cache_data:
                # Check if the inner key exists for the given id
                if key in cache_data[id]:
                    return cache_data[id][key]
                else:
                    return None  # Inner key doesn't exist
            else:
                return None  # Id doesn't exist
        except FileNotFoundError:
            return None  # Cache file doesn't exist

class RAG:
    def __init__(self, api_key):
        self.api_key = api_key
        self.embedding_function = OpenAIEmbeddings(api_key=self.api_key)
        self.data_collection, self.data_collection_wrapper = self.setup_collection()
        self.vector_db = self.setup_vector_database()
        self.vector_db_retriever = self.get_retriever(self.vector_db)
        self.collection_retriever = self.get_retriever(self.data_collection_wrapper)
        self.prompts = {
            "CITY": self.generate_prompt(
                messages=[
                    ("system", "You are a machine that prints city names and nothing more."),
                    ("human", "If this text contains the name of an Ecuadorian city, print it; otherwise, print 'None'."),
                    ("human", "The city may be misspelled. Use the context to find the potential correction and print it."),
                    ("human", "Text: {text}"),
                    ("human", "Context: {context}"),
                ],
            ),
            "DATE": self.generate_prompt(
                messages=[
                    ("system", "You are a machine that prints dates in YYYY-MM-DD format and nothing more."),
                    ("human", "If this text contains a date, print it in YYYY-MM-DD format; otherwise, print 'None'."),
                    ("human", "Text: {text}"),
                ],
            ),
            "CLIENT_NAME": self.generate_prompt(
                messages=[
                    ("system", "You are a machine that prints client full names and nothing more."),
                    ("human", "This text should contain the full name of a client to whom a check is being paid."),
                    ("human", "The client name can be the name of an organization."),
                    ("human", "The client name can include a first name, middle name, and two surnames, but not always."),
                    ("human", "These names are Ecuadorian and/or Latin American."),
                    ("human", "The client name may be misspelled."),
                    ("human", "You will be given a context that has some client names (CLIENT_NAME) to help you."),
                    ("human", "Use this context to find the potential correction and print it."),
                    ("human", "If you don't find a match in the context, print the client name as it is."),
                    ("human", "If it's a name you've never seen, print it anyway."),
                    ("human", "If you find the name, print it; otherwise, print 'None'."),
                    ("human", "Text: {text}"),
                    ("human", "Context: {context}"),
                ],
            ),
            "ACCOUNT_NAME": self.generate_prompt(
                messages=[
                    ("system", "You are a machine that prints account names and nothing more."),
                    ("human", "This text should contain the full name of an account/client/organization to whom a check is being paid."),
                    ("human", "You will be given a context that has some account names (ACCOUNT_NAME) to help you."),
                    ("human", "Use this context to find the potential correction and print it."),
                    ("human", "If you don't find the name in the context, print the account name as it is."),
                    ("human", "Text: {text}"),
                    ("human", "Context: {context}"),
                ],
            )
        }
        self.llm = self.setup_llm()
        self.llm_cache = LLMCache()

        self.store_data()

    def load_territories(self):
        loader = TextLoader('territories/territories.txt')
        documents = loader.load()
        return documents
    
    def prepare_data(self):
        # Read Excel data
        excel_path = "../../data.xlsx"
        excel_data = pd.read_excel(excel_path, usecols=["NOMBRE-CUENTA", "BENEFICIARIO", "ID"])
        excel_data.fillna("", inplace=True)

        # Read embedded.json
        json_path = "llm/embedded/embedded.json"
        # Check if the file exists
        if os.path.exists(json_path):
            # File exists, read its contents
            with open(json_path, 'r') as json_file:
                embedded_data = json.load(json_file)
        else:
            # File doesn't exist, create an empty JSON file
            os.makedirs("llm/embedded/", exist_ok=True)
            with open(json_path, 'w') as json_file:
                embedded_data = []
                json.dump(embedded_data, json_file)

        # Create a temporary folder if it doesn't exist
        temp_folder = "llm/embedded/temp"
        os.makedirs(temp_folder, exist_ok=True)

        # List to store paths of newly created JSON files
        new_json_files = []

        # Iterate through each row in Excel data
        for _, row in excel_data.iterrows():
            account_name = row["NOMBRE-CUENTA"]
            client_name = row["BENEFICIARIO"]
            entry_id = row["ID"]

            # Check if entry exists in embedded.json
            if any(entry['ID'] == entry_id for entry in embedded_data):
                # Compare and update if necessary
                for entry in embedded_data:
                    if entry['ID'] == entry_id:
                        if entry['ACCOUNT_NAME'] != account_name or entry['CLIENT_NAME'] != client_name:
                            entry['ACCOUNT_NAME'] = account_name
                            entry['CLIENT_NAME'] = client_name
                            
                            # Create a new JSON file in the temp folder
                            temp_json_path = temp_folder + f"/{entry_id}.json"
                            new_json_files.append(temp_json_path)
                            new_entry = {"ACCOUNT_NAME": account_name, "CLIENT_NAME": client_name}
                            with open(temp_json_path, 'w') as temp_json_file:
                                json.dump(new_entry, temp_json_file)
            else:
                # Create a new JSON file in the temp folder
                temp_json_path = temp_json_path = temp_folder + f"/{entry_id}.json"
                new_json_files.append(temp_json_path)
                new_entry = {"ACCOUNT_NAME": account_name, "CLIENT_NAME": client_name, "ID": entry_id}
                with open(temp_json_path, 'w') as temp_json_file:
                    json.dump(new_entry, temp_json_file)

                # Add new entry to embedded_data
                embedded_data.append(new_entry)

        return new_json_files, embedded_data

    def update_embedded_data(self, embedded_data):
        json_path = "llm/embedded/embedded.json"
        # Update embedded.json
        with open(json_path, 'w') as updated_json_file:
            json.dump(embedded_data, updated_json_file)

    def remove_temp_folder(self):
        temp_folder = "llm/embedded/temp"
        shutil.rmtree(temp_folder)
        print(f"The {temp_folder} folder has been successfully removed.")

    def load_json_to_string(self, json_path):
        try:
            with open(json_path, 'r') as json_file:
                # make sure it's lowercase before embedding because query is lowercase as well
                json_string = json_file.read().lower()
            return json_string
        except FileNotFoundError:
            print(f"File not found: {json_path}")
            return None
        except Exception as e:
            print(f"An error occurred while loading JSON: {e}")
            return None

    def store_data(self):
        new_data, updated_json = self.prepare_data()
        for doc in new_data:
            print(doc)
            self.data_collection.upsert(
                ids=[doc.split('.')[0]],
                # embeddings is a 2D array of vectors, that's why I do [0]
                embeddings=[self.embedding_function.embed_documents([self.load_json_to_string(doc)])][0],
                documents=[self.load_json_to_string(doc)],
            )
        self.update_embedded_data(updated_json)
        self.remove_temp_folder()

    def chunk_documents(self, documents):
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunked_documents = text_splitter.split_documents(documents)
        return chunked_documents

    def setup_vector_database(self):
        vector_db_path = "llm/vectordb"
        vector_db = None
        if not os.path.exists(vector_db_path):
            documents = self.load_territories()
            chunked_documents = self.chunk_documents(documents)
            vector_db = Chroma.from_documents(
                documents=chunked_documents,
                embedding=self.embedding_function,
                persist_directory=vector_db_path
            )
            vector_db.persist()
        else:
            vector_db = Chroma(
                persist_directory=vector_db_path, 
                embedding_function=self.embedding_function,
            )
        return vector_db
    
    def setup_collection(self):
        collection_path = "llm/collection"
        collection = None
        collection_wrapper = None
        if not os.path.exists(collection_path):
            persistent_client = chromadb.PersistentClient(collection_path)
            collection = persistent_client.get_or_create_collection("data")
            collection_wrapper = Chroma(
                client=persistent_client,
                collection_name="data",
                embedding_function=self.embedding_function,
                persist_directory=collection_path,
            )
            collection_wrapper.persist()
        else:
            persistent_client = chromadb.PersistentClient(collection_path)
            collection = persistent_client.get_or_create_collection("data")
            collection_wrapper = Chroma(
                persist_directory=collection_path, 
                embedding_function=self.embedding_function,
            ) 
        return collection, collection_wrapper

    def get_retriever(self, vectorstore):
        return vectorstore.as_retriever()

    def generate_prompt(self, messages):
        prompt = ChatPromptTemplate.from_messages(messages)
        return prompt

    def setup_llm(self, model_name="gpt-4-0125-preview", temperature=0):
        llm = ChatOpenAI(api_key=self.api_key, model_name=model_name, temperature=temperature)
        return llm

    def setup_rag_chain(self, retriever, prompt, llm):
        rag_chain = (
            {"context": retriever, "text": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        return rag_chain
    

    def get_result(self, key, text):
        prompt = self.prompts[key]
        retrievers = {
            "CITY": self.vector_db_retriever,
            "DATE": self.vector_db_retriever, # not used
            "CLIENT_NAME": self.collection_retriever,
            "ACCOUNT_NAME": self.collection_retriever,
        }
        rag_chain = self.setup_rag_chain(retrievers[key], prompt, self.llm)
        result = rag_chain.invoke(text.lower())
        return "" if result == "None" else result.upper()
    

    def query(self, key, id, text) -> str:
        res = self.llm_cache.read(id, key)
        if res is None:
            res = self.get_result(
                key=key,
                text=text,
            )
            self.llm_cache.write(id, key, res)
        return res
    

class LLMClient:
    def __init__(self):
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.rag = RAG(api_key=self.api_key)
