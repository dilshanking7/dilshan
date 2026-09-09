// ============================================================
//  COMMON HELPERS + NAVIGATION - JAC Class 10 Study Hub
// ============================================================

// Loaded after data.js so SUBJECTS etc. are globals.

// ---- Site navigation (injected centrally so the language switcher
//      and new pages appear on every page automatically) ----
const NAV_LINKS = [
  { href:'index.html',    icon:'🏠', i18n:'nav_home' },
  { href:'subjects.html', icon:'📚', i18n:'nav_subjects' },
  { href:'quiz.html',     icon:'📝', i18n:'nav_quiz' },
  { href:'notes.html',    icon:'📖', i18n:'nav_notes' },
  { href:'formulas.html', icon:'🧮', i18n:'nav_formulas' },
  { href:'periodic.html', icon:'🧪', i18n:'nav_periodic' },
  { href:'lab.html',      icon:'🔬', i18n:'nav_lab' },
  { href:'mathlab.html',  icon:'📉', i18n:'nav_mathlab' },
  { href:'practical.html',icon:'🧫', i18n:'nav_practical' },
  { href:'diagrams.html', icon:'🖼️', i18n:'nav_diagrams' },
  { href:'stories.html',  icon:'📗', i18n:'nav_stories' },
  { href:'history.html',  icon:'🕰️', i18n:'nav_history' },
  { href:'pdf.html',      icon:'📄', i18n:'nav_pdf' },
  { href:'analysis.html', icon:'📊', i18n:'nav_analysis' }
];

function buildNav() {
  const host = document.getElementById('siteHeader') || document.querySelector('header.navbar');
  if (!host) return;
  const page = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  const links = NAV_LINKS.map(l => {
    const active = (l.href.split('?')[0] === page) ? ' class="active"' : '';
    return `<a href="${l.href}"${active}>${l.icon} <span data-i18n="${l.i18n}">·</span></a>`;
  }).join('');

  host.innerHTML = `
    <div class="logo"><span class="logo-icon">🎓</span> JAC 10th <b>Study Hub</b></div>
    <nav class="nav-links" id="navLinks">${links}</nav>
    <select class="lang-select" id="langSelect" title="Language / भाषा" onchange="setLang(this.value)">
      <option value="hi">हिंदी</option>
      <option value="en">English</option>
      <option value="hg">Hinglish</option>
    </select>
    <button class="hamburger" id="hamburger">☰</button>`;

  const ham = document.getElementById('hamburger');
  const nav = document.getElementById('navLinks');
  ham.addEventListener('click', () => nav.classList.toggle('show'));
  nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => nav.classList.remove('show')));
}

// ---- Render subject cards into a grid ----
function renderSubjectCards(containerId, page) {
  const grid = document.getElementById(containerId);
  if (!grid) return;
  let html = '';
  for (const s in SUBJECTS) {
    const sub = SUBJECTS[s];
    const qty = (QUESTION_DATA[s] && QUESTION_DATA[s].questions) ? QUESTION_DATA[s].questions.length : 0;
    html += `
    <div class="subject-card" onclick="location.href='${page}?subject=${s}'">
      <div class="card-icon" style="background:${sub.color}">${sub.emoji}</div>
      <h3>${sub.name}</h3>
      <p>${sub.desc}</p>
      <div class="tag" style="background:${sub.color}22;color:${sub.color}">${qty || 300}+ प्रश्न</div>
    </div>`;
  }
  grid.innerHTML = html;
}

// ---- Read ?subject= from URL ----
function getURLParam(name) {
  const p = new URLSearchParams(location.search);
  return p.get(name);
}

// ---- Escape HTML ----
function escapeHtml(str) {
  return String(str || '').replace(/[&<>"']/g, m => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[m]));
}

// ---- Animate counters ----
function animateValue(el, target, suffix) {
  if (!el) return;
  let cur = 0;
  const step = Math.max(1, Math.ceil(target / 80));
  const t = setInterval(() => {
    cur += step;
    if (cur >= target) { cur = target; clearInterval(t); }
    el.textContent = cur + (suffix || '');
  }, 18);
}

// ---- Subjects dropdown options for a select ----
function fillSubjectSelect(sel) {
  if (!sel) return;
  for (const s in SUBJECTS) {
    const o = document.createElement('option');
    o.value = s; o.textContent = SUBJECTS[s].emoji + ' ' + SUBJECTS[s].name;
    sel.appendChild(o);
  }
}

// ---- Spelling corrector (surface-level) ----
function fixSpelling(text) {
  if (!text) return text;
  let t = String(text);
  if (typeof CORRECT_SPELLINGS !== 'undefined') {
    for (const wrong in CORRECT_SPELLINGS) {
      const re = new RegExp(wrong.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
      t = t.replace(re, CORRECT_SPELLINGS[wrong][0]);
    }
  }
  return t;
}

// ---- Show a colored toast ----
function toast(msg, type) {
  let box = document.getElementById('toastBox');
  if (!box) {
    box = document.createElement('div');
    box.id = 'toastBox';
    box.style.cssText = 'position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:9999;';
    document.body.appendChild(box);
  }
  const colors = { success:'#22c55e', error:'#ef4444', info:'#6366f1' };
  const el = document.createElement('div');
  el.textContent = msg;
  el.style.cssText = `background:${colors[type]||'#6366f1'};color:#fff;padding:12px 22px;border-radius:12px;font-weight:700;box-shadow:0 6px 20px rgba(0,0,0,.25);margin-bottom:8px;`;
  box.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; el.style.transition = 'opacity .4s'; }, 2200);
  setTimeout(() => el.remove(), 2700);
}

// ---- Auto setup on DOM ready ----
document.addEventListener('DOMContentLoaded', buildNav);

// export for tests (harmless in the browser)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { buildNav, renderSubjectCards, getURLParam, escapeHtml, animateValue, fillSubjectSelect, fixSpelling, toast };
}