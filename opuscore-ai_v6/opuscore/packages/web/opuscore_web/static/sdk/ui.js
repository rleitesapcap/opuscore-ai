// SDK das telas: componentes e utilitários comuns (design system em JS).
// As telas recebem tudo isto pelo ctx.ui; não importam este arquivo diretamente.
const API = "";
const $ = s => document.querySelector(s);
const el = (h) => { const t=document.createElement("template"); t.innerHTML=h.trim(); return t.content.firstChild; };
const esc = s => String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
async function api(path, opts){ const r = await fetch(API+path, opts); const txt = await r.text();
  let data; try{data=JSON.parse(txt);}catch{data=txt;} if(!r.ok) throw new Error((data&&data.detail)||txt||r.status); return data; }


async function post(path, body){
  return api(path, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
}
async function put(path, body){
  const r = await fetch(API+path, {method:"PUT", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
  const txt=await r.text(); let d; try{d=JSON.parse(txt);}catch{d={detail:txt};}
  if(!r.ok) throw new Error(d.detail||("HTTP "+r.status));
  return d;
}


// ---------- Analisar (configuração de MM no ambiente) ----------

// saída padrão de uma tela: o elemento #devout dentro da área do consultor
function out(html){ const o=$("#devout"); if(o) o.innerHTML=html; }
function outLoading(msg){ out(`<div class="devcard loading2"><span class="spin2"></span>${esc(msg)}</div>`); }
function outErr(msg){ out(`<div class="msg err">${esc(msg)}</div>`); }
// ---- botões de download dos arquivos gerados ----
const DL_ROTULO = {docx: "Baixar ET (Word)", md: "Baixar Markdown", abap: "Baixar código", txt: "Baixar texto", pdf: "Baixar PDF"};
function downloadsHtml(lista, rotulos){
  if(!lista || !lista.length) return "";
  const rot = Object.assign({}, DL_ROTULO, rotulos||{});
  const kb = n => n>1048576 ? (n/1048576).toFixed(1)+" MB" : Math.max(1,Math.round(n/1024))+" KB";
  return `<div class="dlrow">` + lista.map((d,i)=>
    `<a class="btn${i===0?"":" ghost"}" href="${d.url}" download="${esc(d.nome)}" title="${esc(d.nome)}">⬇ ${esc(rot[d.tipo]||("Baixar ."+d.tipo))} <span class="dlsz">${kb(d.tamanho)}</span></a>`
  ).join("") + `</div>`;
}

// ---- Upload da EF (componente reutilizável: validação no navegador + no servidor) ----
const EF_OK_EXT = [".docx", ".pdf"];
const EF_MAX = 25 * 1024 * 1024;
const efState = { et: null, rem: null };   // EF validada por aba: {ef_id, filename, ext, size, chars, preview}
function fmtSize(b){ return b>1048576 ? (b/1048576).toFixed(1)+" MB" : Math.max(1,Math.round(b/1024))+" KB"; }
function efUploadHtml(k){ return `
    <label class="drop" id="${k}Drop">
      <input type="file" id="${k}File" accept=".docx,.pdf,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" hidden>
      <div class="drop-ic">⇪</div>
      <div class="drop-t">Arraste a EF aqui ou <u>clique para escolher</u></div>
      <div class="drop-s">Somente .docx ou .pdf · até 25 MB · o arquivo é validado antes do uso</div>
    </label>
    <div id="${k}Card"></div>`; }
function setEFButtons(botoes, on){ (botoes||[]).forEach(id=>{ const b=$(id); if(b) b.disabled=!on; }); }
function renderEFCard(k, botoes){
  const card=$(`#${k}Card`), drop=$(`#${k}Drop`); if(!card||!drop) return;
  const ef=efState[k];
  if(!ef){ card.innerHTML=""; setEFButtons(botoes,false); drop.style.display=""; return; }
  drop.style.display="none";
  card.innerHTML = `<div class="efcard">
    <div class="ef-ic">${ef.ext===".pdf"?"PDF":"DOCX"}</div>
    <div class="ef-info"><div class="ef-nm">${esc(ef.filename)}</div>
      <div class="ef-meta">✓ validada · ${fmtSize(ef.size)} · ${ef.chars.toLocaleString("pt-BR")} caracteres de texto</div>
      <div class="ef-prev">${esc(ef.preview.slice(0,240))}${ef.preview.length>240?"…":""}</div></div>
    <button class="iconbtn" id="${k}Remove" title="Trocar arquivo">✕</button></div>`;
  $(`#${k}Remove`).onclick=()=>{ efState[k]=null; renderEFCard(k, botoes); };
  setEFButtons(botoes,true);
}
async function handleEFFile(k, botoes, file){
  if(!file) return;
  const name=file.name||""; const ext=name.slice(name.lastIndexOf(".")).toLowerCase();
  if(ext===".doc"){ outErr("Formato .doc não é aceito. Salve como .docx ou exporte para PDF."); return; }
  if(!EF_OK_EXT.includes(ext)){ outErr(`Formato não aceito (${ext||"sem extensão"}). A EF precisa ser .docx ou .pdf.`); return; }
  if(file.size===0){ outErr("Arquivo vazio."); return; }
  if(file.size>EF_MAX){ outErr("Arquivo acima do limite de 25 MB."); return; }
  outLoading(`Validando ${name}…`);
  try{
    const fd=new FormData(); fd.append("file", file);
    const r=await fetch(API+"/api/plataforma/uploads",{method:"POST",body:fd});
    const txt=await r.text(); let data; try{data=JSON.parse(txt);}catch{data={detail:txt};}
    if(!r.ok) throw new Error(data.detail||("HTTP "+r.status));
    efState[k]=data; out(""); renderEFCard(k, botoes);
  }catch(e){ efState[k]=null; renderEFCard(k, botoes); outErr("EF recusada: "+e.message); }
}
function wireEFUpload(k, botoes){
  const drop=$(`#${k}Drop`), input=$(`#${k}File`); if(!drop||!input) return;
  input.onchange=()=>{ handleEFFile(k, botoes, input.files[0]); input.value=""; };
  ["dragenter","dragover"].forEach(ev=>drop.addEventListener(ev,e=>{e.preventDefault();drop.classList.add("over");}));
  ["dragleave","drop"].forEach(ev=>drop.addEventListener(ev,e=>{e.preventDefault();drop.classList.remove("over");}));
  drop.addEventListener("drop",e=>{ const f=e.dataTransfer.files&&e.dataTransfer.files[0]; handleEFFile(k, botoes, f); });
  renderEFCard(k, botoes);   // mantém a EF já validada ao voltar para a aba
}


function usoHtml(u){
  if(!u || !u.tokens || !u.chamadas) return "";
  const t=u.tokens, n=x=>Number(x||0).toLocaleString("pt-BR");
  const usd=x=>x==null?"—":"US$ "+Number(x).toFixed(4);
  const eco = u.economia_cache_usd==null ? "" :
    ` · <span class="${u.economia_cache_usd>0?"eco-ok":"eco-neg"}">economia do cache ${usd(u.economia_cache_usd)}</span>`;
  return `<div class="uso" title="${esc(u.observacao||"")}">IA: ${u.chamadas} chamada(s) · entrada ${n(t.input)} · `+
         `cache lido ${n(t.cache_read)} · cache gravado ${n(t.cache_creation)} · saída ${n(t.output)} · `+
         `custo ${usd(u.custo_estimado_usd)}${eco}</div>`;
}
function mdLite(texto){
  // Markdown simples e SEGURO: escapa tudo antes de formatar.
  const linhas = esc(texto||"").split("\n"); const out=[]; let lista=false, tabela=[];
  const inline = t => t.replace(/`([^`]+)`/g,"<code>$1</code>").replace(/\*\*([^*]+)\*\*/g,"<b>$1</b>");
  const fechaTabela = ()=>{ if(!tabela.length) return;
    const cel = l => l.trim().replace(/^\||\|$/g,"").split("|").map(c=>inline(c.trim()));
    const corpo = tabela.filter(l=>!/^\s*\|?\s*:?-{2,}/.test(l));
    out.push(`<div class="tblwrap"><table class="cfgtbl"><thead><tr>${cel(corpo[0]).map(c=>`<th>${c}</th>`).join("")}</tr></thead><tbody>${
      corpo.slice(1).map(l=>`<tr>${cel(l).map(c=>`<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
    tabela=[]; };
  for(const l of linhas){
    if(/^\s*\|.*\|\s*$/.test(l)){ if(lista){out.push("</ul>");lista=false;} tabela.push(l); continue; }
    fechaTabela();
    const h=l.match(/^(#{1,4})\s+(.*)/), b=l.match(/^\s*[-*]\s+(.*)/);
    if(b){ if(!lista){out.push("<ul>");lista=true;} out.push(`<li>${inline(b[1])}</li>`); continue; }
    if(lista){ out.push("</ul>"); lista=false; }
    if(h){ out.push(`<div class="mdh">${inline(h[2])}</div>`); continue; }
    out.push(l.trim()? `<p>${inline(l)}</p>` : "");
  }
  fechaTabela(); if(lista) out.push("</ul>");
  return out.join("");
}


export const UI = {$, el, esc, api, post, put, out, outLoading, outErr, efUploadHtml, wireEFUpload, efState, fmtSize,
                   downloadsHtml, usoHtml, mdLite};
export {$, el, esc, api, post, usoHtml};
