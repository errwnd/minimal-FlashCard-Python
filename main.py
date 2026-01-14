import os
import tempfile

import PyPDF2
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.post("/upload")
async def upload(file: UploadFile = File(...), api_key: str = Form(None)):
    # Use provided API key or fall back to environment variable
    key = api_key or API_KEY
    if not key:
        return {"error": "API key is required"}

    # Save uploaded PDF to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Extract text from PDF
    text = ""
    with open(tmp_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""

    if not text.strip():
        return {"error": "No text found in PDF"}

    # Generate flashcards using Gemini
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=key)

    prompt = f"""Create 20 simple flashcards from this text.
Format each as: Q: question | A: answer
One flashcard per line. Keep it simple.

Text:
{text[:15000]}"""

    response = llm.invoke(prompt)

    # Parsing flashcards
    cards = []
    for line in response.content.split("\n"):
        if "Q:" in line and "A:" in line:
            cards.append(line.strip())

    return {"cards": cards}
