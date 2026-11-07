/* WebSocial v3.4 — progressive-enhancement header for inner pages */
(function(){
 const sections=[['/','Home','خانه'],['/research/shahsavan/','Research','پژوهش'],['/publications/','Publications','انتشارات'],['/films/','Films','فیلم‌ها'],['/photography/','Photography','عکاسی'],['/about/','About & CV','درباره و رزومه'],['/contact/','Contact','ارتباط']];
 function sectionFor(path){if(path.startsWith('/research/'))return sections[1];if(path.startsWith('/publications/'))return sections[2];if(path.startsWith('/films/'))return sections[3];if(path.startsWith('/photography/'))return sections[4];return sections.find(s=>s[0]===path)||sections[0]}
 function init(){
  const header=document.querySelector('body > header');if(!header)return;
  const wrap=header.querySelector('.wrap');if(!wrap)return;
  const section=sectionFor(location.pathname);const label=document.createElement('span');label.className='ws-section-label';label.dataset.en=section[1];label.dataset.fa=section[2];
  const controls=document.createElement('div');controls.className='ws-header-controls';
  const details=document.createElement('details');details.className='ws-header-menu';
  const summary=document.createElement('summary');summary.dataset.en='Menu';summary.dataset.fa='منو';details.append(summary);
  const panel=document.createElement('div');panel.className='ws-menu-panel';panel.setAttribute('role','navigation');panel.setAttribute('aria-label','Site sections');
  for(const [href,en,fa] of sections){const a=document.createElement('a');a.href=href;a.dataset.en=en;a.dataset.fa=fa;if(section[0]===href)a.setAttribute('aria-current','page');panel.append(a)}
  details.append(panel);controls.append(details);
  const switcher=header.querySelector('button[data-lang-switch]');if(switcher)controls.append(switcher);
  wrap.append(label,controls);document.body.classList.add('ws-sticky-ready');
  function sync(){const fa=document.documentElement.lang==='fa';for(const el of [label,summary,...panel.querySelectorAll('a')])el.textContent=el.dataset[fa?'fa':'en'];}
  sync();new MutationObserver(sync).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
  document.addEventListener('click',e=>{if(!details.contains(e.target))details.open=false});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')details.open=false});
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
