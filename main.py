from flask import Flask, render_template, request, redirect, url_for
from app.pdf_extraction import extract_text_from_pdf
from app.openai_utils import get_topic, get_summary, get_translation, get_sentiment, translate_text, count_tokens
from app.database import init_db
from app.crud import save_interaction, get_text_by_doc_id, get_all_uploads
from flask import session
import os


app = Flask(__name__)
init_db()
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
app.secret_key = APP_SECRET_KEY


@app.route("/", methods=['GET'])
def home():
    doc_id = session.get('last_doc_id')
    uploaded_file = session.get('uploaded_file')
    message = session.pop('message', None)
    if doc_id:
        document = get_text_by_doc_id(doc_id)
    else:
        document = None
    return render_template("index.html", document=document, doc_id=doc_id, uploaded_file=uploaded_file, message=message)


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename.endswith('.pdf'):
            content = uploaded_file.read()
            text = extract_text_from_pdf(content)
            if not text:
                return render_template("index.html", message="No extractable text found in the upload.")
            token_count = count_tokens(text)
            message = f"Size of PDF: {token_count} tokens."
            if token_count > 16000:
                message += "Truncated to first 16000 tokens to enable processing."
            title = uploaded_file.filename[:-4].title()
            doc_id = save_interaction(type='upload', 
                                      messages="", 
                                      title=title, 
                                      response="Uploaded PDF", 
                                      text=text)

            session['last_doc_id'] = doc_id
            session['uploaded_file'] = title
            session['message'] = message
            return redirect(url_for('home'))
        else:
            return render_template("index.html", message="Only pdf-files are supported.")
    return render_template("index.html")


@app.route("/process", methods=['POST'])
def process():
    doc_id = int(request.form['doc_id'])
    action = request.form['action']
    lang = request.form.get('lang', '')
    model = request.form.get('model', 'gpt-4o-mini')
    title = request.form.get('title')
    
    uploaded_file = session.get('uploaded_file')

    result = None
    prompt = None
    message = ""

    if action == "topic":
        result, prompt = get_topic(doc_id, model=model)
        last_action = action

    elif action == "summary":
        result, prompt = get_summary(doc_id, model=model)
        last_action = action

    elif action == "translate":
        result, prompt = get_translation(doc_id, lang, model=model)
        last_action = action

    elif action == "sentiment":
        result, prompt = get_sentiment(doc_id, model=model)
        last_action = action

    elif action == "translate_topic":
        original_text = request.form.get('original_text')
        lang = request.form.get("lang")
        translated_result = translate_text(original_text, lang, model=model)
        prompt = None
        message = f"Topic translation to {lang} generated successfully."
        last_action = "topic"
        return render_template("index.html", doc_id=doc_id,
                        result=original_text,
                        translated_result=translated_result,
                        message=message,
                        last_action=action,
                        model=model,
                        uploaded_file=uploaded_file)

    elif action == "translate_summary":
        original_text = request.form.get('original_text')
        lang = request.form.get("lang")
        translated_result = translate_text(original_text, lang, model=model)
        prompt = None
        message = f"Summary translation to {lang} generated successfully."
        last_action = "summary"
        return render_template("index.html", doc_id=doc_id,
                        result=original_text,
                        translated_result=translated_result,
                        message=message,
                        last_action=action,
                        model=model,
                        uploaded_file=uploaded_file)
        
    elif action == "translate_sentiment":
        original_text = request.form.get('original_text')
        lang = request.form.get("lang")
        translated_result = translate_text(original_text, lang, model=model)
        prompt = None
        message = f"Sentiment translation to {lang} generated successfully."
        last_action = "sentiment"
        return render_template("index.html", doc_id=doc_id, 
                               result=original_text, 
                               translated_result=translated_result,
                               message=message,
                               last_action=action,
                               model=model,
                               uploaded_file=uploaded_file)
    else:
        result = "Invalid action"
        prompt = None
    
    
    save_interaction(type=action, messages=prompt, title=title, response=result, doc_id=doc_id)
    return render_template("index.html", 
                           doc_id=doc_id, 
                           result=result, 
                           message=message or f"{action.title()}  generated successfully.", 
                           last_action=last_action, 
                           model=model,
                           uploaded_file=uploaded_file)


@app.route("/history", methods=['GET'])
def history():
    uploads = get_all_uploads()
    return render_template("history.html", uploads=uploads)


@app.route("/view/<int:doc_id>")
def view_doc(doc_id):
    text = get_text_by_doc_id(doc_id)
    return render_template("view_doc.html", doc_id=doc_id, text=text)


if __name__ =="__main__":
    app.run(debug=True)