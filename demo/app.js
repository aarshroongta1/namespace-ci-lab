'use strict';
(async()=>{
  const $=id=>document.getElementById(id);
  const stages=[
    {id:'wait',name:'Wait to start',color:'#d5d9e1',description:'Time from the shared workflow dispatch to the start of this job. Includes GitHub dispatch and runner scheduling.',log:null},
    {id:'setup',name:'Setup',color:'#b9c0cc',description:'Check out the source and install ccache and Pixi.',log:null},
    {id:'cache',name:'Cache',color:'#b69bd9',description:'Restore an archive or attach a Cache Volume. A restored archive can still contain compiler outputs that do not match this build.',log:null},
    {id:'environment',name:'Environment',color:'#63b1b5',description:'Create the same locked Pixi Python 3.12 environment from cached packages.',log:'environment'},
    {id:'build',name:'Build',color:'#525cc2',description:'Build pandas from source. Removing the extra LC_ALL cache input restored the GitHub-generated compiler entries on Namespace.',log:'build'},
    {id:'tests',name:'Tests',color:'#d6a45e',description:'Run the same 4,045 groupby tests. All three jobs passed, with 2 skipped.',log:'unit'},
    {id:'finish',name:'Finish',color:'#e0e3e9',description:'Upload results, handle post-job cache work, and complete the job. Small timing gaps are included here.',log:null}
  ];
  const changes={
    environment:{description:'Ccache hashes both the value and presence of these locale variables. The representative compiler inputs otherwise matched.',beforeLabel:'GitHub environment',afterLabel:'Namespace environment',before:'LANG=C.UTF-8\n# LC_ALL is unset',after:'LANG=C.UTF-8\nLC_ALL=C.UTF-8',detail:'Both jobs use the C.UTF-8 locale. The redundant LC_ALL value creates a different ccache key. Compiler versions, files, and the checked headers matched.'},
    fix:{description:'Remove LC_ALL from the Namespace build/test process. Keep LANG=C.UTF-8 and restore the same existing archive.',beforeLabel:'Unchanged Namespace job',afterLabel:'Fixed Namespace job',before:'python3 scripts/measure_pandas.py',after:'env -u LC_ALL python3 scripts/measure_pandas.py',detail:'No dependency, compiler, source, test, or cache-key setting changed. The original archive went from 3/59 to 59/59 compiler-cache hits. The regression check fails without this change and passes with it.'}
  };
  let data,records,max=0,elapsed=0,playing=false,last=0,raf=0,selected='build';
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  const fmt=n=>n===0?'<1s':Number.isInteger(n)?`${n}s`:`${n.toFixed(2)}s`;
  function controls(){ $('play').querySelector('span').textContent=playing?'Pause':elapsed>0&&elapsed<max?'Continue':'Replay';$('finish').hidden=elapsed>=max; }
  function stop(){playing=false;cancelAnimationFrame(raf);controls();}
  function change(key){const c=changes[key];$('change-description').textContent=c.description;$('before-label').textContent=c.beforeLabel;$('after-label').textContent=c.afterLabel;$('before-code').textContent=c.before;$('after-code').textContent=c.after;$('change-detail').textContent=c.detail;document.querySelectorAll('[data-change]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.change===key)));}
  function inspect(id){
    selected=id;const i=stages.findIndex(s=>s.id===id),s=stages[i];
    $('stage-title').textContent=s.name;$('stage-description').textContent=s.description;
    document.querySelectorAll('.legend-button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.stage===id)));
    document.querySelectorAll('.segment').forEach(b=>b.classList.toggle('selected',b.dataset.stage===id));
    $('stage-evidence').innerHTML=records.map(r=>{
      const note=id==='build'?`${r.hits}/${r.calls} compiler-cache hits`:id==='cache'?`${r.files.toLocaleString()} files at start`:id==='tests'?`${r.passed.toLocaleString()} passed`:'';
      const url=s.log?`${r.logbase}${r.prefix}-${s.log}.log`:r.url;
      return `<div class="evidence-stat"><span class="stat-provider">${r.title}</span><strong>${fmt(r.times[i])}</strong><span class="evidence-note">${note}</span><a href="${url}" target="_blank" rel="noopener">${s.log?'Log':'CI job'}</a></div>`;
    }).join('');
  }
  function paint(){
    $('scrubber').value=String(Math.round(elapsed/max*1000));$('elapsed').textContent=`${Math.round(elapsed)}s`;
    records.forEach(r=>{
      const t=Math.min(elapsed,r.total),lane=document.querySelector(`[data-variant="${r.id}"]`);let start=0,current='Wait to start';
      lane.querySelector('.lane-time-value').textContent=`${Math.round(t)}s`;lane.querySelector('.lane-time small').textContent=t>=r.total?'passed':'recorded time';
      lane.querySelectorAll('.segment').forEach((b,i)=>{const d=r.times[i],part=d?Math.max(0,Math.min(1,(t-start)/d)):t>=start?1:0;b.style.clipPath=`inset(0 ${100-part*100}% 0 0)`;if(t>=start)current=stages[i].name;start+=d;});
      const cursor=lane.querySelector('.cursor');cursor.style.left=`${t/max*100}%`;cursor.style.display=t<r.total&&elapsed<max?'block':'none';
      document.querySelector(`[data-status="${r.id}"]`).textContent=t>=r.total?`${r.hits}/${r.calls} compiler-cache hits; ${r.passed.toLocaleString()} tests passed`:current;
    });controls();
  }
  function frame(now){if(!playing)return;if(!last)last=now;elapsed=Math.min(max,elapsed+(now-last)/1000*(max/12));last=now;paint();if(elapsed>=max){playing=false;controls();return;}raf=requestAnimationFrame(frame);}
  try{
    const response=await fetch('/namespace-ci/verification.json');if(!response.ok)throw new Error('Missing results');data=await response.json();records=data.variants;max=Math.max(...records.map(r=>r.total));elapsed=max;
    $('ticks').innerHTML=[0,1,2,3,4].map(i=>`<span>${Math.round(max*i/4)}s</span>`).join('');
    $('lanes').innerHTML=records.map(r=>{let offset=0;const segments=r.times.map((d,i)=>{const left=offset/max*100;offset+=d;return `<button class="segment" data-stage="${stages[i].id}" style="left:${left}%;width:${Math.max(d/max*100,.1)}%" aria-label="${r.title} ${stages[i].name}, ${d.toFixed(2)} seconds" title="${stages[i].name}: ${fmt(d)}"></button>`;}).join('');return `<div class="lane" data-variant="${r.id}"><div class="provider-name">${r.title}<span class="configuration-label">${r.description}</span></div><div class="track"><div class="segments">${segments}</div><div class="cursor"></div></div><div class="lane-time"><span class="lane-time-value"></span><small></small></div></div><div class="lane-meta"><p data-status="${r.id}"></p><a href="${r.url}" target="_blank" rel="noopener">CI job</a></div>`;}).join('');
    $('legend').innerHTML=stages.map(s=>`<button class="legend-button" data-stage="${s.id}" aria-pressed="${s.id===selected}"><span class="legend-swatch" style="background:${s.color}"></span>${s.name}</button>`).join('');
    document.querySelectorAll('[data-stage]').forEach(b=>b.addEventListener('click',()=>inspect(b.dataset.stage)));
    document.querySelectorAll('[data-change]').forEach(b=>b.addEventListener('click',()=>change(b.dataset.change)));
    $('play').addEventListener('click',()=>{if(playing){stop();return;}if(elapsed>=max)elapsed=0;if(reduced.matches){elapsed=max;paint();return;}playing=true;last=0;paint();raf=requestAnimationFrame(frame);});
    $('finish').addEventListener('click',()=>{stop();elapsed=max;paint();});
    $('scrubber').addEventListener('input',e=>{stop();elapsed=Number(e.target.value)/1000*max;paint();});
    document.addEventListener('visibilitychange',()=>{if(document.hidden&&playing)stop();});
    inspect('build');change('environment');paint();
  }catch(error){console.error(error);$('load-error').hidden=false;}
})();
