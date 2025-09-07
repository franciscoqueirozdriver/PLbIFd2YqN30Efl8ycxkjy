import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from src.models.user import db

class Indicador(db.Model):
    __tablename__ = 'indicadores'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), nullable=False)
    telefone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    empresa = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com indicações (lazy loading para evitar problemas de importação circular)
    indicacoes = db.relationship('Indicacao', backref='indicador', lazy=True)
    
    def __repr__(self):
        return f'<Indicador {self.nome}>'

