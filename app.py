import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard OJM 3 Zona", layout="wide", page_icon="🔒")

# ================== PASSWORD ==================
# SENHA - Troca aqui pela senha que queres partilhar com a equipa
PASSWORD_CORRETA = "OJM2026"  # <--- TROCA AQUI

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 Acesso Restrito - Dashboard OJM 3ª Zona")
        st.write("Digite a senha para entrar")
        pwd = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            # No Streamlit Cloud, usa secrets se existir
            try:
                senha_secrets = st.secrets["password"]
            except:
                senha_secrets = PASSWORD_CORRETA

            if pwd == senha_secrets:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        return False
    return True

if not check_password():
    st.stop()
# ================== FIM PASSWORD ==================

st.title("👥 Dashboard - Registo de Membros OJM - 3ª Zona")
st.sidebar.success("✅ Logado")
if st.sidebar.button("Sair"):
    st.session_state.authenticated = False
    st.rerun()

# --- Resto do código ---
@st.cache_data
def load_default():
    try:
        df = pd.read_excel("FICHA_DE_REGISTO_OS_OJM.xlsx")
        return df
    except:
        return pd.DataFrame()

df_default = load_default()
uploaded = st.sidebar.file_uploader("Carrega novo Excel", type=["xlsx","xls","csv"])

if uploaded:
    df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
else:
    df = df_default

if df.empty:
    st.warning("Carrega o ficheiro Excel")
    st.stop()

if 'Sexo' in df.columns:
    df['Sexo'] = df['Sexo'].astype(str).str.lower().str.strip()
if 'Tem_Cartao_da_OJM' in df.columns:
    df['Tem_Cartao_da_OJM'] = df['Tem_Cartao_da_OJM'].astype(str).str.lower().str.strip()
if 'Idade' in df.columns:
    df['Idade'] = pd.to_numeric(df['Idade'], errors='coerce')
    df = df[df['Idade'] < 100]

st.sidebar.subheader("Filtros")
circulos = st.sidebar.multiselect("Círculo", sorted(df['Circulo'].dropna().unique()) if 'Circulo' in df else [])
df_filt = df[df['Circulo'].isin(circulos)] if circulos else df

c1,c2,c3,c4 = st.columns(4)
c1.metric("Total", len(df_filt))
c2.metric("Masculino", len(df_filt[df_filt['Sexo']=='masculino']) if 'Sexo' in df_filt else 0)
c3.metric("Feminino", len(df_filt[df_filt['Sexo']=='feminino']) if 'Sexo' in df_filt else 0)
c4.metric("Com Cartão", len(df_filt[df_filt['Tem_Cartao_da_OJM']=='sim']) if 'Tem_Cartao_da_OJM' in df_filt else 0)

col1, col2 = st.columns(2)
with col1:
    if 'Sexo' in df_filt:
        st.plotly_chart(px.pie(df_filt, names='Sexo', title='Por Sexo', hole=0.4), use_container_width=True)
    if 'Circulo' in df_filt:
        df_c = df_filt['Circulo'].value_counts().reset_index()
        df_c.columns=['Circulo','Total']
        st.plotly_chart(px.bar(df_c, x='Circulo', y='Total', title='Por Círculo', text_auto=True), use_container_width=True)
with col2:
    if 'Funcao' in df_filt:
        df_f = df_filt['Funcao'].value_counts().reset_index()
        df_f.columns=['Funcao','Total']
        st.plotly_chart(px.bar(df_f, x='Total', y='Funcao', orientation='h', title='Por Função'), use_container_width=True)
    if 'Nivel_Academico' in df_filt:
        st.plotly_chart(px.pie(df_filt, names='Nivel_Academico', title='Nível Académico'), use_container_width=True)

st.dataframe(df_filt, use_container_width=True)
