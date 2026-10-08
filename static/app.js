"use strict";
const $ = id => document.getElementById(id);
let state = [];
let latestRequest = 0;
const minutes = text => { const [h,m] = text.split(":").map(Number); return h*60+m; };
const fmt = n => `${n.toFixed(1)} min`;
const clock = n => { const t = Math.ceil(n); return `${String(Math.floor(t/60)%24).padStart(2,"0")}:${String(t%60).padStart(2,"0")}`; };
const escapeHTML = value => String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
async function api(path, body) {
  const response = await fetch(path, body === undefined ? {} : {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}
function showError(error) { $("error").textContent = error.message; $("error").hidden = false; }
async function calculate() {
  const request = ++latestRequest;
  try {
    $("error").hidden = true;
    const data = await api("/api/recommend", {party:Number($("party").value), buffer:Number($("buffer").value), now_min:minutes($("now").value), class_min:minutes($("class").value), out_mode:$("out").value, back_mode:$("back").value});
    if (request !== latestRequest) return;
    $("summary").textContent = `${data.options.budget} minutes until class · ${data.options.buffer} min buffer · ranked by cautious total`;
    $("cards").innerHTML = data.restaurants.map((r,index) => {
      const s = r.scenarios.typical, c = r.scenarios.cautious;
      const labels = {"on-time":"WITHIN TIME BUDGET",tight:"TIGHT TIMING",late:"LIKELY LATE",unavailable:"NO SUITABLE TABLE"};
      const breakdown = s ? [["Travel to restaurant",s.outbound],["Wait after arrival",s.wait],["Dining session",s.dining],["Travel back to class",s.inbound]] : [];
      const occupied = r.tables.filter(t=>t.party>0).length;
      return `<article class="card ${index===0 && r.status==='on-time'?'best':''}"><div class="card-top"><span class="number">OPTION 0${index+1}</span><span class="badge ${r.status}">${labels[r.status]}</span></div><h3>${escapeHTML(r.name)}</h3><div class="sub">${occupied}/${r.tables.length} tables occupied · ${r.queue.length} groups waiting<br>${r.outbound_m} m outbound / ${r.return_m} m back · preset routes</div><div class="big">${s?clock(s.return_at):'—'} <small>typical return</small></div><div class="margin">${c?`Cautious return ${clock(c.return_at)} · ${Math.abs(c.margin).toFixed(1)} min ${c.margin>=0?'spare after buffer':'over budget'}`:'Your group cannot be seated.'}</div><div class="segments" aria-hidden="true">${breakdown.map(([,n])=>`<i style="flex:${Math.max(n,.01)}"></i>`).join('')}</div><div class="breakdown">${breakdown.map(([key,n])=>`<span>${key}</span><span>${fmt(n)}</span>`).join('')}${s?`<strong>Typical round trip</strong><strong>${fmt(s.total)}</strong><span>Cautious round trip</span><span>${fmt(c.total)}</span>`:''}</div><details><summary>Table estimates & queue</summary><p>Queue sizes: ${r.queue.join(' → ')||'No waiting groups'}</p><div class="tables">${r.tables.map(t=>`<div class="seat ${t.party?'':'free'}"><strong>${escapeHTML(t.id)} · ${t.capacity} seats</strong>${t.party?`${t.party} seated · ${t.elapsed} min elapsed<br>~${t.remaining.minutes.toFixed(1)} min left<br><small>${t.remaining.fallback?'Low support: fallback estimate':`${t.remaining.support} matching synthetic samples`}</small>`:'Free now'}</div>`).join('')}</div><p>Remaining time excludes table cleanup (2–3 min).</p></details></article>`;
    }).join('');
  } catch(error) { if(request===latestRequest){$("cards").innerHTML='';$("summary").textContent='';showError(error);} }
}
function selectedRestaurant() { return state.find(r=>r.id===$("restaurant").value); }
function fillTableValues() {
  const table = selectedRestaurant().tables.find(t=>t.id===$("table").value);
  $("seated").max = table.capacity; $("seated").value = table.party; $("elapsed").value = table.elapsed;
}
function fillTables() {
  const r = selectedRestaurant();
  $("table").innerHTML = r.tables.map(t=>`<option value="${t.id}">${t.id} (${t.capacity} seats)</option>`).join('');
  $("queue").value=r.queue.join(', '); fillTableValues();
}
async function refreshState() {
  const oldRestaurant=$("restaurant").value, oldTable=$("table").value;
  state=(await api('/api/state')).restaurants;
  $("restaurant").innerHTML=state.map(r=>`<option value="${r.id}">${escapeHTML(r.name)}</option>`).join('');
  if(state.some(r=>r.id===oldRestaurant)) $("restaurant").value=oldRestaurant;
  fillTables();
  if(selectedRestaurant().tables.some(t=>t.id===oldTable)){ $("table").value=oldTable;fillTableValues(); }
}
async function mutation(path,body) {
  try { await api(path,body); await refreshState(); await calculate(); $("operator-status").textContent='Demo snapshot updated.'; }
  catch(error) {showError(error);}
}
$("plan").addEventListener('submit',event=>{event.preventDefault();calculate();});
$("restaurant").addEventListener('change',fillTables);
$("table").addEventListener('change',fillTableValues);
$("table-form").addEventListener('submit',event=>{event.preventDefault();mutation('/api/update',{restaurant:$("restaurant").value,table:$("table").value,party:Number($("seated").value),elapsed:Number($("elapsed").value)});});
$("queue-form").addEventListener('submit',event=>{event.preventDefault();const value=$("queue").value.trim();if(value && !/^\d+(\s*,\s*\d+)*$/.test(value)){showError(new Error('Enter comma-separated group sizes, e.g. 2, 1, 4.'));return;}mutation('/api/update',{restaurant:$("restaurant").value,queue:value?value.split(',').map(Number):[]});});
$("reset").addEventListener('click',()=>mutation('/api/reset',{}));
refreshState().then(calculate).catch(showError);
