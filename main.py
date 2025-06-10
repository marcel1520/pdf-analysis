from flask import Flask, render_template, request, redirect, url_for
from app.pdf_extraction import extract_text_from_pdf
from app.openai_utils import get_topic, get_summary, get_translation, get_sentiment
from app.database import init_db
from app.crud import save_interaction, get_text_by_doc_id


app = Flask(__name__)
init_db()


@app.route("/", methods=['GET'])
def home():
    return render_template("index.html")


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.endswith('.pdf'):
            content = uploaded_file.read()
            text = extract_text_from_pdf(content)
            if not text:
                return render_template("index.html", message="no extractable text found in the upload.")
            doc_id = save_interaction("upload", "", "", text=text)
            return render_template("index.html", doc_id=doc_id, message='pdf uploaded.')
        else:
            return render_template("index.html", message="Only pdf-files are supported.")
    return render_template("index.html")


@app.route("/process", methods=['POST'])
def process():
    doc_id = int(request.form['doc_id'])
    action = request.form['action']
    lang = request.form.get('lang', '')

    if action == "topic":
        result, prompt = get_topic(doc_id)
    elif action == "summary":
        result, prompt = get_summary(doc_id)
    elif action == "translate":
        result, prompt = get_translation(doc_id, lang)
    elif action == "sentiment":
        result, prompt = get_sentiment(doc_id)
    else:
        result, prompt = "Invalid action"
    
    save_interaction(action, prompt, result, doc_id)
    return render_template("index.html", doc_id=doc_id, result=result, message=f"{action.title()}  generated successfully.")

if __name__ =="__main__":
    app.run(debug=True)