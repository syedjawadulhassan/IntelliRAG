# src/generate.py

import os
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4o-mini')

prompt_template = """You are a helpful assistant. Use the sources quoted below.  
When you assert a fact, add (source: <source>, chunk: <chunk>) after the sentence.

Sources:
{sources}

Question:
{question}

Answer concisely. If you cannot find the answer in the sources, say "I do not have enough information."  
"""

template = PromptTemplate(input_variables=["sources", "question"], template=prompt_template)

# gpt-4o-mini (and most current OpenAI models) only support the chat-completions
# endpoint, so we use ChatOpenAI rather than the legacy completions-only OpenAI class.
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model=LLM_MODEL, temperature=0.0)

# Build a simple "prompt -> llm -> string" pipeline
chain = template | llm | StrOutputParser()


def answer_query(question, retrieved_chunks):
    sources_text = "\n\n".join([
        f"{meta.get('source', 'unknown')}_chunk_{meta.get('chunk', '?')}: {text}"
        for meta, text in retrieved_chunks
    ])
    result = chain.invoke({"sources": sources_text, "question": question})
    return result
