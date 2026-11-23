
import os
from dotenv import load_dotenv

# Change this import to your actual provider path
from stores.llm.providers.OpenAIProvider import OpenAIProvider
from helpers.config import get_settings

settings = get_settings()
load_dotenv()


def test_embedding():

    # 1. Initialize Provider
    provider = OpenAIProvider(
        api_key=settings.NIVDIA_API_KEY,
        api_url=settings.NIVDIA_API_URL
    )

    # 2. Set Embedding Model
    provider.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=1536
    )

    # 3. Prepare Input Texts
    texts = [
        "What is artificial intelligence?",
        # "Machine learning is a subset of AI.",
        # "Python is a programming language."
    ]

    # 4. Generate Embeddings
    embeddings = provider.embed_text(texts)

    # 5. Validate Results
    assert embeddings is not None, "Embedding failed!"

    assert len(embeddings) == len(texts), \
        "Number of embeddings does not match texts!"

    for i, (text, embedding) in enumerate(zip(texts, embeddings)):

        assert len(embedding) == provider.embedding_size

        print(f"\nText {i + 1}: {text}")
        print(f"Embedding Dimensions: {len(embedding)}")
        print(f"First 5 Values: {embedding[:5]}")

    print("\nAll embedding tests passed!")


if __name__ == "__main__":
    test_embedding()
