# from sqlalchemy.orm import DeclarativeBase

# from app.database import Base, engine
# import app.models #rejeseracja modeli

# def create_tables() -> None:
#     """Tworzy tabele w bazie danych na podstawie zdefiniowanych modeli."""
#     Base.metadata.create_all(bind = engine)
#     print("Tabele zostały utworzone w bazie danych.")

# if __name__ == "__main__":
#     create_tables()

import app.models
from app.database import Base, engine


Base.metadata.create_all(bind=engine)
print("Tabele utworzone lub już istniały.")