#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de exemplo
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Adiciona o diretório raiz do projeto ao PATH
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.models.user import db
from src.models.indicador import Indicador
from src.models.indicacao import Indicacao, StatusRecompensa

# Dados de exemplo para indicadores
INDICADORES_EXEMPLO = [
    {
        "nome": "João Silva Santos",
        "telefone": "+5511987654321",
        "email": "joao.silva@email.com",
        "empresa": "Tech Solutions Ltda"
    },
    {
        "nome": "Maria Oliveira Costa",
        "telefone": "+5511876543210",
        "email": "maria.oliveira@empresa.com",
        "empresa": "Inovação Digital"
    },
    {
        "nome": "Carlos Eduardo Pereira",
        "telefone": "+5511765432109",
        "email": "carlos.pereira@negocio.com.br",
        "empresa": "Consultoria Estratégica"
    },
    {
        "nome": "Ana Paula Rodrigues",
        "telefone": "+5511654321098",
        "email": "ana.rodrigues@comercial.com",
        "empresa": "Vendas & Marketing"
    },
    {
        "nome": "Roberto Almeida Lima",
        "telefone": "+5511543210987",
        "email": "roberto.lima@industria.com.br",
        "empresa": "Indústria Moderna S.A."
    },
    {
        "nome": "Fernanda Santos Souza",
        "telefone": "+5511432109876",
        "email": "fernanda.souza@servicos.com",
        "empresa": "Serviços Profissionais"
    },
    {
        "nome": "Paulo Henrique Martins",
        "telefone": "+5511321098765",
        "email": "paulo.martins@tecnologia.com.br",
        "empresa": "TechStart Inovações"
    },
    {
        "nome": "Juliana Ferreira Dias",
        "telefone": "+5511210987654",
        "email": "juliana.dias@consultoria.com",
        "empresa": "Consultoria Empresarial"
    },
    {
        "nome": "Ricardo Barbosa Nunes",
        "telefone": "+5511109876543",
        "email": "ricardo.nunes@comercio.com.br",
        "empresa": "Comércio & Distribuição"
    },
    {
        "nome": "Camila Torres Ribeiro",
        "telefone": "+5511098765432",
        "email": "camila.ribeiro@marketing.com",
        "empresa": "Agência de Marketing"
    }
]

# Nomes para indicados
NOMES_INDICADOS = [
    "Alexandre Costa Mendes", "Beatriz Lima Cardoso", "Daniel Rocha Fernandes",
    "Eduarda Alves Monteiro", "Felipe Gomes Barbosa", "Gabriela Santos Moreira",
    "Henrique Silva Araújo", "Isabela Oliveira Cunha", "José Carlos Pereira",
    "Larissa Ferreira Lopes", "Marcos Vinícius Dias", "Natália Rodrigues Castro",
    "Otávio Almeida Ramos", "Patrícia Souza Martins", "Rafael Barbosa Neves",
    "Sabrina Costa Ribeiro", "Thiago Lima Santos", "Vanessa Alves Carvalho",
    "William Pereira Sousa", "Yasmin Oliveira Torres", "Bruno Henrique Silva",
    "Carolina Fernandes Lima", "Diego Santos Rocha", "Eliana Costa Almeida",
    "Fábio Rodrigues Nunes", "Giovana Barbosa Dias", "Hugo Alves Monteiro",
    "Ísis Ferreira Castro", "João Pedro Souza", "Karina Lima Cardoso"
]

# Telefones para indicados (formato brasileiro)
def gerar_telefone():
    """Gera um número de telefone brasileiro válido"""
    ddd = random.choice(['11', '21', '31', '41', '51', '61', '71', '81', '85', '91'])
    numero = f"9{random.randint(10000000, 99999999)}"
    return f"+55{ddd}{numero}"

def criar_indicadores():
    """Cria indicadores de exemplo"""
    indicadores = []
    
    for dados in INDICADORES_EXEMPLO:
        indicador = Indicador(
            nome=dados["nome"],
            telefone=dados["telefone"],
            email=dados["email"],
            empresa=dados["empresa"]
        )
        db.session.add(indicador)
        indicadores.append(indicador)
    
    db.session.commit()
    print(f"✓ Criados {len(indicadores)} indicadores")
    return indicadores

