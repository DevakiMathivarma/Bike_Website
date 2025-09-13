// contact.js - robust select validation + fallback to option text
(function () {
  document.addEventListener('DOMContentLoaded', init);

  function init() {
    // Helpers
    function qs(sel){ return document.querySelector(sel); }

    const nameInput = qs('#name');
    const emailInput = qs('#email');
    const phoneInput = qs('#phone');
    const reasonSelect = qs('#reason');
    const channelSelect = qs('#channel');
    const messageInput = qs('#message');
    const form = qs('#contactForm');

    if (!form) {
      console.error('contact form element not found (#contactForm)');
      return;
    }

    // Regexes
    const NAME_FULL_REGEX = /^[A-Za-z\s\.\-']{2,100}$/;
    const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    const PHONE_REGEX = /^[0-9]{7,15}$/;

    // CSRF cookie helper
    function getCookie(name) {
      const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
      return v ? v.pop() : '';
    }
    const csrftoken = getCookie('csrftoken');

    // small input listeners (optional -- keep as before)
    if (nameInput) {
      nameInput.addEventListener('keypress', function(e){
        const ch = String.fromCharCode(e.which || e.keyCode);
        if(!/^[A-Za-z\s\.\-']$/.test(ch)) e.preventDefault();
      });
    }
    if (phoneInput) {
      phoneInput.addEventListener('keypress', function(e){
        const ch = String.fromCharCode(e.which || e.keyCode);
        if(!/^[0-9]$/.test(ch)) e.preventDefault();
      });
    }
    if (messageInput) {
      messageInput.addEventListener('keypress', function(e){
        const ch = String.fromCharCode(e.which || e.keyCode);
        if(!/^[A-Za-z\s\.\,\?\!\-'\(\)]$/.test(ch)) e.preventDefault();
      });
    }

    // ---- Robust select validator ----
    // Returns { ok: boolean, reason: string, debug: {...} }
    function checkSelect(sel, label) {
      if(!sel) {
        return { ok:false, reason:`${label} SELECT NOT FOUND`, debug: null };
      }
      const idx = sel.selectedIndex;
      const opt = sel.options && typeof idx === 'number' ? sel.options[idx] : null;
      const debug = {
        selectedIndex: idx,
        optionExists: !!opt,
        optionDisabled: opt ? !!opt.disabled : null,
        optionValue: opt ? String(opt.value || '').trim() : null,
        optionText: opt ? String(opt.text || '').trim() : null,
        selectValue: String(sel.value || '').trim()
      };

      // If option missing or disabled -> invalid
      if(!opt) {
        return { ok:false, reason:`${label} no option`, debug };
      }
      if(opt.disabled) {
        return { ok:false, reason:`${label} selected option is disabled`, debug };
      }

      // If option value has content => valid
      if(debug.optionValue && debug.optionValue.length > 0) {
        return { ok:true, reason:'ok', debug };
      }

      // If option text has content => valid
      if(debug.optionText && debug.optionText.length > 0) {
        // but treat common placeholders explicitly as invalid (optional)
        const placeholderRegex = /reason to contact|how did you find out about us|\bselect\b/i;
        if(placeholderRegex.test(debug.optionText)) {
          return { ok:false, reason:`${label} placeholder selected`, debug };
        }
        return { ok:true, reason:'ok (text)', debug };
      }

      // fallback: look at select.value
      if(debug.selectValue && debug.selectValue.length > 0) {
        return { ok:true, reason:'ok (select.value)', debug };
      }

      return { ok:false, reason:`${label} empty value/text`, debug };
    }

    // Utility to pick text or value to send to server
    function selectedTextOrValue(sel) {
      if(!sel) return '';
      const opt = sel.options && sel.options[sel.selectedIndex];
      if(opt) {
        const v = (opt.value || '').toString().trim();
        if(v.length) return v;
        const t = (opt.text || '').toString().trim();
        return t;
      }
      return (sel.value || '').toString().trim();
    }

    // Final validation & submit
    form.addEventListener('submit', function(ev){
      ev.preventDefault();

      const name = nameInput ? nameInput.value.trim() : '';
      const email = emailInput ? emailInput.value.trim() : '';
      const phone = phoneInput ? phoneInput.value.trim() : '';
      const message = messageInput ? messageInput.value.trim() : '';

      // name
      if(!NAME_FULL_REGEX.test(name)){
        alert('Please enter a valid name (letters and spaces only, at least 2 characters).');
        if(nameInput) nameInput.focus();
        return;
      }
      // email
      if(!EMAIL_REGEX.test(email)){
        alert('Please enter a valid email address.');
        if(emailInput) emailInput.focus();
        return;
      }
      // phone
      if(!PHONE_REGEX.test(phone)){
        alert('Please enter a valid phone number (digits only, 7-15 characters).');
        if(phoneInput) phoneInput.focus();
        return;
      }

      // selects
      const reasonCheck = checkSelect(reasonSelect, 'Reason to Contact');
      const channelCheck = checkSelect(channelSelect, 'How did you find out about us?');

      if(!reasonCheck.ok || !channelCheck.ok) {
        // helpful console debug
        console.warn('Select validation failed', { reasonCheck, channelCheck });
        // Build friendly message for alert
        let alertMsg = 'Please select options for both "Reason to Contact" and "How did you find out about us?".';
        // If you want to show exact reason in alert (optional), uncomment next line:
        // alertMsg += '\n\nDebug:\n' + JSON.stringify({ reasonCheck, channelCheck }, null, 2);
        alert(alertMsg);
        return;
      }

      // message
      if(message.length < 5){
        alert('Please enter a descriptive message (at least 5 characters).');
        if(messageInput) messageInput.focus();
        return;
      }
      if(!/^[A-Za-z\s\.\,\?\!\-'\(\)]{5,1000}$/.test(message)){
        alert('Message contains invalid characters. Use letters, spaces and basic punctuation only.');
        if(messageInput) messageInput.focus();
        return;
      }

      // compose payload (use visible option text if value empty)
      const payload = {
        name,
        email,
        phone,
        reason: selectedTextOrValue(reasonSelect),
        channel: selectedTextOrValue(channelSelect),
        message
      };

      // send to backend
      fetch('/contact/submit/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json;charset=UTF-8',
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(payload)
      })
      .then(r => r.json().catch(()=>({ success:false, error:'Invalid server response' })))
      .then(data => {
        if(data && data.success){
          alert('Message sent successfully. Thank you!');
          form.reset();
        } else {
          alert('Error sending message: ' + (data && data.error ? data.error : 'Server error'));
        }
      })
      .catch(err => {
        console.error(err);
        alert('Network error while sending message. Try again later.');
      });
    });
  } // end init
})();
