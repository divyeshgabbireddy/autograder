import os
import base64
from openai import OpenAI
from pdf2image import convert_from_path
import tempfile
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key 
api_key="your-api-key-here"

if not api_key:
    raise ValueError("No OpenAI API key found. Please check your .env file.")

client = OpenAI(api_key=api_key)

def encode_image(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def convert_pdf_to_images(pdf_path):
    """Convert PDF to images and save them temporarily."""
    print(f"Converting PDF: {pdf_path}")
    temp_dir = tempfile.mkdtemp()
    images = convert_from_path(pdf_path)
    image_paths = []
    
    for i, image in enumerate(images):
        path = os.path.join(temp_dir, f'page_{i}.jpg')
        image.save(path, 'JPEG')
        image_paths.append(path)
    
    print(f"Converted {len(image_paths)} pages")
    return image_paths

def grade_test(test_images, rubric_images):
    """Grade the entire test using all images at once."""
    print("\nAnalyzing test and rubric...")
    
    # First, analyze the rubric
    print("Analyzing rubric first...")
    rubric_content = [
        {
            "type": "text",
            "text": """Carefully analyze this answer key/rubric. For each section:
            1. Multiple Choice Section:
                - Note all question numbers
                - Record correct answers (A,B,C,D)
                - Note point values
            2. True/False Section:
                - Note all question numbers
                - Record correct answers
                - Note point values
            3. Short Answer Section:
                - Note all question numbers
                - Record expected answers
                - Note point values and grading criteria
            
            Respond with 'UNDERSTOOD' once you've analyzed the complete rubric."""
        }
    ]
    
    for img_path in rubric_images:
        rubric_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{encode_image(img_path)}"}
        })
    
    rubric_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": rubric_content}],
        max_tokens=1000
    )
    
    print("Rubric response:", rubric_response.choices[0].message.content)
    
    # Now grade the test
    print("\nGrading student test...")
    content = [
        {
            "type": "text",
            "text": """Grade this test section by section using the rubric you analyzed. You MUST respond in this exact JSON format:
            {
                "sections": [
                    {
                        "name": "Multiple Choice",
                        "questions": [
                            {
                                "number": "1.1",
                                "student_answer": "B",
                                "correct_answer": "C",
                                "points_earned": 0,
                                "points_possible": 1,
                                "feedback": "Incorrect. Selected B, correct is C."
                            }
                        ]
                    },
                    {
                        "name": "True/False",
                        "questions": []
                    },
                    {
                        "name": "Short Answer",
                        "questions": []
                    }
                ],
                "total_score": 0,
                "total_possible": 0,
                "percentage": 0,
                "section_scores": {
                    "Multiple Choice": {"earned": 0, "possible": 0},
                    "True/False": {"earned": 0, "possible": 0},
                    "Short Answer": {"earned": 0, "possible": 0}
                }
            }
            
            For each section:
            1. Multiple Choice: Note which bubble (A,B,C,D) is filled
            2. True/False: Check if True or False is marked
            3. Short Answer: Grade against rubric criteria"""
        }
    ]
    
    # Add test images
    for img_path in test_images:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{encode_image(img_path)}"}
        })
    
    try:
        print("Grading in progress...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a precise test grader. Grade each section separately and provide detailed feedback."},
                {"role": "user", "content": content}
            ],
            max_tokens=4000
        )
        
        result = response.choices[0].message.content
        
        # Clean and parse JSON response
        json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
        result = result.strip()
        if result.startswith("```") and result.endswith("```"):
            result = result[3:-3]
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            print("Failed to parse JSON. Raw response:")
            print(result)
            return {
                "sections": [],
                "total_score": 0,
                "total_possible": 0,
                "percentage": 0,
                "error": "Failed to parse response"
            }
            
    except Exception as e:
        print(f"Error during grading: {str(e)}")
        print("Raw response:", response.choices[0].message.content)
        return None

def display_results(results):
    """Display grading results in a readable format."""
    if not results:
        print("\nError: Could not process grading results.")
        return
    
    print("\n" + "="*50)
    print("GRADING RESULTS")
    print("="*50)
    
    sections = results.get("sections", [])
    for section in sections:
        print(f"\n{section['name']} Section:")
        print("-"*30)
        
        for q in section.get("questions", []):
            print(f"\nQuestion {q.get('number', 'N/A')}:")
            print(f"Student Answer: {q.get('student_answer', 'N/A')}")
            print(f"Correct Answer: {q.get('correct_answer', 'N/A')}")
            print(f"Score: {q.get('points_earned', '0')}/{q.get('points_possible', '0')}")
            print(f"Feedback: {q.get('feedback', 'N/A')}")
            print("-"*20)
        
        section_score = results.get("section_scores", {}).get(section['name'], {})
        print(f"\nSection Total: {section_score.get('earned', 0)}/{section_score.get('possible', 0)}")
    
    print("\nFinal Score:")
    print(f"Total Points: {results.get('total_score', '0')}/{results.get('total_possible', '0')}")
    print(f"Percentage: {results.get('percentage', '0')}%")
    print("="*50)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Grade a test using GPT-4 Vision')
    parser.add_argument('test_pdf', help='Path to the student\'s completed test PDF')
    parser.add_argument('rubric_pdf', help='Path to the answer key/rubric PDF')
    args = parser.parse_args()
    
    # Convert both PDFs to images
    test_images = convert_pdf_to_images(args.test_pdf)
    rubric_images = convert_pdf_to_images(args.rubric_pdf)
    
    # Grade the test
    results = grade_test(test_images, rubric_images)
    
    # Display results
    display_results(results)

if __name__ == "__main__":
    main()