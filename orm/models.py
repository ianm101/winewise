from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
load_dotenv()

EMBED_DIM = os.getenv("EMBED_DIM")

Base = declarative_base()

class VECTOR(ARRAY):
    def __init__(self, dimensions, **kw):
        super(VECTOR, self).__init__(Float, dimensions, **kw)


class WineReview(Base):
    __tablename__ = 'wine_reviews'
    uuid = Column(String, primary_key=True)
    country = Column(String)
    description = Column(String)
    designation = Column(String)
    points = Column(Integer)
    price = Column(Float)
    province = Column(String)
    region_1 = Column(String)
    region_2 = Column(String)
    taster_name = Column(String)
    taster_twitter_handle = Column(String)
    title = Column(String)
    variety = Column(String)
    winery = Column(String)

class WineReviewVector(Base):
    __tablename__ = "wine_vectors"
    uuid = Column(String, primary_key=True)
    embedding = Column(VECTOR(EMBED_DIM))  # Adding a vector column with EMBED_DIM dimensions
    
    
    

