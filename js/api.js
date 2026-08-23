/**
 * CampusAI — API Service Client
 */
const API = {
  baseUrl: '',

  async sendQuery(queryText) {
    try {
      const response = await fetch(`${this.baseUrl}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryText })
      });
      return await response.json();
    } catch (err) {
      console.error('API Error sendQuery:', err);
      return {
        answer: "⚠️ Unable to connect to local CampusAI server. Please verify backend is running.",
        sources: [],
        type: "error"
      };
    }
  },

  async fetchOpportunities() {
    try {
      const response = await fetch(`${this.baseUrl}/api/opportunities`);
      const data = await response.json();
      return data.opportunities || [];
    } catch (err) {
      console.error('API Error fetchOpportunities:', err);
      return [];
    }
  },

  async fetchRadar() {
    try {
      const response = await fetch(`${this.baseUrl}/api/radar`);
      return await response.json();
    } catch (err) {
      console.error('API Error fetchRadar:', err);
      return {};
    }
  },

  async recommendInterests(interestsArray) {
    try {
      const response = await fetch(`${this.baseUrl}/api/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interests: interestsArray })
      });
      return await response.json();
    } catch (err) {
      console.error('API Error recommendInterests:', err);
      return null;
    }
  },

  async ingestNotice(payload) {
    try {
      const response = await fetch(`${this.baseUrl}/api/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      return await response.json();
    } catch (err) {
      console.error('API Error ingestNotice:', err);
      return { success: false, message: 'Server communication failed.' };
    }
  }
};
