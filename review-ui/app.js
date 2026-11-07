'use strict';
const $ = id => document.getElementById(id);
let state, decisions, cases, selectedCase, selectedIssue, dirty = false;
const originNames = {reviewer:'Modellreview',translator:'Übersetzerhinweis',literal_check:'Automatischer Vergleich',domain_question:'Fachfrage',undocumented_change:'Unbegründete Modelländerung'};
const fields = {prompt:'Frage',required_facts:'Referenzfakt',anchor:'Anker',official_frame_markers:'Rahmungsmarker'};
const done = q => decisions.has(q.issue_id) && decisions.get(q.issue_id).decision !== 'defer';
const important = q => ['critical','major'].includes(q.severity) || q.origin === 'domain_question';
function text(id, value) { $(id).textContent = value ?? ''; }
function matches(q) {
  const filter = $('filter').value;
  return (filter==='all' || filter==='open' && !done(q) || filter==='done' && done(q) || filter==='defer' && decisions.get(q.issue_id)?.decision==='defer')
    && ($('priority').value==='all' || important(q));
}
function discard() { return !dirty || window.confirm('Ungespeicherte Änderungen verwerfen?'); }
function renderCases() {
  const complete = state.issues.filter(done).length;
  text('remaining', state.issues.length-complete);
  text('counts', `${cases.size} Fälle · ${complete} von ${state.issues.length} entschieden`);
  $('progress').max = state.issues.length; $('progress').value = complete;
  const query = $('search').value.toLocaleLowerCase('de');
  const visible = [...cases.entries()].filter(([id, qs]) => qs.some(matches) &&
    (!query || JSON.stringify([id, qs, state.sources.find(s=>s.id===id)]).toLocaleLowerCase('de').includes(query)));
  text('case-count', visible.length); $('cases').replaceChildren();
  if (!visible.some(([id])=>id===selectedCase)) { selectedCase=visible[0]?.[0]; selectedIssue=null; }
  $('workspace').hidden=!selectedCase; $('empty').hidden=!!selectedCase;
  for (const [id, qs] of visible) {
    const button=document.createElement('button'); button.type='button'; button.className='case-button'+(id===selectedCase?' active':'');
    const title=document.createElement('strong'); title.textContent=`Fall ${id}`;
    const description=document.createElement('span'); description.textContent=state.translations.find(s=>s.id===id)?.anchor || qs[0].translation;
    const count=document.createElement('small'); count.textContent=`${qs.filter(q=>!done(q)).length} offen / ${qs.length} Hinweise${qs.some(important)?' · Fachprüfung':''}`;
    button.append(title,description,count); button.onclick=()=>{if(!discard())return;dirty=false;selectedCase=id;selectedIssue=null;render();};
    $('cases').append(button);
  }
}
function renderIssue() {
  if (!selectedCase) return;
  const qs=cases.get(selectedCase);
  if (!qs.some(q=>q.issue_id===selectedIssue)) selectedIssue=(qs.find(matches)||qs[0]).issue_id;
  const q=qs.find(q=>q.issue_id===selectedIssue), saved=decisions.get(q.issue_id);
  const source=state.sources.find(s=>s.id===selectedCase), translated=state.translations.find(s=>s.id===selectedCase);
  text('case-meta', `FALL ${selectedCase} / ${source.question_description || ''}`);
  text('case-title', translated.anchor || 'Übersetzung prüfen');
  const url=source.source_url; $('source-link').hidden=!/^https?:\/\//i.test(url||'');
  if (!$('source-link').hidden) $('source-link').href=url;
  $('issues').replaceChildren();
  qs.forEach((item,index)=>{const b=document.createElement('button');b.type='button';b.textContent=`${done(item)?'✓ ':''}${index+1} · ${fields[item.field]||item.field}`;b.className=item.issue_id===selectedIssue?'selected':'';b.setAttribute('aria-pressed',String(item.issue_id===selectedIssue));b.onclick=()=>{if(!discard())return;dirty=false;selectedIssue=item.issue_id;renderIssue();};$('issues').append(b);});
  text('issue-meta', `${originNames[q.origin]||q.origin} / ${fields[q.field]||q.field}${q.index!==null?' '+(q.index+1):''}${q.severity?' / '+q.severity:''}`);
  text('original',q.source);text('translation',q.translation);text('reason',q.reason);text('uncertainty',q.uncertainty);
  const suggestion=q.suggestion||q.alternative; text('suggestion',suggestion);$('suggestion-wrap').hidden=!suggestion;
  document.querySelector('input[value="accept"]').disabled=!suggestion;
  $('context').replaceChildren();
  for (const [language,item] of [['Englisch',source],['Deutsch',translated]]) {
    const column=document.createElement('div');const title=document.createElement('h4');title.textContent=language;column.append(title);
    for (const field of ['prompt','required_facts','anchor','official_frame_markers']) {
      if (!item[field]) continue;
      const heading=document.createElement('h4');heading.textContent=fields[field];column.append(heading);
      const content=document.createElement('p');content.textContent=Array.isArray(item[field])?item[field].map((x,i)=>`${i+1}. ${x}`).join('\n\n'):item[field];column.append(content);
    }
    $('context').append(column);
  }
  document.querySelectorAll('input[name="decision"]').forEach(r=>r.checked=saved?.decision===r.value);
  $('decision-reason').value=saved?.reason||'';$('evidence').value=(saved?.evidence||[]).join('\n');
  $('final-text').value=saved?.final_text||q.translation;setChoice(false);
  text('saved-status',saved?`${saved.decision==='defer'?'Zurückgestellt':'Gespeichert'} · ${saved.reviewer}`:'Noch nicht entschieden');
  text('message','');
}
function render(){renderCases();renderIssue();}
function setChoice(updateText=true) {
  const choice=document.querySelector('input[name="decision"]:checked')?.value;
  const q=cases.get(selectedCase).find(q=>q.issue_id===selectedIssue);
  $('final-label').hidden=choice==='defer';$('final-text').readOnly=choice!=='modify';
  if(updateText)$('final-text').value=choice==='accept'?(q.suggestion||q.alternative||''):q.translation;
}
async function save(event) {
  event.preventDefault();
  const choice=document.querySelector('input[name="decision"]:checked')?.value;
  if(!choice){text('message','Bitte eine Entscheidung auswählen.');return;}
  $('save').disabled=true;text('message','Wird gespeichert …');
  try {
    const decision={issue_id:selectedIssue,decision:choice,reviewer:$('reviewer').value.trim(),reviewer_role:$('role').value.trim(),reason:$('decision-reason').value.trim(),final_text:choice==='defer'?null:$('final-text').value,evidence:$('evidence').value.split('\n').map(x=>x.trim()).filter(Boolean)};
    const response=await fetch('/api/decision',{method:'POST',headers:{'Content-Type':'application/json','X-Review-Token':state.token},body:JSON.stringify({revision:state.revision,decision})});
    const result=await response.json();if(!response.ok)throw Error(result.error);
    state.revision=result.revision;decisions.set(result.decision.issue_id,result.decision);dirty=false;
    localStorage.setItem('reviewer',$('reviewer').value);localStorage.setItem('reviewer_role',$('role').value);
    render();text('message','Entscheidung gespeichert.');
  } catch(error){text('message',error.message);} finally{$('save').disabled=false;}
}
async function init(){
  try {
    const response=await fetch('/api/state');if(!response.ok)throw Error('Prüfliste konnte nicht geladen werden.');state=await response.json();
    decisions=new Map(state.decisions.map(d=>[d.issue_id,d]));cases=new Map();
    state.issues.forEach(q=>{if(!cases.has(q.item_id))cases.set(q.item_id,[]);cases.get(q.item_id).push(q);});
    $('reviewer').value=localStorage.getItem('reviewer')||'';$('role').value=localStorage.getItem('reviewer_role')||'';
    render();
    for(const id of ['search','filter','priority']) $(id).addEventListener(id==='search'?'input':'change',()=>{if(!discard())return;dirty=false;render();});
    $('decision-form').addEventListener('input',()=>dirty=true);
    document.querySelectorAll('input[name="decision"]').forEach(r=>r.addEventListener('change',()=>setChoice()));
    $('decision-form').addEventListener('submit',save);
    window.addEventListener('beforeunload',event=>{if(dirty){event.preventDefault();event.returnValue='';}});
  } catch(error){text('case-title',error.message);}
}
init();
