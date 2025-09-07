import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask

# Ensure project root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db, User
from src.models.indicador import Indicador
from src.models.indicacao import Indicacao
from src.models.config import Config
from lib import google_sheets as gs


def to_iso(dt):
    return dt.isoformat() if dt else datetime.utcnow().isoformat()


def generate_id(prefix: str, index: int) -> str:
    return f"{prefix}_{index:04d}"


def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    load_dotenv(os.path.join(base_dir, '.env'))

    app = Flask(__name__)
    db_path = os.path.join(base_dir, 'src', 'database', 'app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        now = datetime.utcnow().isoformat()

        configs = Config.query.order_by(Config.id).all()
        config_rows = []
        for idx, cfg in enumerate(configs, start=1):
            cfg_id = generate_id('CFG', idx)
            config_rows.append({
                'config_id': cfg_id,
                'chave': cfg.key,
                'valor': cfg.value,
                'created_at': now,
                'updated_at': now,
                'status': 'active',
            })

        users = User.query.order_by(User.id).all()
        user_rows = []
        for idx, user in enumerate(users, start=1):
            usr_id = generate_id('USR', idx)
            user_rows.append({
                'usuario_id': usr_id,
                'username': user.username,
                'email': user.email,
                'created_at': now,
                'updated_at': now,
                'status': 'active',
            })

        indicadores = Indicador.query.order_by(Indicador.id).all()
        indicador_rows = []
        indicador_id_map = {}
        for idx, ind in enumerate(indicadores, start=1):
            ind_id = generate_id('IND', idx)
            indicador_id_map[ind.id] = ind_id
            indicador_rows.append({
                'indicador_id': ind_id,
                'nome': ind.nome,
                'telefone': ind.telefone,
                'email': ind.email or '',
                'empresa': ind.empresa or '',
                'created_at': to_iso(ind.created_at),
                'updated_at': to_iso(ind.updated_at),
                'status': 'active',
            })

        indicacoes = Indicacao.query.order_by(Indicacao.id).all()
        indicacao_rows = []
        for idx, inc in enumerate(indicacoes, start=1):
            inc_id = generate_id('INC', idx)
            indicacao_rows.append({
                'indicacao_id': inc_id,
                'indicador_id': indicador_id_map.get(inc.indicador_id, ''),
                'data_indicacao': to_iso(inc.data_indicacao),
                'nome_indicado': inc.nome_indicado,
                'telefone_indicado': inc.telefone_indicado,
                'gerou_venda': inc.gerou_venda,
                'faturamento_gerado': inc.faturamento_gerado,
                'status_recompensa': inc.status_recompensa.value if inc.status_recompensa else '',
                'observacoes': inc.observacoes or '',
                'created_at': to_iso(inc.created_at),
                'updated_at': to_iso(inc.updated_at),
                'status': 'active',
            })

        gs.clear_and_insert('Configuracoes', config_rows)
        print(f'Migrados {len(config_rows)} registros para Configuracoes')
        gs.clear_and_insert('Usuarios', user_rows)
        print(f'Migrados {len(user_rows)} registros para Usuarios')
        gs.clear_and_insert('Indicadores', indicador_rows)
        print(f'Migrados {len(indicador_rows)} registros para Indicadores')
        gs.clear_and_insert('Indicacoes', indicacao_rows)
        print(f'Migrados {len(indicacao_rows)} registros para Indicacoes')


if __name__ == '__main__':
    main()
