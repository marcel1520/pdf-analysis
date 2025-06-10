import openai
from openai import OpenAI
from .crud import get_text_by_doc_id
from dotenv import load_dotenv
import os


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


openai.api_key = OPENAI_API_KEY
client = OpenAI(api_key=openai.api_key)


def call_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def get_topic(doc_id):
    text = get_text_by_doc_id(doc_id)
    prompt = f"Extract the topic from this text in one word:\n\n{text}"
    result = call_openai(prompt)
    return result, prompt 


def get_summary(doc_id):
    text = get_text_by_doc_id(doc_id)
    prompt = f"Summarize this text:\n\n{text}"
    result = call_openai(prompt)
    return result, prompt


def get_translation(doc_id, lang):
    text = get_text_by_doc_id(doc_id)
    prompt = f"Translate this text to {lang}:\n\n{text}"
    result = call_openai(prompt)
    return result, prompt


def get_sentiment(doc_id):
    text = get_text_by_doc_id(doc_id)
    prompt = f"Analyze the sentiment of this text:\n\n{text}"
    result = call_openai(prompt)
    return result, prompt