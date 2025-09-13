// bike_payment.js - selection, UI class toggle, and confirm modal
document.addEventListener('DOMContentLoaded', function () {
  const radios = document.querySelectorAll('input[name="pay"]');
  const labels = Array.from(document.querySelectorAll('.pm-label'));
  const confirmBtn = document.getElementById('confirmBtn');
  const successModal = document.getElementById('successModal');
  const successClose = document.getElementById('successClose');

  // helper to clear checked class
  function clearChecked() {
    labels.forEach(l => l.classList.remove('checked'));
  }

  // Attach click handlers to labels so clicking anywhere toggles radio
  labels.forEach(label => {
    label.addEventListener('click', function (e) {
      // find the input inside this label and check it
      const input = label.querySelector('input[type="radio"]');
      if (!input) return;
      // set checked and update classes
      input.checked = true;
      clearChecked();
      label.classList.add('checked');
    });
  });

  // keyboard accessible: when radio changed (via keyboard), update UI
  radios.forEach(r => {
    r.addEventListener('change', function () {
      clearChecked();
      const parentLabel = this.closest('.pm-label');
      if (parentLabel) parentLabel.classList.add('checked');
    });
  });

  confirmBtn.addEventListener('click', function (e) {
    const sel = document.querySelector('input[name="pay"]:checked');
    if (!sel) {
      // show a focused inline error instead of simple alert
      confirmBtn.focus();
      confirmBtn.animate([{ transform: 'translateY(-3px)' }, { transform: 'translateY(0)' }], { duration: 200 });
      alert("Please select a payment method before confirming.");
      return;
    }

    // show modal
    successModal.style.display = 'flex';
    successModal.setAttribute('aria-hidden', 'false');

    // simulate server-side booking and redirect after a pause
    setTimeout(function () {
      // close and redirect (or you could POST to server)
      // you said you want popup then redirect; adjust as needed
      successModal.style.display = 'none';
      successModal.setAttribute('aria-hidden', 'true');
      // redirect back to home or details page
      window.location.href = '/'; 
    }, 1800);
  });

  if (successClose) {
    successClose.addEventListener('click', function () {
      successModal.style.display = 'none';
      successModal.setAttribute('aria-hidden', 'true');
    });
  }
});
