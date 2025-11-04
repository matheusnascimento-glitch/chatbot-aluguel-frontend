import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Chatbot CarroAluguel V1",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Chatbot CarroAluguel V1")

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
                    
                    # Verifica se há erro na execução da Step Function
                    if result.get("status") == "FAILED":
                        error_cause = result.get("cause", "Erro desconhecido")
                        error_msg = f"❌ Erro na Step Function: {error_cause}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    else:
                        # Tenta extrair a resposta do chatbot
                        bot_response = result.get("output", {}).get("question", "Resposta não encontrada")
                        
                        # Se não encontrou na estrutura padrão, tenta outras possibilidades
                        if bot_response == "Resposta não encontrada":
                            # Verifica se há filtro de erro
                            if "filter" in str(result) and "ERRO_PARAMETROS" in str(result):
                                bot_response = "❌ Erro nos parâmetros fornecidos. Verifique se a data está no formato correto (DD/MM/AAAA)."
                            else:
                                bot_response = f"Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}"
                        
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
    st.header("Locais para Copiar e Colar")
    
    st.subheader("Local Retirada (dados mockados - copiar e colar)")
    retirada_data = json.dumps({"tipo_retirada": "bairro", "ref_retirada": "reboucas", "cid_retirada": 6015})
    st.code(retirada_data, language="json")
    
    st.subheader("Local Devolução (dados mockados - copiar e colar)")
    devolucao_data = json.dumps({"tipo_devolucao": "aeroporto", "ref_devolucao": 9, "cid_devolucao": 8452})
    st.code(devolucao_data, language="json")
