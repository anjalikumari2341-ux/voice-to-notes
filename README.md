# 🎓 Lecture Voice-to-Notes Generator

A **Streamlit-based AI application** that converts lectures and documents into structured **study material** — including **notes, MCQs, and flashcards** — using **Groq LLaMA** and **Whisper**.

---

## 🚀 Features

✅ Generate structured study notes  
✅ Automatically create MCQs  
✅ Create flashcards for revision  
✅ Supports multiple input formats  
✅ Built-in file size & token safety  
✅ Works smoothly on Streamlit Cloud  

---

## 📥 Supported Input Types

| Input Type | Description |
|-----------|-------------|
| 📺 YouTube Link | Uses captions or Whisper fallback |
| 🎧 Audio File | MP3, WAV, M4A transcription |
| 📄 PDF File | Safe text extraction with limits |

---

## 🧠 AI Models Used

- **Groq LLaMA 3.1 – 8B Instant**
- **Groq Whisper Large v3**

---

## 🛡️ Safety & Stability Features

This project includes **production-level protections**:

- ✅ PDF size limit
- ✅ Extracted text length limit
- ✅ Token overflow prevention
- ✅ Groq TPM (6000 tokens) protection
- ✅ Graceful error handling
- ✅ No crashes on large files

If a file is too large, the app displays:

PDF is too large to transcribe.
Please upload a smaller file.

---

## 🗂️ Project Structure

Voice_to_Notes/
│
├── app.py
├── text_utils.py
├── llm_utils.py
├── pdf_utils.py
├── .env
├── README.md


---

## ⚙️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/voice-to-notes.git
cd voice-to-notes

2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate

3️⃣ Install dependencies
pip install streamlit
pip install groq
pip install python-dotenv
pip install yt-dlp
pip install youtube-transcript-api
pip install PyPDF2
pip install reportlab

4️⃣ Create .env file
GROQ_API_KEY=your_groq_api_key_here

▶️ Run the app
streamlit run app.py

👩‍💻 Author

Anjali Kumari
Project — AI & Machine Learning

