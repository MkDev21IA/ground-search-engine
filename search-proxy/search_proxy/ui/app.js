// Ground Search Engine — Frontend Application Logic

(function () {
  'use strict';

  // --- State & DOM References ---
  const state = {
    byok: {
      model: localStorage.getItem('ground_llm_model') || '',
      baseUrl: localStorage.getItem('ground_llm_base_url') || '',
      apiKey: localStorage.getItem('ground_llm_api_key') || '',
    },
    defaultModel: 'meta-llama/llama-3.2-3b-instruct',
    isSearching: false,
    timerInterval: null,
    startTime: null,
    accumulatedAnswer: '',
    sources: [],
    citations: [],
    lastTelemetry: null,
  };

  const DOM = {
    // Health & Model
    healthBadge: document.getElementById('healthBadge'),
    healthDot: document.getElementById('healthDot'),
    healthText: document.getElementById('healthText'),
    modelBadge: document.getElementById('modelBadge'),
    modelNameText: document.getElementById('modelNameText'),

    // Search Controls
    searchForm: document.getElementById('searchForm'),
    searchInput: document.getElementById('searchInput'),
    searchSubmitBtn: document.getElementById('searchSubmitBtn'),
    langSelect: document.getElementById('langSelect'),
    maxResultsSelect: document.getElementById('maxResultsSelect'),
    sampleChips: document.querySelectorAll('.sample-chip'),

    // Pipeline Section
    pipelineSection: document.getElementById('pipelineSection'),
    pipelineTimer: document.getElementById('pipelineTimer'),
    stageSearch: document.getElementById('stageSearch'),
    stageExtract: document.getElementById('stageExtract'),
    stageSynthesis: document.getElementById('stageSynthesis'),

    // Sources Section
    sourcesSection: document.getElementById('sourcesSection'),
    sourcesContainer: document.getElementById('sourcesContainer'),
    sourcesCountBadge: document.getElementById('sourcesCountBadge'),

    // Answer Section
    answerSection: document.getElementById('answerSection'),
    answerContent: document.getElementById('answerContent'),
    copyAnswerBtn: document.getElementById('copyAnswerBtn'),
    copyBtnText: document.getElementById('copyBtnText'),
    citationsFooter: document.getElementById('citationsFooter'),
    citationsPillsContainer: document.getElementById('citationsPillsContainer'),

    // Telemetry Section
    telemetrySection: document.getElementById('telemetrySection'),
    telSearchMs: document.getElementById('telSearchMs'),
    telExtractMs: document.getElementById('telExtractMs'),
    telSynthMs: document.getElementById('telSynthMs'),
    telTotalMs: document.getElementById('telTotalMs'),
    telTokens: document.getElementById('telTokens'),
    telTotalTokens: document.getElementById('telTotalTokens'),
    telCostUsd: document.getElementById('telCostUsd'),
    exportTelemetryBtn: document.getElementById('exportTelemetryBtn'),

    // Settings Modal
    openSettingsBtn: document.getElementById('openSettingsBtn'),
    closeSettingsBtn: document.getElementById('closeSettingsBtn'),
    settingsModal: document.getElementById('settingsModal'),
    settingsForm: document.getElementById('settingsForm'),
    settingModelSelect: document.getElementById('settingModelSelect'),
    settingCustomModel: document.getElementById('settingCustomModel'),
    settingBaseUrl: document.getElementById('settingBaseUrl'),
    settingApiKey: document.getElementById('settingApiKey'),
    toggleApiKeyVisBtn: document.getElementById('toggleApiKeyVisBtn'),
    resetSettingsBtn: document.getElementById('resetSettingsBtn'),
  };

  // --- Initial Setup ---
  async function init() {
    setupSettingsEvents();
    setupSearchEvents();
    setupAnswerActions();
    loadBYOKToForm();
    await fetchHealthAndModels();
  }

  // --- Fetch System Health and Available Models ---
  async function fetchHealthAndModels() {
    try {
      const [healthRes, modelsRes] = await Promise.all([
        fetch('/api/health'),
        fetch('/api/models'),
      ]);

      if (healthRes.ok) {
        const health = await healthRes.json();
        if (health.searxng_connected) {
          DOM.healthDot.className = 'w-2 h-2 rounded-full bg-emerald-400';
          DOM.healthText.textContent = 'SearXNG: Connected';
          DOM.healthText.className = 'font-mono text-[11px] text-emerald-400';
        } else {
          DOM.healthDot.className = 'w-2 h-2 rounded-full bg-amber-400';
          DOM.healthText.textContent = 'SearXNG: Degraded';
          DOM.healthText.className = 'font-mono text-[11px] text-amber-400';
        }
        if (health.default_model) {
          state.defaultModel = health.default_model;
        }
      }

      if (modelsRes.ok) {
        const modelsData = await modelsRes.json();
        populateModelSelect(modelsData.recommended_models || []);
      }
    } catch (err) {
      console.warn('Failed to load initial system status:', err);
      DOM.healthDot.className = 'w-2 h-2 rounded-full bg-rose-500';
      DOM.healthText.textContent = 'Backend Offline';
      DOM.healthText.className = 'font-mono text-[11px] text-rose-400';
    }

    updateActiveModelBadge();
  }

  function populateModelSelect(recommendedList) {
    if (!recommendedList.length) return;
    const currentVal = state.byok.model;
    const select = DOM.settingModelSelect;
    
    // Check if custom or in list
    let matched = false;
    for (let i = 0; i < select.options.length; i++) {
      if (select.options[i].value === currentVal) {
        matched = true;
        break;
      }
    }

    if (currentVal && !matched) {
      select.value = 'custom';
      DOM.settingCustomModel.classList.remove('hidden');
      DOM.settingCustomModel.value = currentVal;
    }
  }

  function updateActiveModelBadge() {
    const activeModel = state.byok.model || state.defaultModel;
    DOM.modelNameText.textContent = activeModel;
    DOM.modelNameText.title = activeModel;
  }

  // --- BYOK Settings Management ---
  function setupSettingsEvents() {
    DOM.openSettingsBtn.addEventListener('click', () => {
      loadBYOKToForm();
      DOM.settingsModal.classList.remove('hidden');
      DOM.settingsModal.classList.add('flex');
    });

    DOM.closeSettingsBtn.addEventListener('click', () => {
      DOM.settingsModal.classList.add('hidden');
      DOM.settingsModal.classList.remove('flex');
    });

    DOM.settingsModal.addEventListener('click', (e) => {
      if (e.target === DOM.settingsModal) {
        DOM.settingsModal.classList.add('hidden');
        DOM.settingsModal.classList.remove('flex');
      }
    });

    DOM.settingModelSelect.addEventListener('change', () => {
      if (DOM.settingModelSelect.value === 'custom') {
        DOM.settingCustomModel.classList.remove('hidden');
        DOM.settingCustomModel.focus();
      } else {
        DOM.settingCustomModel.classList.add('hidden');
      }
    });

    DOM.toggleApiKeyVisBtn.addEventListener('click', () => {
      const type = DOM.settingApiKey.getAttribute('type') === 'password' ? 'text' : 'password';
      DOM.settingApiKey.setAttribute('type', type);
      DOM.toggleApiKeyVisBtn.textContent = type === 'password' ? '👁️' : '🔒';
    });

    DOM.resetSettingsBtn.addEventListener('click', () => {
      localStorage.removeItem('ground_llm_model');
      localStorage.removeItem('ground_llm_base_url');
      localStorage.removeItem('ground_llm_api_key');
      state.byok = { model: '', baseUrl: '', apiKey: '' };
      loadBYOKToForm();
      updateActiveModelBadge();
      DOM.settingsModal.classList.add('hidden');
      DOM.settingsModal.classList.remove('flex');
    });

    DOM.settingsForm.addEventListener('submit', (e) => {
      e.preventDefault();
      let chosenModel = DOM.settingModelSelect.value;
      if (chosenModel === 'custom') {
        chosenModel = DOM.settingCustomModel.value.trim();
      }

      const baseUrl = DOM.settingBaseUrl.value.trim();
      const apiKey = DOM.settingApiKey.value.trim();

      state.byok.model = chosenModel;
      state.byok.baseUrl = baseUrl;
      state.byok.apiKey = apiKey;

      if (chosenModel) localStorage.setItem('ground_llm_model', chosenModel);
      else localStorage.removeItem('ground_llm_model');

      if (baseUrl) localStorage.setItem('ground_llm_base_url', baseUrl);
      else localStorage.removeItem('ground_llm_base_url');

      if (apiKey) localStorage.setItem('ground_llm_api_key', apiKey);
      else localStorage.removeItem('ground_llm_api_key');

      updateActiveModelBadge();
      DOM.settingsModal.classList.add('hidden');
      DOM.settingsModal.classList.remove('flex');
    });
  }

  function loadBYOKToForm() {
    const { model, baseUrl, apiKey } = state.byok;
    DOM.settingBaseUrl.value = baseUrl;
    DOM.settingApiKey.value = apiKey;

    if (!model) {
      DOM.settingModelSelect.value = '';
      DOM.settingCustomModel.classList.add('hidden');
      DOM.settingCustomModel.value = '';
    } else {
      let optionExists = false;
      for (let i = 0; i < DOM.settingModelSelect.options.length; i++) {
        if (DOM.settingModelSelect.options[i].value === model) {
          DOM.settingModelSelect.value = model;
          DOM.settingCustomModel.classList.add('hidden');
          optionExists = true;
          break;
        }
      }
      if (!optionExists) {
        DOM.settingModelSelect.value = 'custom';
        DOM.settingCustomModel.classList.remove('hidden');
        DOM.settingCustomModel.value = model;
      }
    }
  }

  // --- Search Form and Actions ---
  function setupSearchEvents() {
    DOM.searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const query = DOM.searchInput.value.trim();
      if (!query || state.isSearching) return;
      executeSearch(query);
    });

    DOM.sampleChips.forEach((chip) => {
      chip.addEventListener('click', () => {
        const query = chip.getAttribute('data-query');
        DOM.searchInput.value = query;
        executeSearch(query);
      });
    });
  }

  // --- Execute Streaming Search ---
  async function executeSearch(query) {
    state.isSearching = true;
    state.accumulatedAnswer = '';
    state.sources = [];
    state.citations = [];
    state.lastTelemetry = null;

    DOM.searchSubmitBtn.disabled = true;
    DOM.searchSubmitBtn.classList.add('opacity-50', 'cursor-not-allowed');

    // Reset View Containers
    DOM.pipelineSection.classList.remove('hidden');
    DOM.sourcesSection.classList.add('hidden');
    DOM.sourcesContainer.innerHTML = '';
    DOM.answerSection.classList.add('hidden');
    DOM.answerContent.innerHTML = '';
    DOM.citationsFooter.classList.add('hidden');
    DOM.citationsPillsContainer.innerHTML = '';
    DOM.telemetrySection.classList.add('hidden');

    resetStage(DOM.stageSearch, '1. Web Search', 'Querying SearXNG...');
    resetStage(DOM.stageExtract, '2. Text Extraction', 'Waiting for search results...');
    resetStage(DOM.stageSynthesis, '3. Grounded Synthesis', 'Waiting for context...');

    setStageStatus(DOM.stageSearch, 'running');

    // Start Timer
    state.startTime = performance.now();
    DOM.pipelineTimer.textContent = '0.0s';
    clearInterval(state.timerInterval);
    state.timerInterval = setInterval(() => {
      const elapsed = ((performance.now() - state.startTime) / 1000).toFixed(1);
      DOM.pipelineTimer.textContent = `${elapsed}s`;
    }, 100);

    const lang = DOM.langSelect.value;
    const maxResults = DOM.maxResultsSelect.value;
    const streamUrl = `/api/search/stream?q=${encodeURIComponent(query)}&lang=${lang}&max_results=${maxResults}`;

    const headers = {};
    if (state.byok.apiKey) headers['X-LLM-API-Key'] = state.byok.apiKey;
    if (state.byok.baseUrl) headers['X-LLM-Base-URL'] = state.byok.baseUrl;
    if (state.byok.model) headers['X-LLM-Model'] = state.byok.model;

    try {
      const response = await fetch(streamUrl, { headers });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const blocks = buffer.split('\n\n');
        buffer = blocks.pop(); // keep trailing incomplete block

        for (const block of blocks) {
          if (!block.trim()) continue;
          handleSSEBlock(block);
        }
      }

    } catch (err) {
      console.error('Search streaming error:', err);
      setStageStatus(DOM.stageSearch, 'error', `Failed: ${err.message}`);
      setStageStatus(DOM.stageExtract, 'error');
      setStageStatus(DOM.stageSynthesis, 'error');
    } finally {
      clearInterval(state.timerInterval);
      state.isSearching = false;
      DOM.searchSubmitBtn.disabled = false;
      DOM.searchSubmitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
  }

  // --- SSE Chunk Parsing ---
  function handleSSEBlock(block) {
    const lines = block.split('\n');
    let eventType = 'message';
    let dataStr = '';

    for (const line of lines) {
      if (line.startsWith('event: ')) {
        eventType = line.substring(7).trim();
      } else if (line.startsWith('data: ')) {
        dataStr = line.substring(6).trim();
      }
    }

    if (!dataStr) return;

    let payload;
    try {
      payload = JSON.parse(dataStr);
    } catch {
      payload = dataStr;
    }

    switch (eventType) {
      case 'status':
        handleStatusEvent(payload);
        break;
      case 'search_results':
        handleSearchResultsEvent(payload);
        break;
      case 'extraction_complete':
        handleExtractionCompleteEvent(payload);
        break;
      case 'token':
        handleTokenEvent(payload);
        break;
      case 'citations':
        handleCitationsEvent(payload);
        break;
      case 'telemetry':
        handleTelemetryEvent(payload);
        break;
      case 'done':
        handleDoneEvent();
        break;
      case 'error':
        handleErrorEvent(payload);
        break;
    }
  }

  // --- SSE Event Handlers ---
  function handleStatusEvent(payload) {
    const { stage, message } = payload;
    if (stage === 'search') {
      setStageStatus(DOM.stageSearch, 'running', message);
    } else if (stage === 'extract') {
      setStageStatus(DOM.stageSearch, 'done');
      setStageStatus(DOM.stageExtract, 'running', message);
    } else if (stage === 'synthesis') {
      setStageStatus(DOM.stageExtract, 'done');
      setStageStatus(DOM.stageSynthesis, 'running', message);
    }
  }

  function handleSearchResultsEvent(results) {
    if (Array.isArray(results)) {
      state.sources = results;
      DOM.sourcesCountBadge.textContent = `${results.length} sources`;
    }
  }

  function handleExtractionCompleteEvent(payload) {
    setStageStatus(DOM.stageExtract, 'done', `Extracted ${payload.successful || 0}/${payload.total || 0} pages`);
    renderSources(state.sources);
  }

  function handleTokenEvent(payload) {
    DOM.answerSection.classList.remove('hidden');
    const token = payload.text || '';
    state.accumulatedAnswer += token;
    renderMarkdownAnswer(state.accumulatedAnswer);
  }

  function handleCitationsEvent(citations) {
    if (Array.isArray(citations) && citations.length > 0) {
      state.citations = citations;
      DOM.citationsFooter.classList.remove('hidden');
      DOM.citationsPillsContainer.innerHTML = citations
        .map(
          (c, idx) => `
          <a href="${c.url}" target="_blank" class="citation-badge" data-url="${c.url}">
            <span>[${idx + 1}]</span>
            <span class="truncate max-w-[200px]">${escapeHtml(c.label)}</span>
          </a>
        `
        )
        .join('');
      attachCitationHoverEvents();
    }
  }

  function handleTelemetryEvent(telemetry) {
    state.lastTelemetry = telemetry;
    DOM.telemetrySection.classList.remove('hidden');

    const lat = telemetry.latencies || {};
    DOM.telSearchMs.textContent = `${lat.search_ms || 0} ms`;
    DOM.telExtractMs.textContent = `${lat.extract_ms || 0} ms`;
    DOM.telSynthMs.textContent = `${lat.synthesis_ms || 0} ms`;
    DOM.telTotalMs.textContent = `${((lat.total_ms || 0) / 1000).toFixed(2)} s`;

    const tok = telemetry.tokens || {};
    DOM.telTokens.textContent = `Prompt: ${tok.prompt_tokens || 0} | Output: ${tok.completion_tokens || 0}`;
    DOM.telTotalTokens.textContent = `${tok.total_tokens || 0} tok`;

    DOM.telCostUsd.textContent = `$${(telemetry.cost_usd || 0).toFixed(6)}`;
  }

  function handleDoneEvent() {
    setStageStatus(DOM.stageSynthesis, 'done', 'Synthesis complete');
    clearInterval(state.timerInterval);
    if (state.lastTelemetry && state.lastTelemetry.latencies) {
      DOM.pipelineTimer.textContent = `${((state.lastTelemetry.latencies.total_ms || 0) / 1000).toFixed(2)}s`;
    }
  }

  function handleErrorEvent(payload) {
    const errorMsg = payload.error || 'An unexpected error occurred';
    setStageStatus(DOM.stageSynthesis, 'error', errorMsg);
    clearInterval(state.timerInterval);
  }

  // --- Source Cards Rendering ---
  function renderSources(sources) {
    if (!sources || !sources.length) return;
    DOM.sourcesSection.classList.remove('hidden');

    DOM.sourcesContainer.innerHTML = sources
      .map((s, idx) => {
        const domain = s.domain || extractDomain(s.url);
        const faviconUrl = `https://www.google.com/s2/favicons?domain=${domain}&sz=32`;
        const tier = s.tier || 'Full Text';
        const isFullText = tier.toLowerCase().includes('full');

        return `
          <div class="source-card p-3 rounded-xl bg-surface-900 border border-slate-800 flex flex-col justify-between gap-2.5" data-source-url="${s.url}" data-source-idx="${idx + 1}">
            <div class="flex items-start justify-between gap-2">
              <div class="flex items-center gap-2 min-w-0">
                <img src="${faviconUrl}" alt="" class="w-4 h-4 rounded-sm flex-shrink-0" onerror="this.style.display='none'">
                <span class="text-[11px] font-mono font-medium text-slate-400 truncate">${escapeHtml(domain)}</span>
              </div>
              <span class="px-1.5 py-0.5 rounded text-[10px] font-mono font-medium ${
                isFullText
                  ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              }">
                ${isFullText ? 'Full Text' : 'Snippet'}
              </span>
            </div>

            <a href="${s.url}" target="_blank" class="text-xs font-semibold text-slate-200 hover:text-brand-400 line-clamp-2 transition leading-snug">
              ${escapeHtml(s.title || s.url)}
            </a>

            <p class="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
              ${escapeHtml(s.snippet || 'Extracted factual context...')}
            </p>

            <div class="pt-1 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-500 font-mono">
              <span>Source #${idx + 1}</span>
              <a href="${s.url}" target="_blank" class="hover:text-slate-300 flex items-center gap-1">
                <span>Open</span>
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
              </a>
            </div>
          </div>
        `;
      })
      .join('');
  }

  // --- Markdown Rendering & Citation Transformation ---
  function renderMarkdownAnswer(rawMarkdown) {
    if (!window.marked) {
      DOM.answerContent.textContent = rawMarkdown;
      return;
    }

    // Configure marked for clean, safe rendering
    const html = window.marked.parse(rawMarkdown);
    DOM.answerContent.innerHTML = html;

    // Transform all generated <a> tags into interactive citation badges
    const links = DOM.answerContent.querySelectorAll('a');
    links.forEach((a) => {
      a.setAttribute('target', '_blank');
      a.classList.add('citation-badge');
      a.setAttribute('data-url', a.href);

      // Prepend small link icon
      if (!a.querySelector('.cit-icon')) {
        const iconSpan = document.createElement('span');
        iconSpan.className = 'cit-icon';
        iconSpan.textContent = '🔗';
        a.prepend(iconSpan);
      }
    });

    attachCitationHoverEvents();
  }

  // --- Citation Hover Highlighting ---
  function attachCitationHoverEvents() {
    const badges = document.querySelectorAll('.citation-badge');
    badges.forEach((badge) => {
      badge.onmouseenter = () => {
        const url = badge.getAttribute('data-url');
        if (!url) return;
        highlightSourceCard(url, true);
      };
      badge.onmouseleave = () => {
        const url = badge.getAttribute('data-url');
        if (!url) return;
        highlightSourceCard(url, false);
      };
    });
  }

  function highlightSourceCard(url, enable) {
    const cards = DOM.sourcesContainer.querySelectorAll('.source-card');
    cards.forEach((card) => {
      const cardUrl = card.getAttribute('data-source-url');
      if (cardUrl && (cardUrl === url || url.includes(cardUrl) || cardUrl.includes(url))) {
        if (enable) {
          card.classList.add('active-highlight');
          card.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
        } else {
          card.classList.remove('active-highlight');
        }
      }
    });
  }

  // --- Copy & Export Actions ---
  function setupAnswerActions() {
    DOM.copyAnswerBtn.addEventListener('click', async () => {
      if (!state.accumulatedAnswer) return;
      try {
        await navigator.clipboard.writeText(state.accumulatedAnswer);
        DOM.copyBtnText.textContent = 'Copied!';
        DOM.copyAnswerBtn.classList.add('text-brand-400', 'border-brand-500/50');
        setTimeout(() => {
          DOM.copyBtnText.textContent = 'Copy Markdown';
          DOM.copyAnswerBtn.classList.remove('text-brand-400', 'border-brand-500/50');
        }, 2000);
      } catch (err) {
        console.error('Failed to copy text:', err);
      }
    });

    DOM.exportTelemetryBtn.addEventListener('click', () => {
      if (!state.lastTelemetry) return;
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(state.lastTelemetry, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute('href', dataStr);
      downloadAnchor.setAttribute('download', `ground-telemetry-${Date.now()}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    });
  }

  // --- Stage UI Helper Functions ---
  function resetStage(stageEl, title, initialMsg) {
    stageEl.className = 'stage-card p-3 rounded-lg bg-surface-850/50 border border-slate-800 flex items-start gap-2.5 transition';
    stageEl.querySelector('.stage-icon').innerHTML = `
      <svg class="w-4 h-4 animate-spin-slow" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke-width="3" stroke-dasharray="32" stroke-linecap="round"></circle></svg>
    `;
    stageEl.querySelector('.stage-msg').textContent = initialMsg;
  }

  function setStageStatus(stageEl, status, message) {
    stageEl.classList.remove('stage-running', 'stage-done', 'stage-error');
    if (message) {
      stageEl.querySelector('.stage-msg').textContent = message;
    }

    if (status === 'running') {
      stageEl.classList.add('stage-running');
      stageEl.querySelector('.stage-icon').innerHTML = `
        <svg class="w-4 h-4 animate-spin text-brand-400" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
      `;
    } else if (status === 'done') {
      stageEl.classList.add('stage-done');
      stageEl.querySelector('.stage-icon').innerHTML = `
        <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
      `;
    } else if (status === 'error') {
      stageEl.classList.add('stage-error');
      stageEl.querySelector('.stage-icon').innerHTML = `
        <svg class="w-4 h-4 text-rose-500" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
      `;
    }
  }

  function extractDomain(url) {
    try {
      return new URL(url).hostname.replace('www.', '');
    } catch {
      return '';
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // --- Run on DOM Ready ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
