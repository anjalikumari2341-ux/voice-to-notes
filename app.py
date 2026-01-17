import streamlit as st
from dotenv import load_dotenv
from text_utils import (
    extract_text_from_youtube,
    extract_text_from_pdf,
    groq_whisper_transcribe_audio,
    generate_mcqs_safe,
    generate_notes_safe,
    generate_flashcards_safe
)
from pdf_utils import save_pdf

load_dotenv()

st.set_page_config(
    page_title="Lecture Voice-to-Notes (Groq)",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Lecture Voice-to-Notes Generator")
st.caption("Groq LLaMA + Whisper | Works even without captions")

# -------------------------
# INPUT SELECTION
# -------------------------
input_type = st.selectbox(
    "Choose Input Type",
    ["YouTube Link", "Audio File", "PDF File"]
)

content = ""

# -------------------------
# YOUTUBE INPUT
# -------------------------
if input_type == "YouTube Link":
    video_input = st.text_input("Enter YouTube URL or ID")
    if video_input:
        with st.spinner("Processing video..."):
            content = extract_text_from_youtube(video_input)
        if not content:
            st.error("Failed to extract text from the video.")

# -------------------------
# AUDIO FILE INPUT
# -------------------------
elif input_type == "Audio File":
    audio_file = st.file_uploader("Upload Audio File", type=["mp3", "wav", "m4a"])
    if audio_file:
        with st.spinner("Transcribing audio..."):
            content = groq_whisper_transcribe_audio(audio_file)
        if not content:
            st.error("Failed to transcribe audio.")

# -------------------------
# PDF FILE INPUT
# -------------------------
elif input_type == "PDF File":
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

    if pdf_file:

        # =========================
        # PDF SIZE CHECK
        # =========================
        pdf_size_mb = pdf_file.size / (1024 * 1024)

        if pdf_size_mb > 18:
            st.error("❌ PDF is too large to transcribe. Please upload a smaller file.")
            st.stop()

        # =========================
        # SAFE EXTRACTION
        # =========================
        try:
            content = extract_text_from_pdf(pdf_file)

        except ValueError as e:
            if "PDF_TOO_LARGE" in str(e):
                st.error("❌ PDF is too large to transcribe. Please upload a smaller file.")
                st.stop()

        # =========================
        # EMPTY CONTENT CHECK
        # =========================
        if not content:
            st.error("Failed to extract text from PDF.")


# -------------------------
# MAIN ACTION: GENERATE MATERIAL
# -------------------------
if st.button("🚀 Generate Study Material"):
    if not content or len(content) < 50:
        st.warning("Not enough content to generate study material.")
    else:

        # =========================
        # FINAL SAFETY CHECK
        # =========================
       
        MAX_SAFE_CHARS = 20_000   # ≈ 5,000 tokens

        if len(content) > MAX_SAFE_CHARS:
            st.error(
                "❌ PDF is too large to process with the free Groq tier.\n\n"
                "Please upload a smaller PDF or split it into parts."
    )
            st.stop()




        # =========================
        # LLM GENERATION
        # =========================
        with st.spinner("Generating Notes..."):
            notes = generate_notes_safe(content)

        with st.spinner("Generating MCQs..."):
            mcqs = generate_mcqs_safe(content)

        with st.spinner("Generating Flashcards..."):
            flashcards = generate_flashcards_safe(content)

        # -------------------------
        # DISPLAY RESULTS
        # -------------------------
        st.subheader("📝 Study Notes")
        st.markdown(notes)

        st.subheader("❓ MCQs")
        st.markdown(mcqs)

        st.subheader("🧠 Flashcards")
        st.markdown(flashcards)

        # -------------------------
        # SAVE PDFs
        # -------------------------
        notes_pdf = save_pdf("Notes.pdf", notes)
        mcqs_pdf = save_pdf("MCQs.pdf", mcqs)
        flashcards_pdf = save_pdf("Flashcards.pdf", flashcards)

        # -------------------------
        # DOWNLOAD BUTTONS
        # -------------------------
        col1, col2, col3 = st.columns(3)

        with col1:
            with open(notes_pdf, "rb") as f:
                st.download_button("📄 Download Notes", f, "Notes.pdf")

        with col2:
            with open(mcqs_pdf, "rb") as f:
                st.download_button("📄 Download MCQs", f, "MCQs.pdf")

        with col3:
            with open(flashcards_pdf, "rb") as f:
                st.download_button("📄 Download Flashcards", f, "Flashcards.pdf")

