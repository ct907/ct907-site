/* Behaviour for pages migrated from Readymag: the "Browse Projects" drawer and the
   floating "back to sections" button. Pages render fully without this file. */
(() => {
  const root = document.documentElement;
  const toggles = document.querySelectorAll('[data-drawer-toggle]');
  const drawer = document.getElementById('rm-drawer');

  function setOpen(open) {
    root.classList.toggle('rm-drawer-open', open);
    toggles.forEach((t) => t.setAttribute('aria-expanded', String(open)));
    if (drawer) drawer.toggleAttribute('inert', !open);
  }
  if (drawer && toggles.length) {
    setOpen(false);
    toggles.forEach((t) => {
      t.addEventListener('click', (e) => { e.preventDefault(); setOpen(!root.classList.contains('rm-drawer-open')); });
      t.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setOpen(!root.classList.contains('rm-drawer-open')); }
      });
    });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setOpen(false); });
    document.addEventListener('click', (e) => {
      if (!root.classList.contains('rm-drawer-open')) return;
      if (e.target.closest('#rm-drawer .w, [data-drawer-toggle]')) return;
      setOpen(false);
    });
    const close = document.querySelector('.rm-drawer-close');
    if (close) close.addEventListener('click', () => setOpen(false));
  }

  const fixed = document.querySelector('.rm-fixed');
  if (fixed) {
    const threshold = Number(fixed.dataset.showAfter || 0);
    const onScroll = () => {
      const unit = Math.min(window.innerWidth, 2560) / 1024;
      const past = window.innerWidth >= 900 ? window.scrollY > threshold * unit : window.scrollY > 600;
      root.classList.toggle('rm-scrolled', past);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }
})();
