from marshmallow import Schema, fields, validate, pre_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from src.models.indicador import Indicador
import phonenumbers

class IndicadorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Indicador
        load_instance = True
        include_fk = True
    
    id = fields.UUID(dump_only=True)
    nome = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    telefone = fields.Str(required=True)
    email = fields.Email(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @pre_load
    def normalize_phone(self, data, **kwargs):
        if 'telefone' in data:
            try:
                # Normalizar telefone para formato E.164 brasileiro
                parsed = phonenumbers.parse(data['telefone'], 'BR')
                if phonenumbers.is_valid_number(parsed):
                    data['telefone'] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                else:
                    raise ValueError("Telefone inválido")
            except:
                raise ValueError("Não foi possível normalizar o telefone")
        return data

indicador_schema = IndicadorSchema()
indicadores_schema = IndicadorSchema(many=True)

