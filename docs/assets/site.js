(() => {
  const card = document.querySelector('#word-card');
  const wordData = document.querySelector('#word-data');
  if (card && wordData) {
    const words = JSON.parse(wordData.textContent);
    const fields = {
      word: '#word-term', phonetic: '#word-phonetic', meaning: '#word-meaning',
      line_one: '#word-line-one', line_two: '#word-line-two',
      highlight: '#word-highlight', caption: '#word-caption'
    };
    let index = 0;
    let turning = false;
    function renderWord() {
      const word = words[index];
      Object.entries(fields).forEach(([field, selector]) => {
        document.querySelector(selector).textContent = word[field];
      });
      card.dataset.theme = word.theme;
      card.setAttribute('aria-label', `翻到下一个单词；当前单词 ${word.word}`);
      document.querySelector('#word-number').textContent = `No. ${String(index + 1).padStart(3, '0')}`;
      document.querySelector('#word-progress').textContent = `${String(index + 1).padStart(2, '0')} / ${String(words.length).padStart(2, '0')}`;
      document.querySelector('#word-announcement').textContent = `${index + 1} / ${words.length}：${word.word}，${word.meaning}`;
    }
    async function turnPage(direction) {
      if (turning || words.length < 2) return;
      turning = true;
      card.setAttribute('aria-busy', 'true');
      const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const tilt = direction > 0 ? -40 : 35;
      try {
        if (!reduced && card.animate) {
          await card.animate([
            { transform: 'perspective(900px) rotate(-5deg) rotateY(0deg)', opacity: 1 },
            { transform: `perspective(900px) rotate(-7deg) rotateY(${tilt}deg)`, opacity: 0 }
          ], { duration: 150, easing: 'ease-in', fill: 'forwards' }).finished;
        }
        index = (index + direction + words.length) % words.length;
        renderWord();
        if (!reduced && card.animate) {
          await card.animate([
            { transform: `perspective(900px) rotate(-3deg) rotateY(${-tilt}deg)`, opacity: 0 },
            { transform: 'perspective(900px) rotate(-5deg) rotateY(0deg)', opacity: 1 }
          ], { duration: 190, easing: 'ease-out', fill: 'forwards' }).finished;
        }
      } finally {
        if (card.getAnimations) card.getAnimations().forEach(animation => animation.cancel());
        turning = false;
        card.setAttribute('aria-busy', 'false');
      }
    }
    card.addEventListener('click', () => turnPage(1));
    card.addEventListener('keydown', event => {
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        event.preventDefault();
        turnPage(event.key === 'ArrowLeft' ? -1 : 1);
      }
    });
    document.querySelector('#previous-word').addEventListener('click', () => turnPage(-1));
    document.querySelector('#next-word').addEventListener('click', () => turnPage(1));
  }

  const search = document.querySelector('#article-search');
  if (!search) return;
  const cards = [...document.querySelectorAll('.article-card')];
  function update() {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    cards.forEach(card => {
      const match = card.dataset.search.toLocaleLowerCase().includes(query);
      card.hidden = !match;
      if (match) visible++;
    });
    document.querySelector('#empty-results').hidden = visible > 0;
  }
  search.addEventListener('input', update);
})();
