const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync('docs/js/gold_app.js', 'utf8');

const mockElement = (id) => ({
  id,
  style: {},
  classList: { add: () => {}, remove: () => {}, toggle: () => {}, contains: () => false },
  dataset: {},
  innerText: '',
  innerHTML: '',
  value: '',
  addEventListener: () => {},
  querySelector: () => mockElement('child'),
  querySelectorAll: () => [mockElement('child1')],
  appendChild: () => {},
  remove: () => {},
});

const sandbox = {
  window: { location: { href: 'http://localhost/' } },
  document: {
    readyState: 'complete',
    addEventListener: () => {},
    getElementById: (id) => mockElement(id),
    querySelectorAll: () => [],
    createElement: (tag) => mockElement(tag),
    body: mockElement('body'),
    documentElement: mockElement('html'),
    visibilityState: 'visible',
  },
  localStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
  caches: { open: async () => ({ match: async () => null, put: async () => {} }) },
  fetch: async () => ({ ok: true, clone: () => ({ json: async () => ({ pages: [] }) }) }),
  setTimeout: (fn) => setTimeout(fn, 0),
  clearTimeout: (id) => clearTimeout(id),
  console: console
};

vm.createContext(sandbox);
vm.runInContext(code, sandbox);

const getPageDisplayName = sandbox.window.getPageDisplayName;
console.log('Testing getPageDisplayName:');

// Test 1: Page with numeric placeholder name in USA 5
const p1 = { id: '534342423102401', name: 'Page 142' };
console.log('  p1 (534342423102401, name: "Page 142") -> ' + getPageDisplayName(p1));
if (getPageDisplayName(p1) !== 'The Daily Spark') throw new Error('p1 failed!');

// Test 2: Page with authentic name
const p2 = { id: '988523547680750', name: 'Mix Mood' };
console.log('  p2 (988523547680750, name: "Mix Mood") -> ' + getPageDisplayName(p2));
if (getPageDisplayName(p2) !== 'Mix Mood') throw new Error('p2 failed!');

// Test 3: Page without name but with valid ID in DRIVE_CONFIGURED_PAGES
const p3 = { id: '564341273430022' };
console.log('  p3 (564341273430022, no name) -> ' + getPageDisplayName(p3));
if (getPageDisplayName(p3) !== 'The Chill Spot') throw new Error('p3 failed!');

// Test 4: Page with displayName property
const p4 = { id: '999999999', name: 'Page 99', displayName: 'Super Creative' };
console.log('  p4 (custom, name: "Page 99", displayName: "Super Creative") -> ' + getPageDisplayName(p4));
if (getPageDisplayName(p4) !== 'Super Creative') throw new Error('p4 failed!');

// Test 5: Verify all 156 pages from pages_data.json
const pagesData = JSON.parse(fs.readFileSync('docs/data/pages_data.json', 'utf8'));
let badCount = 0;
for (const p of pagesData.pages) {
  const resolved = getPageDisplayName(p);
  if (!resolved || resolved.toLowerCase().startsWith('page ') || resolved.toLowerCase().startsWith('page_') || /^\d+$/.test(resolved)) {
    console.error('  BAD RESOLUTION:', p.index, p.id, resolved);
    badCount++;
  }
}
console.log('All 156 pages in pages_data.json verified! Bad names count: ' + badCount);
if (badCount > 0) throw new Error('Pages verification failed!');
console.log('ALL PAGE NAME DISPLAY UNIT TESTS PASSED 100%!');
