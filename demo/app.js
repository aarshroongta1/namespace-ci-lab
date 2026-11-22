'use strict';
(async () => {
  const $ = id => document.getElementById(id);
  const stages = [
    {id:'setup',name:'Setup',color:'#bdc4d4',description:'Runner setup, source checkout and tool installation. These are part of the wait too.',log:null},
    {id:'cache',name:'Cache',color:'#b89ce5',description:'GitHub restores an archive. Namespace attaches a cache volume. Attaching a volume does not guarantee reusable data is present.',log:'ccache'},
    {id:'environment',name:'Environment',color:'#67b9bc',description:'Create pandas’ locked Pixi Python 3.12 environment, using cached packages when available.',log:'environment'},
    {id:'build',name:'Source build',color:'#5353d8',description:'Build pandas from source with Meson and two compiler workers. The build directory is fresh on every run; only compiler outputs are cached.',log:'build'},
    {id:'tests',name:'Tests',color:'#e4b36c',description:'Run two existing groupby test files with two pytest workers. Every recorded job passed 4,045 tests, with 2 skipped.',log:'unit'},
    {id:'finish',name:'Finish',color:'#dfe2e9',description:'Upload evidence, save or commit the cache, and finish the job. Small timing gaps are included here.',log:null}
  ];
  const copy = {
    cold:{title:'Start with nothing cached.',description:'Fresh runners, fresh environments, and a full pandas source build.',label:'Whole job, with empty experiment caches',summary:'Namespace finished in 217s. GitHub finished in 299s.',delta:'82s',caption:'less time in this run'},
    warm:{title:'Same build time. Less time around it.',description:'Both builds take about 32 seconds. Watch the rest of the job.',label:'Whole job, with populated caches',summary:'Namespace finished in 76s. GitHub finished in 131s. Setup and cache handling explain most of the difference.',delta:'55s',caption:'less time in this run'},
    edited:{title:'A small edit. The cache still helps.',description:'Rename a local Python helper, then rebuild and run the same tests.',label:'Whole job, after a behavior-preserving Python edit',summary:'Namespace finished in 62s. GitHub finished in 143s. Both reused all 59 cacheable compiler calls.',delta:'81s',caption:'less time in this run'},
    miss:{title:'A repeated run. An empty cache.',description:'The first Namespace repeat started cold, even though caching was enabled.',label:'The onboarding cache miss',summary:'Namespace passed every test but took 208s. The cache contained no reusable files; the verified warm run later took 76s.',delta:'0 files',caption:'cached at the start on Namespace'}
  };
  let data,scenario='warm',selectedStage='build',playing=false,elapsed=0,max=0,raf=0,last=0;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const fmt = n => Number.isInteger(n) ? `${n}s` : `${n.toFixed(2)}s`;
  const name = p => p==='github'?'GitHub':'Namespace';
  const logo = p => p==='namespace'?'N_':'<svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 .8a11.2 11.2 0 0 0-3.54 21.83c.56.1.76-.24.76-.54v-2.1c-3.12.68-3.78-1.32-3.78-1.32-.51-1.3-1.25-1.65-1.25-1.65-1.02-.7.08-.69.08-.69 1.12.08 1.71 1.15 1.71 1.15 1 1.7 2.62 1.21 3.26.93.1-.72.39-1.22.71-1.5-2.49-.28-5.11-1.25-5.11-5.54 0-1.22.44-2.22 1.15-3-.11-.28-.5-1.42.11-2.96 0 0 .94-.3 3.08 1.15a10.7 10.7 0 0 1 5.6 0c2.14-1.45 3.08-1.15 3.08-1.15.61 1.54.22 2.68.11 2.96.72.78 1.15 1.78 1.15 3 0 4.3-2.62 5.25-5.12 5.53.4.35.76 1.03.76 2.08v3.21c0 .3.2.65.77.54A11.2 11.2 0 0 0 12 .8Z"/></svg>';
  function stop(){playing=false;cancelAnimationFrame(raf);updatePlay();}
  function updatePlay(){ $('play').querySelector('span').textContent=playing?'Pause replay':elapsed>0&&elapsed<max?'Continue replay':'Replay comparison'; $('finish').hidden=elapsed>=max; }
  function inspect(id){
    selectedStage=id;
    const i=stages.findIndex(s=>s.id===id),s=stages[i];
    $('stage-title').textContent=s.name;
    $('stage-description').textContent=s.description;
    document.querySelectorAll('.legend-button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.stage===id)));
    document.querySelectorAll('.segment').forEach(b=>b.classList.toggle('selected',b.dataset.stage===id));
    $('stage-evidence').innerHTML=['github','namespace'].map(p=>{
      const r=data[scenario][p],seconds=r.times[i];
      let note=id==='cache'?`${r.files.toLocaleString()} files at start`:id==='build'?`${r.hits} / ${r.calls} compiler-cache hits`:id==='tests'?`${r.passed.toLocaleString()} passed, ${r.skipped} skipped`:'';
      const href=s.log?`${r.logbase}${r.prefix}-${s.log}.log`:r.url;
      const value=id==='cache'&&seconds===0?'<1s':fmt(seconds);
      return `<div class="evidence-stat"><span class="stat-provider">${name(p)}</span><strong>${value}</strong><span class="evidence-note">${note}</span><a href="${href}" target="_blank" rel="noopener">${s.log?'Open recorded log':'Open CI run'}</a></div>`;
    }).join('');
  }
  function paint(){
    $('scrubber').value=String(Math.round(elapsed/max*1000));
    $('elapsed').textContent=`${Math.round(elapsed)}s`;
    for(const p of ['github','namespace']){
      const r=data[scenario][p],t=Math.min(elapsed,r.total),lane=document.querySelector(`[data-provider="${p}"]`);
      lane.querySelector('.lane-time-value').textContent=`${Math.round(t)}s`;
      lane.querySelector('.lane-time small').textContent=t>=r.total?'complete':'recorded time';
      let start=0,current='Setup';
      lane.querySelectorAll('.segment').forEach((b,i)=>{
        const duration=r.times[i],portion=duration>0?Math.max(0,Math.min(1,(t-start)/duration)):t>=start?1:0;
        b.style.clipPath=`inset(0 ${100-portion*100}% 0 0)`;
        if(t>=start)current=stages[i].name;
        start+=duration;
      });
      const cursor=lane.querySelector('.cursor');
      cursor.style.left=`${t/max*100}%`;cursor.style.display=elapsed<max&&t<r.total?'block':'none';
      const status=document.querySelector(`[data-status="${p}"]`);
      if(t>=r.total)status.textContent=scenario==='miss'&&p==='namespace'?'Passed, but cache was empty':`${r.passed.toLocaleString()} passed, ${r.skipped} skipped`;
      else status.textContent=`${current} · recorded replay`;
    }
    updatePlay();
  }
  function choose(key,scroll=false){
    stop();scenario=key;max=Math.max(...Object.values(data[key]).map(r=>r.total));elapsed=max;
    const c=copy[key];
    $('scenario-title').textContent=c.title;$('scenario-description').textContent=c.description;
    $('result-label').textContent=c.label;$('result-summary').textContent=c.summary;$('delta').textContent=c.delta;$('delta-caption').textContent=c.caption;
    $('result-band').classList.toggle('miss',key==='miss');
    document.querySelectorAll('[data-scenario]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.scenario===key)));
    $('ticks').innerHTML=[0,1,2,3,4].map(i=>`<span>${Math.round(max*i/4)}s</span>`).join('');
    $('lanes').innerHTML=['github','namespace'].map(p=>{
      const r=data[key][p];let offset=0;
      const segments=r.times.map((duration,i)=>{const left=offset/max*100;offset+=duration;return `<button class="segment" data-stage="${stages[i].id}" style="left:${left}%;width:${Math.max(duration/max*100,.12)}%" aria-label="${name(p)} ${stages[i].name}: ${duration===0?'under one second':duration.toFixed(2)+' seconds'}" title="${stages[i].name}: ${duration===0?'<1s':fmt(duration)}"></button>`;}).join('');
      return `<div class="lane" data-provider="${p}"><div class="provider-name"><span class="provider-logo ${p}">${logo(p)}</span>${name(p)}</div><div class="track"><div class="segments">${segments}</div><div class="cursor"></div></div><div class="lane-time"><span class="lane-time-value">${r.total}s</span><small>complete</small></div></div><div class="lane-meta"><p data-status="${p}"></p><a href="${r.url}" target="_blank" rel="noopener">CI run</a></div>`;
    }).join('');
    document.querySelectorAll('.segment').forEach(b=>b.addEventListener('click',()=>inspect(b.dataset.stage)));
    inspect(key==='miss'?'cache':selectedStage);paint();
    const url=new URL(location.href);url.searchParams.set('scenario',key);history.replaceState(null,'',url);
    if(scroll)$('experiment-heading').scrollIntoView({behavior:reduced.matches?'instant':'smooth',block:'start'});
  }
  function frame(now){
    if(!playing)return;
    if(!last)last=now;
    elapsed=Math.min(max,elapsed+(now-last)/1000*(max/12));last=now;paint();
    if(elapsed>=max){playing=false;updatePlay();return;}raf=requestAnimationFrame(frame);
  }
  try{
    const response=await fetch('/namespace-ci/data.json');if(!response.ok)throw new Error('Missing data');data=await response.json();
    data.miss={github:data.warm.github,namespace:data.miss.namespace};
    $('legend').innerHTML=stages.map(s=>`<button class="legend-button" data-stage="${s.id}" aria-pressed="${s.id==='build'}"><span class="legend-swatch" style="background:${s.color}"></span>${s.name}</button>`).join('');
    document.querySelectorAll('.legend-button').forEach(b=>b.addEventListener('click',()=>inspect(b.dataset.stage)));
    document.querySelectorAll('[data-scenario]').forEach(b=>b.addEventListener('click',()=>choose(b.dataset.scenario)));
    $('show-miss').addEventListener('click',()=>{choose('miss',true);$('play').click();});
    $('play').addEventListener('click',()=>{
      if(playing){stop();return;}
      if(elapsed>=max)elapsed=0;
      if(reduced.matches){elapsed=max;paint();return;}
      playing=true;last=0;paint();raf=requestAnimationFrame(frame);
    });
    $('finish').addEventListener('click',()=>{stop();elapsed=max;paint();});
    $('scrubber').addEventListener('input',e=>{stop();elapsed=Number(e.target.value)/1000*max;paint();});
    document.addEventListener('visibilitychange',()=>{if(document.hidden&&playing)stop();});
    const requested=new URLSearchParams(location.search).get('scenario');choose(Object.hasOwn(copy,requested)?requested:'warm');
  }catch(error){console.error(error);$('load-error').hidden=false;}
})();
