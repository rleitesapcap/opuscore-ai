"""Handoff para a Etapa 2 (seção 15): legível por máquina, sem reinterpretar a EF."""
from __future__ import annotations

from datetime import datetime, timezone

from .checks import Achado
from .gate import INVALIDO, Gate
from .schema import ExtractionResult


def build_handoff(res: ExtractionResult, gate: Gate, achados: list[Achado], meta: dict,
                  pacote_arquivo: str) -> dict:
    executavel = gate.status != INVALIDO
    sensiveis = [a for a in achados if a.codigo == "DADO_SENSIVEL"] + \
                [i for i in res.itens if i.categoria == "DADO_SENSIVEL"]
    return {
        "etapa_origem": 1,
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "executavel_para_etapa2": executavel,
        "pacote": pacote_arquivo if executavel else None,
        "relatorio_pendencias": None if executavel else pacote_arquivo,
        "ef": {"id": res.controle.id_demanda, "arquivo": meta.get("ef_arquivo"),
               "versao": meta.get("versao"), "estado": meta.get("estado")},
        "anexos_autorizados": meta.get("anexos") or [],
        "gate": {"status": gate.status, "justificativa": gate.justificativa,
                 "bloqueantes": gate.bloqueantes, "bloqueios_a_confirmar": gate.a_confirmar},
        "referencias_tecnicas": [
            {"id": i.id, "valor_original": i.valor_original, "valor_normalizado": i.valor_normalizado,
             "tipo": i.tipo_objeto, "sistema": i.sistema, "escopo": i.escopo or "INDEFINIDO",
             "classificacao": i.classificacao, "confianca": i.confianca,
             "fonte": {"secao": i.fonte.secao, "localizacao": i.fonte.localizacao}}
            for i in res.itens if i.categoria == "REF_TECNICA"
        ],
        "ancoras_funcionais": [
            {"id": i.id, "descricao": i.descricao, "ancora": i.ancora or i.valor_original,
             "fonte": {"secao": i.fonte.secao, "localizacao": i.fonte.localizacao}}
            for i in res.itens if i.categoria == "ANCORA_FUNCIONAL"
        ],
        "componentes": [
            {"id": i.id, "descricao": i.descricao, "natureza": i.natureza,
             "objeto_origem": i.objeto_origem, "ancora": i.ancora}
            for i in res.itens if i.categoria == "COMPONENTE"
        ],
        "plano_verificacoes": [v.model_dump() for v in res.plano_etapa2] if executavel else [],
        "pontos_a_confirmar_nao_bloqueantes": [
            {"id": i.id, "descricao": i.descricao, "fonte": i.fonte.localizacao}
            for i in res.itens if i.classificacao == "PONTO_A_CONFIRMAR"
        ] if executavel else [],
        "politica_sensibilidade": {
            "contem_dados_sensiveis": bool(sensiveis),
            "localizacoes": sorted({l for a in sensiveis for l in
                                    (a.localizacao if isinstance(a, Achado) else a.fonte.localizacao)}),
            "regra": "Valores sensíveis não são reproduzidos no pacote. A Etapa 2 não deve "
                     "copiar dados pessoais ou credenciais para prompts, logs ou entregáveis.",
        },
    }
