import json
from dataclasses import dataclass
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from huggingface_hub import configure_http_backend
import requests


from llama_index.core.response import Response

from modules.DataModels import ResumeData

@dataclass
class EmbedModel:
    """Simple data class to hold embedding model configuration"""
    name: str
    source: str

class ExtractionTask:
    """
    A class for extracting structured information from resumes using LLM models.

    This class handles the extraction of relevant information from resume documents
    and converts it into a structured ResumeData format.
    """

    # This updates the hugging face client to not require a secure session
    def _backend_factory() -> requests.Session:
        session = requests.Session()
        session.verify = False
        return session

    def __init__(self, model: str, embed_model: EmbedModel) -> None:
        """
        Initialize the ExtractionTask with specified models.

        Args:
            model: The main language model for text processing
            embed_model: The embedding model for text vectorization
        """
        self.model = model
        self.embed_model = embed_model

        # setup the ollama client to use the correct models
        Settings.llm = Ollama(model=model, request_timeout=360.0)

        if embed_model.source == "local":
            Settings.embed_model = OllamaEmbedding(model_name=embed_model.name)
        elif embed_model.source == "huggingface":
            configure_http_backend(backend_factory=ExtractionTask._backend_factory)
            Settings.embed_model = HuggingFaceEmbedding(model_name=embed_model.name)

    def _remove_dots_lines(self, json_str: str) -> str:
        """Remove lines containing only dots with optional whitespace"""
        return "\n".join(line for line in json_str.splitlines()
                         if not line.strip().replace('.', '').isspace()
                         and not line.strip() == '...')

    def _remove_comments_and_commas(self, json_str: str) -> str:
        """Remove comment lines and trailing commas before comments"""
        lines = json_str.splitlines()
        result_lines = []
        for i in range(len(lines)):
            if not lines[i].strip().startswith("//"):
                if (i + 1 < len(lines) and
                        lines[i].rstrip().endswith(",") and
                        lines[i + 1].strip().startswith("//")):
                    result_lines.append(lines[i].rstrip()[:-1])  # Remove trailing comma
                else:
                    result_lines.append(lines[i])
        return "\n".join(result_lines)

    def _has_double_quotes(self, json_str: str) -> bool:
        """Check if string contains double quotes"""
        return '"' in json_str

    def _replace_single_quotes(self, json_str: str) -> str:
        """Replace single quotes with double quotes"""
        return json_str.replace("'", '"')

    def _common_cleanup(self, json_str: str) -> str:
        """
        LLMs don't always generate clean JSON output.
        If parsing the JSON fails, this will reformat the json to deal with common LLM JSON issues.

        :param json_str:
        :return: reformatted JSON
        """
        # REMOVE ANY WEIRD WHITE SPACES
        json_str = str(json_str).strip()

        # SOMETIMES THE LLM WRAPS THE JSON IN A STATEMENT, SIMPLY TAKE THE {} BLOB
        json_str = json_str[json_str.find("{"):json_str.rfind("}") + 1]

        # SOMETIMES THE LMM PUTS IN AN ELIPSES TO SHOW CONTENT THEY DIDN'T ADD
        json_str = self._remove_dots_lines(json_str)

        # SOME LLM'S PUT IN COMMENT LINES, USUALLY AFTER A SECTION THAT THE LEAVE A TRAILING COMMA ON
        json_str = self._remove_comments_and_commas(json_str)

        # REPLACE SINGLE QUOTES WITH DOUBLE QUOTES
        if not self._has_double_quotes(json_str):
            json_str = self._replace_single_quotes(json_str)

        return json_str

    def run_extraction(self) -> ResumeData:
        """
        Execute the resume information extraction process.

        Returns:
            ResumeData: Structured data containing extracted resume information
        """

        INPUT_DIR = "./input"

        print("\n" +"="*80)
        print("running extraction:")
        print("   model: " + self.model)
        print("   embed_model: " +self.embed_model.name)
        print("\n")
        print("   > Starting the data load...")

        reader = SimpleDirectoryReader(input_dir=INPUT_DIR)
        documents = reader.load_data()


        print ("   > Vectorize the documents...")
        index = VectorStoreIndex.from_documents(documents)

        print("   > Running the extraction...")
        output_schema = ResumeData.model_json_schema()
        query_engine = index.as_query_engine(output_class=ResumeData)

        q = f"""/
        You are a bot designed to parse resumes and extract data into a standard json object.
        Use the JSON format below for your response. ONLY return the JSON object.
        Your response will be parsed and it must conform to the schema. Be strict about matching attribute names from the schema.
        Use the schema to identify which fields from the resume to extract.
        __________________
        {output_schema}
        """

        response = query_engine.query(q)
        print("   > response:")
        print(80*"-")
        print(response.response)
        print("\n" + 80 * "-")
        print("   > converting to ResumeData")

        failed = False
        resume_data = None
        json_str = response.response

        try:
            json_data = json.loads(json_str)
            resume_data = ResumeData.parse_raw(json.dumps(json_data))
        except (json.JSONDecodeError, ValueError) as e:
            failed = True
            print(f"   > FIRST ATTEMPT Error parsing response: {str(e)}")


        if failed:
            print("   > LLM JSON had errors. Attempting to reformat and recover.")

            try:
                # Try to parse and validate JSON first
                json_str = self._common_cleanup(json_str)
                print("   > reformatted string")
                print(80 * "-")
                print(json_str)
                print("\n" + 80 * "-")

                json_data = json.loads(json_str)
                resume_data = ResumeData.parse_raw(json.dumps(json_data))

            except (json.JSONDecodeError, ValueError) as e:
                print(f"   > FINAL ATTEMPT Error parsing response: {str(e)}")
                print(f"   > returning a NONE ReseumeData Record")

        return resume_data

