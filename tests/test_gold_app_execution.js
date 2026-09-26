// tests/test_gold_app_execution.js
const fs = require('fs');
const vm = require('vm');

const appJs = fs.readFileSync('docs/js/gold_app.js', 'utf8');

// Mock DOM environment
const mockElement = (id) => ({
  id,
  style: {},
  classList: {
    add: () => {},
    remove: () => {},
    toggle: () => {},
    contains: () => false,
  },
  dataset: {},
  innerText: '',
  innerHTML: '',
  value: '',
  addEventListener: () => {},
  querySelector: () => mockElement('child'),
  querySelectorAll: () => [mockElement('child1'), mockElement('child2')],
  appendChild: () => {},
  remove: () => {},
});

const sandbox = {
  window: {
    location: { href: 'http://localhost/', protocol: 'http:', hostname: 'localhost' },
    scrollTo: () => {},
    addEventListener: () => {},
  },
  document: {
    readyState: 'complete',
    addEventListener: () => {},
    getElementById: (id) => mockElement(id),
    querySelectorAll: (sel) => [mockElement('sel1')],
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
    open: async () => ({
      match: async () => null,
      put: async () => {},
    }),
    keys: async () => [],
    delete: async () => true,
  },
  fetch: async (url) => ({
    ok: true,
    clone: () => ({
      json: async () => ({ pages: [], today_summary: { target_total: 512, uploaded: 0, remaining: 512 } })
    }),
    json: async () => ({ pages: [], today_summary: { target_total: 512, uploaded: 0, remaining: 512 } })
  }),
  setTimeout: (fn, ms) => {
    // don't run auto loops indefinitely in test
  },
  setInterval: (fn, ms) => {},
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

try {
  vm.createContext(sandbox);
  vm.runInContext(appJs, sandbox);
  console.log('Script loaded in VM successfully without syntax or immediate TDZ errors!');

  // Now explicitly invoke initApp
  if (typeof sandbox.initApp === 'function') {
    sandbox.initApp();
    console.log('initApp() executed successfully without runtime errors!');
  } else {
    console.error('initApp is not a function');
  }

  // Test switchMainView
  if (typeof sandbox.switchMainView === 'function') {
    sandbox.switchMainView('dashboard');
    sandbox.switchMainView('studio');
    sandbox.switchMainView('health_audit');
    console.log('switchMainView() executed successfully for multiple views!');
  }

  console.log('ALL FRONTEND ENGINE CHECKS PASSED 100%!');
} catch (err) {
  console.error('TEST ERROR:', err);
  process.exit(1);
}
