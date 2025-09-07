from sqlalchemy import Column, Integer, String
from src.models.user import db

class Config(db.Model):
    __tablename__ = 'config'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False, unique=True)
    value = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f'<Config {self.key}: {self.value}>'

