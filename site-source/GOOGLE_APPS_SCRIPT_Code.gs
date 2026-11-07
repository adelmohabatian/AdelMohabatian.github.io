// Example only. Requires explicit deployment by the Gmail account owner.
function doPost(e) {
  try {
    var p = e && e.parameter || {};
    var name = String(p.name || '').trim().slice(0,120);
    var email = String(p.email || '').trim().slice(0,254);
    var subject = String(p.subject || 'WebSocial inquiry').trim().slice(0,160);
    var message = String(p.message || '').trim().slice(0,10000);
    if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || message.length < 10) {
      return HtmlService.createHtmlOutput('<p>Invalid submission. Please return and check the fields.</p>');
    }
    GmailApp.sendEmail('adel.mohabatian2007@gmail.com', '[WebSocial] ' + subject,
      'From: ' + name + '\nReply-to: ' + email + '\n\n' + message,
      {replyTo:email, name:'WebSocial Contact'});
    return HtmlService.createHtmlOutput('<p>Thank you. Your message was submitted.</p>');
  } catch (err) {
    return HtmlService.createHtmlOutput('<p>Delivery failed. Please email adel.mohabatian2007@gmail.com directly.</p>');
  }
}
