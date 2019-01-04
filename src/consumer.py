import math
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import ResultSchema, Base

RESULTS_PER_PAGE = 30


def consume():
    engine = create_engine('sqlite:///matprat.db', echo=False)
    Base.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    Base.query = Session.query_property()
    session = Session()

    page = 1
    total_pages = 1

    while page <= total_pages:
        req = requests.get(url='https://www.matprat.no/api/Search/GetRecipesByFilter?page=' + str(page))
        schema = ResultSchema()
        result = schema.load(req.json())
        total_pages = math.ceil(result['TotalHits'] / RESULTS_PER_PAGE)
        print('page', page, 'of', total_pages)

        session.add_all(result['SearchHits'])

        for hit in result['SearchHits']:
            hit.process_relationships(session)

        page += 1

    session.commit()


if __name__ == '__main__':
    consume()
