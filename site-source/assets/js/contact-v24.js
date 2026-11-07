(()=>{
 const form=document.getElementById('websocial-contact-form');if(!form)return;
 // An optional Google Apps Script endpoint can be configured here after deployment.
 // Leave empty to use the user's email application. Never claim a message was sent automatically.
 const appsScriptUrl='';
 form.addEventListener('submit',event=>{
  event.preventDefault();if(!form.reportValidity())return;
  const name=form.elements.namedItem('name').value.trim();
  const email=form.elements.namedItem('email').value.trim();
  const subject=form.elements.namedItem('subject').value.trim();
  const message=form.elements.namedItem('message').value.trim();
  if(!name||!email||message.length<10)return;
  if(appsScriptUrl && /^https:\/\/script\.google\.com\/macros\/s\//.test(appsScriptUrl)){
   form.action=appsScriptUrl;form.method='POST';form.target='_blank';
   form.submit();return;
  }
  const title=subject||'WebSocial inquiry';
  const body=`Name: ${name}\nEmail: ${email}\n\n${message}`;
  window.location.href='mailto:adel.mohabatian2007@gmail.com?subject='+encodeURIComponent(title)+'&body='+encodeURIComponent(body);
 });
})();