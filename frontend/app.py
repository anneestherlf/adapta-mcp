import streamlit as st
import requests

# URL do nosso Gateway FastAPI
GATEWAY_URL = "http://127.0.0.1:8000/process-command"

st.set_page_config(layout="wide")
st.title("🤖 PoC - Gateway Central Inteligente")
st.caption("Digite um comando em linguagem natural, como 'Busque por iPhone 15 no Mercado Livre'")

# Formulário para entrada do usuário
with st.form(key="command_form"):
    user_prompt = st.text_input("Seu comando:", key="prompt_input")
    submit_button = st.form_submit_button(label="Enviar")

if submit_button and user_prompt:
    with st.spinner("Processando seu pedido..."):
        try:
            # 1. Interface envia comando para o Gateway
            payload = {"prompt": user_prompt}
            response = requests.post(GATEWAY_URL, json=payload)
            response.raise_for_status()

            # 6. Gateway devolve resposta única
            data = response.json()

            # Exibe a resposta
            if data.get("status") == "success":
                st.success("Resposta do Gateway:")
                st.markdown(data.get("data", "Nenhuma resposta gerada."))
            else:
                st.error(f"O Gateway retornou um erro: {data.get('message', 'Erro desconhecido')}")

        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao conectar-se ao Gateway. Ele está rodando? \nDetalhes: {e}")