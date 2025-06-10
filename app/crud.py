from .models import Interactions
from .database import SessionLocal

def save_interaction(type, prompt, response, doc_id=None, text=None):
    session = SessionLocal()
    try:
        if doc_id is None and type == 'upload':
            interaction = Interactions(
                doc_id=doc_id,
                type=type,
                prompt=prompt,
                response=response,
                text=text
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
                response=response
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