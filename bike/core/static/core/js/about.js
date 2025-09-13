// about.js
(function () {
  function onReady(fn){
    if(document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  onReady(function(){
    // Intersection Observer for animations
    const io = new IntersectionObserver((entries)=>{
      entries.forEach(entry=>{
        if(entry.isIntersecting){
          entry.target.classList.add('in-view');
        }
      });
    }, { root: null, rootMargin: '0px', threshold: 0.15 });

    document.querySelectorAll('.js-animate, .js-image').forEach(el=>{
      io.observe(el);
    });

    // subtle hero image parallax on mouse move
    const heroImage = document.querySelector('.hero-image');
    if(heroImage){
      heroImage.addEventListener('mousemove', function(e){
        const rect = heroImage.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;
        const tx = (x - 0.5) * 8; // tilt range
        const ty = (y - 0.5) * 8;
        heroImage.style.transform = `translate3d(${tx}px, ${ty}px, 0) scale(1.01)`;
      });
      heroImage.addEventListener('mouseleave', function(){
        heroImage.style.transform = '';
      });
    }
  });
})();
