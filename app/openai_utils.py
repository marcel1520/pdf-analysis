import google.generativeai as genai
import openai
from openai import OpenAI
from .crud import get_text_by_doc_id
from dotenv import load_dotenv
import os
import tiktoken
from openai import RateLimitError
import time


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


openai.api_key = OPENAI_API_KEY
client = OpenAI(api_key=openai.api_key)


genai.configure(api_key=GEMINI_API_KEY)
model_gemini = genai.GenerativeModel("gemini-2.0-flash-exp")


SYSTEM_ROLES = {
    "topic": "You are a editing specialist. I want you to extract the topic of any using using the 1 word which describes the text best.",
    "summary": "You are a summarization specialist. Given an input I want you to create a summary of up to 10 sentences being factual and concise towards the subject omitting irrelevant facts",
    "translation": "You are a translation expert. Your task is to translate any given input in the required language. Stay as close as possible to the actual meaning of the text in it's originality.",
    "sentiment": "You are a sentiment analyst and your task is to extract the sentiment of the given text. Use the attributes positive, negative or neutral. In addition write a justification for your choice of no more than 5 sentences."
}


TOKEN_LIMIT = 16000


def call_model(messages, model="gpt-4o-mini", max_retries=3, retry_delay=1.5):
    if model.startswith("gpt-"):
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages
                )
                return response.choices[0].message.content.strip()
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    print(f"[Retry {attempt+1}/{max_retries}] Rate limit hit. Waiting {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    raise e
    elif model.startswith("gemini-"):
        lines = []
        for message in messages:
            role = message["role"].capitalize()
            content = message["content"]
            lines.append(f"{role}: {content}")
        prompt = "\n".join(lines)
        response = model_gemini.generate_content(prompt)
        return response.text.strip()
    else:
        raise ValueError(f"Unsupported model: {model}")


def count_tokens(text: str, model: str="gpt-4o-mini") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def truncate_to_token_limit(text, token_limit=TOKEN_LIMIT, model="gpt-4o-mini"):
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    tokens = encoding.encode(text)
    truncated_tokens = tokens[:token_limit]
    return encoding.decode(truncated_tokens)


def get_topic(doc_id, model="gpt-4o-mini"):
    text = get_text_by_doc_id(doc_id)
    text = truncate_to_token_limit(text, token_limit=TOKEN_LIMIT, model=model)
    messages = [
        {"role": "system", "content": SYSTEM_ROLES["topic"]},
        {"role": "user", "content": f"Extract the topic of this text:\n\n{text}"},
    ]
    result = call_model(messages, model)
    return result, messages


def get_summary(doc_id, model="gpt-4o-mini"):
    text = get_text_by_doc_id(doc_id)
    text = truncate_to_token_limit(text, token_limit=TOKEN_LIMIT, model=model)
    messages = [
        {"role": "system", "content": SYSTEM_ROLES["summary"]},
        {"role": "user", "content": f"Provide a summary for this text:\n\n{text}"}
    ]
    result = call_model(messages, model)
    return result, messages


def get_translation(doc_id, lang, model="gpt-4o-mini"):
    text = get_text_by_doc_id(doc_id)
    text = truncate_to_token_limit(text, token_limit=TOKEN_LIMIT, model=model)
    messages = [
        {"role": "system", "content": SYSTEM_ROLES["translation"]},
        {"role": "user", "content": f"Provide a translation of the following text into {lang}:\n\n{text}"}
    ]
    result = call_model(messages, model)
    return result, messages


def get_sentiment(doc_id, model="gpt-4o-mini"):
    text = get_text_by_doc_id(doc_id)
    text = truncate_to_token_limit(text, token_limit=TOKEN_LIMIT, model=model)
    messages = [
        {"role": "system", "content": SYSTEM_ROLES["sentiment"]},
        {"role": "user", "content": f"Provide a sentiment analysis of this text:\n\n{text}"}
    ]
    result = call_model(messages, model)
    return result, messages


def translate_text(text, lang, model="gpt-4o-mini"):
    text = truncate_to_token_limit(text, token_limit=TOKEN_LIMIT, model=model)
    messages = [
        {"role": "system", "content": SYSTEM_ROLES["translation"]},
        {"role": "user", "content": f"Translate the following text into {lang}: \n\n{text}"}
    ]
    result = call_model(messages, model)
    return result

