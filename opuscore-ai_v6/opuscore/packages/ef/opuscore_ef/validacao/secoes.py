"""Regras de validação por seção da EF.

Cada seção tem: título, papéis (como o extrator reconhece a seção no documento),
se é obrigatória, condição (para seções que só valem para certos tipos de
desenvolvimento) e o PROMPT de validação específico dela.

Os valores padrão ficam aqui (pacote EF). Cada consultor funcional aplica por cima os
ajustes do módulo e as edições do projeto, que ele mesmo guarda: `carregar(ajustes)`.
"""
from __future__ import annotations

import copy
import hashlib
import json


# condicao: palavras que, se aparecerem no "Tipo de programa" marcado no Resumo,
# tornam a seção obrigatória. Sem condição = vale para toda EF.
PADRAO: list[dict] = [
    {"id": "capa", "titulo": "Identificação (capa)", "papeis": ["capa"], "obrigatoria": True, "condicao": "",
     "prompt": "Confira se estão preenchidos: ID GAP, Descrição GAP, Projeto, Fase, Módulo, Cenário empresarial, "
               "Processo e Autor. Aponte campo vazio ou com valor genérico (ex.: 'XXX'). Aponte se o Processo não "
               "combina com o Cenário."},
    {"id": "resumo", "titulo": "Resumo do Desenvolvimento", "papeis": ["resumo"], "obrigatoria": True, "condicao": "",
     "prompt": "Confira: tipo de programa marcado; prioridade marcada; natureza de CADA objeto (novo, remediação "
               "ou evolução), não só da EF inteira; se 'existe alternativa no S/4HANA' foi respondido com evidência "
               "(fontes consultadas: configuração standard, SAP Best Practices, Fiori Apps Library, Business "
               "Accelerator Hub, SCFD_REGISTRY), e não só 'Não' ou 'Não se aplica'. Se houver interface ou migração, "
               "volumetria e sistemas de origem/destino precisam estar preenchidos ('A definir' não vale)."},
    {"id": "objetivo", "titulo": "Objetivo, justificativa e processo atendido", "papeis": ["objetivo"],
     "obrigatoria": True, "condicao": "",
     "prompt": "O texto precisa deixar claro: situação atual (AS-IS), problema/necessidade, objetivo (TO-BE), "
               "benefício e um critério de sucesso verificável. Aponte o que faltar. Aponte promessas vagas "
               "('incorporar melhorias', 'aplicação simplificada', 'manter aderência ao Clean Core') sem dizer "
               "quais ou como, e sugira uma redação concreta."},
    {"id": "processos", "titulo": "Processos relacionados", "papeis": ["processos"], "obrigatoria": True,
     "condicao": "",
     "prompt": "Liste o que falta para cada processo: transação S/4HANA, app Fiori (quando houver), papel do "
               "usuário e se é standard ou custom. Aponte transações que não existem mais no S/4HANA (ex.: XK01, "
               "XD01, VD01, substituídas pela BP) sem afirmar nada que não esteja no texto. Aponte se outros "
               "caminhos que alteram o mesmo dado ficaram de fora sem justificativa."},
    {"id": "regras", "titulo": "Regras de negócio", "papeis": ["regras"], "obrigatoria": True, "condicao": "",
     "prompt": "Cada regra precisa ser testável: condição, ação/resultado e exceção. Aponte regras vagas, regras "
               "misturadas num parágrafo longo, e termos como 'aplicável', 'quando necessário', 'os demais', "
               "'etc.'. Sugira a reescrita no formato 'RN-nn: Quando <condição>, o sistema deve <ação>. Exceção: "
               "<exceção>.'. Aponte informação que está só em imagem/esboço sem descrição em texto."},
    {"id": "premissas", "titulo": "Premissas, escopo e dependências", "papeis": ["premissas"], "obrigatoria": True,
     "condicao": "",
     "prompt": "Confira se há escopo incluído E fora de escopo explícitos, premissas e dependências (outros GAPs, "
               "configurações, dados mestres). Aponte contradição entre o que está incluído e excluído. Aponte "
               "premissas copiadas de outro contexto (texto de exemplo do template)."},
    {"id": "fluxo", "titulo": "Fluxo do processo", "papeis": ["fluxo"], "obrigatoria": True, "condicao": "",
     "prompt": "O fluxo precisa estar em texto, passo a passo, com quem executa cada passo (usuário ou sistema), "
               "as decisões (sim/não) e onde cada desenvolvimento entra. Aponte se só existe BPMN/anexo, se há "
               "regras misturadas no meio dos passos e fluxos soltos (ex.: manutenção de parâmetros sem ligação "
               "com o processo principal)."},
    {"id": "sistemas", "titulo": "Sistemas e objetos impactados", "papeis": ["sistemas"], "obrigatoria": True,
     "condicao": "",
     "prompt": "Confira se cada sistema tem tipo (S/4HANA, legado, externo, BTP), papel no processo e se há "
               "integração. Se houver sistema externo com integração, aponte que o bloco de interfaces do Resumo "
               "precisa estar preenchido."},
    {"id": "novos_objetos", "titulo": "Novos objetos / campos", "papeis": ["novos_objetos"], "obrigatoria": False,
     "condicao": "",
     "prompt": "Para campos novos: tipo, tamanho, tela/objeto, ajuda (F4), tabela de verificação e obrigatoriedade. "
               "Se houver campo novo em objeto standard, aponte que a EF deve registrar se foi verificado no "
               "Extensibility Registry (SCFD_REGISTRY) / Custom Fields and Logic."},
    {"id": "parametros", "titulo": "TVARV, BRF+ e tabelas de parâmetros", "papeis": ["parametros"],
     "obrigatoria": False, "condicao": "",
     "prompt": "A seção precisa listar os parâmetros reais do desenvolvimento (nome, tipo: TVARV/BRF+/tabela/app, "
               "valores e quem mantém), e não só o texto de orientação do template. Se a EF citar tabelas de "
               "parâmetro em outras seções, aponte que elas deveriam estar aqui."},
    {"id": "enhancements", "titulo": "Enhancements", "papeis": ["enh_requisitos", "enh_ampliacoes", "enh_implicito",
                                                                "enh_regra"],
     "obrigatoria": False, "condicao": "enhancement",
     "prompt": "Confira: ponto de extensão (BAdI/exit) identificado, objetivo de cada implementação e a regra "
               "que ela aplica. Se houver enhancement IMPLÍCITO ou modificação de objeto standard, aponte como "
               "alerta de Clean Core (nível D) e sugira registrar se foi avaliada uma BAdI liberada. Para objetos "
               "de remediação, confira se está claro o que deve ser mantido e o que sai."},
    {"id": "fiori", "titulo": "Aplicativo Fiori", "papeis": ["fiori"], "obrigatoria": False, "condicao": "fiori",
     "prompt": "Confira: template escolhido (List Report, Object Page, Free Style...), campos da tela com tipo e "
               "obrigatoriedade, filtros, botões e ações, regras e validações, perfis de acesso. Aponte campos "
               "descritos só em esboço/imagem. Para app novo, espera-se RAP/ABAP Cloud (Clean Core nível A)."},
    {"id": "formulario", "titulo": "Formulário", "papeis": ["formulario"], "obrigatoria": False,
     "condicao": "formul",
     "prompt": "Confira: programa extrator ou origem dos dados, tecnologia de saída, condições de disparo, layout "
               "desejado e campos com origem."},
    {"id": "interface_entrada", "titulo": "Interfaces de entrada / conversões", "papeis": ["interface_entrada"],
     "obrigatoria": False, "condicao": "interface|migra",
     "prompt": "Confira: sistema de origem, modo (síncrono, assíncrono, batch, evento), tecnologia, layout e "
               "mapeamento campo a campo, volumetria e tratamento de erros/reprocessamento. Em desenvolvimento "
               "novo, batch-input deve ser apontado como alerta de Clean Core, sugerindo API liberada."},
    {"id": "interface_saida", "titulo": "Interfaces de saída", "papeis": ["interface_saida"], "obrigatoria": False,
     "condicao": "interface",
     "prompt": "Confira: sistema de destino, formato, mapeamento e regras de conversão, periodicidade, volumetria "
               "e tratamento de erros."},
    {"id": "programa", "titulo": "Programas on-line", "papeis": ["programa"], "obrigatoria": False,
     "condicao": "programa|online",
     "prompt": "Confira: layout da tela, consistências, navegação e mensagens. Em desenvolvimento novo, lógica "
               "transacional em BOPF deve ser apontada, sugerindo RAP."},
    {"id": "relatorio", "titulo": "Relatórios", "papeis": ["relatorio"], "obrigatoria": False, "condicao": "relat",
     "prompt": "Confira: tela de seleção (parâmetros e obrigatoriedade), layout do relatório, origem de cada campo, "
               "totais/indicadores e volumetria esperada."},
    {"id": "workflow", "titulo": "Workflow", "papeis": ["workflow"], "obrigatoria": False, "condicao": "workflow",
     "prompt": "Confira: regras de aprovação (quem aprova, níveis, substitutos), ações após aprovação e reprovação, "
               "prazos e notificações."},
    {"id": "teste_proc", "titulo": "Procedimento de testes", "papeis": ["teste_proc"], "obrigatoria": True,
     "condicao": "",
     "prompt": "Os testes precisam cobrir as regras de negócio principais, incluindo os casos de exceção, com "
               "dados de teste ou pré-condições. Aponte regras importantes sem cenário de teste."},
    {"id": "teste_result", "titulo": "Resultados esperados", "papeis": ["teste_result"], "obrigatoria": True,
     "condicao": "",
     "prompt": "Cada cenário de teste precisa de um resultado esperado verificável (mensagem, bloqueio, gravação, "
               "valor). Aponte resultados genéricos como 'funcionar corretamente'."},
    {"id": "nfr", "titulo": "Informações complementares", "papeis": ["nfr"], "obrigatoria": True, "condicao": "",
     "prompt": "Confira periodicidade, tipo de execução, volumetria, janela, tratamento de erros/logs/"
               "reprocessamento e criticidade. 'Não se aplica' é aceito, mas precisa fazer sentido com o tipo de "
               "desenvolvimento (ex.: job em background sem volumetria é um problema)."},
    {"id": "homologacao", "titulo": "Homologação", "papeis": ["homologacao"], "obrigatoria": True, "condicao": "",
     "prompt": "Confira se cada papel de homologação tem uma pessoa nomeada."},
]

CAMPOS_EDITAVEIS = ("titulo", "prompt", "obrigatoria", "condicao", "ativo")


def _padrao() -> list[dict]:
    regras = copy.deepcopy(PADRAO)
    for r in regras:
        r.setdefault("ativo", True)
    return regras


def carregar(*camadas: dict | None) -> list[dict]:
    """Regras vigentes: padrão + camadas de ajuste ({id: {campo: valor}}), a última vence.
    Uma regra alterada por qualquer camada sai com editado=True."""
    out = []
    for r in _padrao():
        mudou = False
        for camada in camadas:
            mud = (camada or {}).get(r["id"]) or {}
            for k in CAMPOS_EDITAVEIS:
                if k in mud:
                    r[k] = mud[k]
                    mudou = True
        r["editado"] = mudou
        out.append(r)
    return out


def ids() -> set[str]:
    return {r["id"] for r in PADRAO}


def assinatura(regras: list[dict]) -> str:
    """Muda quando qualquer regra muda (entra na chave do cache da revisão)."""
    base = json.dumps([{k: r.get(k) for k in ("id",) + CAMPOS_EDITAVEIS} for r in regras],
                      ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(base.encode()).hexdigest()[:16]
