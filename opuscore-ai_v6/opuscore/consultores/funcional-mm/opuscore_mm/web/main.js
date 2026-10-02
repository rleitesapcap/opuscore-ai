// Tela do Consultor Funcional MM (carregada pelo shell; contrato_web v1).
let $, el, esc, api, devPost, devPut, out, outLoading, outErr, efUploadHtml, wireEFUpload, efState, fmtSize,
    downloadsHtml, usoHtml, mdLite, state, PID, AREA, CTX;
// =====================================================================
// Consultor Funcional MM — Gerar EF, Validar EF, Regras por seção
// =====================================================================
let mmTab = "analisar";
let mmConv = null;   // conversa da aba Analisar (criada na primeira pergunta)
const MM_ICO = {OK:"✅", ATENCAO:"⚠️", CRITICO:"❌", NAO_SE_APLICA:"➖", NAO_AVALIADA:"❔"};
const MM_ROT = {OK:"ok", ATENCAO:"precisa de ajuste", CRITICO:"falta o essencial", NAO_SE_APLICA:"não se aplica", NAO_AVALIADA:"não avaliada"};
const MM_TIPO = {FALTA:"Falta", MELHORIA:"Dá pra melhorar", AMBIGUIDADE:"Ficou ambíguo", CLEAN_CORE:"Clean Core"};

function renderMM(){
  const c = state.consultores.find(x=>x.key==="funcional-mm");
  const name = c ? c.name : "Consultor Funcional MM";
  AREA.innerHTML = `
    <p class="eyebrow">Agente · Funcional</p>
    <div class="cerebro-head"><div>
      <h2 class="title">${esc(name)}</h2>
      <p class="lead">Analisa a configuração de MM do ambiente, gera o rascunho da EF a partir do Workshop B e valida EFs seção por seção.</p>
    </div></div>
    <div class="toggle" id="mmtabs">
      <button data-t="analisar">Analisar</button>
      <button data-t="gerar">Gerar EF</button>
      <button data-t="validar">Validar EF</button>
      <button data-t="regras">Regras por seção</button>
    </div>
    <div id="mmbody"></div>`;
  $("#mmtabs").querySelectorAll("button").forEach(b=>{
    b.classList.toggle("on", b.dataset.t===mmTab);
    b.onclick=()=>{ mmTab=b.dataset.t; renderMM(); };
  });
  const body=$("#mmbody");
  if(mmTab==="analisar"){ body.innerHTML = tplMMAnalisar(); wireMMAnalisar(); }
  else if(mmTab==="gerar"){ body.innerHTML = tplMMGerar(); wireMMGerar(); }
  else if(mmTab==="validar"){ body.innerHTML = tplMMValidar(); wireMMValidar(); }
  else { body.innerHTML = `<div id="mmregras"><div class="devcard loading2"><span class="spin2"></span>Carregando as regras…</div></div><div id="devout"></div>`; loadMMRegras(); }
}

function custoTotal(...usos){
  let t=0, tem=false;
  usos.forEach(u=>{ const c=u&&u.custo; if(c&&c.custo_estimado_usd!=null){ t+=c.custo_estimado_usd; tem=true; } });
  return tem ? `custo estimado US$ ${t.toFixed(4)}` : "";
}

// ---------- Gerar EF ----------
function tplMMGerar(){ return `
  <div class="devform">
    <label class="fl">Documento do Workshop B <span class="req">obrigatório · .docx ou .pdf</span></label>
    ${efUploadHtml("ws")}
    <div class="frow2" style="margin-top:14px">
      <div><label class="fl">ID GAP <span class="opt">opcional</span></label><input id="mmGap" class="fin" placeholder="ex.: MM-174"></div>
      <div><label class="fl">Descrição do GAP <span class="opt">opcional</span></label><input id="mmDesc" class="fin" placeholder="ex.: Bloqueio de pedido por fornecedor sem certificação"></div>
    </div>
    <div class="frow" style="margin-top:14px"><button class="btn" id="mmGerar" disabled>Gerar rascunho da EF</button></div>
    <p class="fhint">A EF sai no template oficial, como <b>RASCUNHO</b>. Nada é inventado: o que não estiver no workshop aparece como <b>[A CONFIRMAR]</b>, destacado em amarelo no Word, pra você completar.</p>
  </div><div id="devout"></div>`; }

