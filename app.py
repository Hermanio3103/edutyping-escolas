import streamlit as st
from deep_translator import GoogleTranslator, MyMemoryTranslator
import difflib
import random
import time
from fpdf import FPDF

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="EduTyping Pro v3.1", page_icon="🎓", layout="wide")

# --- FUNÇÕES DE LÓGICA ---

def traduzir_texto(texto, destino='en'):
    """Tenta traduzir usando Google, se falhar por IP, tenta MyMemory (Grátis)"""
    try:
        # Tentativa 1: Google
        return GoogleTranslator(source='auto', target=destino).translate(texto)
    except Exception:
        try:
            # Tentativa 2: MyMemory (Reserva para erro de IP)
            return MyMemoryTranslator(source='pt-BR', target=destino).translate(texto)
        except:
            return "Erro: O servidor de tradução bloqueou o acesso temporariamente."

def analisar_erros(tentativa, correto):
    resultado_visual = []
    erros_digitacao = 0
    for s in difflib.ndiff(tentativa, correto):
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

def gerar_pdf(nome, pontos, wpm, precisao, erros_acumulados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(33, 150, 243) 
    pdf.cell(0, 20, "RELATÓRIO DE DESEMPENHO", ln=True, align='C')
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Plataforma EduTyping Pro", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Aluno(a): {nome}", ln=True)
    pdf.cell(0, 10, f"Data: {time.strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Métricas da Sessão:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"- Pontuação Acumulada: {pontos} pontos", ln=True)
    pdf.cell(0, 10, f"- Velocidade Máxima: {wpm} WPM", ln=True)
    pdf.cell(0, 10, f"- Precisão Média: {precisao}%", ln=True)
    pdf.cell(0, 10, f"- Total de Erros Detectados: {erros_acumulados}", ln=True)
    pdf.ln(40)
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(0, 10, "Documento gerado automaticamente pelo Sistema EduTyping Pro.", align='C')
    return pdf.output(dest='S').encode('latin-1')

# --- BANCO DE FRASES ---
BANCO = {
    "🌱 Iniciante": ["O céu é azul.", "Eu gosto de maçã.", "Bom dia para todos.", "O gato dorme."],
    "🚀 Intermediário": ["A biblioteca é um lugar calmo.", "Nós aprendemos Python na escola.", "A tecnologia ajuda as pessoas."],
    "🏆 Avançado": ["A prática constante leva à perfeição técnica.", "Traduzir requer entender o contexto cultural.", "A educação transforma vidas e sociedades."]
}

# --- INICIALIZAÇÃO ---
if 'pontos' not in st.session_state: st.session_state.pontos = 0
if 'erros_totais' not in st.session_state: st.session_state.erros_totais = 0
if 'wpm_maximo' not in st.session_state: st.session_state.wpm_maximo = 0
if 'ultima_precisao' not in st.session_state: st.session_state.ultima_precisao = 0
if 'frase_atual' not in st.session_state: 
    st.session_state.frase_atual = random.choice(BANCO["🌱 Iniciante"])
    st.session_state.tempo_inicio = time.time()

# --- SIDEBAR ---
with st.sidebar:
    st.title("🎓 Área do Aluno")
    st.metric("Sua Pontuação", f"{st.session_state.pontos} pts")
    nivel_escolhido = st.select_slider("Dificuldade:", options=list(BANCO.keys()))
    idioma_nome = st.selectbox("Idioma do Treino:", ["Inglês (en)", "Espanhol (es)", "Francês (fr)"])
    sigla = idioma_nome.split('(')[1].replace(')', '')
    if st.button("🔄 Próxima Frase / Reset"):
        st.session_state.frase_atual = random.choice(BANCO[nivel_escolhido])
        st.session_state.tempo_inicio = time.time()
        st.rerun()

# --- INTERFACE PRINCIPAL ---
st.title("⌨️ EduTyping Pro")
st.markdown("---")

col_desafio, col_stats = st.columns([2, 1])

with col_desafio:
    st.subheader("Desafio de Escrita")
    st.info(f"**Traduza:** {st.session_state.frase_atual}")
    tentativa = st.text_input("Digite sua tradução e tecle ENTER:", placeholder="Escreva aqui...")

with col_stats:
    st.subheader("Métricas")
    if tentativa:
        correto = traduzir_texto(st.session_state.frase_atual, destino=sigla)
        visual_diff, erros_na_frase = analisar_erros(tentativa, correto)
        tempo_total = time.time() - st.session_state.tempo_inicio
        wpm = int((len(tentativa.split()) / (tempo_total/60))) if tempo_total > 0 else 0
        match = difflib.SequenceMatcher(None, tentativa.lower().strip(), correto.lower().strip())
        precisao = int(match.ratio() * 100)
        st.session_state.ultima_precisao = precisao
        st.session_state.erros_totais += erros_na_frase
        if wpm > st.session_state.wpm_maximo: st.session_state.wpm_maximo = wpm
        st.metric("Velocidade", f"{wpm} WPM")
        st.metric("Precisão", f"{precisao}%")
        st.progress(precisao / 100)

if tentativa:
    st.divider()
    if precisao == 100:
        st.balloons()
        tocar_som_sucesso()
        st.success("🏆 **Incrível! Tradução 100% correta.**")
        if st.button("Coletar Pontos (+20)"):
            st.session_state.pontos += 20
            st.session_state.frase_atual = random.choice(BANCO[nivel_escolhido])
            st.session_state.tempo_inicio = time.time()
            st.rerun()
    else:
        st.error(f"Detectamos {erros_na_frase} erro(s):")
        st.markdown(f"### {visual_diff}")
        st.info(f"Dica (Oficial): {correto}")

st.markdown("---")
with st.expander("📄 Gerar Relatório para o Professor"):
    nome_pdf = st.text_input("Seu Nome Completo:")
    if st.button("Criar PDF Oficial"):
        if nome_pdf:
            pdf_bytes = gerar_pdf(nome_pdf, st.session_state.pontos, st.session_state.wpm_maximo, st.session_state.ultima_precisao, st.session_state.erros_totais)
            st.download_button("📥 Baixar PDF", pdf_bytes, f"Certificado_{nome_pdf}.pdf", "application/pdf")