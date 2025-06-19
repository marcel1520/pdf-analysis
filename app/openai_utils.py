import openai
from openai import OpenAI
from .crud import get_text_by_doc_id
from dotenv import load_dotenv
import os


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


openai.api_key = OPENAI_API_KEY
client = OpenAI(api_key=openai.api_key)


SYSTEM_ROLES = {
    "topic": "You are a editing specialist. I want you to extract the topic of any using using the 1 word which describes the text best.",
    "summary": "You are a summarization specialist. Given an input I want you to create a summary of up to 10 sentences being factual and concise towards the subject omitting irrelevant facts",
    "translation": "You are a translation expert. Your task is to translate any given input in the required language. Stay as close as possible to the actual meaning of the text in it's originality.",
    "sentiment": "You are a sentiment analyst and your task is to extract the sentiment of the given text. Use the attributes positive, negative or neutral. In addition write a justification for your choice of no more than 5 sentences."
}

def call_openai(messages):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content.strip()


def get_topic(doc_id):
    text = get_text_by_doc_id(doc_id)
    messages = [
        {"role": "system", "content": SYSTEM_ROLES["topic"]},
        {"role": "user", "content": f"Extract the topic of this text:\n\n{text}"},
    ]
    result = call_openai(messages)
    return result, messages


def get_summary(doc_id):
    text = get_text_by_doc_id(doc_id)
    messages = [
        {"role": "system", "content": SYSTEM_ROLES["summary"]},
        {"role": "user", "content": f"Provide a summary for this text:\n\n{text}"}
    ]
    result = call_openai(messages)
    return result, messages


def get_translation(doc_id, lang):
    text = get_text_by_doc_id(doc_id)
    messages = [
        {"role": "system", "content": SYSTEM_ROLES["translation"]},
        {"role": "user", "content": f"Provide a translation of this text:\n\n{text} in {lang} langauge."}
    ]
    result = call_openai(messages)
    return result, messages


def get_sentiment(doc_id):
    text = get_text_by_doc_id(doc_id)
    messages = [
        {"role": "system", "content": SYSTEM_ROLES["sentiment"]},
        {"role": "user", "content": f"Provide a sentiment analysis of this text:\n\n{text}"}
    ]
    result = call_openai(messages)
    return result, messages


def translate_text(text, lang):
    messages = [
        {"role": "system", "content": SYSTEM_ROLES["translation"]},
        {"role": "user", "content": f"Translate the following text into {lang}: \n\n{text}"}
    ]
    result = call_openai(messages)
    return result