(()=>{'use strict';
function create(stage,items,render){if(!stage||!items.length)return null;
  stage.classList.add('ws-safe-stage');stage.replaceChildren();
  const base=new Image();base.className='ws-safe-base';base.decoding='async';base.loading='eager';
  const overlay=new Image();overlay.className='ws-safe-overlay';overlay.decoding='async';overlay.alt='';overlay.setAttribute('aria-hidden','true');
  stage.append(base,overlay);
  let index=0,requested=0,token=0,transition=0,ready=false;
  const cache=new Map();
  function load(src){if(cache.has(src))return cache.get(src);const p=new Promise((resolve,reject)=>{const im=new Image();im.decoding='async';im.onload=async()=>{try{if(im.decode)await im.decode()}catch(e){} if(im.naturalWidth)resolve(im);else reject(Error('Image decode failed'))};im.onerror=()=>reject(Error('Image unavailable'));im.src=src;if(im.complete&&im.naturalWidth){if(im.decode)im.decode().then(()=>resolve(im),()=>resolve(im));else resolve(im)}});cache.set(src,p);p.catch(()=>{if(cache.get(src)===p)cache.delete(src)});return p}
  function warm(i){for(const delta of [-1,1,2]){const item=items[(i+delta+items.length)%items.length];load(item.src).catch(()=>{})}}
  function commit(i){index=i;requested=i;render(i,base);warm(i)}
  async function show(n){const target=(n+items.length)%items.length;requested=target;const seq=++token;
    if(transition){clearTimeout(transition);transition=0;overlay.style.transition="none";overlay.style.opacity="0";}
    if(ready&&target===index)return;
    const item=items[target];try{await load(item.src)}catch(e){if(seq===token)stage.dispatchEvent(new CustomEvent('gallery-load-error',{detail:{index:target}}));return}
    if(seq!==token)return;
    // Never fade the only visible image. Keep base opaque throughout the transition.
    if(!ready){base.src=item.src;base.alt='';ready=true;commit(target);return}
    if(transition){clearTimeout(transition);transition=0}
    overlay.style.transition='none';overlay.style.opacity='0';overlay.src=item.src;
    overlay.getBoundingClientRect();
    const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const oldPortrait=base.naturalHeight>base.naturalWidth;
    const newPortrait=overlay.naturalHeight>overlay.naturalWidth;
    const orientationChanged=oldPortrait!==newPortrait;
    overlay.style.transition=(reduced||orientationChanged)?'none':'opacity 280ms ease';overlay.style.opacity='1';
    const finish=()=>{if(seq!==token)return;base.src=item.src;overlay.style.transition='none';overlay.style.opacity='0';commit(target);transition=0};
    if(reduced||orientationChanged)finish();else transition=setTimeout(finish,310);
  }
  // Initial image is immediately assigned, so a late script cannot leave the stage uninitialized.
  show(0);
  return {show,next:()=>show(requested+1),prev:()=>show(requested-1),refresh:()=>render(index,base)};
}
window.WebSocialStableGallery={create};
})();