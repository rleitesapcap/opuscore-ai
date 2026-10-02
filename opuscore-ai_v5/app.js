// ============ OPUSCORE-AI — app shell + views (mesma origem do backend) ============
const API = "";
const $ = s => document.querySelector(s);
const el = (h) => { const t=document.createElement("template"); t.innerHTML=h.trim(); return t.content.firstChild; };
const esc = s => String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
async function api(path, opts){ const r = await fetch(API+path, opts); const txt = await r.text();
  let data; try{data=JSON.parse(txt);}catch{data=txt;} if(!r.ok) throw new Error((data&&data.detail)||txt||r.status); return data; }

const COLOR = {orquestrador:"#ff7a6b",arquiteto:"#2fe0b0","funcional-sd":"#ffb347",integracao:"#9a7bff","lider-tecnico":"#4bc0ff","dev-abap":"#2fe0b0",qualidade:"#ff6b8f"};
const G = {
  orquestrador:'<path d="M12 4v6M6 20l6-8 6 8"/><circle cx="12" cy="4" r="2"/><circle cx="6" cy="20" r="2"/><circle cx="18" cy="20" r="2"/>',
  arquiteto:'<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M12 3v18M4 7.5l8 4.5 8-4.5"/>',
  "funcional-sd":'<path d="M5 4h11a2 2 0 0 1 2 2v14H7a2 2 0 0 1-2-2z"/><path d="M9 8h6M9 12h6"/>',
  integracao:'<circle cx="6" cy="6" r="2"/><circle cx="18" cy="18" r="2"/><path d="M8 6h6a4 4 0 0 1 4 4v6"/>',
  "lider-tecnico":'<path d="M12 3l7 3v6c0 4-3 7-7 9-4-2-7-5-7-9V6z"/><path d="M9 12l2 2 4-4"/>',
  "dev-abap":'<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/>',
  qualidade:'<circle cx="12" cy="12" r="8"/><path d="M8.5 12l2.5 2.5 5-5"/>',
};
const icon = (key,color) => `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="${color||'#9fb4bc'}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${G[key]||G.arquiteto}</svg>`;
const cico = (key) => `<span class="cico" style="background:${(COLOR[key]||'#2fe0b0')}1a">${icon(key,COLOR[key])}</span>`;

const state = { me:null, project:null, consultores:[], environments:[], sel:null, conv:null, convs:[] };

// ---------- boot ----------
async function boot(){
  try{
    state.me = await api("/api/me");
    const projs = await api("/api/projects");
    state.project = projs[0] || null;
    if(state.project){
      state.consultores = await api(`/api/projects/${state.project.id}/consultores`);
      state.environments = await api(`/api/projects/${state.project.id}/environments`);
    }
  }catch(e){ $("#view").innerHTML = `<div class="msg err">Falha ao carregar: ${esc(e.message)}<br>O backend está rodando?</div>`; return; }
  fillShell();
  updateEnvCard();
  window.addEventListener("hashchange", router);
  if(!location.hash) location.hash = "#/cerebro";
  router();
}

function fillShell(){
  $("#railProjName").textContent = state.project ? state.project.name : "Nenhum projeto";
  $("#railProjSub").textContent = state.project ? (state.project.description||"") : "";
  $("#crumbProj").textContent = state.project ? state.project.name : "—";
  $("#navCount").textContent = state.consultores.length || "";
  const me = state.me||{};
  $("#userName").textContent = me.display_name || "Usuário";
  $("#userRole").textContent = me.role || "";
  $("#userAv").textContent = (me.display_name||"U").split(" ").map(w=>w[0]).slice(0,2).join("").toUpperCase();
}

async function updateEnvCard(){
  const card = $("#envCard");
  const live = state.environments.find(e=>e.live);
  if(!live){ card.className="card-mini env-card"; $("#envName").textContent="Sem ambiente"; $("#envSub").textContent="cadastre um ambiente"; return; }
  $("#envName").textContent = live.name;
  try{
    const h = await fetch(API+"/health");
    if(h.ok){ card.className="card-mini env-card up"; $("#envSub").textContent="somente leitura · conectado"; }
    else { card.className="card-mini env-card down"; $("#envSub").textContent="sem conexão com o SAP"; }
  }catch{ card.className="card-mini env-card down"; $("#envSub").textContent="backend offline"; }
}

