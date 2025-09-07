from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.indicador import Indicador
from src.schemas.indicador_schema import indicador_schema, indicadores_schema
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

indicadores_bp = Blueprint('indicadores', __name__)

@indicadores_bp.route('/indicadores', methods=['GET'])
def get_indicadores():
    try:
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        query = Indicador.query
        
        if search:
            query = query.filter(
                (Indicador.nome.ilike(f'%{search}%')) |
                (Indicador.telefone.ilike(f'%{search}%'))
            )
        
        indicadores = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'indicadores': indicadores_schema.dump(indicadores.items),
            'total': indicadores.total,
            'pages': indicadores.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@indicadores_bp.route('/indicadores', methods=['POST'])
def create_indicador():
    try:
        data = request.get_json()
        indicador = indicador_schema.load(data)
        
        db.session.add(indicador)
        db.session.commit()
        
        return jsonify(indicador_schema.dump(indicador)), 201
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Indicador já existe'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@indicadores_bp.route('/indicadores/<uuid:indicador_id>', methods=['GET'])
def get_indicador(indicador_id):
    try:
        indicador = Indicador.query.get_or_404(indicador_id)
        return jsonify(indicador_schema.dump(indicador))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@indicadores_bp.route('/indicadores/<uuid:indicador_id>', methods=['PATCH'])
def update_indicador(indicador_id):
    try:
        indicador = Indicador.query.get_or_404(indicador_id)
        data = request.get_json()
        
        # Atualizar apenas os campos fornecidos
        for key, value in data.items():
            if hasattr(indicador, key) and key not in ['id', 'created_at', 'updated_at']:
                setattr(indicador, key, value)
        
        db.session.commit()
        return jsonify(indicador_schema.dump(indicador))
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@indicadores_bp.route('/indicadores/<uuid:indicador_id>', methods=['DELETE'])
def delete_indicador(indicador_id):
    try:
        indicador = Indicador.query.get_or_404(indicador_id)
        
        # Verificar se há indicações vinculadas
        if indicador.indicacoes:
            return jsonify({'error': 'Não é possível excluir indicador com indicações vinculadas'}), 409
        
        db.session.delete(indicador)
        db.session.commit()
        
        return jsonify({'message': 'Indicador excluído com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

