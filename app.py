import os
import io
import json
import openai
import PyPDF2
import logging
from fastapi import FastAPI, File, UploadFile, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from openai.error import AuthenticationError

app = FastAPI()

# Load environment variables from .env file
load_dotenv()

templates = Jinja2Templates(directory="templates")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_bytes):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        if not text.strip():
            raise ValueError("The PDF file is empty or contains no extractable text.")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise ValueError("Invalid PDF file. Please upload a valid LinkedIn PDF.")

# Function to generate HTML resume using OpenAI
def generate_resume_data(text, api_key):
    try:
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
            raise ValueError("Received empty response from OpenAI API.")
        try:
            if generated_text.startswith("```json") and generated_text.endswith("```"):
                generated_text = generated_text[7:-3].strip()
            elif generated_text.startswith("```") and generated_text.endswith("```"):
                generated_text = generated_text[3:-3].strip()
            resume_data = json.loads(generated_text)
            return resume_data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response from OpenAI: {e}")
            raise ValueError("Received invalid JSON response from OpenAI API.")
    except AuthenticationError as e:
        logger.error(f"AuthenticationError: {e}")
        raise ValueError("Invalid OpenAI API key. Please enter a correct API key.")
    except Exception as e:
        logger.error(f"Error generating resume data using OpenAI: {e}")
        raise ValueError("Failed to generate resume data using OpenAI API.")

# Route to render upload page
@app.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# Route to handle PDF upload and resume generation
@app.post("/generate_resume/", response_class=HTMLResponse)
async def generate_resume(request: Request, file: UploadFile = File(...), api_key: str = Form(...)):
    logger.info("Received request to generate resume")
    try:
        contents = await file.read()
        logger.info("PDF file read successfully")
        extracted_text = extract_text_from_pdf(contents)
        logger.info("Extracted text from PDF")
        
        # Generate structured resume data
        resume_data = generate_resume_data(extracted_text, api_key)
        if resume_data is None:
            logger.error("Error generating resume data")
            raise HTTPException(status_code=500, detail="Error generating resume data")
        logger.info("Resume data generated successfully")
        
        # Render the resume in HTML using Jinja2 template
        return templates.TemplateResponse("resume.html", {"request": request, "resume_data": resume_data})
    except ValueError as e:
        logger.error(f"ValueError: {e}")
        return templates.TemplateResponse("upload.html", {"request": request, "error_message": str(e)})
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return HTMLResponse(content="An internal error occurred", status_code=500)