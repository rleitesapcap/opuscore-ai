# OPUSCORE-AI

Squad de consultores SAP com IA e conectividade real (somente leitura) ao sistema do cliente.
Monorepo dividido em pacotes independentes, para uma equipe trabalhar em paralelo sem
um interferir no outro.

- **Como instalar e executar (tudo ou cada pacote separado):** [docs/COMO_EXECUTAR.md](docs/COMO_EXECUTAR.md)
- **Arquitetura, regras e donos:** [docs/ARQUITETURA.md](docs/ARQUITETURA.md)

```bash
bash scripts/instalar.sh && source .venv/bin/activate
opuscore-servidor                                    # tudo, em http://127.0.0.1:8787
opuscore-dev --plugins funcional-mm --porta 8801     # só um consultor
pytest && lint-imports --config .importlinter        # testes e regras de dependência
```
