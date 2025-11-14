"""
Interface de Apresentação
Passo 1: A "Vitrine" - onde o usuário digita comandos
"""
import streamlit as st
import requests
import json
from typing import Optional

# Configuração da página
st.set_page_config(
    page_title="MCP Gateway",
    page_icon="",
    layout="wide"
)

# URL do backend
BACKEND_URL = "http://localhost:8000"


def set_bg_color(hex_color: str = "#141C1A", btn_color: str = "#00AA97"):
    css = f"""
    <style>
    :root {{
        --bg-color: {hex_color};
        --btn-color: {btn_color};
        --text-color: #E6E6E6;
    }}
    /* App background */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] .main, [data-testid="stAppViewContainer"] [data-testid="stAppBody"] {{
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
    }}
    /* Streamlit main content area fallback selectors */
    .stApp, .main, .block-container {{
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
    }}
    /* Buttons (covers common Streamlit-generated classes) */
    div.stButton > button, .stButton>button, button, button.css-1emrehy, button.css-1ekf0zk, button.css-1w7v3tn {{
        background-color: var(--btn-color) !important;
        border-color: var(--btn-color) !important;
        color: #ffffff !important;
    }}
    /* Hover / focus */
    div.stButton > button:hover, .stButton>button:hover, button:hover {{
        filter: brightness(0.95) !important;
    }}
    /* Inputs and select highlights (accent) */
    .st-bk, .css-1v0mbdj, .css-1lcbmhc {{
        border-color: var(--btn-color) !important;
    }}
    /* Replace inline styles using red #FF4B4B */
    [style*="#FF4B4B"], [style*="#ff4b4b"] {{
        color: var(--btn-color) !important;
        background-color: transparent !important;
        border-color: var(--btn-color) !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def main():
    # Aplicar cor de fundo personalizada e cores dos botões
    set_bg_color("#141C1A", "#00AA97")

    # Exibir logo ao lado do título. Caminho relativo ao workspace.
    logo_path = "frontend/static/adapta-logo.png"
    col1, col2 = st.columns([1, 6])
    with col1:
        try:
            st.image(logo_path, width=250)
        except Exception:
            # Se a imagem não for encontrada, não interrompe a aplicação
            pass
    with col2:
        st.title("MCP Gateway")
    st.markdown("---")

    # Sidebar para navegação
    page = st.sidebar.selectbox(
        "Navegação",
        ["🏠 Executar Comando", "⚙️ Painel de Controle", "📊 Status"]
    )

    if page == "🏠 Executar Comando":
        show_execute_page()
    elif page == "⚙️ Painel de Controle":
        show_admin_panel()
    elif page == "📊 Status":
        show_status_page()


def show_execute_page():
    """Página principal: executar comandos"""
    st.header("Executar Comando")
    st.markdown("Digite seu comando em linguagem natural e o sistema executará as ações necessárias.")

    # Input do usuário
    user_id = st.text_input("ID do Usuário", value="default_user", help="Identificador único do usuário")
    prompt = st.text_area(
        "Comando",
        placeholder='Ex: "Marque uma Reunião de Alinhamento no meu Google Calendar amanhã às 10h e avise no canal #projetos do Slack que a reunião foi marcada."',
        height=150
    )

    if st.button("🚀 Executar", type="primary"):
        if not prompt:
            st.error("Por favor, digite um comando.")
            return

        with st.spinner("Processando comando..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/execute",
                    json={"prompt": prompt, "user_id": user_id},
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()

                    # Resposta consolidada
                    st.success("✅ Comando executado com sucesso!")
                    st.markdown("### Resposta:")
                    st.info(data.get("response", "Comando executado."))

                    # Detalhes (expansível)
                    with st.expander("📋 Ver detalhes técnicos"):
                        st.json(data.get("details", []))
                else:
                    st.error(f"Erro: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Não foi possível conectar ao backend. Certifique-se de que o servidor está rodando em http://localhost:8000")
            except Exception as e:
                st.error(f"Erro: {str(e)}")


def show_admin_panel():
    """Passo 0: Painel de Controle"""
    st.header("⚙️ Painel de Controle")
    st.markdown("Configure as ferramentas e credenciais do sistema.")

    tab1, tab2, tab3 = st.tabs(["🔐 Conectar Google", "🔑 Configurar Chaves", "📋 Ferramentas Configuradas"])

    with tab1:
        st.subheader("Conectar Conta Google (OAuth 2.0)")
        st.markdown("""
        **Tipo A: Autenticação de Usuário**

        Conecte sua conta Google para permitir que o sistema acesse seu Google Calendar.
        """)

        user_id = st.text_input("ID do Usuário", value="default_user", key="oauth_user_id")

        if st.button("🔗 Conectar Google"):
            try:
                # Passar user_id como parâmetro
                response = requests.get(
                    f"{BACKEND_URL}/api/auth/google/authorize",
                    params={"user_id": user_id}
                )

                if response.status_code == 200:
                    data = response.json()
                    auth_url = data.get("auth_url")
                    st.markdown(f"""
                    **Clique no link abaixo para autorizar:**

                    [{auth_url}]({auth_url})

                    Após autorizar, você será redirecionado e as credenciais serão salvas automaticamente.

                    **Nota:** Certifique-se de que a URL de redirecionamento no Google Cloud Console está configurada como:
                    `http://localhost:8000/auth/google/callback`
                    """)
                else:
                    st.error(f"Erro ao gerar URL de autorização: {response.text}")
            except Exception as e:
                st.error(f"Erro: {str(e)}")

    with tab2:
        st.subheader("Configurar Chaves de API Estáticas")
        st.markdown("""
        **Tipo B: Autenticação de Sistema**

        Configure chaves de API estáticas para ferramentas do sistema (ex: Slack).
        """)

        tool_name = st.selectbox("Ferramenta", ["slack", "outra"])
        api_key = st.text_input("Chave de API", type="password")

        if st.button("💾 Salvar Chave"):
            if not api_key:
                st.error("Por favor, insira uma chave de API.")
                return

            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/admin/configure-tool",
                    json={
                        "tool_name": tool_name,
                        "tool_type": "system_static",
                        "credentials": {"token": api_key}
                    }
                )

                if response.status_code == 200:
                    st.success(f"✅ Chave de {tool_name} salva com sucesso!")
                else:
                    st.error(f"Erro: {response.text}")
            except Exception as e:
                st.error(f"Erro: {str(e)}")

    with tab3:
        st.subheader("Ferramentas Configuradas")

        try:
            response = requests.get(f"{BACKEND_URL}/api/admin/tools")

            if response.status_code == 200:
                tools = response.json()

                st.markdown("### Ferramentas de Sistema")
                if tools.get("system_tools"):
                    for tool in tools["system_tools"]:
                        st.success(f"✅ {tool}")
                else:
                    st.info("Nenhuma ferramenta de sistema configurada.")

                st.markdown("### Ferramentas de Usuário")
                if tools.get("user_tools"):
                    for user_id, user_tools in tools["user_tools"].items():
                        st.markdown(f"**Usuário: {user_id}**")
                        for tool in user_tools:
                            st.success(f"✅ {tool}")
                else:
                    st.info("Nenhuma ferramenta de usuário configurada.")
            else:
                st.error("Erro ao carregar ferramentas.")
        except Exception as e:
            st.error(f"Erro: {str(e)}")


def show_status_page():
    """Página de status do sistema"""
    st.header("📊 Status do Sistema")

    try:
        response = requests.get(f"{BACKEND_URL}/")

        if response.status_code == 200:
            data = response.json()
            st.success(f"✅ {data.get('message')}")
            st.info(f"Versão: {data.get('version')}")
            st.info(f"Status: {data.get('status')}")
        else:
            st.error("Backend não está respondendo.")
    except requests.exceptions.ConnectionError:
        st.error("❌ Backend não está rodando. Inicie o servidor com: `uvicorn backend.main:app --reload`")
    except Exception as e:
        st.error(f"Erro: {str(e)}")


if __name__ == "__main__":
    main()
