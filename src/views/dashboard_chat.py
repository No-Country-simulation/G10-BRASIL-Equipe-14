from uuid import uuid4

import streamlit as st

from src.services.sentiment_chat import ask_agent, build_context


def render_chat(frame, filters, loaded_at, quality):
    st.divider()
    st.subheader("Assistente de análise")
    st.caption("O assistente analisa os indicadores dos filtros atuais e uma amostra de publicações. Exemplo: qual sentimento predomina nas FAQs sobre Docker?")
    context = build_context(frame, filters, loaded_at, quality)
    state = st.session_state.setdefault("sentiment_chat", {
        "scope": context["snapshot_id"], "session_id": str(uuid4()), "messages": [],
    })
    if state["scope"] != context["snapshot_id"]:
        state.update(scope=context["snapshot_id"],
                     session_id=str(uuid4()), messages=[])
        st.info(
            "Os filtros ou dados mudaram. Uma nova conversa foi iniciada para este recorte.")
    if st.button("Limpar conversa", key="clear_sentiment_chat"):
        state.update(session_id=str(uuid4()), messages=[])
    conversation = st.container(key="sentiment_messages")
    with conversation:
        for message in state["messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    # The native chat input restores focus when a run finishes, which can scroll
    # the analytical page down to the assistant even before the user interacts.
    with st.form("sentiment_question_form", clear_on_submit=True, border=False):
        question = st.text_area(
            "Sua pergunta",
            placeholder="Pergunte sobre sentimentos, destinos editoriais ou tópicos",
            max_chars=4000,
            height=100,
            key="sentiment_question",
        )
        submitted = st.form_submit_button("Enviar pergunta", type="primary")
    if not submitted or not question or not question.strip():
        return
    with conversation:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            try:
                with st.spinner("Analisando os dados…"):
                    answer = ask_agent(
                        question, state["messages"], context, state["session_id"])
            except ValueError as exc:
                st.error(str(exc))
                return
            st.markdown(answer)
    state["messages"].extend([
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ])
    state["messages"] = state["messages"][-24:]
