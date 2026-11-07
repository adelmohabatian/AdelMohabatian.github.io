(()=>{'use strict';
const viewer=document.querySelector('.ws-film-viewer');if(!viewer)return;
const stage=viewer.querySelector('.ws-film-stage');
const counter=viewer.querySelector('.ws-film-counter'),title=viewer.querySelector('.ws-film-description');
const caption=viewer.querySelector('.ws-film-caption');
const chapter=document.createElement('span');chapter.className='ws-film-chapter';caption.prepend(chapter);
const note=document.createElement('p');note.className='ws-film-note';caption.append(note);
const chapters=[{fa:'\u0633\u0631\u0632\u0645\u06cc\u0646 \u0648 \u062d\u0631\u06a9\u062a',en:'Land & Movement'},{fa:'\u06a9\u0627\u0631 \u0648 \u0645\u0639\u06cc\u0634\u062a',en:'Work & Livelihood'},{fa:'\u0631\u0648\u0627\u0628\u0637 \u0648 \u0642\u062f\u0631\u062a',en:'Relationships & Power'},{fa:'\u062d\u0627\u0641\u0638\u0647 \u0648 \u0628\u0627\u0632\u06af\u0634\u062a',en:'Memory & Return'}];
const lang=()=>document.documentElement.lang==='fa'?'fa':'en';
fetch('/assets/data/photo-film-stills-v51.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('film manifest');return r.json()}).then(slides=>{
 if(!Array.isArray(slides)||slides.length===0)throw Error('empty film gallery');
 const render=(i,im)=>{
  const s=slides[i],l=lang();title.textContent=s[l]||'';
  note.textContent=s['description_'+l]||'';note.hidden=!note.textContent;
  caption.lang=l;caption.dir=l==='fa'?'rtl':'ltr';
  counter.textContent=String(i+1).padStart(2,'0')+' / '+String(slides.length).padStart(2,'0');
  chapter.textContent=chapters[Math.min(3,Math.floor(i/6))][l];im.alt=s['alt_'+l]||s[l]||'';
 };
 const g=WebSocialStableGallery.create(stage,slides,render);
 viewer.querySelector('.ws-film-prev').onclick=g.prev;viewer.querySelector('.ws-film-next').onclick=g.next;
 let x=null;stage.addEventListener('touchstart',e=>x=e.changedTouches[0].clientX,{passive:true});stage.addEventListener('touchend',e=>{if(x===null)return;const d=e.changedTouches[0].clientX-x;x=null;if(Math.abs(d)>55)(d<0?g.next:g.prev)()},{passive:true});
 viewer.tabIndex=0;viewer.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();(e.key==='ArrowRight'?g.next:g.prev)()}});
 new MutationObserver(g.refresh).observe(document.documentElement,{attributes:true,attributeFilter:['lang','dir']});
 stage.addEventListener('gallery-load-error',()=>{note.hidden=false;note.textContent=lang()==='fa'?'\u062a\u0635\u0648\u06cc\u0631 \u0628\u0627\u0631\u06af\u0630\u0627\u0631\u06cc \u0646\u0634\u062f\u061b \u062a\u0635\u0648\u06cc\u0631 \u0641\u0639\u0644\u06cc \u062d\u0641\u0638 \u0634\u062f.':'Image unavailable; current image retained.'});
}).catch(()=>{title.textContent='Film gallery temporarily unavailable.'})})();
