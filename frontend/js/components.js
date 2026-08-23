/**
 * CampusAI — Component Renderer
 */

const Components = {
  
  parseMarkdown(text) {
    if (!text) return '';
    
    // Basic Markdown Parser (headers, tables, bold, lists)
    let html = text
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code>$1</code>');

    // Parse Markdown tables if present
    if (html.includes('|')) {
      const lines = html.split('\n');
      let inTable = false;
      let tableHtml = '<table><thead>';
      const parsedLines = [];

      for (let line of lines) {
        if (line.trim().startsWith('|')) {
          if (line.includes('---')) {
            tableHtml = tableHtml.replace('<thead>', '').replace('</thead>', '') + '<tbody>';
            continue;
          }
          const cells = line.split('|').filter(c => c.trim() !== '' || line.indexOf(c) === 0 || line.lastIndexOf(c) === line.length - 1);
          const cellTag = !inTable ? 'th' : 'td';
          const rowHtml = '<tr>' + cells.slice(1, -1).map(c => `<${cellTag}>${c.trim()}</${cellTag}>`).join('') + '</tr>';
          
          if (!inTable) {
            tableHtml += rowHtml + '</thead>';
            inTable = true;
          } else {
            tableHtml += rowHtml;
          }
        } else {
          if (inTable) {
            tableHtml += 'tbody></table>';
            parsedLines.push(tableHtml);
            inTable = false;
            tableHtml = '<table><thead>';
          }
          parsedLines.push(line);
        }
      }
      if (inTable) {
        tableHtml += '</tbody></table>';
        parsedLines.push(tableHtml);
      }
      html = parsedLines.join('<br>');
    } else {
      html = html.replace(/\n/g, '<br>');
    }

    return html;
  },

  renderUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'message-bubble message-user';
    div.innerHTML = `
      <div class="message-content">${this.escapeHtml(text)}</div>
      <div class="message-meta">
        <span>You</span> • <span>${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
      </div>
    `;
    return div;
  },

  renderAssistantMessage(responseObj) {
    const div = document.createElement('div');
    div.className = 'message-bubble message-assistant';

    const parsedBody = this.parseMarkdown(responseObj.answer);
    
    let sourcesBadge = '';
    if (responseObj.sources && responseObj.sources.length > 0) {
      const srcList = responseObj.sources.join(', ');
      sourcesBadge = `<span class="source-tag" title="Verified source records">📌 Grounded in: ${srcList}</span>`;
    }

    let isRefusalBadge = '';
    if (responseObj.type === 'refusal' || (responseObj.answer && responseObj.answer.includes("don't have enough information"))) {
      isRefusalBadge = `<span class="refusal-badge">🛡️ Hallucination Guardrail Refusal</span>`;
    }

    div.innerHTML = `
      <div class="message-content">${parsedBody}</div>
      <div class="message-meta">
        <span>CampusAI</span> • 
        ${sourcesBadge}
        ${isRefusalBadge}
      </div>
    `;
    return div;
  },

  renderRadarItem(opp) {
    const div = document.createElement('div');
    div.className = 'radar-item';
    div.dataset.id = opp.id;

    const radar = opp.radar || {};
    const badgeClass = radar.color || 'gray';

    div.innerHTML = `
      <span class="radar-name">${opp.name}</span>
      <span class="radar-tag ${badgeClass}">${radar.badge || '⚪ Open'}</span>
    `;
    return div;
  },

  renderOpportunityCard(opp) {
    const div = document.createElement('div');
    div.className = 'opp-card';
    div.dataset.id = opp.id;

    const prize = opp.prize_pool ? `💰 ${opp.prize_pool}` : '⭐ Recruitment';
    const dateDisp = opp.deadline_display || opp.date_display || 'Open';

    div.innerHTML = `
      <div class="opp-card-title">
        <span>${opp.name}</span>
        <span class="opp-card-prize">${prize}</span>
      </div>
      <div class="opp-card-meta">
        📍 ${opp.venue || 'SRM KTR'} • 📅 ${dateDisp}
      </div>
    `;
    return div;
  },

  escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
};
