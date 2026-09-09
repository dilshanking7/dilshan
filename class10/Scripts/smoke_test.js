// Browser-like smoke test: loads each HTML page's scripts (external + inline)
// in order, fires DOMContentLoaded, and reports any runtime error.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const dir = 'E:/logo/class10/website';

const makeEl = (id) => ({
  id, style: {}, dataset: {}, classList: { add() {}, remove() {}, toggle() {}, contains: () => false },
  innerHTML: '', innerText: '', textContent: '', value: '', href: '',
  querySelectorAll: () => [], querySelector: () => null,
  addEventListener() {}, setAttribute() {}, getAttribute: () => null, remove() {},
  appendChild() {}, onclick: null, options: [], selectedIndex: -1,
});

function loadPage(file) {
  const errors = [];
  const handlers = {};
  const els = {};
  const listeners = {};
  const document = {
    getElementById: (id) => (els[id] ||= makeEl(id)),
    querySelectorAll: () => [],
    querySelector: () => null,
    createElement: () => makeEl('__new__'),
    createTextNode: () => ({}),
    addEventListener: (ev, fn) => { (handlers[ev] ||= []).push(fn); },
    body: makeEl('__body__'),
  };
  const sandbox = {
    console, Math, Date, JSON, RegExp, parseInt, parseFloat, isNaN,
    setTimeout, clearTimeout, setInterval, clearInterval,
    encodeURIComponent, decodeURIComponent, globalThis: null, Infinity, NaN, undefined,
    location: { search: '', href: 'file:///E:/logo/class10/website/' + file, pathname: '/' + file },
    document,
    window: { scrollTo: () => {}, scrollBy: () => {}, innerWidth: 1000 },
    localStorage: (() => { const s = {}; return { getItem: (k) => (k in s ? s[k] : null), setItem: (k, v) => { s[k] = String(v); }, removeItem: (k) => { delete s[k]; } }; })(),
    confirm: () => true, alert: () => {}, prompt: () => null, fetch: async () => ({ ok: false }),
    Promise, Object, Array, String, Number, Boolean, Symbol, Error, TypeError, FileReader: class {},
    URLSearchParams, URL,
  };
  sandbox.globalThis = sandbox;
  sandbox.window.window = sandbox.window;

  const context = vm.createContext(sandbox);
  const html = fs.readFileSync(path.join(dir, file), 'utf-8');

  // Ordered script extraction
  const srcRe = /<script[^>]+src="([^"]+)"[^>]*>\s*<\/script>/g;
  const inlineRe = /<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/g;
  const pending = [];
  let m;
  // Merge external & inline in document order: scan raw html in order
  const combined = []; // {src} or {code}
  const re = /<script([^>]*)>([\s\S]*?)<\/script>/g;
  while ((m = re.exec(html)) !== null) {
    const attrs = m[1] || '';
    const content = m[2] || '';
    const srcMatch = /src="([^"]+)"/.exec(attrs);
    if (srcMatch) combined.push({ src: srcMatch[1] });
    else if (content.trim()) combined.push({ code: content });
  }

  for (const item of combined) {
    try {
      const code = item.src
        ? fs.readFileSync(path.join(dir, item.src), 'utf-8')
        : item.code;
      vm.runInContext(code, context, { filename: item.src || ('inline:' + file) });
    } catch (e) {
      errors.push((item.src || 'inline') + ' :: ' + e.message);
      break; // stop subsequent scripts like a browser would
    }
  }

  // fire DOMContentLoaded in registration order
  try {
    for (const fn of handlers.DOMContentLoaded || []) fn();
  } catch (e) {
    errors.push('DOMContentLoaded :: ' + e.message + ' | ' + (e.stack || '').split('\n')[1]);
  }

  return { file, errors, sandbox };
}

let total = 0, failed = 0;
const pages = fs.readdirSync(dir).filter(f => f.endsWith('.html')).sort();
for (const f of pages) {
  total++;
  const r = loadPage(f);
  if (r.errors.length) { failed++; console.log('\nFAIL - ' + f); r.errors.forEach(e => console.log('   ' + e)); }
  else console.log('PASS - ' + f);
}
console.log('\n' + (total - failed) + '/' + total + ' pages OK');
process.exit(failed === 0 ? 0 : 1);