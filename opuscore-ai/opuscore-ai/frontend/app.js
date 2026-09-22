// ===========================================================================
// OPUSCORE-AI — frontend SPA. Servido pelo backend (mesma origem).
// ===========================================================================
const API = ""; // mesma origem

const DOMAINS = {
  abap: { raw:"#28e0c4", label:"Desenvolvedor ABAP", sub:"capacidades do especialista · objetos standard" },
  cpi:  { raw:"#9a7bff", label:"Consultor de Integração", sub:"capacidades · artefatos do Integration Suite" },
  proc: { raw:"#ffb347", label:"Arquiteto de Processos", sub:"capacidades · cenários e transações standard" },
};

const AGENTS = [
  {key:"abap", name:"Desenvolvedor ABAP", tag:"DEV"},
  {key:"cpi",  name:"Consultor de Integração", tag:"CPI"},
  {key:"proc", name:"Arquiteto de Processos", tag:"PROC"},
  {key:"sd",   name:"Consultor SD", soon:true},
  {key:"mm",   name:"Consultor MM", soon:true},
  {key:"fico", name:"Consultor FI/CO", soon:true},
  {key:"tm",   name:"Consultor TM", soon:true},
  {key:"test", name:"Analista de Testes", soon:true},
];

const DATA = {
  abap:{nodes:[
    {id:"Desenvolvedor ABAP",type:"Especialista",kind:"focus",pkg:"OPUSCORE-AI",desc:"Lê o sistema via ADT e entrega relatórios com evidência",
      ev:[["Analisa qualquer objeto do repositório via ADT REST","core/discovery"],["Monta relatório: source, DDIC e where-used","usageReferences"],["Avalia Clean Core contra APIs liberadas","released APIs"]]},
    {id:"Análise de Objeto",type:"Capacidade",kind:"capability",desc:"Source, DDIC e where-used de qualquer objeto standard ou custom"},
    {id:"Clean Core Check",type:"Capacidade",kind:"capability",desc:"Verifica uso de APIs liberadas e risco de upgrade"},
    {id:"Modelagem CDS",type:"Capacidade",kind:"capability",desc:"Cria e analisa CDS sobre o VDM standard do S/4HANA"},
    {id:"Desenvolvimento RAP",type:"Capacidade",kind:"capability",desc:"BO, behavior e projeção no modelo RAP"},
    {id:"Serviços OData",type:"Capacidade",kind:"capability",desc:"Exposição via service definition e binding"},
    {id:"Qualidade",type:"Capacidade",kind:"capability",desc:"Roda ATC e ABAP Unit como parte da análise"},
    {id:"Performance",type:"Capacidade",kind:"capability",desc:"Code pushdown e AMDP para o HANA"},
    {id:"VBAK",type:"Tabela standard (SD)",kind:"standard",desc:"Cabeçalho da ordem de venda"},
    {id:"EKKO",type:"Tabela standard (MM)",kind:"standard",desc:"Cabeçalho do pedido de compra"},
    {id:"MARA",type:"Tabela standard",kind:"standard",desc:"Dados gerais do material"},
    {id:"Released APIs",type:"Contrato C1",kind:"standard",desc:"APIs liberadas para extensão Clean Core"},
    {id:"XCO Library",type:"Biblioteca liberada",kind:"standard",desc:"Acesso programático liberado a metadados"},
    {id:"I_SalesOrder",type:"CDS view (VDM)",kind:"standard",desc:"Interface view standard da ordem de venda"},
    {id:"I_Product",type:"CDS view (VDM)",kind:"standard",desc:"Interface view standard do produto"},
    {id:"I_BusinessPartner",type:"CDS view (VDM)",kind:"standard",desc:"Interface view standard do parceiro"},
    {id:"Behavior Definition",type:"Artefato RAP",kind:"standard",desc:"Comportamento do business object"},
    {id:"Projection View",type:"Artefato RAP",kind:"standard",desc:"View de projeção para o serviço"},
    {id:"Service Definition",type:"Serviço OData",kind:"standard",desc:"Define o que é exposto"},
    {id:"Service Binding",type:"Serviço OData",kind:"standard",desc:"Publica o serviço (OData V2/V4)"},
    {id:"ABAP Unit",type:"Teste",kind:"standard",desc:"Framework de testes unitários ABAP"},
    {id:"ATC",type:"Qualidade",kind:"standard",desc:"ABAP Test Cockpit — checks de qualidade"},
    {id:"AMDP",type:"Pushdown HANA",kind:"standard",desc:"ABAP Managed Database Procedures"},
    {id:"SQL Trace (ST05)",type:"Ferramenta",kind:"standard",desc:"Análise de acessos ao banco"},
  ],links:[
    ["Análise de Objeto","Desenvolvedor ABAP"],["Clean Core Check","Desenvolvedor ABAP"],["Modelagem CDS","Desenvolvedor ABAP"],
    ["Desenvolvimento RAP","Desenvolvedor ABAP"],["Serviços OData","Desenvolvedor ABAP"],["Qualidade","Desenvolvedor ABAP"],["Performance","Desenvolvedor ABAP"],
    ["VBAK","Análise de Objeto"],["EKKO","Análise de Objeto"],["MARA","Análise de Objeto"],
    ["Released APIs","Clean Core Check"],["XCO Library","Clean Core Check"],
    ["I_SalesOrder","Modelagem CDS"],["I_Product","Modelagem CDS"],["I_BusinessPartner","Modelagem CDS"],
    ["Behavior Definition","Desenvolvimento RAP"],["Projection View","Desenvolvimento RAP"],
    ["Service Definition","Serviços OData"],["Service Binding","Serviços OData"],
    ["ABAP Unit","Qualidade"],["ATC","Qualidade"],["AMDP","Performance"],["SQL Trace (ST05)","Performance"],
  ].map(([s,t])=>({source:s,target:t}))},

  cpi:{nodes:[
    {id:"Consultor de Integração",type:"Especialista",kind:"focus",pkg:"OPUSCORE-AI",desc:"Desenha e analisa integrações no SAP Integration Suite",
      ev:[["Lê iFlows e artefatos via API do tenant","design/iflows"],["Mapeia dependências e pontos de erro","usage"]]},
    {id:"Desenho de iFlow",type:"Capacidade",kind:"capability",desc:"Modela e revisa pipelines de integração"},
    {id:"Mapeamento",type:"Capacidade",kind:"capability",desc:"Message mapping e transformação"},
    {id:"Adapters",type:"Capacidade",kind:"capability",desc:"Conectividade de entrada e saída"},
    {id:"Tratamento de Erro",type:"Capacidade",kind:"capability",desc:"Exception handling e reprocessamento"},
    {id:"Monitoria",type:"Capacidade",kind:"capability",desc:"Observabilidade e alertas"},
    {id:"iFlow",type:"Artefato standard",kind:"standard",desc:"Integration Flow do Integration Suite"},
    {id:"Message Mapping",type:"Artefato standard",kind:"standard",desc:"Mapeamento gráfico de mensagens"},
    {id:"Groovy Script",type:"Script",kind:"standard",desc:"Transformação programática"},
    {id:"OData Adapter",type:"Adapter",kind:"standard",desc:"Conector OData"},
    {id:"SOAP / REST",type:"Adapter",kind:"standard",desc:"Web services SOAP e REST"},
    {id:"IDoc",type:"Interface standard",kind:"standard",desc:"Documento intermediário SAP"},
    {id:"Exception Subprocess",type:"Padrão",kind:"standard",desc:"Subprocesso de exceção do iFlow"},
    {id:"Advanced Event Mesh",type:"Mensageria",kind:"standard",desc:"AEM / Solace — eventos assíncronos"},
    {id:"Message Monitoring",type:"Monitoria",kind:"standard",desc:"Rastreio de mensagens no tenant"},
  ],links:[
    ["Desenho de iFlow","Consultor de Integração"],["Mapeamento","Consultor de Integração"],["Adapters","Consultor de Integração"],
    ["Tratamento de Erro","Consultor de Integração"],["Monitoria","Consultor de Integração"],
    ["iFlow","Desenho de iFlow"],["Message Mapping","Mapeamento"],["Groovy Script","Mapeamento"],
    ["OData Adapter","Adapters"],["SOAP / REST","Adapters"],["IDoc","Adapters"],
    ["Exception Subprocess","Tratamento de Erro"],["Advanced Event Mesh","Monitoria"],["Message Monitoring","Monitoria"],
  ].map(([s,t])=>({source:s,target:t}))},

  proc:{nodes:[
    {id:"Arquiteto de Processos",type:"Especialista",kind:"focus",pkg:"OPUSCORE-AI",desc:"Descobre o AS-IS a partir do que o sistema realmente roda",
      ev:[["Reconstrói o fluxo a partir de metadados","metadata"],["Aponta pontos de decisão e variações","process"]]},
    {id:"Descoberta AS-IS",type:"Capacidade",kind:"capability",desc:"Reconstrói o processo executado"},
    {id:"Mapa de Processo",type:"Capacidade",kind:"capability",desc:"Desenha o fluxo em BPMN"},
    {id:"Análise de Impacto",type:"Capacidade",kind:"capability",desc:"Onde uma mudança bate"},
    {id:"Fit-Gap",type:"Capacidade",kind:"capability",desc:"Compara com o standard e as Best Practices"},
    {id:"Order to Cash",type:"Cenário standard",kind:"standard",desc:"Processo de vendas ponta a ponta"},
    {id:"Procure to Pay",type:"Cenário standard",kind:"standard",desc:"Processo de compras ponta a ponta"},
    {id:"Record to Report",type:"Cenário standard",kind:"standard",desc:"Processo financeiro/contábil"},
    {id:"VA01",type:"Transação standard",kind:"standard",desc:"Criar ordem de venda"},
    {id:"ME21N",type:"Transação standard",kind:"standard",desc:"Criar pedido de compra"},
    {id:"FB01",type:"Transação standard",kind:"standard",desc:"Lançamento contábil"},
    {id:"BPMN",type:"Notação",kind:"standard",desc:"Modelagem do fluxo"},
    {id:"SAP Best Practices",type:"Referência",kind:"standard",desc:"Processos de referência SAP"},
    {id:"SAP Signavio",type:"Ferramenta",kind:"standard",desc:"Process mining / modelagem"},
  ],links:[
    ["Descoberta AS-IS","Arquiteto de Processos"],["Mapa de Processo","Arquiteto de Processos"],["Análise de Impacto","Arquiteto de Processos"],["Fit-Gap","Arquiteto de Processos"],
    ["Order to Cash","Descoberta AS-IS"],["Procure to Pay","Descoberta AS-IS"],["Record to Report","Descoberta AS-IS"],
    ["VA01","Mapa de Processo"],["ME21N","Mapa de Processo"],["FB01","Mapa de Processo"],["BPMN","Mapa de Processo"],
    ["SAP Best Practices","Fit-Gap"],["SAP Signavio","Fit-Gap"],["SAP Signavio","Análise de Impacto"],
  ].map(([s,t])=>({source:s,target:t}))},
};

