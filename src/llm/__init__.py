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
from langchain.docstore.document import Document
from langchain_community.embeddings import FakeEmbeddings
import shutil


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
    def __init__(self, api_key, vectordb_updates, model_name="gpt-3.5-turbo-0125"):
        self.api_key = api_key
        self.embedding_function = OpenAIEmbeddings(api_key=self.api_key)
        self.clean_vector_databases(vectordb_updates)
        self.vector_db_territories = self.setup_vector_database(name="territories")
        self.vector_db_client_names = self.setup_vector_database(name="client_names")
        self.vector_db_account_names = self.setup_vector_database(name="account_names")
        self.vector_db_territories_retriever = self.get_retriever(self.vector_db_territories, k=1) # there's only 1 doc
        self.vector_db_client_names_retriever = self.get_retriever(self.vector_db_client_names, k=1) 
        self.vector_db_account_names_retriever = self.get_retriever(self.vector_db_account_names, k=1) 
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
                    ("human", "These names are Ecuadorian and/or Latin American and they are usually in Spanish."),
                    ("human", "The client name may be misspelled."),
                    ("human", "You will be given a context that has some of our clients names to help you."),
                    ("human", "Use this context to find the potential correction and print it."),
                    ("human", "If you don't find a potential correction in the context, print the client name as it is."),
                    ("human", "If the text is a number, print 'None'."),
                    ("human", "Text: {text}"),
                    ("human", "Context: {context}"),
                ],
            ),
            "ACCOUNT_NAME": self.generate_prompt(
                messages=[
                    ("system", "You are a machine that prints account names and nothing more."),
                    ("human", "This text should contain the full name of an account/client/organization to whom a check is being paid."),
                    ("human", "You will be given a context that has some of our clients account names to help you."),
                    ("human", "Use this context to find the potential correction and print it."),
                    ("human", "If you don't find a potential correction in the context, print the account name as it is."),
                    ("human", "If the text is a number, print 'None'."),
                    ("human", "Text: {text}"),
                    ("human", "Context: {context}"),
                ],
            )
        }
        self.llm = self.setup_llm(model_name=model_name)
        self.llm_cache = LLMCache()

    def load_documents(self, name):
        paths = {
            "territories":'data/territories.txt',
            "client_names":'data/client_names.txt',
            "account_names":'data/account_names.txt',
        }
        loader = TextLoader(paths[name])
        documents = loader.load()
        return documents

    def chunk_documents(self, documents):
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunked_documents = text_splitter.split_documents(documents)
        if len(chunked_documents) == 0:
            chunked_documents = [Document(page_content="")]
        return chunked_documents

    def clean_vector_databases(self, vectordb_updates):
        # remove folder instead of calling reset() because at this point vectorstores may not be initialized
        if "territories" in vectordb_updates:
            if os.path.exists("llm/vectordb/territories"):
                shutil.rmtree("llm/vectordb/territories")
        if "client_names" in vectordb_updates:
            if os.path.exists("llm/vectordb/client_names"):
                shutil.rmtree("llm/vectordb/client_names")
        if "account_names" in vectordb_updates:
            if os.path.exists("llm/vectordb/account_names"):
                shutil.rmtree("llm/vectordb/account_names")

    def setup_vector_database(self, name):
        vector_db_path = f"llm/vectordb/{name}"
        vector_db = None
        if not os.path.exists(vector_db_path):
            documents = self.load_documents(name)
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

    def get_retriever(self, vectorstore, k=4):
        return vectorstore.as_retriever(search_kwargs={"k": k})

    def generate_prompt(self, messages):
        prompt = ChatPromptTemplate.from_messages(messages)
        return prompt

    def setup_llm(self, model_name="gpt-3.5-turbo-0125", temperature=0):
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
    
    # DATE doesn't use context
    # Useful for testing
    def create_empty_vectorstore_retriever(self):
        return Chroma.from_documents(
            documents=[Document(page_content="")],
            embedding=FakeEmbeddings(size=1),
        ).as_retriever(search_kwargs={"k": 1})

    def get_result(self, key, text):
        prompt = self.prompts[key]
        retrievers = {
            "CITY": self.vector_db_territories_retriever,
            "DATE": self.create_empty_vectorstore_retriever(),
            "CLIENT_NAME": self.vector_db_client_names_retriever,
            "ACCOUNT_NAME": self.vector_db_account_names_retriever,
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
    def __init__(self, vectordb_updates, model_name="gpt-3.5-turbo-0125"):
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.rag = RAG(api_key=self.api_key, vectordb_updates=vectordb_updates, model_name=model_name)
