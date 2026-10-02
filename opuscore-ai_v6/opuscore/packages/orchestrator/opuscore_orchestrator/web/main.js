// Tela do Orquestrador: painel por GAP, pendências por consultor, handoffs e fila de falhas.
let CTX, AREA, $, esc, api, post, out, outErr;
const ACOES = {CRIADO:["aceitar","devolver","cancelar"], ACEITO:["iniciar","concluir","devolver"], EM_ANDAMENTO:["concluir","devolver"]};
const ROT = {aceitar:"Aceitar", iniciar:"Iniciar", concluir:"Concluir", devolver:"Devolver", cancelar:"Cancelar"};
const nomeDe = key => (CTX.consultores.find(c=>c.key===key)||{}).name || key;
const dt = s => new Date(s).toLocaleString("pt-BR");

async function carregar(){
  const pid = CTX.projeto && CTX.projeto.id;
  if(!pid){ out(`<div class="msg err">Nenhum projeto ativo.</div>`); return; }
  try{
    const p = await api(`/api/plataforma/orquestracao/painel?projeto_id=${pid}`);
    const pend = Object.entries(p.pendentes_por_consultor||{});
    $("#orqPend").innerHTML = pend.length ? pend.map(([k,n])=>`<div><b>${n}</b><span>${esc(nomeDe(k))}</span></div>`).join("")
      : `<div><b>0</b><span>pendências</span></div>`;
    $("#orqGaps").innerHTML = (p.gaps||[]).length ? p.gaps.map(g=>`
      <div class="devcard orq-gap">
        <div class="ch">GAP ${esc(g.gap_id)}</div>
        <div class="orq-tl">${g.eventos.map(e=>`<span class="orq-ev"><b>${esc(e.tipo)}</b> · ${esc(nomeDe(e.origem))} · ${dt(e.em)}</span>`).join("")||"<span class='fhint'>sem eventos</span>"}</div>
        ${g.handoffs.map(h=>`<div class="orq-ho" data-id="${h.id}">
          <span class="tag">${esc(h.estado)}</span> <b>${esc(nomeDe(h.de))} → ${esc(nomeDe(h.para))}</b>: ${esc(h.titulo)}
          ${h.motivo?`<div class="fhint">Motivo: ${esc(h.motivo)}</div>`:""}
          <div class="orq-acts">${(ACOES[h.estado]||[]).map(a=>`<button class="btn ${a==="aceitar"||a==="concluir"?"":"ghost"}" data-a="${a}">${ROT[a]}</button>`).join("")}</div>
        </div>`).join("")}
      </div>`).join("") : `<div class="fhint">Nenhum evento neste projeto ainda. Quando um funcional enviar uma EF validada, ela aparece aqui.</div>`;
    $("#orqFalhas").innerHTML = (p.falhas||[]).length ? p.falhas.map(f=>`<div class="orq-falha">
        <b>${esc(nomeDe(f.destino))}</b> · ${esc(f.tratador)} · ${f.tentativas} tentativa(s)<div class="fhint">${esc(f.erro)}</div>
        <button class="btn ghost" data-r="${f.id}">Reprocessar</button></div>`).join("") : `<div class="fhint">Nenhuma entrega com falha. 👌</div>`;
    AREA.querySelectorAll(".orq-ho button").forEach(b=>b.onclick=async ()=>{
      let motivo="";
      if(b.dataset.a==="devolver"){ motivo=prompt("Motivo da devolução:")||""; if(!motivo.trim()) return; }
      try{ await post(`/api/plataforma/orquestracao/handoffs/${b.closest(".orq-ho").dataset.id}/acao`, {acao:b.dataset.a, motivo}); carregar(); }
      catch(e){ outErr(e.message); }
    });
    AREA.querySelectorAll("[data-r]").forEach(b=>b.onclick=async ()=>{
      try{ await post(`/api/plataforma/orquestracao/entregas/${b.dataset.r}/reprocessar`, {}); carregar(); }catch(e){ outErr(e.message); }
    });
  }catch(e){ outErr(e.message); }
}

export async function mount(area, ctx){
  CTX = ctx; AREA = area;
  ({$, esc, api, post, out, outErr} = ctx.ui);
  area.innerHTML = `
    <p class="eyebrow">Agente · Coordenação</p>
    <h2 class="title">${esc(ctx.consultor.name)}</h2>
    <p class="lead">Linha do tempo de cada GAP, handoffs entre consultores e entregas com falha.</p>
    <div class="frow" style="margin:6px 0 14px"><button class="btn ghost" id="orqAtualizar">Atualizar</button></div>
    <div class="fl">Pendências por consultor</div><div class="orq-stats" id="orqPend"></div>
    <div class="fl" style="margin-top:18px">GAPs</div><div id="orqGaps"></div>
    <div class="fl" style="margin-top:18px">Entregas com falha</div><div id="orqFalhas"></div>
    <div id="devout"></div>`;
  $("#orqAtualizar").onclick = carregar;
  await carregar();
}

export function unmount(){}
