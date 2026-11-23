
import os
from dotenv import load_dotenv

from stores.llm.providers.OpenAIProvider import OpenAIProvider
from helpers.config import get_settings
settings = get_settings()

load_dotenv()


def test_generation():

    # 1. Initialize Provider
    provider = OpenAIProvider(
        api_key=settings.OPENAI_API_KEY,
        api_url=settings.OPENAI_API_URL
    )

    # 2. Set Generation Model
    provider.set_generation_model(
        model_id=settings.GENERATION_MODEL_ID,
    )

    # 3. Prepare Prompt
    prompt = "Explain what a RAG system is in 3 sentences."

    # 4. Generate Text
    response = provider.generate_text(
        prompt=prompt,
        max_output_tokens=200,
        temperature=0.2
    )

    # 5. Validate Results
    assert response is not None, "Generation failed!"
    assert isinstance(response, str), "Response must be a string!"
    assert response.strip(), "Response is empty!"

    print("\n========== GENERATION TEST ==========")

    print(f"\nModel: {provider.generation_model_id}")
    print(f"\nPrompt: {prompt}")
    print(f"\nGenerated Response:\n{response}")

    print("\nAll generation tests passed!")


if __name__ == "__main__":
    test_generation()
