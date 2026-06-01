import asyncio
import streamlit as st
from datetime import datetime
from parlant.client import AsyncParlantClient

# ----------------------
# Setup Parlant Client
# ----------------------
client = AsyncParlantClient(base_url="http://localhost:8800")

# ----------------------
# Event Storage
# ----------------------
if "events" not in st.session_state:
    st.session_state.events = []
if "last_offset" not in st.session_state:
    st.session_state.last_offset = 0

# ----------------------
# UI Display Functions
# ----------------------
def render_message(message, source, participant_name, timestamp):
    if source == "customer":
        st.markdown(f"**🧍‍♂️ Customer [{timestamp}]:** {message}")
    elif source == "ai_agent":
        st.markdown(f"**🤖 AI [{timestamp}]:** {message}")
    elif source == "human_agent":
        st.markdown(f"**🙋 {participant_name} [{timestamp}]:** {message}")
    elif source == "human_agent_on_behalf_of_ai_agent":
        st.markdown(f"**👤 (Human as AI) [{timestamp}]:** {message}")
    else:
        st.markdown(f"**🕵️ Unknown [{timestamp}]:** {message}")


async def fetch_events(session_id):
    try:
        events = await client.sessions.list_events(
            session_id=session_id,
            kinds="message",
            min_offset=st.session_state.last_offset,
            wait_for_data=5
        )
        for event in events:
            message = event.data.get("message")
            source = event.source
            participant_name = event.data.get("participant", {}).get("display_name", "Unknown")
            timestamp = getattr(event, "created", None) or event.data.get("created", "Unknown Time")
            event_id = getattr(event, "id", "Unknown ID")

            st.session_state.events.append(
                (message, source, participant_name, timestamp, event_id)
            )
            st.session_state.last_offset = max(st.session_state.last_offset, event.offset + 1)

    except Exception as e:
        st.error(f"Error fetching events: {e}")


async def send_human_message(session_id: str, message: str, operator_name: str = "Tier-2 Operator"):
    event = await client.sessions.create_event(
        session_id=session_id,
        kind="message",
        source="human_agent",
        message=message,
        participant={
            "id": "operator-001",
            "display_name": operator_name
        }
    )
    return event


async def send_message_as_ai(session_id: str, message: str):
    event = await client.sessions.create_event(
        session_id=session_id,
        kind="message",
        source="human_agent_on_behalf_of_ai_agent",
        message=message
    )
    return event


# ----------------------
# Streamlit UI
# ----------------------
st.title("💼 Human Handoff Assistant")

session_id = st.text_input("Enter Parlant Session ID:")

if session_id:
    st.subheader("Chat History")
    if st.button("Refresh Messages"):
        asyncio.run(fetch_events(session_id))

    for msg, source, participant_name, timestamp, event_id in st.session_state.events:
        render_message(msg, source, participant_name, timestamp)

    st.subheader("Send a Message")
    operator_msg = st.text_input("Type your message:")

    if st.button("Send as Human"):
        if operator_msg.strip():
            asyncio.run(send_human_message(session_id, operator_msg))
            st.success("Message sent as human agent ✅")
            asyncio.run(fetch_events(session_id))

    if st.button("Send as AI"):
        if operator_msg.strip():
            asyncio.run(send_message_as_ai(session_id, operator_msg))
            st.success("Message sent as AI ✅")
            asyncio.run(fetch_events(session_id))