function wireMMGerar(){
  wireEFUpload("ws", ["#mmGerar"]);
  $("#mmGerar").onclick = async ()=>{
    const ws=efState.ws; if(!ws){ outErr("Envie o documento do Workshop B."); return; }
    outLoading(`Lendo ${ws.filename} e montando o rascunho da EF…`);
    try{
      const r = await devPost("/api/c/funcional-mm/ef/gerar", {project_id:PID(), workshop_id:ws.ef_id,
                               id_gap:$("#mmGap").value.trim(), descricao:$("#mmDesc").value.trim(), modulo:"MM"});
      const k=r.contagem||{};
      out(`<div class="devcard"><div class="ch">Rascunho gerado a partir de ${esc(r.workshop)} · artefato salvo</div>
        ${downloadsHtml(r.downloads, {docx:"Baixar rascunho (Word)", md:"Baixar resumo"})}
        <div class="mmstats">
          <div><b>${k.objetos||0}</b><span>objetos</span></div><div><b>${k.regras||0}</b><span>regras</span></div>
          <div><b>${k.fluxo||0}</b><span>passos de fluxo</span></div><div><b>${k.testes||0}</b><span>testes</span></div>
          <div class="warn"><b>${r.a_confirmar||0}</b><span>a confirmar</span></div></div>
        ${r.observacoes?`<p class="mmobs">${esc(r.observacoes)}</p>`:""}
        ${(r.pontos_a_confirmar||[]).length?`<div class="fl" style="margin-top:12px">Pontos a confirmar com o negócio</div>
          <ul class="mmlist">${r.pontos_a_confirmar.map(p=>`<li>${esc(p)}</li>`).join("")}</ul>`:""}
        <p class="fhint">Completou o rascunho? Manda na aba <b>Validar EF</b>.</p>
        ${usoLinha(r.uso_ia)}</div>`);
    }catch(e){ outErr(e.message); }
  };
}

function usoLinha(u){
  if(!u || !u.tokens) return "";
  const t=u.tokens, n=x=>Number(x||0).toLocaleString("pt-BR");
  return `<div class="uso">IA: ${u.chamadas||1} chamada(s) · entrada ${n(t.input)} · saída ${n(t.output)}${u.custo_estimado_usd!=null?` · custo US$ ${Number(u.custo_estimado_usd).toFixed(4)}`:""}</div>`;
}

// ---------- Validar EF ----------
function tplMMValidar(){ return `
  <div class="devform">
    <label class="fl">EF — Especificação Funcional <span class="req">obrigatória · .docx ou .pdf</span></label>
    ${efUploadHtml("val")}
    <div class="frow2" style="margin-top:14px">
      <div><label class="fl">Estado da EF</label>
        <select id="mmEstado" class="fin"><option value="RASCUNHO">Rascunho</option><option value="EM_REVISAO">Em revisão</option><option value="APROVADA">Aprovada</option></select></div>
      <div><label class="fl">Ler imagens</label>
        <select id="mmImg" class="fin"><option value="esbocos">Só esboços de tela</option><option value="todas">Todas as imagens</option><option value="nenhuma">Nenhuma</option></select></div>
    </div>
    <div class="frow" style="margin-top:14px"><button class="btn" id="mmValidar" disabled>Validar EF</button></div>
    <p class="fhint">Cada seção é conferida com a regra dela (dá pra editar em <b>Regras por seção</b>). O resultado vem em linguagem de gente, com o que falta e a sugestão de texto pra EF.</p>
  </div><div id="devout"></div>`; }

