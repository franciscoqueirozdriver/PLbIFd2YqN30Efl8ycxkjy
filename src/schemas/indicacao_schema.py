from marshmallow import Schema, fields, validate, pre_load, post_load, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from src.models.indicacao import Indicacao, StatusRecompensa
from datetime import datetime
import phonenumbers

class IndicacaoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Indicacao
        load_instance = True
        include_fk = True
    
    id = fields.UUID(dump_only=True)
    data_indicacao = fields.DateTime(required=True)
    nome_indicado = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    telefone_indicado = fields.Str(required=True)
    gerou_venda = fields.Bool(load_default=False)
    faturamento_gerado = fields.Int(load_default=0)
    status_recompensa = fields.Enum(StatusRecompensa, load_default=StatusRecompensa.NAO)
    observacoes = fields.Str(allow_none=True)
    indicador_id = fields.UUID(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @pre_load
    def validate_and_normalize(self, data, **kwargs):
        # Normalizar telefone
        if 'telefone_indicado' in data:
            try:
                parsed = phonenumbers.parse(data['telefone_indicado'], 'BR')
                if phonenumbers.is_valid_number(parsed):
                    data['telefone_indicado'] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                else:
                    raise ValidationError("Telefone do indicado inválido")
            except:
                raise ValidationError("Não foi possível normalizar o telefone do indicado")
        
        # Validar data não futura
        if 'data_indicacao' in data:
            if isinstance(data['data_indicacao'], str):
                try:
                    data['data_indicacao'] = datetime.fromisoformat(data['data_indicacao'])
                except:
                    raise ValidationError("Formato de data inválido")
            
            if data['data_indicacao'].date() > datetime.now().date():
                raise ValidationError("Data da indicação não pode ser futura")
        
        return data
    
    @post_load
    def validate_business_rules(self, data, **kwargs):
        # Regras de negócio para venda e faturamento
        if data.gerou_venda:
            if data.faturamento_gerado <= 0:
                raise ValidationError("Faturamento deve ser maior que 0 quando gerou venda")
            data.status_recompensa = StatusRecompensa.EM_PROCESSAMENTO
        else:
            data.faturamento_gerado = 0
            data.status_recompensa = StatusRecompensa.NAO
        
        return data

indicacao_schema = IndicacaoSchema()
indicacoes_schema = IndicacaoSchema(many=True)