// ---- estado ----
let dom = "abap";
let mode = "map";              // "map" | "analysis"
let currentDataset = DATA.abap;
let lastReport = null;

const esc = s => String(s??"").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const $ = id => document.getElementById(id);

// ---- squad ----
AGENTS.forEach(a=>{
  const el = document.createElement(a.soon?"div":"button");
  el.className = "agent"+(a.soon?" soon":"");
  el.dataset.key = a.key;
  el.setAttribute("aria-selected", a.key===dom);
  const c = DOMAINS[a.key]?DOMAINS[a.key].raw:"#3a486a";
  el.innerHTML = `<span class="dot" style="background:${c};box-shadow:${DOMAINS[a.key]?'0 0 8px '+c:'none'}"></span>
    <span>${a.name}</span><span class="tag">${a.soon?'em breve':a.tag}</span>`;
  if(!a.soon) el.onclick = ()=>switchDomain(a.key);
  $("squad").appendChild(el);
});

$("legend").innerHTML = `
  <span><span class="dot" style="background:var(--abap)"></span>ABAP</span>
  <span><span class="dot" style="background:var(--cpi)"></span>Integração</span>
  <span><span class="dot" style="background:var(--proc)"></span>Processos</span>
  <span style="color:var(--faint)">● capacidade · ○ objeto</span>`;