function wireMMValidar(){
  wireEFUpload("val", ["#mmValidar"]);
  $("#mmValidar").onclick = async ()=>{
    const ef=efState.val; if(!ef){ outErr("Envie a EF (.docx ou .pdf)."); return; }
    outLoading(`Validando ${ef.filename} seção por seção…`);
    try{
      const r = await devPost("/api/c/funcional-mm/ef/validar", {project_id:PID(), ef_id:ef.ef_id,
                               estado:$("#mmEstado").value, imagens:$("#mmImg").value});
      out(mmResultado(r));
      if(r.pode_enviar){
        const box=document.createElement("div"); box.className="frow"; box.style.marginTop="14px";
        box.innerHTML=`<button class="btn" id="mmEnviar">Enviar para o desenvolvimento</button><span class="fhint" style="margin:0 0 0 12px">Cria o handoff para o Desenvolvedor ABAP (Etapa 2), com esta mesma EF.</span>`;
        $("#devout .devcard").appendChild(box);
        $("#mmEnviar").onclick=async ()=>{
          try{ const e=await devPost("/api/c/funcional-mm/ef/enviar",{project_id:PID(), artifact_id:r.artifact_id});
            box.innerHTML=`<div class="fhint" style="color:var(--ok)">✓ Enviada! Handoff criado para o Desenvolvedor ABAP${e.gap_id?` (GAP ${esc(e.gap_id)})`:""}.</div>`; }
          catch(err){ outErr(err.message); }
        };
      }
      document.querySelectorAll(".mmsec-h").forEach(h=>h.onclick=()=>h.parentElement.classList.toggle("open"));
    }catch(e){ outErr(e.message); }
  };
}

function mmResultado(r){
  const gcls = r.gate==="VALIDO_PARA_DESCOBERTA"?"ok":(r.gate==="INVALIDO_PARA_DESCOBERTA"?"bad":"mid");
  const gtxt = {ok:"Tá redondinha! Pode seguir.", mid:"Dá pra seguir, mas tem ajuste a fazer.", bad:"Ainda não dá pra seguir: tem coisa travando."}[gcls];
  const secs = (r.secoes||[]).filter(x=>x.status!=="NAO_SE_APLICA");
  const cont = st => secs.filter(x=>x.status===st).length;
  const conf = (r.a_confirmar||[]).map(a=>`<div class="mmconf"><b>🤔 ${esc(a.codigo)} — ${esc(a.descricao)}</b><div>${esc(a.evidencia)}</div><div class="fhint">A IA achou sensível. Você decide se procede.</div></div>`).join("");
  const bloq = (r.bloqueantes||[]).map(b=>`<div class="mmconf bad"><b>🚧 ${esc(b.codigo)} — ${esc(b.descricao)}</b><div>${esc(b.evidencia)}</div></div>`).join("");
  const cards = secs.map(x=>`
    <div class="mmsec st-${x.status}${x.status==="CRITICO"?" open":""}">
      <div class="mmsec-h"><span class="ico">${MM_ICO[x.status]||""}</span><b>${esc(x.titulo)}</b>
        <span class="tag">${MM_ROT[x.status]||x.status}</span>${x.origem==="regra"?`<span class="tag ghost">regra</span>`:""}
        <span class="res">${esc(x.resumo||"")}</span><span class="chev">▾</span></div>
      <div class="mmsec-b">
        ${x.onde?`<div class="fhint">Onde: ${esc(x.onde)}</div>`:""}
        ${(x.achados||[]).map((a,i)=>`<div class="mmach">
          <div><span class="tipo t-${a.tipo}">${MM_TIPO[a.tipo]||a.tipo}</span> ${esc(a.descricao)}</div>
          ${a.trecho?`<div class="trecho">“${esc(a.trecho)}”${a.trecho_confirmado===false?` <em>(não achei esse trecho na EF, confere)</em>`:""}</div>`:""}
          ${a.sugestao?`<div class="sug"><span>Sugestão pra EF</span>${esc(a.sugestao)}</div>`:""}
        </div>`).join("") || `<div class="fhint">Nada a apontar. 👏</div>`}
      </div></div>`).join("");
  const u=r.uso_ia||{}, e1=u.etapa1||{}, rv=u.revisao||{};
  return `<div class="devcard">
    <div class="mmgate ${gcls}"><div class="g1">${gcls==="ok"?"🟢":gcls==="bad"?"🔴":"🟡"} ${esc(r.gate.replaceAll("_"," "))}</div><div class="g2">${gtxt}</div></div>
    ${downloadsHtml(r.downloads, {md:"Baixar relatório"})}
    <div class="mmstats">
      <div class="ok"><b>${cont("OK")}</b><span>ok</span></div><div class="warn"><b>${cont("ATENCAO")}</b><span>ajustar</span></div>
      <div class="bad"><b>${cont("CRITICO")}</b><span>crítico</span></div><div><b>${(r.a_confirmar||[]).length}</b><span>a confirmar</span></div></div>
    ${bloq}${conf}
    <div class="fl" style="margin-top:16px">Revisão seção por seção</div>
    <div class="mmsecs">${cards}</div>
    <div class="uso">IA: etapa 1 com ${e1.chamadas||0} chamada(s)${e1.cache?" (cache)":""} · revisão com ${rv.chamadas||0} chamada(s)${rv.cache?" (cache)":""} · ${custoTotal(e1, rv)||"sem custo registrado"}</div>
  </div>`;
}

