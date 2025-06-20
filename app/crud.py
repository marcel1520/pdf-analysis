from .models import Interactions
from .database import SessionLocal
import json


def get_all_uploads():
    session = SessionLocal()
    try:
        uploads = (
            session.query(Interactions.title, Interactions.doc_id)
            .filter(Interactions.type =='upload')
            .group_by(Interactions.title, Interactions.doc_id)
            .order_by(Interactions.id.desc())
            .all()
        )
        return uploads
    finally:
        session.close()


def save_interaction(type, messages, title, response, doc_id=None, text=None, translated_response=None, translation_language=None):
    session = SessionLocal()
    prompt = json.dumps(messages) if isinstance(messages, list) else messages
    try:
        interaction = Interactions(
            doc_id=doc_id,
            type=type,
            prompt=prompt,
            title=title,
            response=response,
            text=text,
            translated_response=translated_response,
            translation_language=translation_language
        )
        session.add(interaction)
        session.commit()

        if doc_id is None and type == 'upload':
            interaction.doc_id = interaction.id
            session.commit()
        
        return interaction.doc_id or interaction.id
    finally:
        session.close()


def get_text_by_doc_id(doc_id):
    session = SessionLocal()
    try:
        interaction = (
            session.query(Interactions)
            .filter_by(doc_id=doc_id, type='upload')
            .first())
        if interaction:
            return interaction.text
        return ""
    finally:
        session.close()