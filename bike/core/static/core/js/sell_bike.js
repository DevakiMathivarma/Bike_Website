// sell_bike.js
document.addEventListener('DOMContentLoaded', function () {
  function openPopup(popup) {
    popup.style.display = 'block';
    popup.setAttribute('aria-hidden', 'false');
    popup.animate(
      [{ opacity: 0, transform: 'translateY(-8px)' }, { opacity: 1, transform: 'translateY(0)' }],
      { duration: 240, easing: 'ease-out' }
    );

    // clamp to right if overflowing viewport
    const rect = popup.getBoundingClientRect();
    if (rect.right > (window.innerWidth - 8)) {
      popup.classList.add('clamp-right');
    } else {
      popup.classList.remove('clamp-right');
    }
  }
  function closePopup(popup) {
    if (!popup) return;
    popup.style.display = 'none';
    popup.setAttribute('aria-hidden', 'true');
  }

  // wire up pseudo select popups
  document.querySelectorAll('.pseudo').forEach(function (pseudo) {
    const field = pseudo.dataset.name;
    const popup = document.querySelector('.popup-' + field);
    if (!popup) return;

    pseudo.addEventListener('click', function () {
      document.querySelectorAll('.popup-list').forEach(p => { if (p !== popup) closePopup(p); });
      openPopup(popup);
      const s = popup.querySelector('.popup-search');
      if (s) setTimeout(() => s.focus(), 60);
    });

    popup.querySelectorAll('.list li').forEach(function (li) {
      li.addEventListener('click', function () {
        const value = li.textContent.trim();
        pseudo.textContent = value;
        const hid = document.getElementById('input_' + field);
        if (hid) hid.value = value;
        closePopup(popup);
      });
    });

    const search = popup.querySelector('.popup-search');
    if (search) {
      search.addEventListener('input', function () {
        const q = this.value.trim().toLowerCase();
        popup.querySelectorAll('.list li').forEach(function (li) {
          li.style.display = li.textContent.toLowerCase().includes(q) ? '' : 'none';
        });
      });
    }
  });

  // generate years
  (function fillYears() {
    const lis = document.getElementById('yearList');
    if (!lis) return;
    const current = new Date().getFullYear();
    for (let y = current; y >= 2005; y--) {
      const li = document.createElement('li');
      li.textContent = String(y);
      lis.appendChild(li);
    }
    lis.querySelectorAll('li').forEach(function (li) {
      li.addEventListener('click', function () {
        const value = this.textContent.trim();
        const pseudo = document.querySelector('[data-name="year"]');
        pseudo.textContent = value;
        const hid = document.getElementById('input_year');
        if (hid) hid.value = value;
        closePopup(document.querySelector('.popup-year'));
      });
    });
  })();

  // close when clicking outside
  document.addEventListener('click', function (e) {
    if (e.target.closest('.pseudo') || e.target.closest('.popup-list')) return;
    document.querySelectorAll('.popup-list').forEach(p => closePopup(p));
  });

  // CSRF helper
  function getCSRF() {
    const el = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (el) return el.value;
    const getCookie = (name) => {
      let v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
      return v ? v[2] : null;
    };
    return getCookie('csrftoken');
  }

  // Get Price
  const getBtn = document.getElementById('getPrice');
  const modal = document.getElementById('sellModal');
  const sellClose = document.getElementById('sellClose');
  const quoteOk = document.getElementById('quoteOk');
  const quoteText = document.getElementById('quoteText');

  if (getBtn) {
    getBtn.addEventListener('click', function () {
      const payload = {
        brand: document.getElementById('input_brand').value,
        model: document.getElementById('input_model').value,
        variant: document.getElementById('input_variant').value,
        year: document.getElementById('input_year').value,
        kms: document.getElementById('input_kms').value,
        owner: document.getElementById('input_owner').value,
        name: document.getElementById('seller_name').value,
        phone: document.getElementById('seller_phone').value
      };

      if (!payload.brand || !payload.model || !payload.variant || !payload.year || !payload.kms || !payload.owner) {
        getBtn.animate([{ transform: 'translateY(-6px)' }, { transform: 'translateY(0)' }], { duration: 180 });
        alert('Please select brand, model, variant, year, kms and owner to continue.');
        return;
      }

      fetch(window.location.origin + '/sell-bike/get-price/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
          'X-CSRFToken': getCSRF()
        },
        body: new URLSearchParams(payload).toString()
      })
        .then(r => r.json())
        .then(data => {
          if (!data || !data.ok) {
            alert(data && data.error ? data.error : 'Server error');
            return;
          }
          quoteText.textContent = 'Estimated resale value: ₹' + Number(data.price).toLocaleString();
          modal.style.display = 'flex';
          modal.setAttribute('aria-hidden', 'false');
        })
        .catch(err => {
          console.error(err);
          alert('Request failed — try again');
        });
    });
  }

  if (sellClose) sellClose.addEventListener('click', () => { modal.style.display = 'none'; });
  if (quoteOk) quoteOk.addEventListener('click', () => { modal.style.display = 'none'; });
});
