# -*- coding: utf-8 -*-
"""
===============================================================================
 langchain.py  —  TESTE RÁPIDO DE CONEXÃO (não faz parte da solução principal)
===============================================================================

O QUE ESTE ARQUIVO É:
    Um programinha mínimo que só serve para responder a
    UMA pergunta: "a conexão com a Inteligência Artificial está funcionando?"

QUANDO USAR:
    Se você desconfia que as credenciais (a chave de acesso à IA) estão erradas,
    ou que a internet/servidor não está respondendo, roda este arquivo. Se ele
    imprimir uma frase sobre um unicórnio, a conexão está OK.

IMPORTANTE:
    Este arquivo NÃO é usado pelo run_pipeline.py nem pela remediação. É só uma
    ferramenta de diagnóstico, separada. Pode ignorá-lo no dia a dia.

COMO USAR:
    python langchain.py
===============================================================================
"""

from langchain_openai import ChatOpenAI   # a "ponte" que fala com a IA
from dotenv import load_dotenv            # para ler o arquivo .env com a chave
import os

# Lê o arquivo .env, onde fica guardada a chave de acesso (LLM_API_KEY).
load_dotenv()

# Prepara a conexão com a IA (aqui, o modelo "nova-lite" do servidor Capgemini).
# base_url = o endereço do servidor;  api_key = a chave lida do .env.
llm = ChatOpenAI(
    model="amazon.nova-lite-v1:0",
    base_url="https://openai.generative.engine.capgemini.com/v1", 
    api_key=os.getenv("LLM_API_KEY"),
)

# Manda uma pergunta simples só para testar, e imprime a resposta.
# Se aparecer uma frase sobre um unicórnio, a conexão está funcionando.
response = llm.invoke("Write a one-sentence bedtime story about a unicorn.")
print(response)