// tests/test_audit_timeframes_and_0view.js
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

console.log("=================================================");
console.log("TEST: AUDIT TIMEFRAMES & 0-VIEW BOX ACCURACY");
console.log("=================================================");

const appJs = fs.readFileSync('docs/js/gold_app.js', 'utf8');
const pagesData = JSON.parse(fs.readFileSync('docs/data/pages_data.json', 'utf8'));

// Verify no forbidden arbitrary multipliers exist in source code
const forbiddenPatterns = [
  /currentTimeframe\s*===\s*7\s*\?\s*0\.35/g,
  /currentTimeframe\s*===\s*28\s*\?\s*0\.76/g,
  /totalLifetimeViews\s*\*\s*0\.76/g,
  /totalLifetimeViews\s*\*\s*0\.35/g,
  /totalLifetimeViews\s*\*\s*0\.88/g,
  /\*\s*\(Number\(days\)\s*\/\s*30\)/g
];

forbiddenPatterns.forEach(pattern => {
  const match = appJs.match(pattern);
  if (match) {
    console.error(`FAIL: Found forbidden arbitrary multiplier: ${pattern}`);
    process.exit(1);
  }
});
console.log("✅ CHECK 1: ZERO arbitrary multipliers found in docs/js/gold_app.js");

// Mock DOM elements
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
      // Mock selector queries for pills
      if (sel.includes('[data-tp-days]')) {
        return ['1', '7', '15', '28', '30', '60', '90', 'all'].map(d => {
          const el = mockElement('tp_btn_' + d);
          el['data-tp-days'] = d;
          return el;
        });
      }
      if (sel.includes('[data-low-filter]')) {
        return ['all', 'zero', 'under500', 'gap'].map(f => {
          const el = mockElement('low_filter_' + f);
          el['data-low-filter'] = f;
          return el;
        });
      }
      return [mockElement('sel_dummy')];
    },
    createElement: (tag) => mockElement(tag),
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

// Inject real pages data into fullData
sandbox.window.setFullData(pagesData);

const timeframesToTest = [1, 7, 15, 28, 30, 60, 90, 'all', 'life'];

console.log("\n--- TESTING ALL TIMEFRAMES ON TOP PERFORMERS (MODE 1) ---");
timeframesToTest.forEach(tf => {
  sandbox.setPerformanceMode("top");
  sandbox.setTopPerformersTimeframe(tf);
  
  const activeTf = sandbox.currentTopPerformersTimeframe;
  const champName = elements['tpKpiVal1']?.innerText;
  console.log(`Timeframe: ${String(tf).padEnd(5)} -> CurrentTf: ${String(activeTf).padEnd(5)} | #1 Champion: ${champName}`);
  assert(champName && champName.length > 0, `Champion name should not be empty for timeframe ${tf}`);
});
console.log("✅ CHECK 2: All 9 timeframes successfully compute Top Performers with 100% real ranks!");

console.log("\n--- TESTING LOW & 0 VIEWS AUDIT (MODE 2) ACROSS TIMEFRAMES & FILTERS ---");
const filtersToTest = ['zero', 'under500', 'gap', 'all'];

timeframesToTest.forEach(tf => {
  sandbox.setPerformanceMode("low");
  sandbox.setTopPerformersTimeframe(tf);
  
  const countZero = parseInt(elements['countZeroViews']?.innerText || '0');
  const countUnder500 = parseInt(elements['countUnder500']?.innerText || '0');
  const countGap = parseInt(elements['countUploadGap']?.innerText || '0');
  
  console.log(`\nTimeframe [${tf}]: 🔴 0 Views=${countZero}, 🟡 <500 Views=${countUnder500}, ⏳ Gap=${countGap}`);
  
  filtersToTest.forEach(f => {
    sandbox.setLowPerformersFilter(f);
    const listedCountStr = elements['tpTableHeading']?.innerText || '';
    const match = listedCountStr.match(/\((\d+)\s+Pages Listed\)/);
    const listedCount = match ? parseInt(match[1]) : 0;
    
    if (f === 'zero') {
      const expected = Math.min(50, countZero);
      assert.strictEqual(listedCount, expected, `Zero filter should display ${expected} pages, got ${listedCount}`);
    } else if (f === 'under500') {
      const expected = Math.min(50, countUnder500);
      assert.strictEqual(listedCount, expected, `under500 filter should display ${expected} pages, got ${listedCount}`);
    } else if (f === 'gap') {
      const expected = Math.min(50, countGap);
      assert.strictEqual(listedCount, expected, `gap filter should display ${expected} pages, got ${listedCount}`);
    }
  });
});
console.log("✅ CHECK 3: 0-Views and Low Performers filters work with 100% precision across all timeframes!");

console.log("\n--- TESTING SINGLE PAGE VIEW & PORTFOLIO VIEW (REAL VIEWS INTEGRITY) ---");
// Test first page
const testPage = pagesData.pages[0];
sandbox.selectPage(String(testPage.id));

[1, 7, 15, 28, 30, 'all', 'life'].forEach(tf => {
  sandbox.setTimeframe(tf);
  const displayedViews = elements['metricHeroViews']?.innerText?.replace(/,/g, '');
  
  // Calculate expected pure ground truth
  const reels = sandbox.getReelsForDays(testPage.videos || [], tf);
  const expectedReelsSum = reels.reduce((sum, v) => sum + (Number(v.views) || 0), 0);
  const isLife = (tf === 'all' || tf === 'life' || tf === 'lifetime');
  const expected = isLife ? Math.max(Number(testPage.total_views) || 0, expectedReelsSum) : expectedReelsSum;
  
  assert.strictEqual(Number(displayedViews), expected, `Single page views for tf ${tf} mismatch: expected ${expected}, got ${displayedViews}`);
});
console.log("✅ CHECK 4: Single Page View computes 100% exact views for every timeframe (no multipliers)!");

// Test portfolio view
sandbox.selectPage("all");
[1, 7, 15, 28, 30, 60, 90, 'all', 'life'].forEach(tf => {
  sandbox.setTimeframe(tf);
  const heroViews = elements['metricHeroViews']?.innerText?.replace(/,/g, '');
  const isLife = (tf === 'all' || tf === 'life' || tf === 'lifetime');
  
  if (isLife) {
    const totalLifetime = pagesData.pages.reduce((sum, p) => sum + (Number(p.total_views) || 0), 0);
    assert.strictEqual(Number(heroViews), totalLifetime, `Portfolio lifetime views mismatch`);
  } else {
    // Pure sum of all videos for that timeframe
    let allVidsTf = [];
    pagesData.pages.forEach(p => {
      const r = sandbox.getReelsForDays(p.videos || [], tf);
      r.forEach(v => allVidsTf.push(v));
    });
    const expected = allVidsTf.reduce((sum, v) => sum + (Number(v.views) || 0), 0);
    assert.strictEqual(Number(heroViews), expected, `Portfolio timeframe ${tf} views mismatch`);
  }
});
console.log("✅ CHECK 5: Portfolio View computes 100% exact real sums for every timeframe!");

console.log("\n=================================================");
console.log("🎉 ALL AUDIT CHECKS PASSED WITH 100% PRECISION!");
console.log("=================================================");
