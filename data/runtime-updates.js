(() => {
  'use strict';

  const personnel = Array.isArray(window.DAI2_PERSONNEL) ? window.DAI2_PERSONNEL : [];

  const silvana = {
    rank: '3º Sgt',
    name: 'Silvana Tiengo',
    org: 'AFAS',
    subunit: '',
    phone: '(31) 99174-3862'
  };

  const patrick = {
    rank: 'Ten Cel',
    name: 'Patrick Tavares Gomes',
    org: 'SEMAD',
    subunit: '',
    number: '128.969-3',
    phone: '(32) 98834-5605'
  };

  const addIfMissing = (person, position = personnel.length) => {
    const exists = personnel.some((item) =>
      String(item?.name || '').trim().toLocaleLowerCase('pt-BR') === person.name.toLocaleLowerCase('pt-BR')
    );
    if (!exists) personnel.splice(position, 0, person);
  };

  addIfMissing(silvana, 1);
  addIfMissing(patrick);

  window.DAI2_DDQOD = window.DAI2_DDQOD || {};
  window.DAI2_DDQOD.SEMAD = {
    'Sd/Cb': 0,
    'Sgt/SubTen': 0,
    'Ten': 0,
    'Cap': 0,
    'Maj': 0,
    'Ten-Cel': 1
  };

  window.DAI2_BIRTHDAYS = Object.assign(window.DAI2_BIRTHDAYS || {}, {
    'Silvana Tiengo': '23/03',
    'Patrick Tavares Gomes': '18/08'
  });

  const ensureSemadCard = () => {
    if (document.querySelector('.block[data-orgao="SEMAD"]')) return;
    const listToggle = document.querySelector('.list-toggle');
    if (!listToggle || !listToggle.parentElement) return;

    const row = document.createElement('section');
    row.className = 'row';
    row.innerHTML = '<div class="block" data-orgao="SEMAD"><h3>SEMAD</h3><canvas id="chart-semad"></canvas><div class="numbers">Previsto: 1 <br /> Existente: 1 <br /> Claro: 0</div></div>';
    listToggle.parentElement.insertBefore(row, listToggle);
  };

  ensureSemadCard();
})();
