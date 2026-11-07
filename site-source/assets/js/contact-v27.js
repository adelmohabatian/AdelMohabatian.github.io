/* Keep the Google-hosted form in sync with WebSocial language preference. */
(()=>{'use strict';
const frame=document.getElementById('websocial-google-form');
const fallback=document.getElementById('websocial-open-form');
if(!frame)return;
const base='https://script.google.com/macros/s/AKfycbzpqLk3ce5CYZRZ3UwkFrvLS4j6-pRPpY-TE-KY9_b1YA5J7Mzkf1D4dTwGH5wJZHpM2g/exec';
let current='en';
function sync(){
 const lang=document.documentElement.lang==='fa'?'fa':'en';
 if(lang===current && frame.dataset.ready==='yes')return;
 current=lang;
 const target=base+'?lang='+lang;
 if(frame.getAttribute('src')!==target)frame.setAttribute('src',target);
 frame.dataset.ready='yes';
 frame.setAttribute('title',lang==='fa'?'فرم ارتباط با عادل محبتیان':'Contact Adel Mohabatian');
 if(fallback)fallback.href=target;
}
sync();
new MutationObserver(sync).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
})();
