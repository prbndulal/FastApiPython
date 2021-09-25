from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base ,sessionmaker

SQLALCHEMY_DATABASE_URL="mssql+pymssql://sql_prabin:sql_prabin@/PizzaDelivery"#os.getenv("DB_CONN")

engine = create_engine(SQLALCHEMY_DATABASE_URL,echo=True
)

Base=declarative_base()
Session=sessionmaker()

