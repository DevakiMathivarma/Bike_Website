// accessible-drawer (robust) - replace existing drawer JS with this
document.addEventListener('DOMContentLoaded', function () {
  const menuToggle = document.getElementById('menuToggle');
  const navLinks = document.getElementById('navLinks');
  const overlay = document.getElementById('mobileOverlay');
  const pageMain = document.getElementById('pageMain');
  const pageHeader = document.getElementById('pageHeader');

  if (!menuToggle || !navLinks) return;

  // try to find close button (direct id or inside navLinks)
  let menuClose = document.getElementById('menuClose');
  if (!menuClose) menuClose = navLinks.querySelector('.menu-close');

  // store what had focus before opening
  let previousFocus = null;

  function getFocusableInDrawer() {
    return navLinks.querySelectorAll('a, button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
  }

  function makeInert(el) {
    try {
      el.inert = true;
    } catch (e) {
      el.setAttribute('aria-hidden', 'true');
      const focusables = el.querySelectorAll('a, button, [href], input, select, textarea, [tabindex]');
      focusables.forEach(f => {
        if (f.hasAttribute('tabindex')) f.dataset._savedTabindex = f.getAttribute('tabindex');
        f.setAttribute('tabindex', '-1');
      });
    }
  }

  function removeInert(el) {
    try {
      el.inert = false;
    } catch (e) {
      el.removeAttribute('aria-hidden');
      const focusables = el.querySelectorAll('[data-_saved-tabindex], a, button, [href], input, select, textarea, [tabindex]');
      focusables.forEach(f => {
        if (f.dataset._savedTabindex !== undefined) {
          f.setAttribute('tabindex', f.dataset._savedTabindex);
          delete f.dataset._savedTabindex;
        } else if (f.hasAttribute('tabindex') && f.getAttribute('tabindex') === '-1') {
          f.removeAttribute('tabindex');
        }
      });
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') {
      closeDrawer();
      return;
    }

    if (e.key === 'Tab') {
      const focusables = Array.from(getFocusableInDrawer());
      if (!focusables.length) return;

      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      const active = document.activeElement;

      if (!e.shiftKey && active === last) {
        e.preventDefault();
        first.focus();
      } else if (e.shiftKey && active === first) {
        e.preventDefault();
        last.focus();
      }
    }
  }

  function openDrawer() {
    previousFocus = document.activeElement;
    navLinks.classList.add('show');
    overlay.classList.add('active');

    navLinks.setAttribute('aria-modal', 'true');
    navLinks.setAttribute('role', 'dialog');

    if (pageMain) makeInert(pageMain);
    if (pageHeader) makeInert(pageHeader);

    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';

    // focus the close button if available, else first focusable
    const focusables = getFocusableInDrawer();
    if (menuClose) menuClose.focus();
    else if (focusables.length) focusables[0].focus();

    document.addEventListener('keydown', handleKeydown);
  }

  function closeDrawer() {
    navLinks.classList.remove('show');
    overlay.classList.remove('active');

    navLinks.setAttribute('aria-modal', 'false');
    navLinks.removeAttribute('role');

    if (pageMain) removeInert(pageMain);
    if (pageHeader) removeInert(pageHeader);

    document.documentElement.style.overflow = '';
    document.body.style.overflow = '';

    if (previousFocus && typeof previousFocus.focus === 'function') previousFocus.focus();

    document.removeEventListener('keydown', handleKeydown);
  }

  // menu toggle click
  menuToggle.addEventListener('click', function () {
    if (navLinks.classList.contains('show')) closeDrawer();
    else openDrawer();
  });

  // Event delegation for close button (robust) and for nav link clicks
  navLinks.addEventListener('click', function (evt) {
    const closeBtn = evt.target.closest('.menu-close');
    if (closeBtn) {
      // ensure it's the drawer close control
      closeDrawer();
      return;
    }

    const link = evt.target.closest('.nav-link');
    if (link && window.innerWidth <= 480) {
      // clicking a menu item closes the drawer on mobile
      // small timeout is ok if the link is internal (lets navigation begin)
      setTimeout(closeDrawer, 50);
    }
  });

  // overlay click: only close when clicking the overlay itself (not if clicking drawer)
  if (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeDrawer();
    });
  }

  // safety: if menuClose exists attach click (duplicate safe)
  if (menuClose && !menuClose.dataset.listenerAttached) {
    menuClose.addEventListener('click', function (e) {
      closeDrawer();
    });
    menuClose.dataset.listenerAttached = '1';
  }

  // set active link by path
  const links = document.querySelectorAll('.nav-links .nav-link');
  const path = window.location.pathname.replace(/\/+$/,'') || '/';
  let matched = false;
  links.forEach(link => {
    const href = link.getAttribute('href') || '';
    if (!href.startsWith('http') && href.replace(/\/+$/,'') === path) {
      link.classList.add('active');
      matched = true;
    }
  });
  if (!matched) {
    links.forEach(link => { if (link.getAttribute('href') === '/' && path === '/') link.classList.add('active'); });
  }

  // apply brand colors (unchanged)
  (function () {
    const brandEl = document.getElementById('brand');
    if (!brandEl) return;
    const left = brandEl.dataset.leftColor || '#2b8ecb';
    const right = brandEl.dataset.rightColor || '#ff6b6b';
    brandEl.style.setProperty('--left-color', left);
    brandEl.style.setProperty('--right-color', right);
  })();
});


// footer.js
document.addEventListener('DOMContentLoaded', function () {
  // simple crossfade carousel for .bike-slide
  const slides = Array.from(document.querySelectorAll('.bike-slide'));
  if (slides.length > 0) {
    let idx = 0;
    slides.forEach((s,i) => { if (i!==0) s.classList.remove('active'); else s.classList.add('active'); });
    setInterval(() => {
      slides[idx].classList.remove('active');
      idx = (idx + 1) % slides.length;
      slides[idx].classList.add('active');
    }, 3500); // change every 3.5s
  }

  // Make social icons touch-friendly: open link in new window (already does) but we add ripple on click
  document.querySelectorAll('.social').forEach(btn=>{
    btn.addEventListener('click', e=>{
      // small click scale effect handled by CSS hover; we add aria-pressed for a11y moment
      btn.setAttribute('aria-pressed','true');
      setTimeout(()=>btn.removeAttribute('aria-pressed'),500);
    });
  });
});