// ---------- Regras por seção ----------
async function loadMMRegras(){
  try{
    const regras = await api(`/api/c/funcional-mm/secoes?project_id=${PID()}`);
    $("#mmregras").innerHTML = `<p class="fhint" style="margin:0 0 14px">Cada seção da EF é validada com o prompt dela. Edite, salve e a próxima validação já usa a regra nova. <b>Obrigatória</b>: vale para toda EF. <b>Condição</b>: a seção passa a ser exigida quando o tipo de programa marcado no Resumo contém essas palavras (ex.: <code>interface|migra</code>).</p>` +
      regras.map(r=>`
      <div class="mmrule${r.ativo?"":" off"}" data-id="${r.id}">
        <div class="mmrule-h">
          <b>${esc(r.titulo)}</b>
          ${r.obrigatoria?`<span class="tag">obrigatória</span>`:(r.condicao?`<span class="tag ghost">condição: ${esc(r.condicao)}</span>`:`<span class="tag ghost">opcional</span>`)}
          ${r.editado?`<span class="tag edit">editada</span>`:""}
        </div>
        <textarea class="fta mmprompt" rows="4">${esc(r.prompt)}</textarea>
        <div class="mmrule-f">
          <label><input type="checkbox" class="mmativo" ${r.ativo?"checked":""}> validar esta seção</label>
          <label><input type="checkbox" class="mmobrig" ${r.obrigatoria?"checked":""}> obrigatória</label>
          <label>condição <input class="fin mmcond" value="${esc(r.condicao||"")}" placeholder="ex.: fiori"></label>
          <span class="sp"></span>
          ${r.editado?`<button class="btn ghost mmrest">Restaurar padrão</button>`:""}
          <button class="btn mmsave">Salvar</button>
        </div>
      </div>`).join("");
    document.querySelectorAll(".mmrule").forEach(card=>{
      const id=card.dataset.id;
      card.querySelector(".mmsave").onclick = async ()=>{
        try{
          await devPut(`/api/c/funcional-mm/secoes/${id}`, {project_id:PID(), prompt:card.querySelector(".mmprompt").value,
            ativo:card.querySelector(".mmativo").checked, obrigatoria:card.querySelector(".mmobrig").checked,
            condicao:card.querySelector(".mmcond").value.trim()});
          loadMMRegras();
        }catch(e){ outErr(e.message); }
      };
      const rest=card.querySelector(".mmrest");
      if(rest) rest.onclick = async ()=>{ try{ await devPost(`/api/c/funcional-mm/secoes/${id}/restaurar`,{project_id:PID()}); loadMMRegras(); }catch(e){ outErr(e.message); } };
    });
  }catch(e){ $("#mmregras").innerHTML=`<div class="msg err">${esc(e.message)}</div>`; }
}

