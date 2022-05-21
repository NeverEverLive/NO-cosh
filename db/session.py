# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
# from contextlib import contextmanager
# import typing
import psycopg2
from core.config import settings
# from core.config import settings
def connect():
    print(settings.POSTGRES_SERVER, 
        settings.POSTGRES_PORT, 
        settings.POSTGRES_DB, 
        settings.POSTGRES_USER, 
        settings.POSTGRES_PASSWORD)
    connection = psycopg2.connect(
        host=settings.POSTGRES_SERVER, 
        port=settings.POSTGRES_PORT, 
        database=settings.POSTGRES_DB, 
        user=settings.POSTGRES_USER, 
        password=settings.POSTGRES_PASSWORD)
    return connection


# SQLALCHEMY_DATABASE_URL = 'postgresql://nel:123@localhost:5432/test' # settings.DATABASE_URL # postgresql://nel:123@localhost:5432/test
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

# SessionLocal = sessionmaker(bind=engine)

# current_session = scoped_session(SessionLocal)

# DeclarativeBase = declarative_base()


# @contextmanager
# def session(**kwargs) -> typing.ContextManager[SessionLocal]:
#     new_session = SessionLocal(**kwargs)
#     try:
#         yield new_session
#         new_session.commit()
#     except Exception:
#         new_session.rollback()
#         raise
#     finally:
#         new_session.close()


# def create_db():
#     DeclarativeBase.metadata.create_all(engine)