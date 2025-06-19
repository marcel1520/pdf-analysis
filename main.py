from flask import Flask, render_template, request, redirect, url_for
from app.pdf_extraction import extract_text_from_pdf
from app.openai_utils import get_topic, get_summary, get_translation, get_sentiment, translate_text
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
    

    result = None
    prompt = None
    message = ""

    if action == "topic":
        result, prompt = get_topic(doc_id)
        last_action = action
    elif action == "summary":
        result, prompt = get_summary(doc_id)
        last_action = action
    elif action == "translate":
        result, prompt = get_translation(doc_id, lang)
        last_action = action
    elif action == "sentiment":
        result, prompt = get_sentiment(doc_id)
        last_action = action
    elif action == "translate_topic":
        original_text = request.form.get('original_text')
        lang = request.form.get("lang")
        result = translate_text(original_text, lang)
        prompt = None
        message = f"Topic translation to {lang} generated successfully."
        last_action = action
    elif action == "translate_summary":
        original_text = request.form.get('original_text')
        lang = request.form.get("lang")
        result = translate_text(original_text, lang)
        prompt = None
        message = f"Summary translation to {lang} generated successfully."
        last_action = action
    elif action == "translate_sentiment":
        original_text = request.form.get('original_text')
        lang = request.form.get("lang")
        result = translate_text(original_text, lang)
        prompt = None
        message = f"Sentiment translation to {lang} generated successfully."
        last_action = action
    else:
        result = "Invalid action"
        prompt = None
    
    
    save_interaction(action, prompt, result, doc_id)
    return render_template("index.html", doc_id=doc_id, result=result, message=message or f"{action.title()}  generated successfully.", last_action=last_action)

if __name__ =="__main__":
    app.run(debug=True)








