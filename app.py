from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import openai
import PyPDF2
import io
from dotenv import load_dotenv
import os
import re
import json
import yaml

app = FastAPI()

# Load environment variables from .env file
load_dotenv()


templates = Jinja2Templates(directory="templates")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_bytes):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


# Function to generate HTML resume using OpenAI
def generate_resume_data(text,api_key):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Generate a structured resume from the following text, and give it in a JSON format with keys as name, email, contact, top_skills, certifications, honors_awards, summary, experience, education: {text}"}
        ]
    )
    generated_text = response.choices[0].message['content']
    if not generated_text.strip():
        print("Error: Empty response from OpenAI")
        return None
    try:
        # Remove triple backticks if present
        if generated_text.startswith("```json") and generated_text.endswith("```"):
            generated_text = generated_text[7:-3].strip()
        elif generated_text.startswith("```") and generated_text.endswith("```"):
            generated_text = generated_text[3:-3].strip()
        print(generated_text)
        resume_data = json.loads(generated_text)
        return resume_data
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        return None

# Route to render upload page
@app.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# Route to handle PDF upload and resume generation
@app.post("/generate_resume/", response_class=HTMLResponse)
async def generate_resume(request: Request, file: UploadFile = File(...),api_key: str = Form(...)):
    contents = await file.read()
    extracted_text = extract_text_from_pdf(contents)
    
    # Generate structured resume data
    resume_data = generate_resume_data(extracted_text,api_key)
    if resume_data is None:
        return HTMLResponse(content="Error generating resume data", status_code=500)
    print(resume_data)
    
    # Render the resume in HTML using Jinja2 template
    return templates.TemplateResponse("resume.html", {"request": request, "resume_data": resume_data})