def criar_indicacoes(indicadores):
    """Cria indicações de exemplo"""
    indicacoes = []
    
    # Criar indicações para os últimos 6 meses
    data_inicio = datetime.now() - timedelta(days=180)
    
    for i in range(50):  # 50 indicações de exemplo
        # Escolher um indicador aleatório
        indicador = random.choice(indicadores)
        
        # Gerar data aleatória nos últimos 6 meses
        dias_aleatorios = random.randint(0, 180)
        data_indicacao = data_inicio + timedelta(days=dias_aleatorios)
        
        # Escolher nome do indicado
        nome_indicado = random.choice(NOMES_INDICADOS)
        
        # Gerar telefone do indicado
        telefone_indicado = gerar_telefone()
        
        # 70% de chance de gerar venda
        gerou_venda = random.random() < 0.7
        
        # Se gerou venda, definir faturamento e status
        if gerou_venda:
            faturamento_gerado = random.randint(50000, 500000)  # R$ 500 a R$ 5.000 em centavos
            status_recompensa = random.choice([
                StatusRecompensa.EM_PROCESSAMENTO,
                StatusRecompensa.SIM
            ])
        else:
            faturamento_gerado = 0
            status_recompensa = StatusRecompensa.NAO
        
        # Observações aleatórias (30% de chance)
        observacoes = None
        if random.random() < 0.3:
            observacoes_opcoes = [
                "Cliente muito interessado no produto",
                "Precisa de follow-up na próxima semana",
                "Indicação de alta qualidade",
                "Cliente já conhecia a empresa",
                "Fechou negócio rapidamente",
                "Necessita de proposta personalizada",
                "Cliente corporativo com potencial",
                "Indicação através de networking"
            ]
            observacoes = random.choice(observacoes_opcoes)
        
        indicacao = Indicacao(
            data_indicacao=data_indicacao.date(),
            nome_indicado=nome_indicado,
            telefone_indicado=telefone_indicado,
            gerou_venda=gerou_venda,
            faturamento_gerado=faturamento_gerado,
            status_recompensa=status_recompensa,
            observacoes=observacoes,
            indicador_id=indicador.id
        )
        
        db.session.add(indicacao)
        indicacoes.append(indicacao)
    
    db.session.commit()
    print(f"✓ Criadas {len(indicacoes)} indicações")
    return indicacoes

def main():
    """Função principal para popular o banco de dados"""
    with app.app_context():
        print("🌱 Populando banco de dados com dados de exemplo...")
        
        # Verificar se já existem dados
        if Indicador.query.count() > 0:
            resposta = input("⚠️  Já existem dados no banco. Deseja limpar e recriar? (s/N): ")
            if resposta.lower() in ['s', 'sim', 'y', 'yes']:
                print("🗑️  Limpando dados existentes...")
                Indicacao.query.delete()
                Indicador.query.delete()
                db.session.commit()
            else:
                print("❌ Operação cancelada")
                return
        
        # Criar dados de exemplo
        indicadores = criar_indicadores()
        indicacoes = criar_indicacoes(indicadores)
        
        # Estatísticas
        total_vendas = sum(1 for i in indicacoes if i.gerou_venda)
        faturamento_total = sum(i.faturamento_gerado for i in indicacoes) / 100  # Converter centavos para reais
        taxa_conversao = (total_vendas / len(indicacoes)) * 100
        
        print("\n📊 Estatísticas dos dados criados:")
        print(f"   • Indicadores: {len(indicadores)}")
        print(f"   • Indicações: {len(indicacoes)}")
        print(f"   • Vendas: {total_vendas}")
        print(f"   • Taxa de conversão: {taxa_conversao:.1f}%")
        print(f"   • Faturamento total: R$ {faturamento_total:,.2f}")
        print("\n✅ Dados de exemplo criados com sucesso!")

if __name__ == "__main__":
    main()