// ---- grafo (d3) ----
const svg = d3.select("#graph");
let W, H, sim;
const defs = svg.append("defs");
Object.keys(DOMAINS).forEach(k=>{
  defs.append("marker").attr("id","arrow-"+k).attr("viewBox","0 -5 10 10")
    .attr("refX",22).attr("refY",0).attr("markerWidth",6).attr("markerHeight",6)
    .attr("orient","auto").append("path").attr("d","M0,-4L8,0L0,4").attr("fill",DOMAINS[k].raw).attr("opacity",.6);
});
const gZoom = svg.append("g");
gZoom.append("g").attr("class","links");
gZoom.append("g").attr("class","nodes");
svg.call(d3.zoom().scaleExtent([.35,2.5]).on("zoom",e=>gZoom.attr("transform",e.transform)));
let linkSel, nodeSel, NB = {};

function size(){
  const r = document.querySelector(".stage").getBoundingClientRect();
  W=r.width; H=r.height; svg.attr("viewBox",`0 0 ${W} ${H}`);
}

function renderGraph(dataset, meta){
  currentDataset = dataset;
  size();
  const R = {focus:18, capability:11, standard:6.5, user:8};
  const arrow = DOMAINS[dom]?`url(#arrow-${dom})`:"";
  const nodes = dataset.nodes.map(d=>Object.assign({},d));
  const links = dataset.links.map(d=>Object.assign({},d));

  linkSel = gZoom.select(".links").selectAll("line").data(links, d=>(d.source.id||d.source)+"|"+(d.target.id||d.target));
  linkSel.exit().remove();
  linkSel = linkSel.enter().append("line").attr("class","link").attr("marker-end",arrow).merge(linkSel);

  nodeSel = gZoom.select(".nodes").selectAll("g.node").data(nodes, d=>d.id);
  nodeSel.exit().remove();
  const enter = nodeSel.enter().append("g").attr("class",d=>"node "+d.kind)
    .call(d3.drag().on("start",dragS).on("drag",dragM).on("end",dragE));
  enter.append("circle")
    .attr("r",d=>R[d.kind]||8)
    .attr("fill",d=>(d.kind==="focus"||d.kind==="capability")?meta.raw:"#0e1524")
    .attr("stroke",meta.raw)
    .attr("stroke-width",d=>d.kind==="focus"?2.5:d.kind==="capability"?2:1.4)
    .attr("fill-opacity",d=>d.kind==="focus"?.95:d.kind==="capability"?.28:1)
    .style("filter",d=>d.kind==="focus"?`drop-shadow(0 0 16px ${meta.raw})`:d.kind==="capability"?`drop-shadow(0 0 8px ${meta.raw}66)`:"none")
    .on("click",(e,d)=>{e.stopPropagation();openInspect(d);})
    .on("mouseenter",(e,d)=>hover(d,true)).on("mouseleave",(e,d)=>hover(d,false));
  enter.append("text").attr("x",d=>(R[d.kind]||8)+5).attr("dy",".32em").text(d=>d.id);
  nodeSel = enter.merge(nodeSel);

  sim && sim.stop();
  sim = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d=>d.id).distance(l=>(l.source.kind==="focus"||l.target.kind==="focus")?150:80).strength(.75))
    .force("charge", d3.forceManyBody().strength(-540))
    .force("center", d3.forceCenter(W/2, H/2))
    .force("collide", d3.forceCollide(d=>(d.kind==="standard"||d.kind==="user")?26:40))
    .on("tick",tick);

  NB = {};
  links.forEach(l=>{const s=l.source.id||l.source,t=l.target.id||l.target;
    (NB[s]=NB[s]||new Set()).add(t);(NB[t]=NB[t]||new Set()).add(s);});
}
function tick(){
  linkSel.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
  nodeSel.attr("transform",d=>`translate(${d.x},${d.y})`);
}
function hover(d,on){
  if(!on){nodeSel.classed("dim",false);linkSel.classed("dim",false).classed("hot",false);return;}
  const near=NB[d.id]||new Set();
  nodeSel.classed("dim",n=>n.id!==d.id&&!near.has(n.id));
  linkSel.classed("dim",l=>!(l.source.id===d.id||l.target.id===d.id)).classed("hot",l=>l.source.id===d.id||l.target.id===d.id);
}
function dragS(e,d){if(!e.active)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y;}
function dragM(e,d){d.fx=e.x;d.fy=e.y;}
function dragE(e,d){if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}

