from flask import Flask, render_template, request, flash
import os
from werkzeug.utils import secure_filename
from main import convert_pdf_to_images, grade_test, display_results

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flashing messages

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if both files are present
        if 'test' not in request.files or 'rubric' not in request.files:
            flash('Both test and rubric files are required')
            return render_template('index.html')
        
        test_file = request.files['test']
        rubric_file = request.files['rubric']
        
        # Check if files are selected
        if test_file.filename == '' or rubric_file.filename == '':
            flash('No selected files')
            return render_template('index.html')
        
        if test_file and rubric_file and allowed_file(test_file.filename) and allowed_file(rubric_file.filename):
            # Save files
            test_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(test_file.filename))
            rubric_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(rubric_file.filename))
            
            test_file.save(test_path)
            rubric_file.save(rubric_path)
            
            try:
                # Convert PDFs to images
                test_images = convert_pdf_to_images(test_path)
                rubric_images = convert_pdf_to_images(rubric_path)
                
                # Grade the test
                results = grade_test(test_images, rubric_images)
                
                # Clean up uploaded files
                os.remove(test_path)
                os.remove(rubric_path)
                
                return render_template('results.html', results=results)
                
            except Exception as e:
                flash(f'Error processing files: {str(e)}')
                return render_template('index.html')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)