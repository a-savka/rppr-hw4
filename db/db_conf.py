from sqlalchemy.orm import declarative_base

PG_URL = "postgresql+asyncpg://postgres:postgres@localhost:5454/rppr_l_3?ssl=disable"

Base = declarative_base()
