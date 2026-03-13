import streamlit as st
import difflib
import random
import time
from fpdf import FPDF

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="EduTyping Pro v3.3", page_icon="🎓", layout="wide")

# --- BANCO DE DADOS LOCAL (TRADUÇÕES PRONTAS) ---
# Aqui não usamos internet, por isso o erro de IP desaparece.
BANCO_DADOS = {
    "🌱 Iniciante": [
        {"pt": "O céu é azul.", "en": "The sky is blue.", "es": "El cielo es azul."},
        {"pt": "Eu gosto de maçã.", "en": "I like apple.", "es": "Me gusta la manzana."},
        {"pt": "Bom dia para todos.", "en": "Good morning to everyone.", "es": "Buenos días a todos."},
        {"pt": "O gato dorme.", "en": "The cat sleeps.", "es": "El gato duerme."}
    ],
    "🚀 Intermediário": [
        {"pt": "A biblioteca é um lugar calmo.", "en": "The library is a quiet place.", "es": "La biblioteca es un lugar tranquilo."},
        {"pt": "Nós aprendemos Python na escola.", "en": "We learn Python at school.", "es": "Aprendemos Python en la escuela."},
        {"pt": "A tecnologia ajuda as pessoas.", "en": "Technology helps people.", "es": "La tecnología ajuda a las personas."}
    ],
    "🏆 Avançado": [
        {"pt": "A prática leva à perfeição.", "en": "Practice leads to perfection.", "es": "La práctica lleva a la perfección."},
        {"pt": "A educação transforma vidas.", "en": "Education transforms lives.", "es": "La educación transforma vidas."},
        {"pt": "O conhecimento é poder.", "en": "Knowledge is power.", "es": "El conocimiento es poder."}
    ]
}

# --- FUNÇÕES ---
def analisar_erros(tentativa, correto):
    resultado_visual = []
    erros_digitacao = 0
    # Compara strings ignorando espaços extras no início/fim
    t = tentativa.lower().strip()
    c = correto.lower().strip()
    for s in difflib.ndiff(t, c):
        if s[0] == ' ': resultado_visual.append(s[-1])
        elif s[0] == '-': 
            resultado_visual.append(f"~~{s[-1]}~~")
            erros_digitacao += 1
        elif s[0] == '+': 
            resultado_visual.append(f"**{s[-1]}**")
            erros_digitacao += 1
    return "".join(resultado_visual), erros_digitacao

def tocar_som_sucesso():
    audio_url = "https://www.soundjay.com/buttons/sounds/button-09.mp3"
    st.markdown(f'<audio autoplay><source src="{audio_url}" type="audio/mp3"></audio>', unsafe_allow_html=True)

def gerar_pdf(nome, pontos, wpm, precisao, erros):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 20, "RELATORIO EDUTYPING PRO", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Aluno: {nome}", ln=True)
    pdf.cell(0, 10, f"Pontuacao: {pontos}", ln=True)
    pdf.cell(0, 10, f"Velocidade: {wpm} WPM", ln=True)
    pdf.cell(0, 10, f"Erros Totais: {erros}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- ESTADO DO SISTEMA ---
if 'pontos' not in st.session_state: st.session_state.pontos = 0
if 'erros_totais' not in st.session_state: st.session_state.erros_totais = 0
if 'wpm_max' not in st.session_state: st.session_state.wpm_max = 0
if 'item_atual' not in st.session_state:
    st.session_state.item_atual = random.choice(BANCO_DADOS["🌱 Iniciante"])
    st.session_state.tempo_inicio = time.time()

# --- SIDEBAR ---
with st.sidebar:
    st.title("🎓 Painel Escola")
    st.metric("Meus Pontos", st.session_state.pontos)
    nivel = st.select_slider("Nível:", options=list(BANCO_DADOS.keys()))
    idioma = st.radio("Idioma Alvo:", ["Inglês", "Espanhol"])
    lang_key = 'en' if idioma == "Inglês" else 'es'
    
    if st.button("🔄 Próxima Frase"):
        st.session_state.item_atual = random.choice(BANCO_DADOS[nivel])
        st.session_state.tempo_inicio = time.time()
        st.rerun()

# --- INTERFACE ---
st.title("⌨️ EduTyping Pro")
st.markdown(f"### TRADUZA PARA {idioma.upper()}:")
st.info(f"**{st.session_state.item_atual['pt']}**")

tentativa = st.text_input("Sua resposta:", key="input_clean")

if tentativa:
    correto = st.session_state.item_atual[lang_key]
    visual, erros = analisar_erros(tentativa, correto)
    
    tempo = time.time() - st.session_state.tempo_inicio
    wpm = int((len(tentativa.split()) / (tempo/60))) if tempo > 0 else 0
    precisao = int(difflib.SequenceMatcher(None, tentativa.lower().strip(), correto.lower().strip()).ratio() * 100)
    
    st.session_state.erros_totais += erros
    if wpm > st.session_state.wpm_max: st.session_state.wpm_max = wpm

    c1, c2 = st.columns(2)
    c1.metric("Precisão", f"{precisao}%")
    c2.metric("Velocidade", f"{wpm} WPM")
    
    if precisao == 100:
        st.balloons()
        tocar_som_sucesso()
        st.success("Perfeito!")
        if st.button("Confirmar e Continuar"):
            st.session_state.pontos += 10
            st.session_state.item_atual = random.choice(BANCO_DADOS[nivel])
            st.session_state.tempo_inicio = time.time()
            st.rerun()
    else:
        st.markdown(f"**Análise:** {visual}")
        st.caption(f"Dica: {correto}")

# --- PDF ---
st.divider()
nome_aluno = st.text_input("Nome para o PDF:")
if st.button("Gerar Relatório"):
    if nome_aluno:
        pdf = gerar_pdf(nome_aluno, st.session_state.pontos, st.session_state.wpm_max, 100, st.session_state.erros_totais)
        st.download_button("Download PDF", pdf, "relatorio.pdf", "application/pdf")
