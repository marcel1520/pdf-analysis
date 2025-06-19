from .models import Interactions
from .database import SessionLocal
import json

def save_interaction(type, messages, response, doc_id=None, text=None, translated_response=None, translation_language=None):
    session = SessionLocal()
    prompt = json.dumps(messages) if isinstance(messages, list) else messages
    try:
        if doc_id is None and type == 'upload':
            interaction = Interactions(
                doc_id=doc_id,
                type=type,
                prompt=prompt,
                response=response,
                text=text,
                translated_response=translated_response,
                translation_language=translation_language
            )
            session.add(interaction)
            session.commit()
            interaction.doc_id = interaction.id
            session.commit()
        else:
            interaction = Interactions(
                doc_id=doc_id,
                type=type,
                prompt=prompt,
                response=response,
                translated_response=translated_response,
                translation_language=translation_language
            )
            session.add(interaction)
            session.commit()
        return interaction.doc_id
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