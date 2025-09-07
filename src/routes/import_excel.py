from flask import Blueprint, request, jsonify
import pandas as pd
import openpyxl
from src.models.user import db
from src.models.indicador import Indicador
from src.models.indicacao import Indicacao, StatusRecompensa
from datetime import datetime
import phonenumbers
import uuid
import re

import_bp = Blueprint('import', __name__)

@import_bp.route('/import/excel', methods=['POST'])
def import_excel():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Arquivo deve ser Excel (.xlsx ou .xls)'}), 400
        
        # Ler o arquivo Excel
        df = pd.read_excel(file)
        
        # Relatório de importação
        relatorio = {
            'total_linhas': len(df),
            'linhas_processadas': 0,
            'linhas_criadas': 0,
            'linhas_com_erro': 0,
            'erros': []
        }
        
        for index, row in df.iterrows():
            try:
                # Pular linhas vazias
                if pd.isna(row).all():
                    continue
                
                relatorio['linhas_processadas'] += 1
                
                # Mapear colunas (ajustar conforme estrutura real da planilha)
                data_indicacao = row.get('Data da Indicação') or row.get('Data')
                nome_indicador = row.get('Nome do Cliente Indicador') or row.get('Indicador')
                telefone_indicador = row.get('Telefone do Cliente Indicador') or row.get('Telefone Indicador')
                nome_indicado = row.get('Nome da Indicação') or row.get('Indicado')
                telefone_indicado = row.get('Telefone da Indicação') or row.get('Telefone Indicado')
                gerou_venda = row.get('Gerou Venda?') or row.get('Venda')
                faturamento = row.get('Faturamento Gerado') or row.get('Faturamento')
                
                # Validar dados obrigatórios
                if pd.isna(data_indicacao) or pd.isna(nome_indicador) or pd.isna(nome_indicado):
                    relatorio['erros'].append(f'Linha {index + 1}: Dados obrigatórios faltando')
                    relatorio['linhas_com_erro'] += 1
                    continue
                
                # Processar data
                if isinstance(data_indicacao, str):
                    try:
                        data_indicacao = datetime.strptime(data_indicacao, '%d/%m/%Y')
                    except:
                        try:
                            data_indicacao = datetime.strptime(data_indicacao, '%Y-%m-%d')
                        except:
                            relatorio['erros'].append(f'Linha {index + 1}: Formato de data inválido')
                            relatorio['linhas_com_erro'] += 1
                            continue
                
                # Processar telefones
                try:
                    telefone_indicador_norm = normalizar_telefone(telefone_indicador)
                    telefone_indicado_norm = normalizar_telefone(telefone_indicado)
                except:
                    relatorio['erros'].append(f'Linha {index + 1}: Telefone inválido')
                    relatorio['linhas_com_erro'] += 1
                    continue
                
                # Processar venda e faturamento
                gerou_venda_bool = False
                faturamento_centavos = 0
                
                if not pd.isna(gerou_venda):
                    gerou_venda_str = str(gerou_venda).lower()
                    gerou_venda_bool = gerou_venda_str in ['sim', 'yes', 'true', '1']
                
                if gerou_venda_bool and not pd.isna(faturamento):
                    try:
                        # Limpar formatação de moeda
                        faturamento_str = str(faturamento).replace('R$', '').replace('.', '').replace(',', '.')
                        faturamento_float = float(re.sub(r'[^\d,.]', '', faturamento_str))
                        faturamento_centavos = int(faturamento_float * 100)
                    except:
                        faturamento_centavos = 0
                
                # Encontrar ou criar indicador
                indicador = Indicador.query.filter_by(
                    nome=nome_indicador,
                    telefone=telefone_indicador_norm
                ).first()
                
                if not indicador:
                    indicador = Indicador(
                        id=uuid.uuid4(),
                        nome=nome_indicador,
                        telefone=telefone_indicador_norm
                    )
                    db.session.add(indicador)
                    db.session.flush()
                
                # Criar indicação
                status_recompensa = StatusRecompensa.EM_PROCESSAMENTO if gerou_venda_bool else StatusRecompensa.NAO
                
                indicacao = Indicacao(
                    id=uuid.uuid4(),
                    data_indicacao=data_indicacao,
                    nome_indicado=nome_indicado,
                    telefone_indicado=telefone_indicado_norm,
                    gerou_venda=gerou_venda_bool,
                    faturamento_gerado=faturamento_centavos,
                    status_recompensa=status_recompensa,
                    indicador_id=indicador.id
                )
                
                db.session.add(indicacao)
                relatorio['linhas_criadas'] += 1
                
            except Exception as e:
                relatorio['erros'].append(f'Linha {index + 1}: {str(e)}')
                relatorio['linhas_com_erro'] += 1
                continue
        
        db.session.commit()
        
        return jsonify({
            'message': 'Importação concluída',
            'relatorio': relatorio
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro na importação: {str(e)}'}), 500

def normalizar_telefone(telefone):
    """Normaliza telefone para formato E.164 brasileiro"""
    if pd.isna(telefone):
        raise ValueError("Telefone vazio")
    
    telefone_str = str(telefone).strip()
    if not telefone_str:
        raise ValueError("Telefone vazio")
    
    try:
        parsed = phonenumbers.parse(telefone_str, 'BR')
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        else:
            raise ValueError("Telefone inválido")
    except:
        raise ValueError("Não foi possível normalizar o telefone")

