import importlib.util
import sys
from enum import Enum
from pathlib import Path
from types import SimpleNamespace
from types import ModuleType
from unittest import TestCase, mock


def load_nlp_controller():
    package_name = "_nlp_controller_test_package"
    package = ModuleType(package_name)
    package.__path__ = []

    base_controller_module = ModuleType(f"{package_name}.BaseController")

    class BaseController:
        def __init__(self):
            pass

    base_controller_module.BaseController = BaseController

    db_schemes_module = ModuleType("models.db_schemes")
    db_schemes_module.project_scheme = object
    db_schemes_module.chunk_scheme = object

    llm_enums_module = ModuleType("stores.llm.LLMEnums")

    class DocumentTypeEnum(Enum):
        DOCUMENT = "passage"
        QUERY = "query"

    llm_enums_module.DocumentTypeEnum = DocumentTypeEnum

    dependency_modules = {
        package_name: package,
        f"{package_name}.BaseController": base_controller_module,
        "models": ModuleType("models"),
        "models.db_schemes": db_schemes_module,
        "stores": ModuleType("stores"),
        "stores.llm": ModuleType("stores.llm"),
        "stores.llm.LLMEnums": llm_enums_module,
    }

    controller_path = Path(__file__).parents[1] / "controllers" / "NLPController.py"
    spec = importlib.util.spec_from_file_location(
        f"{package_name}.NLPController",
        controller_path,
    )
    module = importlib.util.module_from_spec(spec)

    with mock.patch.dict(sys.modules, dependency_modules):
        spec.loader.exec_module(module)

    return module.NLPController


NLPController = load_nlp_controller()


class EmbeddingClientStub:
    def __init__(self):
        self.calls = []

    def embed_text(self, texts, document_type):
        self.calls.append((texts, document_type))
        return [[0.1, 0.2, 0.3]]


class VectorDBClientStub:
    def __init__(self):
        self.calls = []

    def search_by_vector(self, collection_name, vector, limit):
        self.calls.append((collection_name, vector, limit))
        return [{"text": "matching chunk", "score": 0.9}]


class NLPQueryEmbeddingTest(TestCase):
    def test_query_is_embedded_as_one_item_and_vector_is_flattened(self):
        embedding_client = EmbeddingClientStub()
        vectordb_client = VectorDBClientStub()
        controller = NLPController(
            vectordb_client=vectordb_client,
            generation_client=None,
            embedding_client=embedding_client,
        )

        results = controller.search_vector_db_collection(
            project=SimpleNamespace(project_id="10"),
            text="What is RAG?",
            limit=3,
        )

        self.assertEqual(embedding_client.calls, [(["What is RAG?"], "query")])
        self.assertEqual(vectordb_client.calls, [("collection_10", [0.1, 0.2, 0.3], 3)])
        self.assertEqual(results, [{"text": "matching chunk", "score": 0.9}])

