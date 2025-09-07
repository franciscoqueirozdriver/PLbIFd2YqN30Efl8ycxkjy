import sys
import os

# Adiciona o diretório raiz do projeto ao PATH para que as importações funcionem
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app as application

# Este arquivo é o ponto de entrada para o Vercel
# O Vercel espera uma variável chamada `application` (ou `app`)
# que seja a sua instância do Flask ou outro framework WSGI.
# No nosso caso, a instância do Flask é `app` em src/main.py, e a renomeamos para `application` aqui.


