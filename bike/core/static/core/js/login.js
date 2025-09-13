// login.js - client validation & nice micro-animations (no AOS)
document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('loginForm');
  const username = document.getElementById('username');
  const password = document.getElementById('password');
  const feedback = document.getElementById('formFeedback');
  const submitBtn = document.getElementById('submitLogin');

  // disallow typing digits/special chars into username:
  username.addEventListener('input', function (e) {
    // keep only letters and spaces
    const cleaned = this.value.replace(/[^A-Za-z\s]/g, '');
    if (cleaned !== this.value) {
      this.value = cleaned;
    }
  });

  // prevent paste that contains invalid chars
  username.addEventListener('paste', function (e) {
    const text = (e.clipboardData || window.clipboardData).getData('text');
    if (/[^A-Za-z\s]/.test(text)) {
      e.preventDefault();
      // insert cleaned text
      const cleaned = text.replace(/[^A-Za-z\s]/g, '');
      const start = this.selectionStart || 0;
      const end = this.selectionEnd || 0;
      this.value = this.value.slice(0, start) + cleaned + this.value.slice(end);
    }
  });

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    feedback.textContent = '';

    const nameVal = username.value.trim();
    const pwd = password.value;

    // client-side checks
    if (!nameVal || nameVal.length < 2) {
      feedback.style.color = '#b33';
      feedback.textContent = 'Please enter a valid name (2+ letters).';
      username.focus();
      return;
    }
    if (!/^[A-Za-z\s]{2,40}$/.test(nameVal)) {
      feedback.style.color = '#b33';
      feedback.textContent = 'Name may only contain letters and spaces.';
      username.focus();
      return;
    }
    if (!pwd || pwd.length < 4) {
      feedback.style.color = '#b33';
      feedback.textContent = 'Please enter your password (min 4 chars).';
      password.focus();
      return;
    }

    // micro animation while submitting
    submitBtn.disabled = true;
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Signing in...';
    submitBtn.style.transform = 'translateY(-2px)';

    // let the server handle auth (standard POST form)
    form.submit();
  });
});
