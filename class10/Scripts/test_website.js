// Functional test harness for the rebuilt site JS (CommonJS hooks + browser globals).
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const dir = 'E:/logo/class10/website/js';

// Minimal browser globals
const makeEl = (id) => ({
  id, style: {}, dataset: {}, classList: { add() {}, remove() {}, toggle() {}, contains: () => false },
  innerHTML: '', innerText: '', textContent: '', value: '',
  querySelectorAll: () => [], querySelector: () => null,
  addEventListener() {}, setAttribute() {}, getAttribute: () => null,
  appendChild() {}, onclick: null, options: [], selectedIndex: -1,
});
const els = {};
global.window = { scrollTo: () => {}, scrollBy: () => {} };
global.document = {
  getElementById: (id) => (els[id] ||= makeEl(id)),
  querySelectorAll: () => [],
  querySelector: () => null,
  createElement: () => makeEl('__new__'),
  addEventListener() {},
};
global.location = { search: '' };
const store = {};
global.localStorage = {
  getItem: (k) => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v); },
  removeItem: (k) => { delete store[k]; },
};

// Load embedded 3000-question bank into window (like the <script> tag does)
vm.runInThisContext(fs.readFileSync(path.join(dir, 'allquestions.js'), 'utf-8'));

const data = require(path.join(dir, 'data.js'));
const common = require(path.join(dir, 'common.js'));

// Make the browser-global functions quiz.js/common.js pages expect
global.SUBJECTS = data.SUBJECTS;
global.QUESTION_DATA = data.QUESTION_DATA;
global.getQuestions = data.getQuestions;
global.shuffleArray = data.shuffleArray;
global.extractKeywords = data.extractKeywords;
global.getURLParam = common.getURLParam;
global.fillSubjectSelect = common.fillSubjectSelect;
global.setupNav = common.setupNav;
global.fixSpelling = common.fixSpelling;
global.renderSubjectCards = common.renderSubjectCards;
global.escapeHtml = common.escapeHtml;
global.toast = common.toast;

let failures = 0;
const ok = (name, cond) => { if (!cond) failures++; console.log((cond ? 'PASS' : 'FAIL') + ' - ' + name); };

(async () => {
  await data.loadAllData();
  console.log('Total questions:', data.getTotalQuestions());

  ok('10 subjects present', Object.keys(data.QUESTION_DATA).length === 10);
  const counts = {};
  for (const s in data.QUESTION_DATA) counts[s] = data.QUESTION_DATA[s].questions.length;
  for (const s in data.QUESTION_DATA) ok(s + ' has >=300', counts[s] >= 300);

  let bad = 0, ugly = 0, mcq = 0, write = 0;
  const uglyPat = /अध्याय\s*\d+\s*[:：]/;
  for (const s in data.QUESTION_DATA) {
    for (const q of data.QUESTION_DATA[s].questions) {
      if (!q.q || !q.chapter || !q.type || (q.type === 'mcq' && (!Array.isArray(q.options) || q.options.length < 2 || typeof q.answer !== 'number'))) bad++;
      if (uglyPat.test(q.q)) ugly++;
      q.type === 'mcq' ? mcq++ : write++;
    }
  }
  ok('all questions well-formed', bad === 0);
  ok('no अध्याय-N: prefixes in question text', ugly === 0);
  console.log('  MCQ:', mcq, '| write:', write);

  // ---- Quiz engine flow (browser-like) ----
  const quiz = require(path.join(dir, 'quiz.js'));
  quiz.initQuizForSubject('physics');
  ok('quiz initialized for physics', !!quiz.currentQuiz && quiz.currentQuiz.subject === 'physics');
  quiz.startQuiz();
  ok('quiz has questions', quiz.currentQuiz.questions.length > 0);
  console.log('  physics mcq-mode question count:', quiz.currentQuiz.questions.length);

  const first = quiz.currentQuiz.questions[0];
  if (first.type === 'mcq') {
    const before = quiz.currentQuiz.answers[0];
    quiz.selectOption(0);
    ok('answer selected+locked', quiz.currentQuiz.answers[0].selected !== null);
    const after = quiz.currentQuiz.answers[0];
    ok('correct flag matches answer', !!after.correct === (after.selected === first.answer));
  }

  quiz.nextQuestion();
  ok('nextQuestion advances', quiz.currentQuiz.currentIndex === 1);

  // write-mode quiz for physics
  global.location = { search: '?subject=physics&mode=write' };
  quiz.currentQuiz.chapter = 'all';
  quiz.currentQuiz.mode = 'write';
  els['quizModeSel'].value = 'write';
  quiz.startQuiz();
  ok('write mode filters to write questions', quiz.currentQuiz.questions.every(q => q.type === 'write'));

  quiz.submitQuiz();
  ok('submitQuiz finished', quiz.currentQuiz.finished === true);
  const results = data.getResults ? [] : [];
  const saved = quiz.getResults();
  console.log('  saved results:', saved.length);
  ok('result saved to localStorage', saved.length >= 1);

  // write-answer grading hooks
  ok('extractKeywords works', Array.isArray(data.extractKeywords('ओम का नियम प्रतिरोध विभवांतर')) && data.extractKeywords('ओम का नियम प्रतिरोध').length > 0);
  ok('shuffleArray works', data.shuffleArray([1, 2, 3, 4, 5]).length === 5);

  // chapter filter returns chapter questions only
  const chs = data.QUESTION_DATA.maths.chapters;
  if (chs.length) {
    const chQ = data.getQuestions('maths', chs[0]);
    ok('chapter filter works', chQ.length > 0 && chQ.every(q => q.chapter === chs[0]));
  }

  console.log(failures === 0 ? '\nALL TESTS PASSED' : '\n' + failures + ' FAILURES');
  process.exit(failures === 0 ? 0 : 1);
})();