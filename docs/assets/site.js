(() => {
  const search = document.querySelector('#article-search');
  if (!search) return;
  const filters = [...document.querySelectorAll('.filter')];
  const cards = [...document.querySelectorAll('.article-card')];
  let category = 'all';
  function update() {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    cards.forEach(card => {
      const match = (category === 'all' || card.dataset.category === category) && card.dataset.search.toLocaleLowerCase().includes(query);
      card.hidden = !match;
      if (match) visible++;
    });
    document.querySelector('#empty-results').hidden = visible > 0;
  }
  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.category;
    filters.forEach(filter => {
      const active = filter === button;
      filter.classList.toggle('active', active);
      filter.setAttribute('aria-pressed', String(active));
    });
    update();
  }));
  search.addEventListener('input', update);
})();