function tplMMAnalisar(){ return `
  <div class="devform">
    <label class="fl">Pergunte ao Consultor MM sobre o ambiente</label>
    <textarea id="mmPerg" class="fta" rows="3" placeholder="Ex.: Quais tipos de pedido de compra existem e quais são custom? · Como está a estratégia de liberação? · Quais centros pertencem à organização de compras 1000?"></textarea>
    <div class="frow" style="margin-top:10px"><button class="btn" id="mmPergBtn">Perguntar</button>
      <span class="fhint" style="margin:0 0 0 12px">A IA consulta o SAP conectado (configuração, objetos e where-used) e responde com o que encontrou.</span></div>
  </div>
  <div id="mmResp"></div>
  <div class="fl" style="margin:22px 0 10px">Análises rápidas de configuração</div>
  <div class="mmcards" id="mmCards"><div class="devcard loading2"><span class="spin2"></span>Carregando…</div></div>
  <div class="devform" style="margin-top:18px">
    <label class="fl">Consultar uma tabela de configuração</label>
    <div class="frow"><input id="mmTab" class="fin" style="max-width:260px" placeholder="ex.: T161, T156, T001W">
      <button class="btn ghost" id="mmTabBtn">Consultar</button></div>
    <p class="fhint">Só tabelas de <b>configuração</b> são lidas: a classe de entrega é conferida no SAP, e tabelas de cadastro ou movimento (classe A) são recusadas. Até 500 linhas.</p>
  </div>
  <div id="devout"></div>`; }

async function wireMMAnalisar(){
  $("#mmPergBtn").onclick = mmPerguntar;
  $("#mmPerg").addEventListener("keydown", e=>{ if(e.key==="Enter" && (e.ctrlKey||e.metaKey)) mmPerguntar(); });
  $("#mmTabBtn").onclick = async ()=>{
    const t=$("#mmTab").value.trim(); if(!t){ outErr("Informe a tabela."); return; }
    outLoading(`Lendo ${t.toUpperCase()} no SAP…`);
    try{ const d=await devPost("/api/c/funcional-mm/tabela",{project_id:PID(), tabela:t}); out(cfgBlocosHtml([d])); wireCsv([d]); }
    catch(e){ outErr(e.message); }
  };
  $("#mmTab").addEventListener("keydown", e=>{ if(e.key==="Enter") $("#mmTabBtn").click(); });
  try{
    const lista = await api("/api/c/funcional-mm/analises");
    $("#mmCards").innerHTML = lista.map(a=>`<button class="mmcard" data-id="${a.id}">
        <b>${esc(a.titulo)}</b><span>${esc(a.descricao)}</span><em>${a.tabelas.map(esc).join(" · ")}</em></button>`).join("");
    document.querySelectorAll(".mmcard").forEach(c=>c.onclick = async ()=>{
      outLoading(`Lendo ${c.querySelector("b").textContent} no SAP…`);
      try{
        const r = await devPost(`/api/c/funcional-mm/analises/${c.dataset.id}`, {project_id:PID()});
        out(`<div class="devcard"><div class="ch">${esc(r.titulo)}</div><p class="fhint" style="margin-top:0">${esc(r.descricao)}</p>${cfgBlocosHtml(r.blocos)}</div>`);
        wireCsv(r.blocos);
      }catch(e){ outErr(e.message); }
    });
  }catch(e){ $("#mmCards").innerHTML = `<div class="msg err">${esc(e.message)}</div>`; }
}

