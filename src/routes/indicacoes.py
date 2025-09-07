from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.indicacao import Indicacao, StatusRecompensa
from src.models.indicador import Indicador
from src.schemas.indicacao_schema import indicacao_schema, indicacoes_schema
from marshmallow import ValidationError
from datetime import datetime
from sqlalchemy import func

indicacoes_bp = Blueprint('indicacoes', __name__)

@indicacoes_bp.route('/indicacoes', methods=['GET'])
def get_indicacoes():
    try:
        # Parâmetros de filtro
        search = request.args.get('search', '')
        data_inicio = request.args.get('from')
        data_fim = request.args.get('to')
        indicador_id = request.args.get('indicador_id')
        gerou_venda = request.args.get('gerou_venda')
        status_recompensa = request.args.get('status_recompensa')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        query = Indicacao.query.join(Indicador)
        
        # Filtros
        if search:
            query = query.filter(
                (Indicacao.nome_indicado.ilike(f'%{search}%')) |
                (Indicacao.telefone_indicado.ilike(f'%{search}%')) |
                (Indicador.nome.ilike(f'%{search}%'))
            )
        
        if data_inicio:
            query = query.filter(Indicacao.data_indicacao >= datetime.fromisoformat(data_inicio))
        
        if data_fim:
            query = query.filter(Indicacao.data_indicacao <= datetime.fromisoformat(data_fim))
        
        if indicador_id:
            query = query.filter(Indicacao.indicador_id == indicador_id)
        
        if gerou_venda is not None:
            query = query.filter(Indicacao.gerou_venda == (gerou_venda.lower() == 'true'))
        
        if status_recompensa:
            query = query.filter(Indicacao.status_recompensa == StatusRecompensa(status_recompensa))
        
        indicacoes = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'indicacoes': indicacoes_schema.dump(indicacoes.items),
            'total': indicacoes.total,
            'pages': indicacoes.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@indicacoes_bp.route('/indicacoes', methods=['POST'])
def create_indicacao():
    try:
        data = request.get_json()
        
        # Se indicador_id não foi fornecido, tentar encontrar ou criar indicador
        if 'indicador_id' not in data and 'indicador' in data:
            indicador_data = data['indicador']
            indicador = Indicador.query.filter_by(
                nome=indicador_data['nome'],
                telefone=indicador_data['telefone']
            ).first()
            
            if not indicador:
                # Criar novo indicador
                from src.schemas.indicador_schema import indicador_schema
                indicador = indicador_schema.load(indicador_data)
                db.session.add(indicador)
                db.session.flush()  # Para obter o ID
            
            data['indicador_id'] = str(indicador.id)
        
        indicacao = indicacao_schema.load(data)
        
        db.session.add(indicacao)
        db.session.commit()
        
        return jsonify(indicacao_schema.dump(indicacao)), 201
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@indicacoes_bp.route('/indicacoes/<uuid:indicacao_id>', methods=['GET'])
def get_indicacao(indicacao_id):
    try:
        indicacao = Indicacao.query.get_or_404(indicacao_id)
        return jsonify(indicacao_schema.dump(indicacao))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@indicacoes_bp.route('/indicacoes/<uuid:indicacao_id>', methods=['PATCH'])
def update_indicacao(indicacao_id):
    try:
        indicacao = Indicacao.query.get_or_404(indicacao_id)
        data = request.get_json()
        
        # Validar transições de status de recompensa
        if 'status_recompensa' in data:
            novo_status = StatusRecompensa(data['status_recompensa'])
            status_atual = indicacao.status_recompensa
            
            # Impedir regressão de Sim para outros status (exceto Admin)
            if status_atual == StatusRecompensa.SIM and novo_status != StatusRecompensa.SIM:
                return jsonify({'error': 'Não é possível regredir status de recompensa de Sim'}), 400
        
        # Atualizar campos
        for key, value in data.items():
            if hasattr(indicacao, key) and key not in ['id', 'created_at', 'updated_at']:
                if key == 'status_recompensa':
                    setattr(indicacao, key, StatusRecompensa(value))
                else:
                    setattr(indicacao, key, value)
        
        # Aplicar regras de negócio
        if indicacao.gerou_venda:
            if indicacao.faturamento_gerado <= 0:
                return jsonify({'error': 'Faturamento deve ser maior que 0 quando gerou venda'}), 400
            if indicacao.status_recompensa == StatusRecompensa.NAO:
                indicacao.status_recompensa = StatusRecompensa.EM_PROCESSAMENTO
        else:
            indicacao.faturamento_gerado = 0
            indicacao.status_recompensa = StatusRecompensa.NAO
        
        db.session.commit()
        return jsonify(indicacao_schema.dump(indicacao))
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@indicacoes_bp.route('/indicacoes/<uuid:indicacao_id>', methods=['DELETE'])
def delete_indicacao(indicacao_id):
    try:
        indicacao = Indicacao.query.get_or_404(indicacao_id)
        
        db.session.delete(indicacao)
        db.session.commit()
        
        return jsonify({'message': 'Indicação excluída com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@indicacoes_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    try:
        # Filtros opcionais
        data_inicio = request.args.get('from')
        data_fim = request.args.get('to')
        indicador_id = request.args.get('indicador_id')
        status_recompensa = request.args.get('status_recompensa')
        
        query = Indicacao.query
        
        # Aplicar filtros
        if data_inicio:
            query = query.filter(Indicacao.data_indicacao >= datetime.fromisoformat(data_inicio))
        
        if data_fim:
            query = query.filter(Indicacao.data_indicacao <= datetime.fromisoformat(data_fim))
        
        if indicador_id:
            query = query.filter(Indicacao.indicador_id == indicador_id)
        
        if status_recompensa:
            query = query.filter(Indicacao.status_recompensa == StatusRecompensa(status_recompensa))
        
        # Calcular KPIs
        total_indicados = query.count()
        total_indicadores = query.join(Indicador).with_entities(Indicacao.indicador_id).distinct().count()
        total_vendas = query.filter(Indicacao.gerou_venda == True).count()
        taxa_conversao = (total_vendas / total_indicados * 100) if total_indicados > 0 else 0
        faturamento_total = query.filter(Indicacao.gerou_venda == True).with_entities(
            func.sum(Indicacao.faturamento_gerado)
        ).scalar() or 0
        
        return jsonify({
            'total_indicados': total_indicados,
            'total_indicadores': total_indicadores,
            'total_vendas': total_vendas,
            'taxa_conversao': round(taxa_conversao, 2),
            'faturamento_total': faturamento_total
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

