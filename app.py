import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Chatbot Aluguel de Carros",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Chatbot Aluguel de Carros")

with st.sidebar:
    st.header("Configuração")
    api_url = st.text_input("URL da API", placeholder="https://sua-api.execute-api.region.amazonaws.com/stage/chat")
    api_key = st.text_input("API Key", type="password", placeholder="sua-api-key")
    customer_id = st.text_input("Customer ID", placeholder="customer123")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua mensagem..."):
    if not api_url or not api_key or not customer_id:
        st.error("Por favor, preencha todas as configurações na barra lateral.")
        st.stop()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            try:
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": api_key
                }
                
                payload = {
                    "CustomerId": customer_id,
                    "Question": prompt
                }
                
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.write("Debug - Resposta completa:", result)
                    bot_response = result.get("FinalResult", {}).get("Result", {}).get("question", "Resposta não encontrada")
                    st.markdown(bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                else:
                    error_msg = f"Erro {response.status_code}: {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Erro de conexão: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

if st.sidebar.button("Limpar Chat"):
    st.session_state.messages = []
    st.rerun()

with st.sidebar:
    st.markdown("---")
    st.markdown("### Sobre")
    st.markdown("Este é um frontend de teste para o chatbot de aluguel de carros hospedado na AWS.")
