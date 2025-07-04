import logging
from typing import Optional, Dict, Any

from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_deepseek import ChatDeepSeek


from .vector_store_manager import get_vector_store
from ..core.config import (
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    DEEPSEEK_API_KEY,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_llm(model_name: str, api_key: Optional[str] = None, **kwargs):
    """Initializes and returns the specified LangChain LLM instance."""
    logger.info(f"Initializing LLM: {model_name}")

    llm_kwargs = {
        "temperature": 1,
        **kwargs
    }

    try:
        if model_name.startswith("gpt-"):
            key = api_key or OPENAI_API_KEY
            if not key:
                raise ValueError("OpenAI API key is required for GPT models but not found.")
            llm_kwargs["model_name"] = model_name
            llm_kwargs["api_key"] = key
            return ChatOpenAI(**llm_kwargs)

        elif model_name.startswith("claude-"):
            key = api_key or ANTHROPIC_API_KEY
            if not key:
                raise ValueError("Anthropic API key is required for Claude models but not found.")
            llm_kwargs["model"] = model_name # Anthropic uses 'model' parameter
            llm_kwargs["api_key"] = key
            return ChatAnthropic(**llm_kwargs)

        elif model_name.startswith("deepseek-"):
            key = api_key or DEEPSEEK_API_KEY
            if not key:
                raise ValueError("DeepSeek API key is required for DeepSeek models but not found.")
            llm_kwargs["model"] = model_name
            llm_kwargs["api_key"] = key
            return ChatDeepSeek(**llm_kwargs)

        else:
            raise ValueError(f"Unsupported LLM model specified: {model_name}")

    except ImportError as e:
        logger.error(f"Missing LLM integration library for {model_name}: {e}. Please install the required package (e.g., pip install langchain-openai langchain-anthropic)")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize LLM '{model_name}': {e}", exc_info=True)
        raise

def create_rag_chain(model_name: str = "gpt-4o", api_key: Optional[str] = None, llm_kwargs: Optional[Dict[str, Any]] = None):
    """Creates the full RAG chain using LCEL."""
    vector_store = get_vector_store()
    if vector_store is None:
        raise RuntimeError("Vector store is not initialized. Add documents first.")

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={'k': 5}
    )

    llm = get_llm(model_name, api_key, **(llm_kwargs or {}))

    template = """
        You are a helpful assistant for question-answering tasks.
        Be friendly and concise.
        Detect the user's input language and respond in the same language throughout the discussion.

        For direct questions, provide accurate and concise answers based solely on the following context. If the context does not contain enough information to answer a direct question, respond with "I don't have enough information to answer that question." Do not use external knowledge or make assumptions beyond the provided context for these answers.

        For non-question inputs or casual remarks, feel free to engage lightly and conversationally to maintain a friendly tone, but avoid providing information outside the context.

        Context: {context}

        User Input: {question}

        Answer:
    """
    prompt = ChatPromptTemplate.from_template(template)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        RunnableParallel(
            context=retriever | format_docs,
            question=RunnablePassthrough()
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    logger.info(f"RAG chain created successfully with model: {model_name}")
    return rag_chain

def query_rag(query: str, model_name: str = "gpt-4o", api_key: Optional[str] = None) -> str:
    """Queries the RAG chain with the provided question and model selection."""
    logger.info(f"Received query: '{query}' for model: {model_name}")
    try:
        rag_chain = create_rag_chain(model_name=model_name, api_key=api_key, llm_kwargs={"temperature": 0.7})
        response = rag_chain.invoke(query)
        logger.info(f"Generated response: '{response}'")
        return response
    except RuntimeError as e:
        logger.error(f"Runtime error during RAG query: {e}")
        return f"Error: {e}"
    except ValueError as e:
        logger.error(f"Configuration error during RAG query: {e}")
        return f"Configuration Error: {e}"
    except Exception as e:
        logger.error(f"An unexpected error occurred during the RAG query: {e}", exc_info=True)
        return "An unexpected error occurred while processing your request."

