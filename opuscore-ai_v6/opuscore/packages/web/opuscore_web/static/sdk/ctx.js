// Monta o ctx entregue a cada tela de consultor (contrato_web v1).
// Acrescentar campos é compatível; mudar ou remover exige contrato_web v2.
import { UI } from "./ui.js";

export const CONTRATO_WEB = 1;

export function criarCtx(consultor, estado){
  return {
    versao: CONTRATO_WEB,
    consultor,                                  // {key, name, profile_id, tela, web...}
    consultores: estado.consultores,
    projeto: estado.project,
    ambientes: estado.environments,
    apiBase: `/api/c/${consultor.key}`,
    ui: UI,
    navegar: (hash) => { location.hash = hash; },
    conversar: () => { location.hash = `#/chat?p=${consultor.profile_id}`; },
  };
}
