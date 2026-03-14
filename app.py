import streamlit as st
import difflib
import random
import time
from fpdf import FPDF

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="EduTyping Pro v3.3", page_icon="🎓", layout="wide")

# --- BANCO DE DADOS LOCAL (TRADUÇÕES PRONTAS) ---
# Aqui os dados ficam guardados no código, eliminando erros de conexão.
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
    t = tentativa.lower().strip()
    c = correto.lower().strip()
    for s in difflib.ndiff(t, c):
        if s[0] == ' ': 
            resultado_visual.append(s[-1])
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
    pdf.cell(0, 10, f"Pontuacao Total: {pontos}", ln=True)
    pdf.cell(0, 10, f"Velocidade: {wpm} WPM", ln=True)
    pdf.cell(0, 10, f"Erros Acumulados: {erros}", ln=True)
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "Documento gerado pelo sistema EduTyping Escola.", align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- ESTADO DO SISTEMA ---
if 'pontos' not in st.session_state: st.session_state.pontos = 0
if 'erros_totais' not in st.session_state: st.session_state.erros_totais = 0
if 'wpm_max' not in st.session_state: st.session_state.wpm_max = 0
if 'item_atual' not in st.session_state:
    st.session_state.item_atual = random.choice(BANCO_DADOS["🌱 Iniciante"])
    st.session_state.tempo_inicio = time.time()

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🎓 Painel Escola")
    st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=80)
    st.metric("Pontuação", st.session_state.pontos)
    nivel = st.select_slider("Dificuldade:", options=list(BANCO_DADOS.keys()))
    idioma = st.radio("Traduzir para:", ["Inglês", "Espanhol"])
    lang_key = 'en' if idioma == "Inglês" else 'es'
    
    if st.button("🔄 Nova Frase / Reset"):
        st.session_state.item_atual = random.choice(BANCO_DADOS[nivel])
        st.session_state.tempo_inicio = time.time()
        st.rerun()

# --- INTERFACE PRINCIPAL ---
st.title("⌨️ EduTyping Pro")
st.markdown(f"### TRADUZA PARA {idioma.upper()}:")
st.info(f"**{st.session_state.item_atual['pt']}**")

tentativa = st.text_input("Escreva sua resposta e tecle ENTER:", key="input_blindado")

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
        st.success("🎯 Sensacional! 100% de acerto.")
        if st.button("Coletar Pontos (+10)"):
            st.session_state.pontos += 10
            st.session_state.item_atual = random.choice(BANCO_DADOS[nivel])
            st.session_state.tempo_inicio = time.time()
            st.rerun()
    else:
        st.markdown(f"**Análise detalhada:** {visual}")
        st.caption(f"Dica: A resposta correta era: {correto}")

# --- GERAR RELATÓRIO ---
st.divider()
with st.expander("📄 Gerar Relatório Final"):
    nome_aluno = st.text_input("Nome do Aluno:")
    if st.button("Criar PDF"):
        if nome_aluno:
            pdf_out = gerar_pdf(nome_aluno, st.session_state.pontos, st.session_state.wpm_max, 100, st.session_state.erros_totais)
            st.download_button("📥 Baixar Relatório", pdf_out, f"Relatorio_{nome_aluno}.pdf", "application/pdf")
        else:
            st.warning("Insira o nome para gerar o PDF.")