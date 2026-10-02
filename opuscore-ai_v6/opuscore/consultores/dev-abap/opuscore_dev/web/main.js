// Tela do Consultor Desenvolvedor ABAP (carregada pelo shell; contrato_web v1).
let $, el, esc, api, devPost, devPut, out, outLoading, outErr, efUploadHtml, wireEFUpload, efState, fmtSize,
    downloadsHtml, usoHtml, mdLite, state, PID, AREA, CTX;
// ============ Tela do Desenvolvedor ============
let devTab = "analisar";
let etMode = "request";

function renderDev(){
  const c = state.consultores.find(x=>x.key==="dev-abap");
  const name = c ? c.name : "Desenvolvedor ABAP";
  AREA.innerHTML = `
    <p class="eyebrow">Agente · Desenvolvimento</p>
    <div class="cerebro-head"><div>
      <h2 class="title">${esc(name)}</h2>
      <p class="lead">Somente leitura no SAP; código gerado é artefato para revisão — nada é escrito no sistema.</p>
    </div></div>
    <div class="toggle" id="devtabs">
      <button data-t="analisar">Analisar</button>
      <button data-t="remediar">Remediar</button>
      <button data-t="rap">Criar Código (EF)</button>
      <button data-t="et">Gerar ET</button>
      <button data-t="handoffs">Handoffs</button>
      <button data-t="artefatos">Artefatos</button>
    </div>
    <div id="devbody"></div>`;
  $("#devtabs").querySelectorAll("button").forEach(b=>{
    b.classList.toggle("on", b.dataset.t===devTab);
    b.onclick=()=>{ devTab=b.dataset.t; renderDev(); };
  });
  const body=$("#devbody");
  body.innerHTML = ({analisar:tplAnalisar, remediar:tplRemediar, rap:tplRap, et:tplET, handoffs:tplHandoffs, artefatos:tplArtefatos}[devTab])();
  wireDev();
}

// ---- Analisar (qualquer objeto SAP) ----
function tplAnalisar(){ return `
  <div class="devform">
    <label class="fl">Objeto SAP</label>
    <div class="frow"><input id="anObj" class="fin" placeholder="ex.: MARA, ZCL_ALGO, ZR_RELATORIO" autocomplete="off">
      <button class="btn" id="anRun">Analisar</button></div>
    <p class="fhint">Digite o nome técnico do objeto (standard ou Z), que é lido via ADT no SAP conectado. Traz finalidade, quem usa e veredito Clean Core. Para pedidos em frase, use a aba Conversas.</p>
  </div><div id="devout"></div>`; }

// ---- Remediar (a partir da EF) ----
function tplRemediar(){ return `
  <div class="devform">
    <label class="fl">EF — Especificação Funcional <span class="req">obrigatória · .docx ou .pdf</span></label>
    ${efUploadHtml("rem")}
    <div class="frow" style="margin-top:14px"><button class="btn" id="remPlan" disabled>Descobrir objetos no S/4</button></div>
    <p class="fhint">A plataforma identifica na EF os objetos custom e busca as dependências Z no S/4. Nada é remediado agora: primeiro você vê a lista e decide o que entra.</p>
  </div><div id="remList"></div><div id="devout"></div>`; }

// ---- Criar Código a partir da EF (RAP) ----
function tplRap(){ return `
  <div class="devform">
    <label class="fl">EF — base para o código</label>
    <textarea id="rapEF" class="fta" placeholder="Cole a EF. Gera um esqueleto RAP Clean Core (CDS, behavior, classe, serviço)."></textarea>
    <div class="frow"><button class="btn" id="rapRun">Gerar código RAP</button></div>
    <p class="fhint">Rascunho para você revisar e transportar. Não escreve no SAP.</p>
  </div><div id="devout"></div>`; }

// ---- Gerar ET (request OU lista + EF obrigatória) ----
function tplET(){ return `
  <div class="devform">
    <label class="fl">Origem dos objetos</label>
    <div class="toggle mini" id="etmode">
      <button data-m="request" class="${etMode==='request'?'on':''}">Por request</button>
      <button data-m="list" class="${etMode==='list'?'on':''}">Por lista de objetos</button>
    </div>
    <div id="etsrc"></div>
    <label class="fl">EF — Especificação Funcional <span class="req">obrigatória · .docx ou .pdf</span></label>
    ${efUploadHtml("et")}
    <div class="frow" style="margin-top:14px"><button class="btn ghost" id="etPlan" disabled>Planejar objetos</button><button class="btn" id="etRun" disabled>Gerar ET</button></div>
  </div><div id="etObjs"></div><div id="devout"></div>`; }
