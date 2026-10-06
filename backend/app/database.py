from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost/presente_db")

print(f"📊 Conectando a base de datos: {DATABASE_URL}")
try:
    engine = create_engine(
        DATABASE_URL,
        echo=True,  
        pool_pre_ping=True, 
    )

    with engine.connect() as conn:
        print("✅ Conexión a base de datos exitosa!")
        
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    print("Verifica que:")
    print("1. MySQL esté ejecutándose")
    print("2. La base de datos 'presente_db' exista")
    print("3. El usuario y contraseña sean correctos en .env")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()