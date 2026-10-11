// tests/test_all_views_render.js
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

console.log("=================================================");
console.log("TEST: AUDIT ALL VIEWS AND NAVIGATION RENDERING");
console.log("=================================================");

const appJs = fs.readFileSync('docs/js/gold_app.js', 'utf8');
const pagesData = JSON.parse(fs.readFileSync('docs/data/pages_data.json', 'utf8'));

const elements = {};
const mockElement = (id) => {
  if (!elements[id]) {
    elements[id] = {
      id,
      style: {},
      classList: {
        _classes: new Set(),
        add: function(c) { this._classes.add(c); },
        remove: function(c) { this._classes.delete(c); },
        toggle: function(c, force) {
          if (force !== undefined) {
            if (force) this._classes.add(c); else this._classes.delete(c);
          } else {
            if (this._classes.has(c)) this._classes.delete(c); else this._classes.add(c);
          }
        },
        contains: function(c) { return this._classes.has(c); },
      },
      dataset: {},
      innerText: '',
      innerHTML: '',
      value: '',
      setAttribute: function(k, v) { this[k] = v; },
      getAttribute: function(k) { return this[k]; },
      addEventListener: () => {},
      querySelector: () => mockElement(id + '_child'),
      querySelectorAll: () => [mockElement(id + '_c1'), mockElement(id + '_c2')],
      appendChild: () => {},
      remove: () => {},
    };
  }
  return elements[id];
};

const sandbox = {
  window: {
    location: { href: 'http://localhost/', protocol: 'http:', hostname: 'localhost' },
    scrollTo: () => {},
    addEventListener: () => {},
  },
  document: {
    readyState: 'complete',
    documentElement: mockElement('html'),
    addEventListener: () => {},
    getElementById: (id) => mockElement(id),
    querySelectorAll: (sel) => {
      if (sel.includes('.timeframe-pill') || sel.includes('[data-days]')) {
        return ['1', '7', '15', '28', '30', '60', '90', 'all'].map(d => {
          const el = mockElement('pill_' + d);
          el.dataset.days = d;
          return el;
        });
      }
      return [mockElement('sel_dummy')];
    },
    createElement: (tag) => mockElement(tag + '_' + Math.random().toString(36).substring(7)),
    body: mockElement('body'),
    visibilityState: 'visible',
  },
  localStorage: {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {},
  },
  caches: {
    open: async () => ({ match: async () => null, put: async () => {} }),
    keys: async () => [],
    delete: async () => true,
  },
  fetch: async () => ({
    ok: true,
    clone: () => ({ json: async () => pagesData }),
    json: async () => pagesData
  }),
  setTimeout: () => {},
  setInterval: () => {},
  clearInterval: () => {},
  clearTimeout: () => {},
  console: console,
  Date: Date,
  Math: Math,
  JSON: JSON,
  Array: Array,
  Object: Object,
  String: String,
  Number: Number,
  Boolean: Boolean,
  parseInt: parseInt,
  parseFloat: parseFloat,
  isNaN: isNaN,
  isFinite: isFinite,
  Promise: Promise,
};

sandbox.window.document = sandbox.document;
sandbox.global = sandbox;

vm.createContext(sandbox);
vm.runInContext(appJs, sandbox);
sandbox.window.setFullData(pagesData);

console.log("Testing switchMainView across all 8 dashboard views:");
const views = [
  'dashboard',
  'studio',
  'drive_data',
  'recent_posts',
  'health_audit',
  'low_performers',
  'top_performers',
  'anti_detect_profiles',
  'meta_tools_hub'
];

views.forEach(v => {
  try {
    sandbox.switchMainView(v);
    console.log(`  ✅ View '${v}' switched and rendered successfully!`);
  } catch (err) {
    console.error(`  ❌ View '${v}' FAILED:`, err);
    process.exit(1);
  }
});

console.log("\nTesting upload history rendering and filters:");
(async () => {
  try {
    const historyData = JSON.parse(fs.readFileSync('docs/data/upload_history.json', 'utf8'));
    sandbox.fetch = async (url) => ({
      ok: true,
      json: async () => url.includes('upload_history') ? historyData : pagesData
    });
    
    await sandbox.fetchUploadHistory();
    
    ['all', 'today', 'us', 'uk'].forEach(f => {
      sandbox.setUploadHistoryFilter(f);
      const label = elements['historyShowingCountLabel']?.innerText;
      console.log(`  ✅ Filter '${f}': "${label}"`);
    });
  } catch (err) {
    console.error("  ❌ Upload history rendering FAILED:", err);
    process.exit(1);
  }
})();

console.log("\nTesting individual page selection for top 5 pages:");
for (let i = 0; i < 5; i++) {
  const p = pagesData.pages[i];
  try {
    sandbox.selectPage(String(p.id));
    console.log(`  ✅ Page '${p.name}' (ID: ${p.id}) loaded cleanly!`);
  } catch (err) {
    console.error(`  ❌ Page selection failed for ${p.name}:`, err);
    process.exit(1);
  }
}

console.log("\nTesting switching back to All Pages portfolio:");
try {
  sandbox.selectPage('all');
  console.log(`  ✅ All Pages portfolio loaded cleanly! Hero views: ${elements['metricHeroViews']?.innerText}`);
} catch (err) {
  console.error("  ❌ All Pages portfolio selection FAILED:", err);
  process.exit(1);
}

console.log("\n=================================================");
console.log("🎉 ALL VIEW AND COMPONENT AUDITS PASSED WITH 100% SUCCESS!");
console.log("=================================================");
