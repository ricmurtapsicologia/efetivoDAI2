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

  const alreadyRegistered = personnel.some((person) =>
    String(person?.name || '').trim().toLocaleLowerCase('pt-BR') === silvana.name.toLocaleLowerCase('pt-BR')
  );

  if (!alreadyRegistered) personnel.splice(1, 0, silvana);

  window.DAI2_BIRTHDAYS = Object.assign(window.DAI2_BIRTHDAYS || {}, {
    'Silvana Tiengo': '23/03'
  });
})();