function etSrcHtml(){ return etMode==="request"
  ? `<label class="fl">Request de transporte</label><input id="etReq" class="fin" placeholder="ex.: DEVK900123">`
  : `<label class="fl">Objetos (um por linha ou separados por espaço/vírgula)</label><textarea id="etList" class="fta small" placeholder="ZR_A&#10;ZCL_B"></textarea>`; }

// ---- Artefatos ----
function tplArtefatos(){ return `<div id="artList" class="lead">carregando artefatos…</div><div id="devout"></div>`; }

function wireDev(){
  if(!PID()){ out('<div class="msg err">Nenhum projeto ativo.</div>'); return; }
  if(devTab==="analisar"){
    $("#anRun").onclick = async ()=>{
      const obj=$("#anObj").value.trim(); if(!obj) return;
      outLoading(`Analisando ${obj} no S/4…`);
      try{ const r=await devPost("/api/c/dev-abap/object-report",{project_id:PID(),object_name:obj}); renderReport(r); }
      catch(e){ outErr(e.message); }
    };
    $("#anObj").addEventListener("keydown",e=>{ if(e.key==="Enter") $("#anRun").click(); });
  }
  else if(devTab==="remediar"){
    wireEFUpload("rem", ["#remPlan"]);
    $("#remPlan").onclick = async ()=>{
      const ef=efState.rem; if(!ef){ outErr("Envie a EF (.docx ou .pdf) antes de continuar."); return; }
      $("#remList").innerHTML=""; outLoading(`Lendo ${ef.filename} e descobrindo objetos e dependências Z no S/4…`);
      try{ const r=await devPost("/api/c/dev-abap/remediation/plan",{project_id:PID(),ef_id:ef.ef_id}); out(""); renderCandidates(r); }
      catch(e){ outErr(e.message); }
    };
  }
  else if(devTab==="rap"){
    $("#rapRun").onclick = async ()=>{
      const ef=$("#rapEF").value.trim(); if(!ef){ outErr("Cole a EF."); return; }
      outLoading("Gerando esqueleto RAP…");
      try{ const r=await devPost("/api/c/dev-abap/rap",{project_id:PID(),ef_text:ef});
        out(`<div class="devcard"><div class="ch">Esqueleto RAP (rascunho) · artefato salvo</div><pre class="code">${esc(r.content||"")}</pre></div>`); }
      catch(e){ outErr(e.message); }
    };
  }
  else if(devTab==="et"){
    $("#etsrc").innerHTML = etSrcHtml();
    wireEFUpload("et", ["#etPlan", "#etRun"]);
    $("#etmode").querySelectorAll("button").forEach(b=>b.onclick=()=>{ etMode=b.dataset.m;
      $("#etmode").querySelectorAll("button").forEach(x=>x.classList.toggle("on",x.dataset.m===etMode)); $("#etsrc").innerHTML=etSrcHtml(); });
    const collect=()=>{
      const etEF = efState.et;
      if(!etEF){ outErr("Envie a EF (.docx ou .pdf) antes de continuar."); return null; }
      if(etMode==="request"){ const rq=$("#etReq").value.trim(); if(!rq){ outErr("Informe a request."); return null; } return {project_id:PID(),ef_id:etEF.ef_id,request_id:rq}; }
      const objs=($("#etList").value||"").split(/[\s,;]+/).filter(Boolean); if(!objs.length){ outErr("Informe ao menos um objeto."); return null; }
      return {project_id:PID(),ef_id:etEF.ef_id,objects:objs};
    };
    $("#etPlan").onclick = async ()=>{ const b=collect(); if(!b) return; $("#etObjs").innerHTML=""; outLoading("Resolvendo objetos…");
      try{ const r=await devPost("/api/c/dev-abap/et/plan",b); out("");
        $("#etObjs").innerHTML=`<div class="devcard"><div class="ch"><b>${r.count}</b> objeto(s) — origem: ${esc(r.source)}</div>
          <div class="chips">${r.objects.map(o=>`<span class="chip">${esc(o)}</span>`).join("")||"nenhum"}</div></div>`;
      }catch(e){ outErr(e.message); } };
    $("#etRun").onclick = async ()=>{ const b=collect(); if(!b) return; outLoading("Gerando ET (buscando source + IA)…");
      try{ const r=await devPost("/api/c/dev-abap/et/run",b);
        out(`<div class="devcard"><div class="ch">${statusLabel(r,"ET gerada")} · EF: ${esc(r.ef||"")} · artefato salvo</div>${diagHtml(r)}
          ${downloadsHtml(r.downloads)}
          <div class="fhint">Objetos: ${(r.objects||[]).map(esc).join(", ")}. Arquivos: ${(r.files||[]).map(esc).join(", ")||"—"}</div>
          <pre class="code">${esc((r.log_tail||"").slice(-1500))}</pre></div>`);
      }catch(e){ outErr(e.message); } };
  }
  else if(devTab==="handoffs"){ loadHandoffs(); }
  else if(devTab==="artefatos"){ loadArtifacts(); }
}


