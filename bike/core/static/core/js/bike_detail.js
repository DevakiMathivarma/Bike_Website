// bike_detail.js
document.addEventListener('DOMContentLoaded', function () {
  // Thumbnail click -> change main image
  document.querySelectorAll('.thumb').forEach(t => {
    t.addEventListener('click', function () {
      const url = this.dataset.src || this.src;
      const main = document.getElementById('mainBikeImage');
      if (main) {
        // simple fade effect
        main.style.transition = 'opacity .25s ease';
        main.style.opacity = 0;
        setTimeout(() => {
          main.src = url;
          main.style.opacity = 1;
        }, 180);
      }
      // mark active thumb visually (optional)
      document.querySelectorAll('.thumb-item').forEach(it => it.classList.remove('active'));
      this.closest('.thumb-item')?.classList.add('active');
    });
  });

  // Modal helpers
  const testDriveModal = document.getElementById('testDriveModal');
  const openBtn = document.getElementById('openTestRideBtn');
  const tdClose = document.getElementById('td-close') || document.getElementById('td-cancel');

  function openTestDrive() {
    if (testDriveModal) {
      testDriveModal.style.display = 'flex';
      // accessibility
      testDriveModal.setAttribute('aria-hidden', 'false');
    }
  }
  function closeTestDrive() {
    if (testDriveModal) {
      testDriveModal.style.display = 'none';
      testDriveModal.setAttribute('aria-hidden', 'true');
    }
  }

  openBtn && openBtn.addEventListener('click', openTestDrive);
  if (tdClose) tdClose.addEventListener('click', closeTestDrive);

  // close modal on clicking outside or ESC
  document.addEventListener('click', function (e) {
    if (!testDriveModal) return;
    if (testDriveModal.style.display === 'flex' && e.target === testDriveModal) {
      closeTestDrive();
    }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeTestDrive();
      const successModal = document.getElementById('successModal');
      if (successModal) successModal.style.display = 'none';
    }
  });

  // ---- AJAX submit book test ride form ----
  const form = document.getElementById('testRideForm');
  const feedback = document.getElementById('td-feedback');
  const submitBtn = document.getElementById('td-submit');

  function getCookie(name) {
    let v = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const c = cookies[i].trim();
        if (c.startsWith(name + '=')) {
          v = decodeURIComponent(c.substring(name.length + 1));
          break;
        }
      }
    }
    return v;
  }
  const csrftoken = getCookie('csrftoken');

  if (form && submitBtn) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      feedback.textContent = '';
      submitBtn.disabled = true;
      submitBtn.textContent = 'Booking...';

      const action = form.getAttribute('action');
      const data = new FormData(form);

      fetch(action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json'
        },
        body: data
      })
        .then(r => r.json())
        .then(json => {
          if (json && json.success) {
            feedback.style.color = 'green';
            feedback.textContent = json.message || 'Booked successfully.';
            setTimeout(() => {
              closeTestDrive();
              // show success modal
              const sm = document.getElementById('successModal');
              if (sm) {
                sm.style.display = 'flex';
                sm.setAttribute('aria-hidden', 'false');
                const ok = document.getElementById('successOk');
                ok && ok.addEventListener('click', function () {
                  sm.style.display = 'none';
                  sm.setAttribute('aria-hidden', 'true');
                });
                setTimeout(() => {
                  sm.style.display = 'none';
                }, 3500);
              }
            }, 800);
          } else {
            feedback.style.color = '#b33';
            feedback.textContent = json.message || 'Could not book. Please try again.';
          }
        })
        .catch(err => {
          console.error(err);
          feedback.style.color = '#b33';
          feedback.textContent = 'Network error. Try again.';
        })
        .finally(() => {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Confirm & Pay ₹1000';
        });
    });
  }

  // small: clicking success OK closes modal
  const successOk = document.getElementById('successOk');
  successOk && successOk.addEventListener('click', function () {
    const sm = document.getElementById('successModal');
    if (sm) sm.style.display = 'none';
  });
});
