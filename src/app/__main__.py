import os
import streamlit as st
from typing import Any, Dict, List, Optional
import logging

from core.ui import ChatUI
from core.db_logger import init_db, log_message, log_feedback
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda
from core.mcp_client_sync import MultiServerMCPClientSync

from google.api_core.exceptions import ResourceExhausted
from openai import RateLimitError, AuthenticationError
from anthropic import NotFoundError

AVAILABLE_PROVIDERS: Dict[str, List[str]] = {
    "Gemini": ["gemini-2.5-flash", "gemini-1.5-flash"],
    "Anthropic": [
        "claude-3-5-haiku-20241022", 
        "claude-sonnet-4-20250514", 
        "claude-opus-4-1-20250805"
    ],
}
MCP_SERVER_URLS: Dict[str, str] = {
    "cyberchef_api": os.environ.get("MCP_CYBERCHEF_URL", default="http://cyberchef_api:8001"),
    "rag_server": os.environ.get("MCP_RAG_URL", default="http://rag_server:8002"),
}
ANTHROPIC_API_KEY: Optional[str] = os.environ.get("ANTHROPIC_API_KEY")

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

def init_agent(tools: List[Any]) -> AgentExecutor:
    provider = st.session_state.selected_provider
    model = st.session_state.selected_model
    user_api_key = st.session_state.api_key

    if provider == "Gemini":
        llm = ChatGoogleGenerativeAI(model=model, google_api_key=user_api_key)
    elif provider == "Anthropic":
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
        llm = ChatAnthropic(model=model, api_key=ANTHROPIC_API_KEY)
    else:
        raise ValueError(f"Unknown provider: {provider}")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    
    st.session_state.agent_executor = agent_executor
    st.session_state.model_for_llm = model
    return agent_executor

def get_client_ip() -> str | None:
    try:
        from streamlit.web.server.server import Server
        session_info = Server.get_current()._get_session_info(st.runtime.get_instance()._session_id)
        return session_info.client.ip if session_info else None
    except Exception:
        try:
            return st.query_params.get("X-Forwarded-For") or st.query_params.get("X-Real-IP")
        except Exception:
            return None

def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in st.session_state.message_store:
        st.session_state.message_store[session_id] = ChatMessageHistory()
    return st.session_state.message_store[session_id]

def parse_agent_output(agent_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses the output from the agent executor to clean up the 'output' key.
    This is crucial for handling Anthropic's structured responses before they
    are passed to the chat history.
    """
    output = agent_output.get("output")

    if isinstance(output, list):
        text_content = "\n".join(
            block.get("text", "") for block in output if isinstance(block, dict)
        )
        agent_output["output"] = text_content.strip()
    elif isinstance(output, str):
        agent_output["output"] = output.strip()
    
    return agent_output

def chat_callback(prompt: str, tools: List[Any]) -> str:
    if st.session_state.selected_provider == "Gemini" and not st.session_state.api_key:
        return "🔑 Please enter your Gemini API key."
    if not st.session_state.get("token_is_valid"):
        return "🔑 Please enter a valid token."

    if "agent_executor" not in st.session_state or st.session_state.model_for_llm != st.session_state.selected_model:
        agent_executor = init_agent(tools)
    else:
        agent_executor = st.session_state.agent_executor
    
    conversation_id = st.session_state.get("conversation_id")
    persistent_conv_id = log_message(
        token=st.session_state.user_token, conversation_id=conversation_id,
        role="user", content=prompt, source_ip=get_client_ip(),
    )
    st.session_state.conversation_id = persistent_conv_id
    history_key = f"{st.session_state.user_token}:{persistent_conv_id}"

    agent_with_parser = agent_executor | RunnableLambda(parse_agent_output)

    agent_with_history = RunnableWithMessageHistory(
        agent_with_parser,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="output",
    )

    try:
        response = agent_with_history.invoke(
            {"input": prompt}, config={"configurable": {"session_id": history_key}}
        )
    except NotFoundError as e:
        logger.error(f"Model not found error: {e}")
        return f"⚠️ Model '{st.session_state.selected_model}' not found."
    except (ResourceExhausted, RateLimitError):
        return "⚠️ API quota exceeded."
    except AuthenticationError:
        return "⚠️ Authentication Error: Invalid API Key."
    except Exception as e:
        logger.exception("Unexpected error in chat_callback")
        return f"⚠️ An unexpected error occurred: {e}"

    answer = response.get("output", "")
    
    log_message(
        token=st.session_state.user_token, conversation_id=persistent_conv_id,
        role=f"assistant ({st.session_state.selected_model})", content=answer, source_ip="server",
    )
    return answer

def main():
    st.set_page_config(page_title="CTFriend", page_icon="💬", layout="wide")
    init_db()
    st.session_state.setdefault("api_key", "")
    st.session_state.setdefault("selected_provider", list(AVAILABLE_PROVIDERS.keys())[0])
    st.session_state.setdefault("selected_model", AVAILABLE_PROVIDERS["Gemini"][0])
    st.session_state.setdefault("message_store", {})
    st.session_state.setdefault("use_mcp", True)
    st.session_state.setdefault("conversation_id", None)
    st.session_state.setdefault("user_token", "")
    tools = []
    if st.session_state.use_mcp:
        try:
            server_config = {name: {"url": f"{url}/sse", "transport": "sse"} for name, url in MCP_SERVER_URLS.items()}
            mcp_client = MultiServerMCPClientSync(server_config)
            tools = mcp_client.get_tools()
            if not tools: st.warning("⚠️ No tools found on MCP servers.")
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            st.error("⚠️ Failed to connect to one or more MCP servers.")
    ui = ChatUI(providers=AVAILABLE_PROVIDERS)
    ui.render(chat_callback=chat_callback, feedback_callback=log_feedback, tools=tools)

if __name__ == "__main__":
    main()