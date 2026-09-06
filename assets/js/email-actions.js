(() => {
  'use strict';

  const emails = window.DAI2_EMAILS || {};
  const personnel = Array.isArray(window.DAI2_PERSONNEL) ? window.DAI2_PERSONNEL : [];
  const candidates = personnel.filter(person => emails[person.name]).sort((a, b) => b.name.length - a.name.length);
  const selector = '.modal-military-item, .birthday-card';
  const validEmail = value => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value || '').trim());

  function resolvePerson(card) {
    const text = String(card?.textContent || '');
    return candidates.find(person => text.includes(person.name)) || null;
  }

  function addEmail(card) {
    if (!card || card.querySelector('[data-dai2-email-action]')) return;
    const person = resolvePerson(card);
    if (!person) return;
    const email = String(emails[person.name] || '').trim();
    if (!validEmail(email)) return;
    const link = document.createElement('a');
    link.className = 'cta-button cta-button-secondary';
    link.textContent = 'Enviar e-mail';
    link.href = `mailto:${email}`;
    link.setAttribute('data-dai2-email-action', 'true');
    link.setAttribute('aria-label', `Enviar e-mail para ${person.rank} ${person.name}`);
    link.style.display = 'inline-flex';
    link.style.alignItems = 'center';
    link.style.justifyContent = 'center';
    link.style.textDecoration = 'none';
    link.style.marginTop = '8px';
    link.style.width = '100%';
    card.appendChild(link);
  }

  function scan(root = document) {
    if (root.matches?.(selector)) addEmail(root);
    root.querySelectorAll?.(selector).forEach(addEmail);
  }

  document.addEventListener('DOMContentLoaded', () => {
    scan();
    const observer = new MutationObserver(mutations => {
      mutations.forEach(mutation => mutation.addedNodes.forEach(node => {
        if (node.nodeType === Node.ELEMENT_NODE) scan(node);
      }));
    });
    observer.observe(document.body, { childList: true, subtree: true });
  });
})();
