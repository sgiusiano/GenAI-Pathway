import streamlit as st
from datetime import datetime
from bizlaunch.app_context import ApplicationContext


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if "app_context" not in st.session_state:
        st.session_state.app_context = ApplicationContext()


def main():
    st.set_page_config(page_title="BizLaunch AI Assistant", page_icon="🚀", layout="wide")

    initialize_session_state()

    st.title("🚀 BizLaunch AI Assistant")
    st.caption("Asistente inteligente para ayudarte a lanzar tu negocio en Córdoba")

    with st.sidebar:
        st.header("Información")
        st.write(f"**Thread ID:** {st.session_state.thread_id}")
        st.write(f"**Mensajes:** {len(st.session_state.messages)}")

        if st.button("🔄 Nueva Conversación", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.rerun()

        st.divider()

        st.subheader("Ejemplos de consultas")
        st.markdown(
            """
        - Quiero abrir una cafetería en Nueva Córdoba con presupuesto de $600.000/mes
        - Necesito analizar el mercado para un restaurant en el Centro
        - Qué trámites necesito para abrir un comercio?
        - Cuánto cuesta montar una tienda de ropa?
        """
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Cuéntame sobre tu proyecto de negocio..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analizando tu solicitud..."):
                graph = st.session_state.app_context.get_graph()

                result = graph.run(user_input=prompt, thread_id=st.session_state.thread_id)

                response = result.get("final_report", "No pude generar un reporte.")

                st.markdown(response)

                st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