function cfgBlocosHtml(blocos){
  return blocos.map((b,i)=>{
    if(b.erro) return `<div class="cfgblk"><div class="cfgh"><b>${esc(b.titulo||b.table)}</b><span class="tag">${esc(b.table)}</span></div><div class="msg err">${esc(b.erro)}</div></div>`;
    const cols=b.columns||[], rows=b.rows||[];
    return `<div class="cfgblk">
      <div class="cfgh"><b>${esc(b.titulo||b.table)}</b><span class="tag">${esc(b.table)}</span>
        ${b.delivery_class?`<span class="tag ghost">classe ${esc(b.delivery_class)}</span>`:""}
        <span class="cnt">${rows.length}${b.truncated?` de ${b.total}`:""} linha(s)</span>
        <button class="btn ghost cfgcsv" data-i="${i}">⬇ CSV</button></div>
      ${b.aviso?`<div class="fhint">${esc(b.aviso)}</div>`:""}
      ${rows.length?`<div class="tblwrap"><table class="cfgtbl"><thead><tr>${cols.map(c=>`<th title="${esc(c.description||"")}">${esc(c.name)}<small>${esc(c.description||"")}</small></th>`).join("")}</tr></thead>
        <tbody>${rows.map(r=>`<tr>${cols.map(c=>`<td>${esc(r[c.name]??"")}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`
        :`<div class="fhint">Tabela sem registros neste ambiente.</div>`}
    </div>`;
  }).join("");
}

function wireCsv(blocos){
  document.querySelectorAll(".cfgcsv").forEach(btn=>btn.onclick=()=>{
    const b=blocos[+btn.dataset.i]; if(!b||!b.columns) return;
    const q=v=>`"${String(v??"").replace(/"/g,'""')}"`;
    const csv=[b.columns.map(c=>q(c.name)).join(";"), ...b.rows.map(r=>b.columns.map(c=>q(r[c.name])).join(";"))].join("\r\n");
    const a=document.createElement("a");
    a.href=URL.createObjectURL(new Blob(["\ufeff"+csv],{type:"text/csv;charset=utf-8"}));
    a.download=`${b.table}.csv`; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href),2000);
  });
}

async function mmPerguntar(){
  const perg=$("#mmPerg").value.trim(); if(!perg) return;
  const c=state.consultores.find(x=>x.key==="funcional-mm");
  if(!c){ $("#mmResp").innerHTML=`<div class="msg err">Consultor MM não encontrado no projeto.</div>`; return; }
  const btn=$("#mmPergBtn"); btn.disabled=true;
  $("#mmResp").innerHTML=`<div class="devcard loading2"><span class="spin2"></span>Consultando o SAP…</div>`;
  try{
    if(!mmConv){ const cv=await devPost("/api/plataforma/conversations",{project_id:PID(), profile_id:c.profile_id, title:"Análise MM"}); mmConv=cv.id; }
    const r=await devPost(`/api/plataforma/conversations/${mmConv}/chat`,{message:perg});
    const fontes=(r.steps||[]).map(s=>s.tool).filter(Boolean);
    $("#mmResp").innerHTML=`<div class="devcard mmans"><div class="fl">Pergunta</div><p class="mmq">${esc(perg)}</p>
      <div class="fl">Resposta</div><div class="md">${mdLite(r.reply)}</div>
      ${fontes.length?`<div class="ev">consultou: ${[...new Set(fontes)].map(esc).join(", ")}</div>`:""}
      ${typeof usoHtml==="function"?usoHtml(r.uso_ia):""}</div>`;
  }catch(e){ $("#mmResp").innerHTML=`<div class="msg err">${esc(e.message)}</div>`; }
  finally{ btn.disabled=false; }
}

export async function mount(area, ctx){
  CTX = ctx; AREA = area;
  ({$, el, esc, api, post: devPost, put: devPut, out, outLoading, outErr, efUploadHtml, wireEFUpload, efState,
    fmtSize, downloadsHtml, usoHtml, mdLite} = ctx.ui);
  state = {consultores: ctx.consultores, project: ctx.projeto, environments: ctx.ambientes};
  PID = () => ctx.projeto && ctx.projeto.id;
  renderMM();
}

export function unmount(){}
