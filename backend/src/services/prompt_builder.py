"""
Prompt builder service.
This module contains functions for building prompts for the OpenAI API.
"""

def build_prompt(question: str, context_docs: str, user_role: str):
    """
    Build a prompt for the OpenAI API.

    Args:
        question: The question to answer.
        context_docs: The context documents to use for answering.
        user_role: The role of the user (patient or professional).

    Returns:
        A list of messages for the OpenAI API.
    """
    role_instruction = (
        "Explain in easy-to-understand terms suitable for a patient."
        if user_role == "patient"
        else "Provide a detailed answer with clinical insights."
    )

    system_msg = (
        "You are a helpful medical assistant. " + role_instruction
    )

    if context_docs:
        system_msg += f"\nUse the following information to answer:\n{context_docs}"

    return [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": question},
    ]
