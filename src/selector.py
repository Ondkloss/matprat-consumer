from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from models import Base, SearchHit


def select():
    engine = create_engine('sqlite:///matprat.db', echo=False)
    Base.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    Base.query = Session.query_property()
    session = Session()

    result = SearchHit.query.all()
    print(result)


if __name__ == '__main__':
    select()