// ---------- router ----------
function parseHash(){ const [path,q]=location.hash.replace(/^#\//,"").split("?"); const params=Object.fromEntries(new URLSearchParams(q||"")); return {path:path||"cerebro",params}; }
function router(){
  const {path,params} = parseHash();
  document.querySelectorAll("#nav a").forEach(a=>a.classList.toggle("on", a.dataset.v===path));
  if(path==="consultores") return renderConsultores();
  if(path==="chat") return renderChat(params.p);
  if(path==="dev") return renderDev();
  return renderCerebro(params.c);
}

// ---------- Cérebro ----------
let cerebroMode = "geral";
function renderCerebro(selKey){
  const v = $("#view");
  const n = state.consultores.length;
  v.innerHTML = `
    <p class="eyebrow">Visão do projeto</p>
    <div class="cerebro-head">
      <div><h2 class="title">${cerebroMode==="geral"?"Cérebro do projeto":"Mapa do consultor"}</h2>
        <p class="lead">Consultores, conhecimento e decisões conectados no mesmo projeto.</p></div>
      <div class="metrics"><span><b>${n}</b>consultores</span><span><b>3</b>análises</span><span><b>2</b>gates</span></div>
    </div>
    <div class="toggle" id="ctoggle">
      <button data-m="geral" class="${cerebroMode==="geral"?"on":""}">⬡ Geral</button>
      <button data-m="consultor" class="${cerebroMode==="consultor"?"on":""}">◈ Consultor</button>
    </div>
    <div class="cerebro">
      <div class="stage-graph" id="graph">
        <div class="grid-bg"></div>
        <div class="legend2"><span><span class="d" style="background:#2fe0b0"></span>Projeto</span>
          <span><span class="d" style="background:#9a7bff"></span>Agente</span>
          <span><span class="d" style="background:#ffb347"></span>Ambiente</span></div>
      </div>
      <div class="side-detail" id="detail"></div>
      <div class="flow">
        <span style="color:var(--muted)">⤳ Fluxo do projeto</span>
        <span class="step done"><span class="d"></span>Workshop B</span><span class="arw">→</span>
        <span class="step cur"><span class="d"></span>Arquitetura</span><span class="arw">→</span>
        <span class="step"><span class="d"></span>EF preliminar</span><span class="arw">→</span>
        <span class="step"><span class="d"></span>Revisão técnica</span>
      </div>
    </div>`;
  $("#ctoggle").querySelectorAll("button").forEach(b=>b.onclick=()=>{cerebroMode=b.dataset.m; renderCerebro(state.sel&&state.sel.key);});
  const graph = $("#graph");
  const nodes = cerebroMode==="geral" ? state.consultores.map(c=>({key:c.key,nm:c.name,sp:c.role,data:c,color:COLOR[c.key]}))
    : [
      {key:"skills",nm:"Skills",sp:"Capacidades",color:"#2fe0b0"},
      {key:"rag",nm:"RAG privado",sp:"Conhecimento",color:"#ffb347"},
      {key:"ctx",nm:"Contexto global",sp:"Projeto",color:"#2fe0b0"},
      {key:"amb",nm:"Ambientes SAP",sp:"Consulta",color:"#9a7bff"},
      {key:"task",nm:"Tarefas",sp:"Trabalho atual",color:"#8aa0a8"},
      {key:"ho",nm:"Handoffs",sp:"Próxima etapa",color:"#8aa0a8"},
    ];
  const centerName = cerebroMode==="geral" ? (state.project?state.project.name:"Projeto") : (state.sel?state.sel.name:"Consultor");
  // brain + linhas
  const cx=50, cy=47, rx=33, ry=30;
  const svgLines = nodes.map((_,i)=>{const a=(-90 + i*(360/nodes.length))*Math.PI/180; const x=cx+rx*Math.cos(a), y=cy+ry*Math.sin(a);
    return `<line x1="${cx}" y1="${cy}" x2="${x}" y2="${y}" class="flowline" vector-effect="non-scaling-stroke"/>`;}).join("");
  graph.insertAdjacentHTML("beforeend", `<svg style="position:absolute;inset:0;width:100%;height:100%" viewBox="0 0 100 100" preserveAspectRatio="none">${svgLines}</svg>`);
  graph.insertAdjacentHTML("beforeend", `<div class="brain">
    <svg width="150" height="120" viewBox="0 0 150 120" fill="none" stroke="#2fe0b0" stroke-width="1.4" opacity="0.9">
      <path d="M75 22c-10-10-30-8-36 6-12 2-16 16-8 25-6 10 2 24 15 23 5 8 20 8 29 2 9 6 24 6 29-2 13 1 21-13 15-23 8-9 4-23-8-25-6-14-26-16-36-6z"/>
      <circle cx="60" cy="55" r="1.6" fill="#2fe0b0"/><circle cx="90" cy="55" r="1.6" fill="#2fe0b0"/><circle cx="75" cy="70" r="1.6" fill="#2fe0b0"/><circle cx="75" cy="45" r="1.6" fill="#2fe0b0"/>
    </svg>
    <div class="lbl">Inteligência do projeto</div><div class="pj">${esc(centerName)}</div>
    <div class="cc">${cerebroMode==="geral"?state.consultores.length+" consultores conectados":"conhecimento do agente"}</div>
  </div>`);
  nodes.forEach((nd,i)=>{const a=(-90 + i*(360/nodes.length))*Math.PI/180; const x=cx+rx*Math.cos(a), y=cy+ry*Math.sin(a);
    const card = el(`<div class="ncard" style="left:${x}%;top:${y}%;--nc:${nd.color||'#34e6bd'}">${cico(nd.key)}<div><div class="nm">${esc(nd.nm)}</div><div class="sp">${esc(nd.sp)}</div></div></div>`);
    if(nd.data) card.onclick=()=>{ state.sel=nd.data; showDetail(nd.data); document.querySelectorAll(".ncard").forEach(c=>c.classList.remove("sel")); card.classList.add("sel"); };
    graph.appendChild(card);
  });
  // detalhe inicial
  const initial = state.sel || (state.consultores.find(c=>c.key===selKey)) || state.consultores[1] || state.consultores[0];
  if(initial){ state.sel=initial; showDetail(initial); }
}
function showDetail(c){
  const envs = state.environments.map(e=>`<div class="kv">${esc(e.name)}<span class="r">${e.live?"Exemplo":"Cadastro"}</span></div>`).join("");
  $("#detail").innerHTML = `
    <p class="k">Consultor selecionado</p>
    <h3>${cico(c.key)} ${esc(c.name)}</h3><div class="sub">${esc(c.specialty||"")}</div>
    <p>${esc(c.role||"")} — atua no ${esc(state.project?state.project.name:"projeto")}.</p>
    <p class="k">Em andamento</p><div class="kv">${esc(c.current_work||"—")}<span class="r">${esc(state.project?state.project.name:"")}</span></div>
    <p class="k">Conhecimento</p>
    <div class="kv">Contexto global do projeto<span class="r">Compartilhado</span></div>
    <div class="kv">RAG do consultor<span class="r">Privado</span></div>
    <p class="k">Ambientes disponíveis</p>${envs||'<div class="kv">nenhum<span class="r"></span></div>'}
    <div class="cta"><button class="btn" onclick="location.hash='#/chat?p=${c.profile_id}'">💬 Conversar</button>
      <button class="btn ghost" onclick="(function(){window.__c='${c.key}';})();location.hash='#/cerebro'">Ver mapa</button></div>`;
}

// ---------- Consultores ----------
function renderConsultores(){
  const rows = state.consultores.map(c=>`
    <div class="crow">
      ${cico(c.key)}
      <div class="id"><div class="nm">${esc(c.name)}</div><div class="sp">${esc(c.specialty||"")}</div></div>
      <div class="work">${esc(c.current_work||"")}</div>
      <div class="role">${esc(c.role||"")}</div>
      <div class="st ${c.status_label==="Em análise"?"analise":""}"><span class="d"></span>${esc(c.status_label||"Ativo")}</div>
      <div class="acts"><button class="iconbtn" title="Ver mapa" onclick="location.hash='#/cerebro?c=${c.key}'">◈</button>
        ${c.key==="dev-abap"?`<button class="btn" onclick="location.hash='#/dev'">Abrir</button>`:``}
        <button class="btn ghost" onclick="location.hash='#/chat?p=${c.profile_id}'">Conversar</button></div>
    </div>`).join("");
  $("#view").innerHTML = `
    <p class="eyebrow">Equipe do projeto</p>
    <h2 class="title">Consultores</h2>
    <p class="lead">Escolha um especialista para explorar seu mapa ou iniciar uma conversa.</p>
    <div class="searchbar"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#5f757e" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
      <input id="cq" placeholder="Buscar consultor ou especialidade"></div>
    <span class="rowcount">${state.consultores.length} consultores</span>
    <div class="clist" id="clist">${rows}</div>`;
  $("#cq").addEventListener("input",e=>{const q=e.target.value.toLowerCase();
    document.querySelectorAll("#clist .crow").forEach((r,i)=>{const c=state.consultores[i];
      r.style.display = (c.name+c.specialty+c.role).toLowerCase().includes(q)?"":"none";});});
}

// ---------- Chat ----------
async function renderChat(profileId){
  state.sel = state.consultores.find(c=>c.profile_id===profileId) || state.sel || state.consultores[0];
  const c = state.sel;
  if(!c){ $("#view").innerHTML='<div class="lead">Nenhum consultor no projeto.</div>'; return; }
  const envOpts = ['<option value="docs">Documentos do projeto</option>']
    .concat(state.environments.map(e=>`<option value="${e.id}">${esc(e.name)}</option>`)).join("");
  const fontes = `<div class="item"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#8aa0a8" stroke-width="1.6"><path d="M5 4h11l3 3v13H5z"/></svg> Documentos do projeto<span class="tag">RAG</span></div>`;
  const ambientes = state.environments.map(e=>`<div class="item ${e.live?"live":""}"><span class="di"></span>${esc(e.name)}<span class="tag">${e.live?"somente leitura":"cadastro"}</span></div>`).join("");
  // view desce fora do padding padrão
  $("#view").style.padding="0"; $("#view").innerHTML = `
    <div class="chatwrap">
      <div class="hist">
        <div class="h"><div><div class="ey">Histórico</div><div class="t">Conversas</div></div><button class="new" id="newConv">+</button></div>
        <div class="search"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#5f757e" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg><input placeholder="Buscar conversa" id="convq"></div>
        <div id="convList"></div>
      </div>
      <div class="chatmain">
        <div class="chathead">${cico(c.key)}<div><div class="ey" style="color:var(--accent)">Consultor do projeto</div><div class="nm">${esc(c.name)}</div><div class="sp">${esc(c.specialty||"")}</div></div>
          <select id="consultorPick" style="margin-left:auto;background:var(--bg2);border:1px solid var(--line2);color:var(--text);border-radius:8px;padding:7px 9px;font-size:12px">
            ${state.consultores.map(x=>`<option value="${x.profile_id}" ${x.profile_id===c.profile_id?"selected":""}>${esc(x.name)}</option>`).join("")}
          </select>
        </div>
        <div class="chatlog" id="chatlog"></div>
        <div class="composer">
          <div class="box"><textarea id="chatq" rows="1" placeholder="Peça uma análise ou faça uma pergunta ao consultor…"></textarea>
            <div class="row">
              <button class="iconbtn" title="Anexar" style="width:30px;height:30px">📎</button>
              <select id="envPick">${envOpts}</select>
              <button class="send" id="chatsend">↑</button>
            </div></div>
          <div class="note">As consultas ao SAP são somente leitura e ficam registradas em auditoria.</div>
        </div>
      </div>
      <div class="ctx">
        <div class="k">Contexto</div><h3>${esc(c.name)}</h3><div class="sub">${esc(c.role||"")}</div>
        <div class="k">Escopo deste consultor</div><p>${esc(c.specialty||"")} — ${esc(c.current_work||"")}</p>
        <div class="k">Fontes disponíveis</div>${fontes}
        <div class="k">Ambientes do projeto</div>${ambientes||'<p>nenhum</p>'}
        <div class="k">Trabalho atual</div><p>${esc(c.current_work||"—")}</p>
      </div>
    </div>`;
  $("#consultorPick").onchange = e=>location.hash=`#/chat?p=${e.target.value}`;
  $("#newConv").onclick = ()=>{ state.conv=null; renderEmpty(); loadConvs(); };
  $("#chatsend").onclick = sendChat;
  const ta=$("#chatq"); ta.addEventListener("input",()=>{ta.style.height="auto";ta.style.height=Math.min(ta.scrollHeight,120)+"px";});
  ta.addEventListener("keydown",e=>{ if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();sendChat();} });
  await loadConvs();
  renderEmpty();
}
function renderEmpty(){
  const c=state.sel;
  $("#chatlog").innerHTML = `<div class="empty"><div class="bi">${icon(c.key,COLOR[c.key])}</div>
    <h3>Converse com ${esc(c.name)}</h3><div>Escolha um assunto para começar.</div>
    <div class="suggest">
      <button onclick="quick(this)">Analise a tabela MARA <span>→</span></button>
      <button onclick="quick(this)">Faça o where-used de um objeto <span>→</span></button>
    </div></div>`;
}
window.quick = (b)=>{ $("#chatq").value=b.childNodes[0].textContent.trim(); sendChat(); };
async function loadConvs(){
  try{ state.convs = await api(`/api/projects/${state.project.id}/conversations?profile_id=${state.sel.profile_id}`); }
  catch{ state.convs=[]; }
  const list=$("#convList"); if(!list) return;
  list.innerHTML = state.convs.map(cv=>`<div class="convo ${state.conv===cv.id?"on":""}" data-id="${cv.id}">
    <div class="t">${esc(cv.title||"Conversa")}</div><div class="m">${new Date(cv.updated_at).toLocaleString("pt-BR")}</div></div>`).join("")
    || '<div class="m" style="color:var(--faint);padding:8px">Nenhuma conversa ainda.</div>';
  list.querySelectorAll(".convo").forEach(x=>x.onclick=()=>openConv(x.dataset.id));
}
async function openConv(cid){
  state.conv=cid; document.querySelectorAll(".convo").forEach(x=>x.classList.toggle("on",x.dataset.id===cid));
  const msgs = await api(`/api/conversations/${cid}/messages`);
  const log=$("#chatlog"); log.innerHTML="";
  if(!msgs.length){ renderEmpty(); return; }
  msgs.forEach(m=>addMsg(m.role==="user"?"user":"bot", m.content, m.evidence));
}
function addMsg(role,text,evidence){
  const log=$("#chatlog"); if(log.querySelector(".empty")) log.innerHTML="";
  const steps = evidence && evidence.steps && evidence.steps.length ? `<div class="ev">evidência: ${evidence.steps.map(s=>esc(s.tool)).join(", ")}</div>` : "";
  const d=el(`<div class="msg ${role}">${esc(text)}${steps}</div>`); log.appendChild(d); log.scrollTop=log.scrollHeight; return d;
}
async function sendChat(){
  const ta=$("#chatq"); const text=ta.value.trim(); if(!text) return;
  ta.value=""; ta.style.height="auto";
  if($("#chatlog").querySelector(".empty")) $("#chatlog").innerHTML="";
  addMsg("user",text);
  const thinking=el(`<div class="msg think">consultando…</div>`); $("#chatlog").appendChild(thinking);
  $("#chatsend").disabled=true;
  try{
    if(!state.conv){ const cv=await api("/api/conversations",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({project_id:state.project.id,profile_id:state.sel.profile_id,title:"Nova conversa"})}); state.conv=cv.id; }
    const env=$("#envPick")?$("#envPick").value:"docs";
    const res=await api(`/api/conversations/${state.conv}/chat`,{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({message:text, environment_id: env==="docs"?null:env})});
    thinking.remove();
    addMsg("bot",res.reply,{steps:res.steps});
    loadConvs();
  }catch(e){ thinking.remove(); addMsg("err",e.message); }
  finally{ $("#chatsend").disabled=false; }
}

