import streamlit as st
import os
from typing import Any, List, Dict, Callable
from tzlocal import get_localzone
from core.db_logger import (
    load_conversations_for_token,
    load_messages_for_conversation,
    create_new_conversation,
    is_valid_token,
)
from langchain_community.chat_message_histories import ChatMessageHistory

ChatCallbackType = Callable[[str, List[Any]], str]
FeedbackCallbackType = Callable[[int, int], None]

class ChatUI:
    def __init__(self, providers: Dict[str, List[str]]):
        self.providers = providers
        self.default_provider = list(providers.keys())[0]
        self.default_model = providers[self.default_provider][0]
        st.session_state.setdefault("messages", [{"role": "assistant", "content": "Ask me anything."}])
        st.session_state.setdefault("selected_provider", self.default_provider)
        st.session_state.setdefault("selected_model", self.default_model)
        st.session_state.setdefault("conversation_id", None)
        st.session_state.setdefault("user_token", "")
        st.session_state.setdefault("token_is_valid", False)

    def _validate_token(self):
        token = st.session_state.user_token
        st.session_state.token_is_valid = is_valid_token(token)
        if not st.session_state.token_is_valid:
            st.session_state.messages = [{"role": "assistant", "content": "Ask me anything."}]
            st.session_state.conversation_id = None

    def _load_and_prime_history(self, conversation_id: str):
        token = st.session_state.user_token
        if not token or not st.session_state.token_is_valid:
            return
        messages = load_messages_for_conversation(conversation_id)
        st.session_state.messages = messages or [{"role": "assistant", "content": "How can I help you?"}]
        history_key = f"{token}:{conversation_id}"
        history = ChatMessageHistory()
        for msg in st.session_state.messages:
            role, content = msg.get("role", "assistant"), msg.get("content", "")
            if role == "user":
                history.add_user_message(content)
            elif "assistant" in role:
                history.add_ai_message(content)
        st.session_state.message_store[history_key] = history

    def render(self, chat_callback: ChatCallbackType, feedback_callback: FeedbackCallbackType, tools: List[Any]):
        with st.sidebar:
            st.title("💬 CTFriend")
            st.subheader("🔑 Login Token")
            st.text_input("Enter your unique login token", key="user_token", on_change=self._validate_token)
            if not st.session_state.token_is_valid and st.session_state.user_token:
                st.error("Invalid or non-whitelisted token.")
            if st.session_state.token_is_valid:
                st.subheader("⚙️ Model Configuration")
                def on_provider_change():
                    st.session_state.selected_model = self.providers[st.session_state.selected_provider][0]
                st.selectbox("Select Provider", list(self.providers.keys()), key="selected_provider", on_change=on_provider_change)
                st.selectbox("Select Model", self.providers.get(st.session_state.selected_provider, []), key="selected_model")
                is_gemini = st.session_state.selected_provider == "Gemini"
                st.text_input("Enter API Key", type="password", key="api_key", placeholder="Required for Gemini models" if is_gemini else "Not required (Key complementary)", disabled=not is_gemini)
                st.checkbox("Enable MCP Servers", key="use_mcp", value=True)
                st.divider()
                st.subheader("Chats")
                def handle_new_chat():
                    new_conv_id = create_new_conversation(st.session_state.user_token)
                    if new_conv_id:
                        st.session_state.conversation_id = new_conv_id
                        st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]
                        st.rerun()
                st.button("➕ New Chat", use_container_width=True, on_click=handle_new_chat)
                conversations = load_conversations_for_token(st.session_state.user_token)
                if conversations:
                    local_tz = get_localzone()
                    options = {str(c.id): f"Chat from {c.started_at.astimezone(local_tz).strftime('%b %d, %H:%M')}" for c in conversations}
                    if st.session_state.conversation_id is None:
                        st.session_state.conversation_id = str(conversations[0].id)
                        self._load_and_prime_history(st.session_state.conversation_id)
                    selected_conv_id = st.selectbox("Load a past chat:", options.keys(), format_func=lambda x: options[x])
                    if st.session_state.conversation_id != selected_conv_id:
                        st.session_state.conversation_id = selected_conv_id
                        self._load_and_prime_history(selected_conv_id)
                        st.rerun()

        for msg in st.session_state.messages:
            with st.chat_message(msg.get("role", "assistant")):
                st.write(msg.get("content", ""))

        is_api_key_missing = st.session_state.selected_provider == "Gemini" and not st.session_state.api_key
        is_disabled = not st.session_state.token_is_valid or is_api_key_missing
        placeholder = "Enter a valid token..." if not st.session_state.token_is_valid else "Enter your Gemini API key..." if is_api_key_missing else "Ask me something..."
        
        if prompt := st.chat_input(placeholder, disabled=is_disabled):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

        if st.session_state.messages and st.session_state.messages[-1].get("role") == "user" and st.session_state.token_is_valid:
            last_prompt = st.session_state.messages[-1]["content"]
            try:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = chat_callback(last_prompt, tools)
                        # Directly append the new message to the UI state and display it
                        st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_message = f"⚠️ An unexpected error occurred: {e}"
                st.session_state.messages.append({"role": "assistant", "content": error_message})
            finally:
                # Rerun one last time to update the display and break the loop
                st.rerun()