function diagHtml(r){
  if(!r || r.rc===0 || !(r.diagnosis&&r.diagnosis.length)) return "";
  return `<div class="diag"><div class="diag-t">Motivo da falha</div>${r.diagnosis.map(l=>`<div class="diag-l">${esc(l)}</div>`).join("")}</div>`;
}
function statusLabel(r, ok){ return r.rc===0 ? ok : `Falhou (rc=${r.rc})`; }

function renderReport(r){
  const rep=r.report||{}; const used=rep.used_by||[];
  out(`<div class="devcard">
    <div class="ch">Relatório — ${esc(rep.name||"")} <span class="ct2">${esc(rep.type||"")}</span></div>
    <pre class="narr2">${esc(r.narrative||"")}</pre>
    ${rep.fields&&rep.fields.length?`<div class="sub2">Campos: ${rep.fields.length}</div>`:""}
    <div class="sub2">Quem usa (${used.length}): ${used.slice(0,30).map(u=>esc(u.name)).join(", ")||"—"}</div>
  </div>`);
}
function renderCandidates(data){
  const rows=(data.candidates||[]).map(d=>`<label class="cand"><input type="checkbox" checked data-nm="${esc(d.name)}">
    <span class="cn">${esc(d.name)}</span><span class="ct2">${esc(d.type||"")}</span>
    ${d.seed?`<span class="tagx seed">EF</span>`:`<span class="tagx dep">dep ${d.depth}</span>`}</label>`).join("");
  $("#remList").innerHTML=`<div class="devcard">
    <div class="ch"><b>${data.count}</b> objeto(s) Z encontrados${data.ef?` a partir de ${esc(data.ef)}`:""} — desmarque o que <u>não</u> quer remediar</div>
    ${data.seeds&&data.seeds.length?`<div class="fhint" style="margin:-4px 0 6px">Objetos citados na EF: ${data.seeds.map(esc).join(", ")}</div>`:""}
    ${data.fora_escopo&&data.fora_escopo.length?`<div class="fhint" style="margin:0 0 10px">Ignorados por estarem fora do escopo da EF: ${data.fora_escopo.map(esc).join(", ")}</div>`:""}
    <div class="cands">${rows||"<div class='fhint'>Nenhum objeto Z identificado.</div>"}</div>
    ${data.count?`<div class="frow" style="margin-top:12px"><button class="btn" id="remRun">Remediar selecionados</button></div>`:""}</div>`;
  const btn=$("#remRun"); if(btn) btn.onclick=async ()=>{
    const objs=[...document.querySelectorAll("#remList input:checked")].map(x=>x.dataset.nm);
    if(!objs.length){ outErr("Selecione ao menos um objeto."); return; }
    outLoading(`Remediando ${objs.length} objeto(s)…`);
    try{ const r=await devPost("/api/c/dev-abap/remediation/run",{project_id:PID(),objects:objs});
      out(`<div class="devcard"><div class="ch">${statusLabel(r,"Remediação concluída")} · artefato salvo</div>${diagHtml(r)}
        ${downloadsHtml(r.downloads, {md: "Baixar relatório", txt: "Baixar relatório"})}
        <div class="fhint">Arquivos: ${(r.files||[]).map(esc).join(", ")||"—"}</div>
        <pre class="code">${esc((r.log_tail||"").slice(-1500))}</pre></div>`);
    }catch(e){ outErr(e.message); }
  };
}
async function loadArtifacts(){
  try{ const arts=await api(`/api/plataforma/projects/${PID()}/artifacts`);
    $("#artList").innerHTML = arts.length ? `<div class="devcard"><div class="ch">${arts.length} artefato(s)</div>`+
      arts.map(a=>`<div class="artrow" data-id="${a.id}"><span class="cn">${esc(a.title)}</span><span class="ct2">${esc(a.kind)}</span><span class="tagx">${new Date(a.created_at).toLocaleString("pt-BR")}</span></div>`).join("")+`</div>`
      : `<div class="fhint">Nenhum artefato ainda. Gere uma ET, um RAP ou uma remediação.</div>`;
    document.querySelectorAll(".artrow").forEach(x=>x.onclick=async ()=>{
      const a=await api(`/api/plataforma/artifacts/${x.dataset.id}`);
      let dl=[]; try{ dl=await api(`/api/plataforma/artefatos/${x.dataset.id}/arquivos`); }catch{}
      const rot = a.kind==="remediation" ? {md:"Baixar relatório", txt:"Baixar relatório"} : {};
      out(`<div class="devcard"><div class="ch">${esc(a.title)} <span class="ct2">${esc(a.kind)}</span></div>${downloadsHtml(dl, rot)}<pre class="code">${esc(a.content||"")}</pre></div>`);
    });
  }catch(e){ $("#artList").innerHTML=`<div class="msg err">${esc(e.message)}</div>`; }
}



