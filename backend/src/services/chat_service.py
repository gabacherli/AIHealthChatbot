"""
Chat service.
This module contains the chat service functions.
"""
from .prompt_builder import build_prompt
from .document_service import DocumentService
from openai import OpenAI
from ..config import get_config

config = get_config()

client = OpenAI(
    api_key=config.OPENAI_API_KEY
)

document_service = DocumentService()

def get_answer_with_context(question: str, role: str, user_id: str = None) -> tuple:
    """
    Get an answer to a question with context.

    Args:
        question: The question to answer.
        role: The role of the user (patient or professional).
        user_id: The ID of the user asking the question.

    Returns:
        A tuple containing the answer and a list of sources.
    """
    # Use the document service to retrieve context
    filters = {
        "user_role": role
    }

    # Add user_id to filters if provided
    if user_id:
        filters["user_id"] = user_id

    # Retrieve context for the query
    search_results = document_service.search_documents(
        query=question,
        filters=filters,
        top_k=3
    )

    # Extract context text and sources
    context_texts = []
    sources = []

    for result in search_results:
        context_texts.append(result["content"])

        # Extract source information
        if "metadata" in result:
            source_info = {
                "source": result["metadata"].get("source", "Unknown"),
                "page": result["metadata"].get("page", None)
            }
            sources.append(source_info)

    # Build the prompt with the context
    prompt_messages = build_prompt(question, context_texts, role)

    response = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=prompt_messages,
        temperature=0.5
    )

    answer = response.choices[0].message.content

    # Return both the answer and the sources
    return answer, sources
