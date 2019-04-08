from sqlalchemy import Column, Integer, String, Date, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MovieCollection(Base):
    __tablename__ = 'movie_collection'

    id = Column(Integer, primary_key = True)
    movie_name = Column(String(80), nullable = False)
    days_from_release = Column(String(250))
    date_of_collection = Column(Date)
    box_office_collection = Column(Float)
    
    # We added this serialize function to be able to send JSON objects in a serializable format
    @property
    def serialize(self):
        return {
        'movie_name': self.movie_name,
        'collection': self.box_office_collection,
        }

# create the database using the given URI
def create_database_engine():
    db_uri = "sqlite:///moviecollection.db"
    engine = create_engine(db_uri, echo=True)
    Base.metadata.create_all(engine)
    return engine
