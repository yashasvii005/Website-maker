# backend/main.py
import os
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables (GEMINI_API_KEY)
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize FastAPI app
app = FastAPI()

# Allow cross-origin requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for the request body
class WebsiteRequest(BaseModel):
    prompt: str

@app.post("/generate-website")
async def generate_website_handler(request: WebsiteRequest):
    """
    Receives a user prompt and uses the Gemini API to generate a complete,
    functional, single-file HTML website.
    """
    print(f"Received prompt: {request.prompt}")

    # Create a detailed prompt for the AI model
    system_prompt = """
    You are an expert web developer AI. Your task is to generate a complete, functional, and visually appealing website based on a user's prompt.

    You MUST follow these rules:
    1.  Generate a SINGLE HTML file.
    2.  ALL CSS must be included inside a `<style>` tag in the `<head>`. Do not link to external stylesheets.
    3.  ALL JavaScript must be included inside a `<script>` tag at the end of the `<body>`. Do not link to external scripts.
    4.  The website must be fully functional. If the user asks for a button, it should have a JavaScript function attached to it. If they ask for a form, it should have basic validation.
    5.  Use modern and clean design principles. Use placeholder text and images where appropriate.
    6.  The code must be complete and ready to be saved into an .html file and opened in a browser.
    7.  Do not include any explanations, comments, or markdown formatting like ```html. Only output the raw HTML code.
    """

    # Call the Gemini API
    try:
        # FIX: Updated the model name to a current, valid model
        model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=system_prompt
        )
        response = await model.generate_content_async(request.prompt)
        
        generated_code = response.text.strip()
        
        # Clean up the response to ensure it's just raw HTML
        if generated_code.startswith("```html"):
            generated_code = generated_code[7:]
        if generated_code.endswith("```"):
            generated_code = generated_code[:-3]

        print("✅ Website code generated successfully.")
        return {"code": generated_code.strip()}

    except Exception as e:
        print(f"❌ Error generating website: {e}")
        return {"error": "Failed to generate website code."}


@app.get("/")
def read_root():
    return {"message": "AI Website Generator API is running."}
