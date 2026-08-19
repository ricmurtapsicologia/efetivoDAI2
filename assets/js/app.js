(() => {
  'use strict';

  const personnel = Array.isArray(window.DAI2_PERSONNEL) ? window.DAI2_PERSONNEL : [];
  const birthdays = window.DAI2_BIRTHDAYS || {};
  const ddqod = window.DAI2_DDQOD || {};
  const normasDB = window.DAI2_LEGAL || {};

  Object.assign(birthdays, {
    'Eva Efigênia da Cruz': '11/04',
    'Cosme Sebastião Costa': '13/06',
    'Rubens Afonso do Carmo Gonçalves': '16/07',
    'Leonardo da Silva Machado': '02/04',
    'Filipe César Gonzaga Evangelista': '13/10',
    'Wilsa Maíra do Nascimento': '20/01',
    'Diego Natalino dos Santos': '25/12',
    'Denilson Andrade': '03/09',
    'Warleysson Flávio Cláudio Melo': '29/08',
    'Matheus Thomaz da Silva': '02/01'
  });

  let currentOnboardingStep = 1;
  const totalOnboardingSteps = 4;
  let pageInitialized = false;

  document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
      document.getElementById('splash').classList.add('hidden');
      document.getElementById('onboarding').classList.remove('hidden');
      currentOnboardingStep = 1;
      showOnboardingStep(currentOnboardingStep);
    }, 2000);
  });

  const showOnboardingStep = (step) => {
    document.querySelectorAll('.onboarding-step').forEach((stepEl) => stepEl.classList.add('hidden'));
    const currentStepEl = document.querySelector(`.onboarding-step[data-step="${step}"]`);
    if (currentStepEl) currentStepEl.classList.remove('hidden');
  };

  const finishOnboarding = () => {
    document.getElementById('onboarding').classList.add('hidden');
    document.getElementById('mainContent').classList.remove('hidden');
    if (!pageInitialized) {
      pageInitialized = true;
      initPageLogic();
    }
  };

  document.addEventListener('click', (e) => {
    if (e.target.classList.contains('btn-continue')) {
      currentOnboardingStep += 1;
      if (currentOnboardingStep <= totalOnboardingSteps) showOnboardingStep(currentOnboardingStep);
      else finishOnboarding();
    }
    if (e.target.classList.contains('btn-skip')) finishOnboarding();
  });

  const normalizeText = (value) => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();

  const normalizePhoneForWA = (raw) => {
    const candidates = String(raw || '').split(/[\/|]/).map((part) => part.replace(/\D/g, '')).filter(Boolean);
    const mobile = candidates.find((digits) => {
      const hasCountryCode = digits.startsWith('55');
      const local = hasCountryCode ? digits.slice(2) : digits;
      return (local.length === 11 && local[2] === '9') || (hasCountryCode && local.length === 10);
    });
    if (!mobile) return null;
    return mobile.startsWith('55') ? mobile : `55${mobile}`;
  };

  const buildWaLink = (rawPhone, customMessage = '') => {
    const wa = normalizePhoneForWA(rawPhone);
    return wa ? `https://wa.me/${wa}?text=${encodeURIComponent(customMessage)}` : null;
  };

  const renderWaButtonHTML = (rawPhone, buttonText, customMessage) => {
    const link = buildWaLink(rawPhone, customMessage);
    if (!link) return `<a class="whatsapp-btn disabled" title="Número incompleto ou inválido"><span class="whatsapp-icon" aria-hidden="true"></span> WhatsApp indisponível</a>`;
    return `<a class="whatsapp-btn" href="${link}" target="_blank" rel="noopener noreferrer"><span class="whatsapp-icon" aria-hidden="true"></span> ${buttonText}</a>`;
  };

  const classifyRank = (rank) => {
    const value = normalizeText(rank);
    if (value.includes('ten cel') || value.includes('ten-cel') || value === 'cel') return 'Ten-Cel';
    if (value.startsWith('maj')) return 'Maj';
    if (value.startsWith('cap')) return 'Cap';
    if (value.includes('sub ten') || value.includes('subten') || value.includes('sgt')) return 'Sgt/SubTen';
    if (value.includes('ten')) return 'Ten';
    if (value.startsWith('cb') || value.startsWith('sd')) return 'Sd/Cb';
    return null;
  };

  const displayMilitary = (person) => `${person.rank} ${person.name}`;
  const renderNumberHTML = (person) => person.number ? `<p><strong>Nr BM:</strong> ${person.number}</p>` : '';

  const initPageLogic = () => {
    const rankOrder = ['Sd/Cb', 'Sgt/SubTen', 'Ten', 'Cap', 'Maj', 'Ten-Cel'];
    const chartMap = {
      AFAS:'chart-afas', ALMG:'chart-almg', CEDEC:'chart-cedec', 'COORDENAÇÃO DAI/2':'chart-coordenacao-dai2',
      CTPM:'chart-ctpm', 'Fundação SALVAR':'chart-salvar', GMG:'chart-gmg', Intendência:'chart-intendencia',
      MPMG:'chart-mpmg', OGE:'chart-oge', 'Secretaria Parlamentar':'chart-secretaria-parlamentar', SEE:'chart-see',
      SEJUSP:'chart-sejusp', SEMAD:'chart-semad', SENASP:'chart-senasp', SES:'chart-ses', TJMG:'chart-tjmg', TJMMG:'chart-tjmmg'
    };

    const orgaos = Object.keys(chartMap);
    const data = Object.fromEntries(orgaos.map((orgao) => [orgao, []]));
    personnel.forEach((person) => { if (data[person.org]) data[person.org].push(person); });

    const rankWeight = {'Ten-Cel':6,Maj:5,Cap:4,Ten:3,'Sgt/SubTen':2,'Sd/Cb':1};
    Object.values(data).forEach((list) => list.sort((a,b) => {
      const ra = rankWeight[classifyRank(a.rank)] || 0;
      const rb = rankWeight[classifyRank(b.rank)] || 0;
      return rb - ra || a.name.localeCompare(b.name,'pt-BR');
    }));

    const getEmptyRankMap = () => rankOrder.reduce((acc,rank) => { acc[rank] = {previsto:0,existente:0}; return acc; },{});
    const distribuicao = {};
    orgaos.forEach((orgao) => {
      distribuicao[orgao] = getEmptyRankMap();
      rankOrder.forEach((rank) => { distribuicao[orgao][rank].previsto = ddqod[orgao]?.[rank] || 0; });
      data[orgao].forEach((person) => {
        const rank = classifyRank(person.rank);
        if (rank) distribuicao[orgao][rank].existente += 1;
      });
    });

    const orgTotals = {};
    orgaos.forEach((orgao) => {
      const previsto = rankOrder.reduce((sum,rank) => sum + distribuicao[orgao][rank].previsto,0);
      const existente = data[orgao].length;
      orgTotals[orgao] = {previsto, existente, claro:Math.max(previsto-existente,0)};
    });

    const totalPrevisto = orgaos.reduce((sum,orgao) => sum + orgTotals[orgao].previsto,0);
    const totalExistente = orgaos.reduce((sum,orgao) => sum + orgTotals[orgao].existente,0);
    const totalClaro = orgaos.reduce((sum,orgao) => sum + orgTotals[orgao].claro,0);

    const generalData = document.querySelector('.general-data');
    if (generalData) generalData.innerHTML = `<p>Total Previsto: ${totalPrevisto}</p><p>Total Existente: ${totalExistente}</p><p>Total Claro: ${totalClaro}</p>`;

    document.querySelectorAll('.block').forEach((block) => {
      const orgao = block.getAttribute('data-orgao');
      const totals = orgTotals[orgao] || {previsto:0,existente:0,claro:0};
      const numbers = block.querySelector('.numbers');
      if (numbers) numbers.innerHTML = `Previsto: ${totals.previsto} <br /> Existente: ${totals.existente} <br /> Claro: ${totals.claro}`;
    });

    const rankLabel = {'Ten-Cel':'Ten-Cel',Maj:'Maj',Cap:'Cap',Ten:'Ten','Sgt/SubTen':'SubTen/Sgt','Sd/Cb':'Cb/Sd'};
    const formatClaroLabel = (rank,quantidade) => `${String(quantidade).padStart(2,'0')} ${rank}`;
    const getClaroBreakdown = (orgao) => rankOrder.map((rank) => {
      const claro = distribuicao[orgao][rank].previsto - distribuicao[orgao][rank].existente;
      return claro > 0 ? {rank,claro} : null;
    }).filter(Boolean);

    const ddqodList = document.querySelector('#militaryList ul');
    if (ddqodList) ddqodList.innerHTML = orgaos.slice().sort((a,b) => a.localeCompare(b,'pt-BR')).map((orgao) => {
      const parts = rankOrder.slice().reverse().map((rank) => distribuicao[orgao][rank].previsto > 0 ? `${distribuicao[orgao][rank].previsto} ${rankLabel[rank]}` : null).filter(Boolean);
      return `<li><strong>${orgao}:</strong> ${parts.join(', ')} <strong>Total: ${orgTotals[orgao].previsto}</strong></li>`;
    }).join('');

    const createChart = (canvasId,previsto,existente,claro) => {
      const canvas = document.getElementById(canvasId);
      if (!canvas || typeof Chart === 'undefined') return;
      new Chart(canvas.getContext('2d'), {type:'doughnut',data:{labels:['Previsto','Existente','Claro'],datasets:[{data:[previsto,existente,Math.max(claro,0)],backgroundColor:['#ffeb3b','#4caf50','#f44336'],borderWidth:1}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});
    };
    Object.entries(chartMap).forEach(([orgao,canvasId]) => { const t = orgTotals[orgao]; createChart(canvasId,t.previsto,t.existente,t.claro); });

    const modal = document.getElementById('modal');
    const militaresList = document.getElementById('militares-list');
    const modalClose = document.getElementById('modalClose');

    const showModal = (orgao) => {
      const militares = data[orgao] || [];
      const claroBreakdown = getClaroBreakdown(orgao);
      const claroHtml = claroBreakdown.length ? `<div class="modal-clear-summary"><p><strong>Discriminação de claro por posto/graduação:</strong> Há claro de ${claroBreakdown.map((item) => formatClaroLabel(item.rank,item.claro)).join(', ')}.</p></div>` : `<div class="modal-clear-summary"><p><strong>Discriminação de claro por posto/graduação:</strong> Não há claro neste órgão.</p></div>`;
      document.getElementById('modalTitle').textContent = `Relação de Militares - ${orgao}`;
      militaresList.innerHTML = militares.length ? militares.map((person) => {
        const nome = displayMilitary(person);
        return `<div class="modal-military-item"><p><strong>Nome:</strong> ${nome}</p>${renderNumberHTML(person)}<p><strong>Telefone:</strong> ${person.phone || 'Não informado'}</p>${renderWaButtonHTML(person.phone,'Enviar WhatsApp',`Olá, ${nome}. Aqui é da DAI/2.`)}</div>`;
      }).join('<hr class="modal-divider">') + claroHtml : '<p style="color: red;">Nenhum militar registrado neste órgão.</p>' + claroHtml;
      modal.style.display = 'flex';
    };

    modalClose.addEventListener('click',() => modal.style.display='none');
    window.addEventListener('click',(event) => { if (event.target === modal) modal.style.display='none'; });
    document.querySelectorAll('.block').forEach((block) => block.addEventListener('click',() => showModal(block.getAttribute('data-orgao'))));

    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const searchResult = document.getElementById('searchResult');

    const searchMilitary = () => {
      const query = normalizeText(searchInput.value.trim());
      let found = false;
      searchResult.innerHTML = '';
      if (!query) return;
      orgaos.forEach((orgao) => data[orgao].forEach((person) => {
        const searchable = normalizeText(`${person.rank} ${person.name} ${person.number || ''} ${orgao} ${person.subunit || ''} ${person.phone || ''} ${classifyRank(person.rank) || ''}`);
        if (!searchable.includes(query)) return;
        found = true;
        const nome = displayMilitary(person);
        searchResult.innerHTML += `<div style="margin-bottom:16px; text-align:left;"><p><strong>Nome:</strong> ${nome}</p>${renderNumberHTML(person)}<p><strong>Telefone:</strong> ${person.phone || 'Não informado'}</p><p><strong>Órgão Externo:</strong> ${orgao}</p>${renderWaButtonHTML(person.phone,'Enviar WhatsApp',`Olá, ${nome}. Aqui é da DAI/2.`)}</div><hr style="border: 1px solid #ddd;">`;
      }));
      if (!found) searchResult.innerHTML = '<p style="color: red;">Nenhum militar encontrado.</p>';
    };
    searchButton.addEventListener('click',searchMilitary);
    searchInput.addEventListener('keydown',(e) => { if (e.key === 'Enter') searchMilitary(); });

    const rankSelect = document.getElementById('rankSelect');
    const rankButton = document.getElementById('rankButton');
    const claroResult = document.getElementById('claroResult');
    const searchClaro = () => {
      const selectedRank = rankSelect.value;
      if (!selectedRank) { claroResult.innerHTML = '<p style="color: red;">Selecione um posto/graduação.</p>'; return; }
      const resultados = orgaos.map((orgao) => {
        const previsto = distribuicao[orgao][selectedRank].previsto;
        const existente = distribuicao[orgao][selectedRank].existente;
        return {orgao,previsto,existente,claro:previsto-existente};
      }).filter((item) => item.claro > 0);
      if (!resultados.length) { claroResult.innerHTML = '<p style="color: red;">Não há claro aberto para este posto/graduação.</p>'; return; }
      claroResult.innerHTML = resultados.sort((a,b) => b.claro-a.claro || a.orgao.localeCompare(b.orgao,'pt-BR')).map((item) => `<p><strong>${item.orgao}</strong>: Previsto = ${item.previsto}, Existente = ${item.existente}, <span style="color: red; font-weight: 700;">Claro = ${item.claro}</span></p>`).join('');
    };
    rankButton.addEventListener('click',searchClaro);

    const showListBtn = document.getElementById('showListBtn');
    const militaryList = document.getElementById('militaryList');
    showListBtn.addEventListener('click',() => militaryList.style.display = !militaryList.style.display || militaryList.style.display === 'none' ? 'block' : 'none');

    const localDateTime = document.getElementById('localDateTime');
    const birthdayContent = document.getElementById('birthdayContent');
    const birthdayPanel = document.getElementById('birthdayPanel');
    const birthdayToggleBtn = document.getElementById('birthdayToggleBtn');
    const birthdayMessage = (nome) => `Olá, ${nome}. Feliz aniversário. Desejo saúde, serenidade e um excelente novo ciclo.`;
    const formatLocalDateTime = () => {
      const now = new Date();
      localDateTime.textContent = `Data local: ${now.toLocaleDateString('pt-BR')} | Hora local: ${now.toLocaleTimeString('pt-BR')}`;
    };
    const renderBirthdays = () => {
      const now = new Date();
      const hoje = `${String(now.getDate()).padStart(2,'0')}/${String(now.getMonth()+1).padStart(2,'0')}`;
      const aniversariantes = personnel.filter((person) => birthdays[person.name] === hoje);
      if (!aniversariantes.length) { birthdayContent.innerHTML = '<div class="birthday-empty"><p><strong>Não há aniversariantes no dia.</strong></p></div>'; return; }
      birthdayContent.innerHTML = aniversariantes.map((person) => {
        const displayName = displayMilitary(person);
        return `<div class="birthday-card"><p><strong>Posto/Graduação e identificação:</strong> ${displayName}</p><p><strong>Nome completo:</strong> ${person.name}</p>${renderNumberHTML(person)}<p><strong>WhatsApp:</strong> ${person.phone || 'Não informado'}</p><span class="orgao-tag">${person.org}</span><div style="margin-top:10px;">${renderWaButtonHTML(person.phone,'Enviar parabéns no WhatsApp',birthdayMessage(person.name))}</div></div>`;
      }).join('');
    };
    birthdayToggleBtn.addEventListener('click',() => birthdayPanel.style.display = !birthdayPanel.style.display || birthdayPanel.style.display === 'none' ? 'block' : 'none');
    formatLocalDateTime(); renderBirthdays(); setInterval(formatLocalDateTime,1000);

    const normasModal = document.getElementById('normasModal');
    const normasContent = document.getElementById('normasContent');
    const normasToggleBtn = document.getElementById('normasToggleBtn');
    const normasModalClose = document.getElementById('normasModalClose');
    const renderNormas = () => {
      const groupsHtml = Object.entries(normasDB).map(([titulo,grupo]) => {
        const badges = titulo.toLowerCase().includes('convênio') ? '<span class="badge-inline badge-convenio">Base institucional</span>' : '';
        return `<div class="norma-group"><h5>${titulo}${badges}</h5><p class="norma-intro">${grupo.intro}</p>${grupo.items.map((item) => `<div class="norma-item"><p><strong>Órgão:</strong> ${item.orgao}${item.base ? '<span class="badge-inline badge-convenio">Base específica</span>' : ''}${item.adicional === 'Sim' ? '<span class="badge-inline badge-adicional">Adicional</span>' : ''}</p><p><strong>Fundamento:</strong> ${item.fundamento}</p>${item.base ? `<p><strong>Base complementar:</strong> ${item.base}</p>` : ''}<p><strong>Leitura objetiva:</strong> ${item.adicional === 'Sim' ? 'Há amparo para disponibilização e existe base informada para pagamento de adicional.' : 'Há amparo para disponibilização, sem indicação de pagamento de adicional nesta classificação.'}</p></div>`).join('')}</div>`;
      }).join('');
      normasContent.innerHTML = `<p class="norma-intro">Este quadro reúne, em linguagem direta, os principais fundamentos associados à disponibilização de militares nos órgãos externos listados. A finalidade aqui é facilitar a consulta rápida, sem substituir a leitura integral dos atos normativos, convênios, leis e bases correlatas aplicáveis a cada caso.</p><div class="normas-grid">${groupsHtml}</div>`;
    };
    renderNormas();
    normasToggleBtn.addEventListener('click',() => normasModal.style.display='flex');
    normasModalClose.addEventListener('click',() => normasModal.style.display='none');
    window.addEventListener('click',(event) => { if (event.target === normasModal) normasModal.style.display='none'; });
  };
})();
