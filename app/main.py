import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
app.config['RESULT_FOLDER'] = 'app/static/results'

# Asegúrate de que las carpetas existan
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return filename.lower().endswith(('.png', '.jpg', '.jpeg'))


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_images():
    if 'file' not in request.files:
        return redirect(request.url)
    files = request.files.getlist('file')
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Procesar la imagen
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            text = pytesseract.image_to_string(Image.open(image_path))

            # Guardar el texto en un archivo .txt
            txt_filename = f"{os.path.splitext(filename)[0]}.txt"
            txt_path = os.path.join(app.config['RESULT_FOLDER'], txt_filename)
            with open(txt_path, 'w') as f:
                f.write(text)

    return redirect(url_for('catalogo'))


@app.route('/catalogo')
def catalogo():
    images = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if allowed_file(filename):
            img_path = url_for('static', filename=f'uploads/{filename}')
            txt_filename = f"{os.path.splitext(filename)[0]}.txt"
            txt_path = os.path.join(app.config['RESULT_FOLDER'], txt_filename)

            # Verifica si el archivo de texto existe antes de intentar abrirlo
            if os.path.exists(txt_path):
                with open(txt_path, 'r') as f:
                    text = f.read()
            else:
                text = "No text found."

            images.append((img_path, text))

    # Generar catalogo.txt si no existe
    catalogo_path = os.path.join(app.config['RESULT_FOLDER'], 'catalogo.txt')
    if not os.path.exists(catalogo_path):
        with open(catalogo_path, 'w') as f:
            for img_path, text in images:
                f.write(f"Image: {img_path}\nText: {text}\n\n")

    return render_template('catalogo.html', images=images)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
