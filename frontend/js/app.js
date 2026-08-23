/**
 * CampusAI — Application Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const chatContainer = document.getElementById('chat-container');
  const chatWelcome = document.getElementById('chat-welcome');
  
  const radarList = document.getElementById('radar-list');
  const oppCardsList = document.getElementById('opp-cards-list');
  
  const promptPills = document.querySelectorAll('.pill-prompt');
  const interestChips = document.querySelectorAll('.chip-interest');
  
  // Modal Elements
  const ingestModal = document.getElementById('ingest-modal');
  const btnIngestModal = document.getElementById('btn-ingest-modal');
  const modalCloseBtn = document.getElementById('modal-close-btn');
  const modalCancelBtn = document.getElementById('modal-cancel-btn');
  const modalSubmitBtn = document.getElementById('modal-submit-btn');
  const tabBtns = document.querySelectorAll('.tab-btn');

  // Load initial data
  loadSidebarData();

  // Handle Form Submission
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    chatInput.value = '';
    await submitQuery(query);
  });

  // Handle Preset Prompt Pills
  promptPills.forEach(pill => {
    pill.addEventListener('click', async () => {
      const query = pill.dataset.query;
      await submitQuery(query);
    });
  });

  // Handle Interest Chips
  interestChips.forEach(chip => {
    chip.addEventListener('click', async () => {
      // Toggle active class
      interestChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');

      const interest = chip.dataset.interest;
      const queryText = `I'm interested in ${interest}. What opportunities can I join?`;
      await submitQuery(queryText);
    });
  });

  // Core Submit Handler
  async function submitQuery(queryText) {
    if (chatWelcome) chatWelcome.style.display = 'none';

    // 1. Append User Message
    const userMsgEl = Components.renderUserMessage(queryText);
    chatContainer.appendChild(userMsgEl);
    scrollToBottom();

    // 2. Append Loading Placeholder
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message-bubble message-assistant';
    loadingDiv.innerHTML = `<div class="message-content">⏳ Searching grounded college data...</div>`;
    chatContainer.appendChild(loadingDiv);
    scrollToBottom();

    // 3. Call Backend API
    const responseData = await API.sendQuery(queryText);

    // 4. Replace Loading Placeholder with Assistant Response
    chatContainer.removeChild(loadingDiv);
    const assistantMsgEl = Components.renderAssistantMessage(responseData);
    chatContainer.appendChild(assistantMsgEl);
    scrollToBottom();
  }

  // Load Sidebar Radar & Opportunity Cards
  async function loadSidebarData() {
    const opps = await API.fetchOpportunities();
    
    if (radarList) {
      radarList.innerHTML = '';
      if (opps.length === 0) {
        radarList.innerHTML = '<div class="radar-loading">No opportunities loaded.</div>';
      } else {
        opps.forEach(opp => {
          const item = Components.renderRadarItem(opp);
          item.addEventListener('click', () => {
            submitQuery(`Tell me all details about ${opp.name}`);
          });
          radarList.appendChild(item);
        });
      }
    }

    if (oppCardsList) {
      oppCardsList.innerHTML = '';
      opps.forEach(opp => {
        const card = Components.renderOpportunityCard(opp);
        card.addEventListener('click', () => {
          submitQuery(`Summarize ${opp.name}`);
        });
        oppCardsList.appendChild(card);
      });
    }
  }

  function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  // Ingestion Modal Management
  btnIngestModal.addEventListener('click', () => ingestModal.classList.add('open'));
  modalCloseBtn.addEventListener('click', () => ingestModal.classList.remove('open'));
  modalCancelBtn.addEventListener('click', () => ingestModal.classList.remove('open'));

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
      
      btn.classList.add('active');
      const tabId = btn.dataset.tab;
      document.getElementById(tabId).classList.add('active');
    });
  });

  modalSubmitBtn.addEventListener('click', async () => {
    const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
    const statusMsg = document.getElementById('ingest-status-msg');
    statusMsg.innerText = 'Processing ingestion...';

    let payload = {};
    if (activeTab === 'tab-ocr') {
      const rawText = document.getElementById('notice-raw-text').value.trim();
      if (!rawText) {
        statusMsg.innerText = 'Please paste notice content first.';
        return;
      }
      payload = { text: rawText };
    } else {
      const jsonStr = document.getElementById('notice-json-text').value.trim();
      try {
        payload = { record: JSON.parse(jsonStr) };
      } catch (err) {
        statusMsg.innerText = 'Invalid JSON syntax.';
        return;
      }
    }

    const res = await API.ingestNotice(payload);
    if (res.success) {
      statusMsg.style.color = '#34d399';
      statusMsg.innerText = res.message || 'Ingestion successful!';
      setTimeout(() => {
        ingestModal.classList.remove('open');
        statusMsg.innerText = '';
        loadSidebarData();
      }, 1200);
    } else {
      statusMsg.style.color = '#f87171';
      statusMsg.innerText = res.message || 'Ingestion failed.';
    }
  });

  // Refresh Sidebar Button
  const btnRefreshOpps = document.getElementById('btn-refresh-opps');
  if (btnRefreshOpps) {
    btnRefreshOpps.addEventListener('click', loadSidebarData);
  }
});
