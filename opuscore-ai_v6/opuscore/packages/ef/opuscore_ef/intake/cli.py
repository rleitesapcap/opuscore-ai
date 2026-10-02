"""CLI da Etapa 1.

  python -m opuscore_ef.cli EF.docx --estado APROVADA
  python -m opuscore_ef.cli EF.docx --so-leitura      # só mostra as seções (sem IA)
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .parser import parse_ef
from .pipeline import executar


def main() -> int:
    ap = argparse.ArgumentParser(description="Etapa 1 — Pacote de Entrada para Descoberta SAP")
    ap.add_argument("ef")
    ap.add_argument("--versao", default="")
    ap.add_argument("--estado", default="RASCUNHO", choices=["RASCUNHO", "EM_REVISAO", "APROVADA"])
    ap.add_argument("--projeto", default="")
    ap.add_argument("--demanda", default="")
    ap.add_argument("--anexo", action="append", default=[])
    ap.add_argument("--saida", default="")
    ap.add_argument("--so-leitura", action="store_true", help="só segmenta a EF, sem chamar a IA")
    ap.add_argument("--sem-ia", action="store_true", help="extração 100%% determinística, sem custo de IA")
    ap.add_argument("--sem-cache", action="store_true", help="ignora o cache e chama a IA de novo")
    ap.add_argument("--imagens", choices=["esbocos", "todas", "nenhuma"], default=None,
                    help="quais imagens a IA lê (padrão: esbocos, ou EF_INTAKE_IMAGENS no .env)")
    a = ap.parse_args()

    ef = Path(a.ef).expanduser()
    if not ef.is_file():
        print(f"EF não encontrada: {ef.resolve()}")
        print("Informe o caminho completo do arquivo (.docx ou .pdf), entre aspas se tiver espaços ou acentos.")
        return 1
    a.ef = str(ef)

    if a.so_leitura:
        d = parse_ef(a.ef)
        print(f"{d.filename}: {len(d.sections)} seções, {d.total_images} imagens")
        print("Cabeçalho:", d.header)
        print("Revisões:", [r["versao"] for r in d.revisions])
        for s in d.sections:
            print(f"  [{s.sid}] {s.path_str}  ({len(s.blocks)} blocos, {s.images} imagens)")
        return 0

    from .extractor import ExtractionError, load_env, provider_info

    env = load_env()
    if not args.saida:
        from opuscore_core.sdk.config import diretorio_dados
        args.saida = str(diretorio_dados() / "artifacts")
    if a.sem_ia:
        print("IA      : desligada (--sem-ia) — extração 100% determinística, sem custo")
    else:
        info = provider_info()
        print(f".env    : {env or 'não encontrado (usando só o ambiente do terminal)'}")
        print(f"IA      : provider={info['provider']} | modelo={info['modelo']} | max_tokens={info['max_tokens']}")
        print("Lendo a EF (estrutura em Python; IA só na parte semântica)...")
    try:
        r = executar(a.ef, versao=a.versao, estado=a.estado, projeto=a.projeto,
                     demanda=a.demanda, anexos=a.anexo, salvar_em=a.saida,
                     usar_ia=not a.sem_ia, usar_cache=not a.sem_cache, imagens=a.imagens)
    except ExtractionError as e:
        print(f"\nERRO: {e}")
        print("Dica: rode com --sem-ia para gerar o pacote sem a IA enquanto ajusta a configuração.")
        return 3
    u = r.uso_ia
    im = u.get("imagens") or {}
    if im.get("extraidas"):
        pt = im.get("por_tipo", {})
        print(f"Imagens : {im['extraidas']} extraída(s) (esboços {pt.get('ESBOCO', 0)}, ECC {pt.get('ECC', 0)}, "
              f"ilustrações {pt.get('ILUSTRACAO', 0)}) | modo {im['modo']} | lidas {im['lidas']} "
              f"(do cache {im['do_cache']})" + (f" | erros: {'; '.join(im['erros'])}" if im.get("erros") else ""))
    if u.get("modo") != "sem IA":
        print(f"Uso de IA: {u['chamadas']} chamada(s){' (resultado do cache)' if u.get('cache') else ''} | "
              f"entrada ~{u['entrada_caracteres'] // 4:,} tokens")
        c = u.get("custo")
        if c:
            t = c["tokens"]
            custo = f"US$ {c['custo_estimado_usd']:.4f}" if c.get("custo_estimado_usd") is not None else "modelo sem preço na tabela"
            print(f"Tokens reais: entrada {t['input']:,} | cache lido {t['cache_read']:,} | "
                  f"cache gravado {t['cache_creation']:,} | saída {t['output']:,} | custo estimado {custo}")
    print(f"Gate: {r.gate.status}")
    for j in r.gate.justificativa:
        print(f"  - {j}")
    print(f"Documento: {r.pasta}/{r.arquivo}")
    print(f"Handoff  : {r.pasta}/handoff_etapa2.json")
    print(f"Feedback : {r.pasta}/{r.feedback_arquivo}   <- relatório para o funcional")
    return 0 if r.gate.status != "INVALIDO_PARA_DESCOBERTA" else 2


if __name__ == "__main__":
    raise SystemExit(main())