// reset padding ao sair do chat
const _view=$("#view"); const _obs=new MutationObserver(()=>{ if(!location.hash.startsWith("#/chat")) _view.style.padding=""; });
_obs.observe(_view,{childList:true});

boot();

// ============ Tela do Desenvolvedor ============
let devTab = "analisar";
let etMode = "request";
let etEF = null;   // {ef_id, filename, ext, size, chars, preview}
const PID = () => state.project && state.project.id;
async function devPost(path, body){
  return api(path, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
}
function out(html){ const o=$("#devout"); if(o) o.innerHTML=html; }
function outLoading(msg){ out(`<div class="devcard loading2"><span class="spin2"></span>${esc(msg)}</div>`); }
function outErr(msg){ out(`<div class="msg err">${esc(msg)}</div>`); }

function renderDev(){
  const c = state.consultores.find(x=>x.key==="dev-abap");
  const name = c ? c.name : "Desenvolvedor ABAP";
  $("#view").innerHTML = `
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
      <button data-t="artefatos">Artefatos</button>
    </div>
    <div id="devbody"></div>`;
  $("#devtabs").querySelectorAll("button").forEach(b=>{
    b.classList.toggle("on", b.dataset.t===devTab);
    b.onclick=()=>{ devTab=b.dataset.t; renderDev(); };
  });
  const body=$("#devbody");
  body.innerHTML = ({analisar:tplAnalisar, remediar:tplRemediar, rap:tplRap, et:tplET, artefatos:tplArtefatos}[devTab])();
  wireDev();
}

// ---- Analisar (qualquer objeto SAP) ----
function tplAnalisar(){ return `
  <div class="devform">
    <label class="fl">Objeto SAP</label>
    <div class="frow"><input id="anObj" class="fin" placeholder="ex.: MARA, ZCL_ALGO, ZR_RELATORIO" autocomplete="off">
      <button class="btn" id="anRun">Analisar</button></div>
    <p class="fhint">Qualquer objeto do repositório (standard ou Z), lido via ADT. Traz finalidade, quem usa e veredito Clean Core.</p>
  </div><div id="devout"></div>`; }

// ---- Remediar (a partir da EF) ----
function tplRemediar(){ return `
  <div class="devform">
    <label class="fl">EF — Especificação Funcional</label>
    <textarea id="remEF" class="fta" placeholder="Cole a EF. A plataforma identifica os objetos e busca as dependências Z no S/4."></textarea>
    <div class="frow"><button class="btn" id="remPlan">Descobrir objetos no S/4</button></div>
    <p class="fhint">Nada é remediado agora: primeiro você vê a lista de objetos Z e decide o que entra.</p>
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
    <label class="drop" id="efDrop">
      <input type="file" id="efFile" accept=".docx,.pdf,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" hidden>
      <div class="drop-ic">⇪</div>
      <div class="drop-t">Arraste a EF aqui ou <u>clique para escolher</u></div>
      <div class="drop-s">Somente .docx ou .pdf · até 25 MB · o arquivo é validado antes do uso</div>
    </label>
    <div id="efCard"></div>
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
      try{ const r=await devPost("/api/dev/object-report",{project_id:PID(),object_name:obj}); renderReport(r); }
      catch(e){ outErr(e.message); }
    };
    $("#anObj").addEventListener("keydown",e=>{ if(e.key==="Enter") $("#anRun").click(); });
  }
  else if(devTab==="remediar"){
    $("#remPlan").onclick = async ()=>{
      const ef=$("#remEF").value.trim(); if(!ef){ outErr("Cole a EF."); return; }
      $("#remList").innerHTML=""; outLoading("Descobrindo objetos e dependências Z…");
      try{ const r=await devPost("/api/dev/remediation/plan",{project_id:PID(),ef_text:ef}); out(""); renderCandidates(r); }
      catch(e){ outErr(e.message); }
    };
  }
  else if(devTab==="rap"){
    $("#rapRun").onclick = async ()=>{
      const ef=$("#rapEF").value.trim(); if(!ef){ outErr("Cole a EF."); return; }
      outLoading("Gerando esqueleto RAP…");
      try{ const r=await devPost("/api/dev/rap",{project_id:PID(),ef_text:ef});
        out(`<div class="devcard"><div class="ch">Esqueleto RAP (rascunho) · artefato salvo</div><pre class="code">${esc(r.content||"")}</pre></div>`); }
      catch(e){ outErr(e.message); }
    };
  }
  else if(devTab==="et"){
    $("#etsrc").innerHTML = etSrcHtml();
    wireEFUpload();
    $("#etmode").querySelectorAll("button").forEach(b=>b.onclick=()=>{ etMode=b.dataset.m;
      $("#etmode").querySelectorAll("button").forEach(x=>x.classList.toggle("on",x.dataset.m===etMode)); $("#etsrc").innerHTML=etSrcHtml(); });
    const collect=()=>{
      if(!etEF){ outErr("Envie a EF (.docx ou .pdf) antes de continuar."); return null; }
      if(etMode==="request"){ const rq=$("#etReq").value.trim(); if(!rq){ outErr("Informe a request."); return null; } return {project_id:PID(),ef_id:etEF.ef_id,request_id:rq}; }
      const objs=($("#etList").value||"").split(/[\s,;]+/).filter(Boolean); if(!objs.length){ outErr("Informe ao menos um objeto."); return null; }
      return {project_id:PID(),ef_id:etEF.ef_id,objects:objs};
    };
    $("#etPlan").onclick = async ()=>{ const b=collect(); if(!b) return; $("#etObjs").innerHTML=""; outLoading("Resolvendo objetos…");
      try{ const r=await devPost("/api/dev/et/plan",b); out("");
        $("#etObjs").innerHTML=`<div class="devcard"><div class="ch"><b>${r.count}</b> objeto(s) — origem: ${esc(r.source)}</div>
          <div class="chips">${r.objects.map(o=>`<span class="chip">${esc(o)}</span>`).join("")||"nenhum"}</div></div>`;
      }catch(e){ outErr(e.message); } };
    $("#etRun").onclick = async ()=>{ const b=collect(); if(!b) return; outLoading("Gerando ET (buscando source + IA)…");
      try{ const r=await devPost("/api/dev/et/run",b);
        out(`<div class="devcard"><div class="ch">ET gerada (rc=${r.rc}) · EF: ${esc(r.ef||"")} · artefato salvo</div>
          <div class="fhint">Objetos: ${(r.objects||[]).map(esc).join(", ")}. Arquivos: ${(r.files||[]).map(esc).join(", ")||"—"}</div>
          <pre class="code">${esc((r.log_tail||"").slice(-1500))}</pre></div>`);
      }catch(e){ outErr(e.message); } };
  }
  else if(devTab==="artefatos"){ loadArtifacts(); }
}

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
    <div class="ch"><b>${data.count}</b> objeto(s) Z encontrados — desmarque o que <u>não</u> quer remediar</div>
    <div class="cands">${rows||"<div class='fhint'>Nenhum objeto Z identificado.</div>"}</div>
    ${data.count?`<div class="frow" style="margin-top:12px"><button class="btn" id="remRun">Remediar selecionados</button></div>`:""}</div>`;
  const btn=$("#remRun"); if(btn) btn.onclick=async ()=>{
    const objs=[...document.querySelectorAll("#remList input:checked")].map(x=>x.dataset.nm);
    if(!objs.length){ outErr("Selecione ao menos um objeto."); return; }
    outLoading(`Remediando ${objs.length} objeto(s)…`);
    try{ const r=await devPost("/api/dev/remediation/run",{project_id:PID(),objects:objs});
      out(`<div class="devcard"><div class="ch">Remediação concluída (rc=${r.rc}) · artefato salvo</div>
        <div class="fhint">Arquivos: ${(r.files||[]).map(esc).join(", ")||"—"}</div>
        <pre class="code">${esc((r.log_tail||"").slice(-1500))}</pre></div>`);
    }catch(e){ outErr(e.message); }
  };
}
async function loadArtifacts(){
  try{ const arts=await api(`/api/projects/${PID()}/artifacts`);
    $("#artList").innerHTML = arts.length ? `<div class="devcard"><div class="ch">${arts.length} artefato(s)</div>`+
      arts.map(a=>`<div class="artrow" data-id="${a.id}"><span class="cn">${esc(a.title)}</span><span class="ct2">${esc(a.kind)}</span><span class="tagx">${new Date(a.created_at).toLocaleString("pt-BR")}</span></div>`).join("")+`</div>`
      : `<div class="fhint">Nenhum artefato ainda. Gere uma ET, um RAP ou uma remediação.</div>`;
    document.querySelectorAll(".artrow").forEach(x=>x.onclick=async ()=>{
      const a=await api(`/api/artifacts/${x.dataset.id}`);
      out(`<div class="devcard"><div class="ch">${esc(a.title)} <span class="ct2">${esc(a.kind)}</span></div><pre class="code">${esc(a.content||"")}</pre></div>`);
    });
  }catch(e){ $("#artList").innerHTML=`<div class="msg err">${esc(e.message)}</div>`; }
}


// ---- Upload da EF (validação no navegador + no servidor) ----
const EF_OK_EXT = [".docx", ".pdf"];
const EF_MAX = 25 * 1024 * 1024;
function fmtSize(b){ return b>1048576 ? (b/1048576).toFixed(1)+" MB" : Math.max(1,Math.round(b/1024))+" KB"; }
function setETButtons(on){ ["#etPlan","#etRun"].forEach(id=>{ const b=$(id); if(b) b.disabled=!on; }); }
function renderEFCard(){
  const card=$("#efCard"); if(!card) return;
  if(!etEF){ card.innerHTML=""; setETButtons(false); $("#efDrop").style.display=""; return; }
  $("#efDrop").style.display="none";
  card.innerHTML = `<div class="efcard">
    <div class="ef-ic">${etEF.ext===".pdf"?"PDF":"DOCX"}</div>
    <div class="ef-info"><div class="ef-nm">${esc(etEF.filename)}</div>
      <div class="ef-meta">✓ validada · ${fmtSize(etEF.size)} · ${etEF.chars.toLocaleString("pt-BR")} caracteres de texto</div>
      <div class="ef-prev">${esc(etEF.preview.slice(0,240))}${etEF.preview.length>240?"…":""}</div></div>
    <button class="iconbtn" id="efRemove" title="Trocar arquivo">✕</button></div>`;
  $("#efRemove").onclick=()=>{ etEF=null; renderEFCard(); };
  setETButtons(true);
}
async function handleEFFile(file){
  if(!file) return;
  const name=file.name||""; const ext=name.slice(name.lastIndexOf(".")).toLowerCase();
  if(ext===".doc"){ outErr("Formato .doc não é aceito. Salve como .docx ou exporte para PDF."); return; }
  if(!EF_OK_EXT.includes(ext)){ outErr(`Formato não aceito (${ext||"sem extensão"}). A EF precisa ser .docx ou .pdf.`); return; }
  if(file.size===0){ outErr("Arquivo vazio."); return; }
  if(file.size>EF_MAX){ outErr("Arquivo acima do limite de 25 MB."); return; }
  outLoading(`Validando ${name}…`);

  try{
    
    const fd=new FormData(); fd.append("file", file);
    const r=await fetch(API+"/api/dev/ef/upload",{method:"POST",body:fd});
    const txt=await r.text(); let data; try{data=JSON.parse(txt);}catch{data={detail:txt};}
    if(!r.ok) throw new Error(data.detail||("HTTP "+r.status));
    etEF=data; out(""); renderEFCard();

  }catch(e){ etEF=null; renderEFCard(); outErr("EF recusada: "+e.message); }
}

function wireEFUpload(){
  const drop=$("#efDrop"), input=$("#efFile"); if(!drop||!input) return;
  input.onchange=()=>{ handleEFFile(input.files[0]); input.value=""; };
  ["dragenter","dragover"].forEach(ev=>drop.addEventListener(ev,e=>{e.preventDefault();drop.classList.add("over");}));
  ["dragleave","drop"].forEach(ev=>drop.addEventListener(ev,e=>{e.preventDefault();drop.classList.remove("over");}));
  drop.addEventListener("drop",e=>{ const f=e.dataTransfer.files&&e.dataTransfer.files[0]; handleEFFile(f); });
  renderEFCard();
}