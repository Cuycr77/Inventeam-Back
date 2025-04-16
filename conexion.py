from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#URL_DB="mysql+mysqlconnector://cristian:0000@localhost:3307/proyecto_sena"
#URL_DB="mysql+mysqlconnector://root:0000@localhost:3306/proyecto_sena"
URL_DB="mysql+mysqlconnector://root:phuYvJhwoDQBhJRnHpJxRJcbFsVMEGKg@mysql.railway.internal:3306/proyecto_sena"

crear=create_engine(URL_DB)
Sessionlocal=sessionmaker(autocommit=False, autoflush=False, bind=crear)
Base=declarative_base()

def get_bd():
    cnn=Sessionlocal()
    try:
        yield cnn
    finally:
        cnn.close()