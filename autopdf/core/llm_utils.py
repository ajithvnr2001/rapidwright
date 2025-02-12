from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from core.config import settings
from typing import Optional, Dict

def generate_text(prompt_template: str, input_data: Dict, model_name: Optional[str] = None) -> str:
    """Generates text using an OpenAI-compatible LLM."""

    prompt = ChatPromptTemplate.from_template(prompt_template)

    # Use the provided model_name if given, otherwise use the default from settings
    effective_model_name = model_name if model_name else settings.model_name

    llm = ChatOpenAI(
        model=effective_model_name,  # Using settings
        openai_api_base=settings.openai_api_base,  # Using settings
        openai_api_key=settings.openai_api_key,  # Using settings
        temperature=0.2,
        max_tokens=1000,
        )
    chain = prompt | llm | StrOutputParser()
    generated_text = chain.invoke(input_data)
    return generated_text
