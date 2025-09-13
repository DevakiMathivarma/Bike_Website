// core/static/core/js/buybike.js
// Full buybike.js: accessible single-click accordion + range sync + apply filters + sort auto-apply

document.addEventListener('DOMContentLoaded', function () {
  // ---------- Accordion toggles (accessible, single-click) ----------
  document.querySelectorAll('.toggle-btn').forEach(btn => {
    try { btn.type = btn.type || 'button'; } catch (e) {}
    const targetSelector = btn.dataset.target;
    const panel = document.querySelector(targetSelector);
    if (!panel) return;

    // ensure panel starts closed
    panel.classList.remove('open');
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', panel.id || '');

    // pointerup for single-click responsiveness
    btn.addEventListener('pointerup', function (ev) {
      ev.preventDefault();
      const isOpen = panel.classList.contains('open');
      if (isOpen) {
        panel.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
      } else {
        panel.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
        // focus first input in panel for keyboard users
        const focusable = panel.querySelector('input, select, button, textarea, a[href]');
        if (focusable) focusable.focus({preventScroll: true});
      }
    });

    // keyboard support (Enter / Space)
    btn.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        btn.dispatchEvent(new Event('pointerup'));
      }
    });
  });

  // ---------- Range / input synchronization ----------
  const priceRange = document.getElementById('priceRange');
  const minPrice = document.getElementById('minPrice');
  const maxPrice = document.getElementById('maxPrice');

  if (priceRange && maxPrice) {
    // initialize range -> numeric input sync
    priceRange.addEventListener('input', () => {
      maxPrice.value = priceRange.value;
    });
    // if user types into maxPrice update range (debounced simple)
    maxPrice.addEventListener('input', () => {
      const v = parseInt(maxPrice.value || 0, 10);
      if (!isNaN(v)) priceRange.value = Math.min(Math.max(v, parseInt(priceRange.min || 0, 10)), parseInt(priceRange.max || 0, 10));
    });
  }

  const yearRange = document.getElementById('yearRange');
  const minYear = document.getElementById('minYear');
  const maxYear = document.getElementById('maxYear');
  if (yearRange && maxYear) {
    yearRange.addEventListener('input', () => { maxYear.value = yearRange.value; });
    maxYear.addEventListener('input', () => {
      const v = parseInt(maxYear.value || 0, 10);
      if (!isNaN(v)) yearRange.value = Math.min(Math.max(v, parseInt(yearRange.min || 0, 10)), parseInt(yearRange.max || 0, 10));
    });
  }

  const kmRange = document.getElementById('kmRange');
  const maxKm = document.getElementById('maxKm');
  if (kmRange && maxKm) {
    kmRange.addEventListener('input', () => { maxKm.value = kmRange.value; });
    maxKm.addEventListener('input', () => {
      const v = parseInt(maxKm.value || 0, 10);
      if (!isNaN(v)) kmRange.value = Math.min(Math.max(v, parseInt(kmRange.min || 0, 10)), parseInt(kmRange.max || 0, 10));
    });
  }

  // ---------- Apply Filters: build query string & redirect ----------
  const applyBtn = document.getElementById('applyFilters');
  if (applyBtn) {
    applyBtn.addEventListener('click', function () {
      const params = new URLSearchParams();

      // categories (multiple)
      document.querySelectorAll('.cat-checkbox:checked').forEach(c => params.append('category', c.value));

      // brands
      document.querySelectorAll('.brand-checkbox:checked').forEach(b => params.append('brand', b.value));

      // price
      if (minPrice && minPrice.value) params.set('min_price', minPrice.value);
      if (maxPrice && maxPrice.value) params.set('max_price', maxPrice.value);

      // year
      if (minYear && minYear.value) params.set('min_year', minYear.value);
      if (maxYear && maxYear.value) params.set('max_year', maxYear.value);

      // km
      if (maxKm && maxKm.value) params.set('max_km', maxKm.value);

      // cc (single radio)
      const cc = document.querySelector('input[name="cc"]:checked');
      if (cc) params.set('cc', cc.value);

      // fuel
      document.querySelectorAll('input[name="fuel"]:checked').forEach(f => params.append('fuel', f.value));

      // sort
      const sort = document.getElementById('sortSelect');
      if (sort && sort.value) params.set('sort', sort.value);

      // keep existing location param if present
      const q = new URLSearchParams(window.location.search);
      if (q.get('location')) params.set('location', q.get('location'));

      // build URL and redirect
      const url = window.location.pathname + (params.toString() ? ('?' + params.toString()) : '');
      window.location.href = url;
    });
  }

  // ---------- sort auto apply ----------
  const sortSelect = document.getElementById('sortSelect');
  if (sortSelect) {
    sortSelect.addEventListener('change', function () {
      // trigger apply button to reuse same logic
      if (applyBtn) applyBtn.click();
      else {
        // fallback: append sort and reload
        const params = new URLSearchParams(window.location.search);
        params.set('sort', sortSelect.value);
        window.location.href = window.location.pathname + '?' + params.toString();
      }
    });
  }

  // ---------- optional: close all panels when clicking outside (nice-to-have) ----------
  document.addEventListener('pointerdown', function (ev) {
    // if click happens outside the filters sidebar, close open panels
    const filters = document.querySelector('.filters');
    if (!filters) return;
    if (!filters.contains(ev.target)) {
      document.querySelectorAll('.filter-panel.open').forEach(p => {
        p.classList.remove('open');
        // find corresponding button and update aria-expanded
        const btn = document.querySelector(`.toggle-btn[data-target="#${p.id}"]`);
        if (btn) btn.setAttribute('aria-expanded', 'false');
      });
    }
  });
});
