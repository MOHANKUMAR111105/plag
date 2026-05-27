from flask import Flask, render_template, request, jsonify
from file_processing import read_file
from text_processing import get_sentences
from plagiarism_checker import check_plagiarism, get_similarity_between_files
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_plagiarism_route():
    option = request.form.get('option')
    text = ""
    files = []

    # ---- Input validation ----
    if not option:
        return jsonify({"error": "No option selected."}), 400

    if option == 'text':
        text = request.form.get('text', '').strip()
        if not text:
            return jsonify({"error": "Please enter some text to check."}), 400

    elif option == 'file':
        uploaded_file = request.files.get('file')
        if not uploaded_file or uploaded_file.filename == '':
            return jsonify({"error": "Please upload a file."}), 400
        text = read_file(uploaded_file)
        if not text:
            return jsonify({"error": "Could not extract text from the uploaded file."}), 400

    elif option == 'similarity':
        uploaded_files = request.files.getlist('files')
        if len(uploaded_files) < 2:
            return jsonify({"error": "Please upload at least 2 files for similarity check."}), 400
        files = [read_file(f) for f in uploaded_files]
        files = [f for f in files if f]  # remove empty
        if len(files) < 2:
            return jsonify({"error": "Could not extract text from uploaded files."}), 400

    else:
        return jsonify({"error": "Invalid option."}), 400

    # ---- Processing ----
    try:
        if option == 'similarity':
            similarity_list = get_similarity_between_files(files)
            return jsonify({"mode": "similarity", "data": similarity_list})
        else:
            sentences = get_sentences(text)
            if not sentences:
                return jsonify({"error": "No valid sentences found in the text."}), 400

            df = check_plagiarism(sentences, text)

            if df.empty:
                return jsonify({"mode": "plagiarism", "data": []})

            return jsonify({"mode": "plagiarism", "data": df.to_dict(orient="records")})

    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({"error": "Something went wrong. Please try again."}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv("FLASK_DEBUG", "False") == "True")
