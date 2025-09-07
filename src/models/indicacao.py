import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from src.models.user import db
import enum

class StatusRecompensa(enum.Enum):
    NAO = "Nao"
    SIM = "Sim"
    EM_PROCESSAMENTO = "EmProcessamento"

class Indicacao(db.Model):
    __tablename__ = 'indicacoes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_indicacao = Column(DateTime, nullable=False)
    nome_indicado = Column(String(255), nullable=False)
    telefone_indicado = Column(String(20), nullable=False)
    gerou_venda = Column(Boolean, default=False)
    faturamento_gerado = Column(Integer, default=0)  # em centavos
    status_recompensa = Column(Enum(StatusRecompensa), default=StatusRecompensa.NAO)
    observacoes = Column(Text, nullable=True)
    indicador_id = Column(UUID(as_uuid=True), ForeignKey('indicadores.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Indicacao {self.nome_indicado}>'

