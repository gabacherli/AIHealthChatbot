"""
Chat service.
This module contains the chat service functions.
"""
from .prompt_builder import build_prompt
from .embedding_service import retrieve_context
from openai import OpenAI
from ..config import get_config

config = get_config()

client = OpenAI(
    api_key=config.OPENAI_API_KEY
)

def get_answer_with_context(question: str, role: str) -> str:
    """
    Get an answer to a question with context.

    Args:
        question: The question to answer.
        role: The role of the user (patient or professional).

    Returns:
        The answer to the question.
    """
    context = retrieve_context(question)

    prompt_messages = build_prompt(question, context, role)

    response = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=prompt_messages,
        temperature=0.5
    )

    return response.choices[0].message.content