// ---- Handoffs recebidos (fila do Orquestrador) ----
function tplHandoffs(){ return `<p class="fhint" style="margin-top:0">EFs validadas e enviadas pelos funcionais. Aceite e use a mesma EF na Remediação ou na ET, sem novo upload.</p><div id="hoList" class="lead">carregando…</div><div id="devout"></div>`; }
const HO_ACOES = {CRIADO:["aceitar","devolver"], ACEITO:["iniciar","concluir","devolver"], EM_ANDAMENTO:["concluir","devolver"]};
const HO_ROT = {aceitar:"Aceitar", iniciar:"Iniciar", concluir:"Concluir", devolver:"Devolver", cancelar:"Cancelar"};
async function loadHandoffs(){
  try{
    const hs = await api(`/api/plataforma/orquestracao/handoffs?projeto_id=${PID()}&para=dev-abap`);
    $("#hoList").innerHTML = hs.length ? hs.map(h=>{
      const p=h.payload||{}, ativo=["ACEITO","EM_ANDAMENTO"].includes(h.estado);
      return `<div class="devcard" data-id="${h.id}">
        <div class="ch">GAP ${esc(h.gap_id)} · ${esc(h.titulo)} <span class="ct2">${esc(h.estado)}</span></div>
        <div class="fhint">De ${esc(h.de)} · EF ${esc(p.ef_arquivo||"")} · gate ${esc(p.gate||"")}</div>
        ${(p.objetos_no_escopo||[]).length?`<div class="chips">${p.objetos_no_escopo.map(o=>`<span class="chip">${esc(o)}</span>`).join("")}</div>`:""}
        ${h.motivo?`<div class="fhint">Motivo: ${esc(h.motivo)}</div>`:""}
        <div class="frow" style="margin-top:10px">
          ${(HO_ACOES[h.estado]||[]).map(a=>`<button class="btn ${a==="devolver"?"ghost":""} hoacao" data-a="${a}">${HO_ROT[a]}</button>`).join("")}
          ${ativo&&p.upload_id?`<button class="btn ghost houso" data-t="remediar">Usar na Remediação</button><button class="btn ghost houso" data-t="et">Usar na ET</button>`:""}
        </div></div>`;}).join("") : `<div class="fhint">Nenhum handoff para o Desenvolvedor ainda.</div>`;
    document.querySelectorAll("#hoList .devcard").forEach(card=>{
      const h = hs.find(x=>x.id===card.dataset.id);
      card.querySelectorAll(".hoacao").forEach(b=>b.onclick=async ()=>{
        let motivo="";
        if(b.dataset.a==="devolver"){ motivo=prompt("Motivo da devolução:")||""; if(!motivo.trim()) return; }
        try{ await devPost(`/api/plataforma/orquestracao/handoffs/${h.id}/acao`,{acao:b.dataset.a, motivo}); loadHandoffs(); }
        catch(e){ outErr(e.message); }
      });
      card.querySelectorAll(".houso").forEach(b=>b.onclick=()=>{
        const p=h.payload;
        efState[b.dataset.t==="remediar"?"rem":"et"] = {ef_id:p.upload_id, filename:p.ef_arquivo, ext:(p.ef_arquivo||"").toLowerCase().endsWith(".pdf")?".pdf":".docx",
          size:0, chars:0, preview:`EF validada pelo funcional (GAP ${h.gap_id}), recebida por handoff.`};
        devTab=b.dataset.t; renderDev();
      });
    });
  }catch(e){ $("#hoList").innerHTML=`<div class="msg err">${esc(e.message)}</div>`; }
}

export async function mount(area, ctx){
  CTX = ctx; AREA = area;
  ({$, el, esc, api, post: devPost, put: devPut, out, outLoading, outErr, efUploadHtml, wireEFUpload, efState,
    fmtSize, downloadsHtml, usoHtml, mdLite} = ctx.ui);
  state = {consultores: ctx.consultores, project: ctx.projeto, environments: ctx.ambientes};
  PID = () => ctx.projeto && ctx.projeto.id;
  renderDev();
}

export function unmount(){}
