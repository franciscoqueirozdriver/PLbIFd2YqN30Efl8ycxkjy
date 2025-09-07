import sys
import os
from datetime import datetime

# Adicionar o diretório raiz ao path para permitir importações de 'src' e 'lib'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app  # Importa o app Flask para ter o contexto da aplicação
from src.models.user import db, User
from src.models.indicador import Indicador
from src.models.indicacao import Indicacao, StatusRecompensa
from src.models.config import Config
from lib.google_sheets import GoogleSheetsClient

# --- Funções de Geração de ID ---
def generate_opaque_id(prefix, number, length=4):
    """Gera um ID opaco como 'USR_0001'."""
    return f"{prefix}_{str(number).zfill(length)}"

# --- Funções de Transformação de Dados ---

def transform_config(configs):
    """Transforma dados de Config para o formato da planilha."""
    data = []
    for i, config in enumerate(configs, 1):
        data.append({
            'config_id': generate_opaque_id('CFG', i),
            'chave': config.key,
            'valor': config.value,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
        })
    return data

def transform_users(users):
    """Transforma dados de User para o formato da planilha."""
    data = []
    for i, user in enumerate(users, 1):
        data.append({
            'usuario_id': generate_opaque_id('USR', i),
            'username': user.username,
            'email': user.email,
            'created_at': datetime.utcnow().isoformat(), # Assumindo que não há no modelo
            'updated_at': datetime.utcnow().isoformat(), # Assumindo que não há no modelo
            'status': 'active'
        })
    return data

def transform_indicadores(indicadores):
    """Transforma dados de Indicador para o formato da planilha."""
    data = []
    # Criar um mapa de UUID para ID opaco para uso posterior nas indicações
    indicador_id_map = {}

    for i, indicador in enumerate(indicadores, 1):
        opaque_id = generate_opaque_id('IND', i)
        indicador_id_map[str(indicador.id)] = opaque_id

        data.append({
            'indicador_id': opaque_id,
            'nome': indicador.nome,
            'telefone': indicador.telefone,
            'email': indicador.email,
            'empresa': indicador.empresa,
            'created_at': indicador.created_at.isoformat() if indicador.created_at else datetime.utcnow().isoformat(),
            'updated_at': indicador.updated_at.isoformat() if indicador.updated_at else datetime.utcnow().isoformat(),
            'status': 'active'
        })
    return data, indicador_id_map

def transform_indicacoes(indicacoes, indicador_id_map):
    """Transforma dados de Indicacao para o formato da planilha."""
    data = []
    for i, indicacao in enumerate(indicacoes, 1):
        data.append({
            'indicacao_id': generate_opaque_id('INC', i),
            'indicador_id': indicador_id_map.get(str(indicacao.indicador_id), ''),
            'data_indicacao': indicacao.data_indicacao.isoformat() if indicacao.data_indicacao else '',
            'nome_indicado': indicacao.nome_indicado,
            'telefone_indicado': indicacao.telefone_indicado,
            'gerou_venda': 'TRUE' if indicacao.gerou_venda else 'FALSE',
            'faturamento_gerado': indicacao.faturamento_gerado / 100.0 if indicacao.faturamento_gerado else 0.0, # Convertendo centavos para float
            'status_recompensa': indicacao.status_recompensa.value if isinstance(indicacao.status_recompensa, StatusRecompensa) else str(indicacao.status_recompensa),
            'observacoes': indicacao.observacoes,
            'created_at': indicacao.created_at.isoformat() if indicacao.created_at else datetime.utcnow().isoformat(),
            'updated_at': indicacao.updated_at.isoformat() if indicacao.updated_at else datetime.utcnow().isoformat(),
            'status': 'active'
        })
    return data

# --- Função Principal ---

def migrate():
    """
    Executa o processo de migração do SQLite para o Google Sheets.
    """
    with app.app_context():
        try:
            print("Iniciando a migração do SQLite para o Google Sheets...")

            # 1. Inicializar o cliente do Google Sheets
            sheets_client = GoogleSheetsClient()
            print("Cliente do Google Sheets inicializado.")

            # 2. Ler e transformar dados na ordem correta

            # Configuracoes
            configs_db = Config.query.all()
            configs_sheet = transform_config(configs_db)

            # Usuarios
            users_db = User.query.all()
            users_sheet = transform_users(users_db)

            # Indicadores
            indicadores_db = Indicador.query.all()
            indicadores_sheet, indicador_id_map = transform_indicadores(indicadores_db)

            # Indicacoes
            indicacoes_db = Indicacao.query.all()
            indicacoes_sheet = transform_indicacoes(indicacoes_db, indicador_id_map)

            print("Dados lidos do SQLite e transformados.")

            # 3. Enviar dados para o Google Sheets

            # Dicionário para iterar e enviar
            tabs_to_migrate = {
                'Configuracoes': configs_sheet,
                'Usuarios': users_sheet,
                'Indicadores': indicadores_sheet,
                'Indicacoes': indicacoes_sheet,
            }

            for tab_name, data in tabs_to_migrate.items():
                if data:
                    sheets_client.clear_and_insert(tab_name, data)
                    print(f"Migrados {len(data)} registros para {tab_name}")
                else:
                    print(f"Nenhum registro para migrar para {tab_name}.")

            print("\nMigração concluída com sucesso!")

        except Exception as e:
            print(f"\nOcorreu um erro durante a migração: {e}")
            sys.exit(1)

if __name__ == '__main__':
    migrate()
