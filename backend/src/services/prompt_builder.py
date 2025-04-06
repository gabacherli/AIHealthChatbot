# Enrich the prompt with the user's role and context documents
def build_prompt(question: str, context_docs: str, user_role: str):
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
