(()=>{
 const messages={publication:{fa:'مقاله در حال انتشار است؛ فایل PDF هنوز برای دریافت مستقیم در سایت موجود نیست.',en:'This article is pending publication and its PDF is not yet available on this website.'},file:{fa:'مقاله دارای اطلاعات انتشار است، اما فایل PDF آن هنوز برای دریافت مستقیم در سایت بارگذاری نشده است.',en:'Publication information is available, but the PDF has not yet been uploaded to this website.'}};
 document.addEventListener('click',async e=>{
   const pending=e.target.closest('[data-pdf-pending]');if(pending){const kind=pending.getAttribute('data-pdf-pending')||'publication';alert(messages[kind][document.documentElement.lang==='fa'?'fa':'en']);return;}
   const btn=e.target.closest('[data-copy-citation]');if(!btn)return;
   const fa=document.documentElement.lang==='fa';const value=btn.getAttribute(fa?'data-cite-fa':'data-cite-en');const feedback=btn.parentElement.querySelector('.ws-copy-feedback');
   try{if(navigator.clipboard && window.isSecureContext){await navigator.clipboard.writeText(value)}else{const ta=document.createElement('textarea');ta.value=value;ta.setAttribute('readonly','');ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();if(!document.execCommand('copy'))throw Error('copy failed');ta.remove();}if(feedback)feedback.textContent=fa?'ارجاع کپی شد':'Citation copied';}
   catch(err){if(feedback)feedback.textContent=fa?'کپی خودکار ممکن نشد؛ متن ارجاع را انتخاب و کپی کنید.':'Could not copy automatically; select the reference text above.';}
 });
})();