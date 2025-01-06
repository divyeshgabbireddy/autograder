# Automated Test Grader

A web application that automatically grades student tests using OpenAI's GPT-4 Vision API. Upload a completed test PDF and answer key/rubric PDF to receive detailed grading results.

## Features
- Automatic grading of:
  - Multiple choice questions
  - True/False questions
  - Short answer responses
- Section-by-section scoring
- Detailed feedback for each question
- Total score calculation
- Clean web interface for PDF uploads

## Prerequisites
- Python 3.x
- pip (Python package installer)
- Poppler (for PDF processing)
  - Mac: `brew install poppler`
  - Ubuntu: `sudo apt-get install poppler-utils`
  - Windows: Download from [poppler releases](http://blog.alivate.com.au/poppler-windows/)

## Installation

1. Clone this repository:

bash

git clone https://github.com/yourusername/autograder.git

cd autograder

2. Install required Python packages:

bash

pip install flask openai pdf2image python-dotenv

3. Replace the API key in `main.py`:
   - Open `main.py`
   - Find the line: `api_key = "your-api-key-here"`
   - Replace with your OpenAI API key (get one at https://platform.openai.com/)

## Usage

1. Start the application:

bash

python app.py

2. Open your web browser and go to: http://127.0.0.1:5000

3. Upload your files:
   - Select a completed test PDF
   - Select the corresponding answer key/rubric PDF
   - Click "Grade Test"

4. View the results:
   - Section scores
   - Individual question feedback
   - Total score and percentage

## Important Notes
- You need an OpenAI API key with access to GPT-4 Vision
- Ensure you have sufficient API credits
- Keep your API key private
- PDFs should be clear and readable
- Multiple choice questions should have clearly marked answers

## Troubleshooting
- If you see "API key not valid" error: Make sure you've replaced the placeholder API key
- If PDFs don't upload: Check that you have Poppler installed correctly
- If grading seems incorrect: Ensure PDFs are clear and properly scanned

## Contributing
Feel free to open issues or submit pull requests if you have suggestions for improvements.
