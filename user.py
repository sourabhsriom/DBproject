from flask_sqlalchemy import SQLAlchemy
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import random, string

Base = declarative_base()

secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))

class User(Base):
    """Class to create database of users"""

    __tablename__ = 'User'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key=True)
    email = Column(String(80), nullable = False)
    password_hash = Column(String(64), nullable=False)
	
    def hash_password(self,passwd):
        self.password_has = pwd_context.encrypt(passwd)
	
    def verify_password(self, passwd):
        return pwd_context.verify(passwd, self.password_hash)	

engine = create_engine('sqlite:///users.db')


Base.metadata.create_all(engine)
		

        
