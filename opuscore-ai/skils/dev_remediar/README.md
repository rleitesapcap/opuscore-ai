* Pré Requisitos

Pelo Portal Empresa ca Capgemini

* Instalar Eclipse e Plugin ABAP Ultima Versão
* Python 3.13 ou superior
* Node.js
* Configurar Variáveis de Ambiente Python

*** Para configurar o Python nas variáveis de ambiente do Windows, adicione o seguinte caminho na variável Path:

***Encontre onde esta intalado o Python no seu notebook , ex

Mostrar mais linhas e adicione

C:\Python313\Scripts

C:\Python313\

Adicione tambpem em  Configurações Avançadas do Sistema → Variáveis de Ambiente → selecione a variável Path → Editar → Novo e informe:

C:\Python313\Scripts

C:\Python313\

* Usar essa API colaborativa  nas variáveis de ambiente, no arquivo .env do projeto ( já configuradas )
  
* Instalar a  Python no VSCode  e Configurar ambiente

<https://code.visualstudio.com/docs/python/environments>

* no Terminal ( Se ocorrer erro é porque não tem env criado pode seguir)

Remove-Item -Recurse -Force venv

python -m venv capremedaicode

.\capremedaicode\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt

pasta "input" colocar de forma resumida o requisito funcional em .txt

pasta "output" vai gerar a saida dos códigos

execute: python run_pipeline.py

* caso ocorre erro do module python-dotenv==1.2.2,

execute pip install python-dotenv

* toda vez que for usar a Ferris AI, vc deve entrar no ambiente novamente execute

.\capremedaicode\Scripts\Activate.ps1


