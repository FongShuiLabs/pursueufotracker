// Filter chips
const chips = document.querySelectorAll('.chip');
const cards = document.querySelectorAll('.card');

chips.forEach(chip => {
  chip.addEventListener('click', () => {
    chips.forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    const f = chip.dataset.filter;
    cards.forEach(card => {
      if (f === 'all' || card.dataset.cat === f || card.dataset.cat === 'all') {
        card.classList.remove('hidden');
      } else {
        card.classList.add('hidden');
      }
    });
  });
});

// Subtle parallax on hero
const hero = document.querySelector('.hero');
window.addEventListener('scroll', () => {
  const y = window.scrollY;
  if (y < 800 && hero) {
    hero.style.transform = `translateY(${y * 0.15}px)`;
    hero.style.opacity = Math.max(0, 1 - y / 600);
  }
});
