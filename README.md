# LinkedIn PDF Resume Generator



This project is a FastAPI-based web application that generates an HTML resume from a PDF downloaded from LinkedIn. The application takes in a PDF as input, extracts the text, and uses the OpenAI API to structure the extracted information into a resume format, which is then rendered in an HTML page.



## Problem Statement



The task is to create a web application that generates a structured HTML resume using a LinkedIn PDF as input. The user will upload the PDF, and an OpenAI API key will be provided for the application to generate the resume data.



### Inputs:

- A PDF file downloaded from LinkedIn.

- An OpenAI API key provided via a form.


### Outputs:

- An HTML file that displays a structured resume.


## Approach


The solution can be divided into multiple steps:



### 1. **Setting Up the FastAPI Application**

   - **FastAPI** is used as the framework to build the web application due to its simplicity and efficiency.

   - We have two routes:

     - A `GET` route (`/`) that renders a page where the user can upload a PDF file and enter their OpenAI API key.

     - A `POST` route (`/generate_resume/`) that handles the PDF file upload, processes the file, and generates the resume.



### 2. **Extracting Text from the PDF**

   - We use the **PyPDF2** library to extract raw text from the uploaded PDF. The text extraction logic involves reading the file in binary format and iterating through its pages to get the text content.

   - This extracted text is then passed to the OpenAI API to structure it into a resume.



### 3. **Generating Structured Resume Data using OpenAI**

   - After extracting the text from the PDF, we use the **OpenAI API** to process the text and generate a structured resume in JSON format.

   - We define a prompt that instructs the AI to output a JSON object containing fields such as:

     - `name`

     - `email`

     - `contact`

     - `top_skills`

     - `certifications`

     - `honors_awards`

     - `summary`

     - `experience`

     - `education`

   - The application dynamically fills these fields based on the user's LinkedIn PDF content.

   

### 4. **Rendering the Resume**

   - Once we receive the structured resume data in JSON format, the application renders it into an HTML format using **Jinja2 templates**.

   - The resume is displayed to the user as a structured and styled HTML page.




## Installation & Setup



### Requirements

- **Python 3.8+**

- **OpenAI Python SDK** to interact with OpenAI's GPT model.




### Environment Setup


1. **Clone the repository**:
   
    ```
    git clone https://github.com/tarun-hegde/gen-html-resume.git  
    cd gen-html-resume
    ```

2.  **Create a virtual environment and activate it**
   
    ```
    python3 -m venv env
    source env/bin/activate
    ```
    
3. **Install the required packages**:

    ```
    pip install -r requirements.txt
    ```


4. **Run the FastAPI application**:

    ```
    uvicorn app:app --reload
    ```



5. Visit `http://localhost:8000/` in your browser to access the web interface.



## Usage

1. Upload the LinkedIn PDF file.

2. Enter your OpenAI API key when prompted.

3. Click the upload button to generate and view the HTML resume.