// ---- inspetor / relatório ----
const insp = $("inspect");
function connections(d){
  return [...new Set(currentDataset.links
    .filter(l=>(l.source.id||l.source)===d.id||(l.target.id||l.target)===d.id)
    .map(l=>{const s=l.source.id||l.source,t=l.target.id||l.target;return s===d.id?t:s;}))];
}
function inspectBody(d){
  let html="";
  const isFocus = d.kind==="focus";
  if(mode==="analysis" && isFocus && lastReport){
    const r = lastReport.report||{};
    html += `<div class="sec">Relatório</div><div class="narr">${esc(lastReport.narrative||"—")}</div>`;
    html += `<div class="sec">Evidência (ADT)</div>`+
      (r.evidence||[]).map(e=>`<div class="ev">${esc(e.fact)}<small>ADT · ${esc(e.source)}</small></div>`).join("");
    if(r.fields && r.fields.length){
      html += `<div class="sec">Campos (${r.fields.length})</div>`+
        r.fields.slice(0,50).map(f=>`<div class="ev">${esc(f.name)} <small>${esc(f.type||"")}${f.key?" · chave":""}</small></div>`).join("");
    }
    const used = r.used_by||[];
    html += `<div class="sec">Quem usa (${used.length})</div><div class="uses">`+
      (used.length?used.map(u=>`<button data-go="${esc(u.name)}">${esc(u.name)}<span class="t">${esc(u.type||"")}</span></button>`).join("")
        :`<div style="color:var(--faint);font-size:12px">Nenhum retornado pelo where-used.</div>`)+`</div>`;
    return html;
  }
  if(isFocus && d.ev){
    html += `<div class="sec">Evidência (ADT)</div>`+d.ev.map(([f,s])=>`<div class="ev">${esc(f)}<small>ADT · ${esc(s)}</small></div>`).join("");
  } else {
    html += `<div class="sec">Sobre</div><div class="ev">${esc(d.desc||"—")}</div>`;
  }
  const conn = connections(d);
  html += `<div class="sec">Conectado a</div><div class="uses">`+
    (conn.length?conn.map(u=>{const n=currentDataset.nodes.find(x=>x.id===u);
      return `<button data-go="${esc(u)}">${esc(u)}<span class="t">${n?esc(n.type):""}</span></button>`}).join("")
      :`<div style="color:var(--faint);font-size:12px">Sem conexões.</div>`)+`</div>`;
  return html;
}
function openInspect(d){
  $("iKind").textContent = d.type||"objeto";
  $("iName").textContent = d.id;
  $("iMeta").textContent = `${d.pkg?("pacote "+d.pkg+" · "):""}${d.desc||""}`;
  $("iBody").innerHTML = inspectBody(d);
  $("iBody").querySelectorAll("button[data-go]").forEach(btn=>btn.onclick=()=>{
    const t=currentDataset.nodes.find(x=>x.id===btn.dataset.go); if(t) openInspect(t);});
  insp.classList.add("open"); insp.setAttribute("aria-hidden","false");
}
function closeInspect(){insp.classList.remove("open");insp.setAttribute("aria-hidden","true");}
$("close").onclick = closeInspect;
svg.on("click", closeInspect);

