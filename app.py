from flask import Flask, render_template, request, redirect, url_for, abort
import os
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "No image part in request.", 400

    image = request.files['image']
    if image.filename == '':
        return "No file selected.", 400

    bw = 'bw' in request.form

    if image:
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)

        if bw:
            try:
                img = Image.open(filepath).convert('L')
                bw_filename = f"bw_{os.path.splitext(filename)[0]}.png"
                bw_filepath = os.path.join(app.config['UPLOAD_FOLDER'], bw_filename)
                img.save(bw_filepath)
                return redirect(url_for('grid', filename=bw_filename))
            except Exception as e:
                return f"Failed to convert to black and white: {e}", 500

        return redirect(url_for('grid', filename=filename))

    return "No image uploaded.", 400

@app.route('/grid/<filename>')
def grid(filename):
    return render_template('grid.html', filename=filename)

@app.errorhandler(413)
def too_large(e):
    return "File too large. Max 5MB allowed.", 413

if __name__ == '__main__':
    app.run(debug=True)
