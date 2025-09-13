// home.js - simple fade carousel that only changes images
document.addEventListener('DOMContentLoaded', function () {
  const carousel = document.getElementById('heroCarousel');
  if (!carousel) return;

  const slides = Array.from(carousel.querySelectorAll('.slide'));
  if (slides.length <= 1) return; // nothing to rotate

  const interval = parseInt(carousel.dataset.interval || '3500', 10);
  let idx = slides.findIndex(s => s.classList.contains('active'));
  if (idx < 0) idx = 0;

  setInterval(() => {
    slides[idx].classList.remove('active');
    idx = (idx + 1) % slides.length;
    slides[idx].classList.add('active');
  }, interval);
});

// feature section homepage
// home-features.js
document.addEventListener('DOMContentLoaded', function () {
  const imgEls = document.querySelectorAll('.js-hp-img');
  const contentEls = document.querySelectorAll('.js-hp-content');

  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
        }
      });
    }, { threshold: 0.2 });

    imgEls.forEach(el => io.observe(el));
    contentEls.forEach(el => io.observe(el));
  } else {
    // fallback: just add immediately
    imgEls.forEach(el => el.classList.add('in-view'));
    contentEls.forEach(el => el.classList.add('in-view'));
  }

  // small hover-like periodic nudge for image (optional)
  imgEls.forEach(img => {
    img.addEventListener('mouseenter', () => img.style.transform = 'rotate(-3deg) scale(1.08)');
    img.addEventListener('mouseleave', () => img.style.transform = '');
  });
});


// support section
// home-support.js - reveal support columns when they scroll into view
document.addEventListener('DOMContentLoaded', function(){
  const cols = document.querySelectorAll('.js-hp-support');

  if('IntersectionObserver' in window){
    const io = new IntersectionObserver((entries)=>{
      entries.forEach(entry=>{
        if(entry.isIntersecting){
          entry.target.classList.add('in-view');
          // Optionally unobserve after reveal
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.18 });

    cols.forEach(c => io.observe(c));
  } else {
    // Fallback: reveal immediately
    cols.forEach(c => c.classList.add('in-view'));
  }
});


document.querySelectorAll(".faq-question").forEach(q => {
  q.addEventListener("click", () => {
    const ans = q.nextElementSibling;
    ans.style.display = ans.style.display === "block" ? "none" : "block";
  });
});