function showError(title, msg){
  $("iKind").textContent="erro"; $("iName").textContent=title; $("iMeta").textContent="";
  $("iBody").innerHTML=`<div class="err">${esc(msg)}</div>`;
  insp.classList.add("open"); insp.setAttribute("aria-hidden","false");
}

// ---- backend ----
async function health(){
  const conn=$("conn");
  try{
    const r = await fetch(API+"/health");
    if(r.ok){
      const d = await r.json();
      conn.className="conn up";
      $("connText").innerHTML = `conectado a <b>${esc(d.sap)}</b>`;
      const p=$("modePill");
      if(d.read_only){p.className="pill ro";p.textContent="SOMENTE-LEITURA";}
      else{p.className="pill rw";p.textContent="ESCRITA HABILITADA";}
    } else {
      conn.className="conn down";
      $("connText").textContent="SAP não conectado — verifique config";
      $("modePill").className="pill"; $("modePill").textContent="backend OK";
    }
  }catch(e){
    conn.className="conn down";
    $("connText").textContent="backend offline — inicie a API";
    $("modePill").className="pill"; $("modePill").textContent="—";
  }
}

async function analyze(name){
  if(!name) return;
  $("loading").classList.add("on");
  $("loadingTxt").textContent = `consultando ${name} no SAP via ADT…`;
  try{
    const r = await fetch(API+"/abap/report", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({object_name:name}),
    });
    const raw = await r.text();
    if(!r.ok){
      let msg=raw; try{msg=JSON.parse(raw).detail||raw;}catch{}
      showError(name, "Falha na análise:\n"+msg);
      return;
    }
    const result = JSON.parse(raw);
    lastReport = result;
    mode = "analysis"; setSeg();
    renderGraph(result.graph, DOMAINS[dom]);
    $("ctxObj").textContent = name;
    $("ctxSub").textContent = "análise ao vivo · where-used do sistema";
    const f = result.graph.nodes.find(n=>n.kind==="focus") || result.graph.nodes[0];
    if(f) openInspect(f);
  }catch(e){
    showError(name, "Erro de rede: "+e.message+"\n\nO backend está rodando? (python -m opuscore.api)");
  }finally{
    $("loading").classList.remove("on");
  }
}

