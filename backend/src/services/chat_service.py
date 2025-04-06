from .prompt_builder import build_prompt
from .embedding_service import retrieve_context
from openai import OpenAI
from ..config.config import Config

config = Config()
client = OpenAI(
  api_key=config.OPENAI_API_KEY
)

def get_answer_with_context(question: str, role: str) -> str:
    context = retrieve_context(question)
    prompt_messages = build_prompt(question, context, role)
    response = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=prompt_messages,
        temperature=0.5
    )
    return response.choices[0].message.content