// ---- controles ----
function switchDomain(k){
  dom=k; mode="map"; setSeg();
  document.querySelectorAll(".agent").forEach(a=>a.setAttribute("aria-selected",a.dataset.key===k));
  $("ctxObj").textContent = DOMAINS[k].label;
  $("ctxSub").textContent = DOMAINS[k].sub;
  renderGraph(DATA[k], DOMAINS[k]);
  closeInspect();
}
function setSeg(){document.querySelectorAll("#seg button").forEach(b=>b.setAttribute("aria-selected",b.dataset.mode===mode));}
document.querySelectorAll("#seg button").forEach(b=>b.onclick=()=>{
  mode=b.dataset.mode; setSeg();
  if(mode==="map"){ renderGraph(DATA[dom],DOMAINS[dom]); $("ctxObj").textContent=DOMAINS[dom].label; $("ctxSub").textContent=DOMAINS[dom].sub; closeInspect(); }
  else if(lastReport){ renderGraph(lastReport.graph,DOMAINS[dom]); const f=lastReport.graph.nodes.find(n=>n.kind==="focus"); if(f) openInspect(f); }
  else { $("ctxSub").textContent="nenhuma análise ainda — digite um objeto e clique Analisar"; }
});
$("run").onclick = ()=>analyze($("q").value.trim());
$("q").addEventListener("keydown",e=>{ if(e.key==="Enter") analyze($("q").value.trim()); });
window.addEventListener("resize",()=>{ size(); sim && sim.force("center",d3.forceCenter(W/2,H/2)).alpha(.3).restart(); });

// ---- init ----
renderGraph(DATA.abap, DOMAINS.abap);
health();
setInterval(health, 15000);

// ---- chat (host + MCP) ----
let chatHistory = [];
const chatlog = $("chatlog");
function addMsg(role, text){
  const d = document.createElement("div");
  d.className = "msg " + role;
  d.textContent = text;
  chatlog.appendChild(d);
  chatlog.scrollTop = chatlog.scrollHeight;
  return d;
}
async function sendChat(){
  const inp = $("chatq");
  const text = inp.value.trim();
  if(!text) return;
  inp.value = "";
  addMsg("user", text);
  chatHistory.push({role:"user", content:text});
  const thinking = addMsg("think", "consultando o SAP…");
  $("chatsend").disabled = true;
  try{
    const r = await fetch(API+"/chat", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({messages: chatHistory}),
    });
    const raw = await r.text();
    thinking.remove();
    if(!r.ok){
      let msg = raw; try{ msg = JSON.parse(raw).detail || raw; }catch{}
      addMsg("err", msg);
      return;
    }
    const reply = JSON.parse(raw).reply || "(sem resposta)";
    addMsg("bot", reply);
    chatHistory.push({role:"assistant", content:reply});
  }catch(e){
    thinking.remove();
    addMsg("err", "Erro de rede: "+e.message+"  (o backend está rodando?)");
  }finally{
    $("chatsend").disabled = false;
    $("chatq").focus();
  }
}
$("chattoggle").onclick = ()=>{ $("chatwin").hidden=false; $("chattoggle").style.display="none"; $("chatq").focus(); };
$("chatclose").onclick = ()=>{ $("chatwin").hidden=true; $("chattoggle").style.display=""; };
$("chatsend").onclick = sendChat;
$("chatq").addEventListener("keydown", e=>{ if(e.key==="Enter") sendChat(); });
