// Test cho tools/review_core.js và trang review.html (fixture tests/fixtures/synthetic).
// Chạy: node --test tools/tests/test_review_core.js
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const vm = require('node:vm');
const { spawnSync } = require('node:child_process');

const TOOLS = path.resolve(__dirname, '..');
const core = require(path.join(TOOLS, 'review_core.js'));
const FIX = path.join(__dirname, 'fixtures', 'synthetic');

function readTarget(rel, enc) {
  const raw = fs.readFileSync(path.join(FIX, rel));
  const text = new TextDecoder(enc === 'cp932' ? 'shift_jis' : 'utf-8').decode(raw);
  return text.replace(/\r\n/g, '\n');
}
function loadPlan() { return JSON.parse(fs.readFileSync(path.join(FIX, 'merge-plan.json'), 'utf8')); }
function loadFiles() {
  return { 'src/eco.c': readTarget('target/src/eco.c', 'utf-8'), 'src/eco.h': readTarget('target/src/eco.h', 'cp932') };
}
function statusOnly(st) { const o = {}; for (const k of Object.keys(st)) o[k] = st[k].status; return o; }
const clone = (x) => JSON.parse(JSON.stringify(x));

// ------------------------------------------------------------------ validate

test('validate: fixture hợp lệ', () => {
  assert.deepStrictEqual(core.validate(loadPlan(), loadFiles()), []);
});

test('validate: đủ 7 kiểm tra + thiếu nội dung file', () => {
  const files = loadFiles();
  const cases = [
    [(p) => { p.chunks[0].file = 'src/nope.c'; }, /K1: file "src\/nope.c" không có trong plan.files/],
    [(p) => { p.chunks[0].target.end = 99; }, /K1: khoảng dòng 4-99 không hợp lệ/],
    [(p) => { p.chunks[0].target.start = 0; }, /K1: khoảng dòng 0-4 không hợp lệ/],
    [(p) => { p.chunks[1].target = { start: 4, end: 12, text: files['src/eco.c'].split('\n').slice(3, 12).join('\n') + '\n' }; }, /K1 \(4-4\) chồng lên K2 \(4-12\)/],
    [(p) => { p.chunks[2].target.text = '    total = page * 3;\n'; }, /K3: target.text không khớp Target dòng 22-22/],
    [(p) => { p.chunks[2].target.text = '    total = page * 2;'; }, /K3: target.text không khớp/],
    [(p) => { p.chunks[3].requires.push({ chunk: 'K99', why: 'x' }); }, /K4: requires trỏ tới chunk không tồn tại K99/],
    [(p) => { p.questions[0].chunks.push('K77'); }, /Q1: chunks trỏ tới chunk không tồn tại K77/],
    [(p) => { p.questions[0].options[1].apply = ['K3']; }, /Q1\/B: apply có K3 không thuộc chunks của câu hỏi/],
    [(p) => { p.questions.push({ id: 'Q2', text: 't', chunks: ['K2'], options: [{ id: 'A', label: 'a', apply: [] }, { id: 'B', label: 'b', apply: ['K2'] }] }); }, /K2 thuộc hai câu hỏi: Q1, Q2/],
    [(p) => { p.chunks[0].rt = p.chunks[0].apply; }, /K1: rt giống hệt apply/],
    [(p) => { p.chunks.push(clone(p.chunks[0])); }, /Trùng id chunk K1/],
  ];
  for (const [mut, re] of cases) {
    const p = loadPlan();
    mut(p);
    const errs = core.validate(p, files);
    assert.ok(errs.some((e) => re.test(e)), `mong lỗi ${re}, nhận: ${JSON.stringify(errs)}`);
  }
  const errs = core.validate(loadPlan(), { 'src/eco.c': files['src/eco.c'] });
  assert.ok(errs.some((e) => /src\/eco.h/.test(e)), JSON.stringify(errs));
});

test('validate: dòng cuối không có \\n — target.text vẫn ghi \\n thì hợp lệ', () => {
  const files = loadFiles();
  assert.ok(!files['src/eco.c'].endsWith('\n'));
  const p = loadPlan();
  assert.strictEqual(p.chunks[5].target.text, '/** EOF **/\n');
  assert.deepStrictEqual(core.validate(p, files), []);
});

// ------------------------------------------------------------------ computeStatus

test('computeStatus: mặc định — câu hỏi, chuỗi BLOCKED qua 2 hunk, FOLLOW nhiều vòng', () => {
  const st = core.computeStatus(loadPlan(), {});
  assert.deepStrictEqual(st, {
    K1: { status: 'APPLIED', choice: 'apply', by: [] },
    K2: { status: 'NEED_CONFIRM', choice: 'target', by: ['Q1'] },
    K3: { status: 'BLOCKED', choice: 'target', by: ['K2'] },
    K4: { status: 'BLOCKED', choice: 'target', by: ['K3'] },
    K5: { status: 'FOLLOW', choice: 'target', by: ['K4'] },
    K6: { status: 'FOLLOW', choice: 'target', by: ['K5'] },
  });
  assert.deepStrictEqual(core.computeStatus(loadPlan(), undefined), st);
  assert.deepStrictEqual(core.computeStatus(loadPlan(), { answers: {} }), st);
});

test('computeStatus: trả lời Q1=A → áp hết; Q1=B → K2 KEPT, chuỗi vẫn chặn', () => {
  const p = loadPlan();
  const a = statusOnly(core.computeStatus(p, { answers: { Q1: 'A' } }));
  assert.deepStrictEqual(a, { K1: 'APPLIED', K2: 'APPLIED', K3: 'APPLIED', K4: 'APPLIED', K5: 'APPLIED', K6: 'APPLIED' });
  const b = core.computeStatus(p, { answers: { Q1: 'B' } });
  assert.deepStrictEqual(statusOnly(b), { K1: 'APPLIED', K2: 'KEPT', K3: 'BLOCKED', K4: 'BLOCKED', K5: 'FOLLOW', K6: 'FOLLOW' });
  assert.deepStrictEqual(b.K3.by, ['K2']);
  // phương án không tồn tại = chưa trả lời
  assert.strictEqual(core.computeStatus(p, { answers: { Q1: 'Z' } }).K2.status, 'NEED_CONFIRM');
});

test('computeStatus: chọn tay giữ K5 → K4 BLOCKED bởi K5, K3 FOLLOW, K2 (thuộc câu hỏi) vẫn APPLIED', () => {
  const st = core.computeStatus(loadPlan(), { answers: { Q1: 'A' }, choices: { K5: 'target' } });
  assert.deepStrictEqual(statusOnly(st), { K1: 'APPLIED', K2: 'APPLIED', K3: 'FOLLOW', K4: 'BLOCKED', K5: 'KEPT', K6: 'FOLLOW' });
  assert.deepStrictEqual(st.K4.by, ['K5']);
  assert.deepStrictEqual(st.K3.by, ['K4']);
});

test('computeStatus: choices ưu tiên hơn answers; chunk chọn tay vẫn bị hạ BLOCKED; rt', () => {
  const p = loadPlan();
  const st = core.computeStatus(p, { answers: { Q1: 'B' }, choices: { K2: 'apply', K1: 'rt' } });
  assert.strictEqual(st.K2.status, 'APPLIED');
  assert.deepStrictEqual(st.K1, { status: 'APPLIED', choice: 'rt', by: [] });
  const st2 = core.computeStatus(p, { choices: { K4: 'apply' } });
  assert.deepStrictEqual(st2.K4, { status: 'BLOCKED', choice: 'target', by: ['K3'] });
  // chunk trong choices không bao giờ thành FOLLOW
  const st3 = core.computeStatus(p, { choices: { K6: 'apply' } });
  assert.strictEqual(st3.K6.status, 'APPLIED');
  // rt khi chunk không có rt → apply; giá trị lạ bị bỏ qua
  const st4 = core.computeStatus(p, { choices: { K6: 'rt', K1: 'xyz' } });
  assert.strictEqual(st4.K6.choice, 'apply');
  assert.strictEqual(st4.K1.choice, 'apply');
});

test('computeStatus: chu trình không bị hạ nếu không có gì chặn', () => {
  const p = loadPlan();
  p.chunks[0].requires = [{ chunk: 'K6', why: 'vòng' }];
  p.chunks[5].requires = [{ chunk: 'K1', why: 'vòng' }];
  const st = core.computeStatus(p, { answers: { Q1: 'A' } });
  assert.strictEqual(st.K1.status, 'APPLIED');
  assert.strictEqual(st.K6.status, 'APPLIED');
  const st2 = core.computeStatus(p, { answers: { Q1: 'A' }, choices: { K1: 'target' } });
  assert.strictEqual(st2.K6.status, 'BLOCKED');
});

// ------------------------------------------------------------------ build

function expected(scn, rel, enc) {
  const raw = fs.readFileSync(path.join(FIX, 'expected', scn, rel));
  return new TextDecoder(enc === 'cp932' ? 'shift_jis' : 'utf-8').decode(raw).replace(/\r\n/g, '\n');
}

test('build: mặc định khớp expected/default (giữ dòng cuối không \\n)', () => {
  const out = core.build(loadPlan(), loadFiles(), {});
  assert.strictEqual(out['src/eco.c'], expected('default', 'src/eco.c'));
  assert.strictEqual(out['src/eco.h'], expected('default', 'src/eco.h', 'cp932'));
  assert.ok(!out['src/eco.c'].endsWith('\n'));
});

test('build: Q1=A khớp expected/q1a (chèn trước neo EOF, file CRLF/cp932)', () => {
  const out = core.build(loadPlan(), loadFiles(), { answers: { Q1: 'A' } });
  assert.strictEqual(out['src/eco.c'], expected('q1a', 'src/eco.c'));
  assert.strictEqual(out['src/eco.h'], expected('q1a', 'src/eco.h', 'cp932'));
});

test('build: không quyết định gì & giữ hết = Target gốc', () => {
  const files = loadFiles();
  const choices = {};
  for (const c of loadPlan().chunks) choices[c.id] = 'target';
  assert.deepStrictEqual(core.build(loadPlan(), files, { choices }), files);
});

test('build: rt, apply rỗng (xóa), xóa dòng cuối, file có \\n cuối', () => {
  const p = loadPlan();
  const files = loadFiles();
  const out = core.build(p, files, { answers: { Q1: 'A' }, choices: { K1: 'rt' } });
  assert.ok(out['src/eco.c'].includes('eco report count (TELINDY)\n'));
  p.chunks[3].apply = '';
  const out2 = core.build(p, files, { answers: { Q1: 'A' } });
  assert.ok(!out2['src/eco.c'].includes('PrintBody'));
  assert.strictEqual(core.splitLines(out2['src/eco.c']).length, 47 - 4);
  // xóa dòng neo cuối (không \n)
  p.chunks[5].apply = '';
  const out3 = core.build(p, files, { answers: { Q1: 'A' } });
  // dòng 37 (trống) thành dòng cuối, vẫn không có \n riêng → text kết thúc bằng '}\n' (không phải '}\n\n')
  assert.ok(out3['src/eco.c'].endsWith('    eco_mode = 0;\n}\n') && !out3['src/eco.c'].endsWith('\n\n'));
  // file có \n cuối: chunk ở dòng cuối vẫn kết thúc bằng \n
  const p2 = loadPlan();
  p2.chunks.push({ id: 'K9', file: 'src/eco.h', unit: 'x', src: 's', summary: 's', target: { start: 8, end: 8, text: '#endif\n' }, apply: '#endif /* ECO_H */\n' });
  const out4 = core.build(p2, files, {});
  assert.ok(out4['src/eco.h'].endsWith('#endif /* ECO_H */\n'));
});

test('buildFile: regions theo số dòng output', () => {
  const p = loadPlan();
  const st = core.computeStatus(p, { answers: { Q1: 'A' } });
  const b = core.buildFile(p, 'src/eco.c', loadFiles()['src/eco.c'], st);
  const r = Object.fromEntries(b.regions.map((x) => [x.chunk, [x.start, x.end]]));
  assert.deepStrictEqual(r, { K1: [4, 5], K2: [13, 13], K3: [23, 24], K4: [29, 32], K6: [42, 47] });
});

// ------------------------------------------------------------------ closure / dependents / thao tác

test('closure / dependents', () => {
  const p = loadPlan();
  assert.deepStrictEqual(core.closure(p, 'K4'), ['K3', 'K5', 'K2', 'K6']);
  assert.deepStrictEqual(core.closure(p, 'K1'), []);
  assert.deepStrictEqual(core.dependents(p, 'K6'), ['K5', 'K4']);
  assert.deepStrictEqual(core.dependents(p, 'K2'), ['K3', 'K4']);
  assert.deepStrictEqual(core.dependents(p, 'K4'), []);
});

test('previewAction: → bị chặn bởi câu hỏi chưa trả lời; sau khi trả lời thì kéo theo', () => {
  const p = loadPlan();
  const r = core.previewAction(p, {}, 'K4', 'apply');
  assert.strictEqual(r.ok, false);
  assert.strictEqual(r.question, 'Q1');
  // Q1 đã trả lời "giữ Target" (B) cho K2 nằm trong bao đóng: không ghi đè âm thầm.
  const rKeep = core.previewAction(p, { answers: { Q1: 'B' } }, 'K4', 'apply');
  assert.strictEqual(rKeep.ok, false);
  assert.strictEqual(rKeep.reason, 'answered-keep');
  assert.strictEqual(rKeep.question, 'Q1');
  assert.strictEqual(rKeep.chunk, 'K2');
  // Chọn tay → ngay trên chunk thuộc câu hỏi thì vẫn được (người duyệt chủ động).
  assert.strictEqual(core.previewAction(p, { answers: { Q1: 'B' } }, 'K2', 'apply').ok, true);
  // Trả lời áp (A): → kéo theo cả bao đóng.
  const r2 = core.previewAction(p, { answers: { Q1: 'A' } }, 'K4', 'apply');
  assert.strictEqual(r2.ok, true);
  assert.deepStrictEqual(r2.decisions.choices, { K4: 'apply', K3: 'apply', K5: 'apply', K2: 'apply', K6: 'apply' });
  const after = core.computeStatus(p, r2.decisions);
  assert.ok(Object.values(after).every((x) => x.status === 'APPLIED'));
});

test('previewAction: ← lùi các chunk phụ thuộc; reset bỏ chọn tay', () => {
  const p = loadPlan();
  const r = core.previewAction(p, { answers: { Q1: 'A' } }, 'K6', 'target');
  assert.deepStrictEqual(r.decisions.choices, { K6: 'target' });
  const ch = Object.fromEntries(r.changes.map((x) => [x.chunk, x.to]));
  assert.deepStrictEqual(ch, { K6: 'KEPT', K5: 'BLOCKED', K4: 'BLOCKED', K3: 'FOLLOW' });
  const r2 = core.previewAction(p, r.decisions, 'K6', 'reset');
  assert.deepStrictEqual(r2.decisions.choices, {});
  const r3 = core.previewAction(p, { answers: { Q1: 'A' } }, 'K1', 'rt');
  assert.deepStrictEqual(r3.changes, [{ chunk: 'K1', from: 'APPLIED', to: 'APPLIED', fromChoice: 'apply', toChoice: 'rt' }]);
});

// ------------------------------------------------------------------ trang HTML (chạy script nhúng trong vm với DOM giả)

function renderHtml(planPath, extra) {
  const out = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'pcv7-')), 'review.html');
  const args = [path.join(TOOLS, 'render_review.py'), '--plan', planPath, '--target-root', path.join(FIX, 'target'), '-o', out].concat(extra || []);
  const r = spawnSync('python3', args, { encoding: 'utf8' });
  return { status: r.status, stdout: r.stdout, stderr: r.stderr, html: fs.existsSync(out) ? fs.readFileSync(out, 'utf8') : null };
}

function scriptsOf(html) {
  const re = /<script([^>]*)>([\s\S]*?)<\/script>/g;
  const out = [];
  let m;
  while ((m = re.exec(html))) out.push({ attrs: m[1], body: m[2] });
  return out;
}

function runPage(html) {
  const scripts = scriptsOf(html);
  const payload = scripts.find((s) => /id="payload"/.test(s.attrs)).body;
  const els = {};
  const downloads = [];
  const blobs = {};
  let nBlob = 0;
  function makeEl(id) {
    return {
      id, innerHTML: '', textContent: '', disabled: false, title: '', value: '', download: '', href: '',
      classList: { _s: new Set(), add(c) { this._s.add(c); }, remove(c) { this._s.delete(c); }, toggle() {}, contains(c) { return this._s.has(c); } },
      style: {}, listeners: {},
      addEventListener(t, f) { this.listeners[t] = f; },
      scrollIntoView() {}, remove() {}, getAttribute() { return null; }, parentNode: null, offsetWidth: 0,
      click() { if (this.download) downloads.push({ name: this.download, text: blobs[this.href] }); },
    };
  }
  const docListeners = {};
  const store = {};
  const ctx = {
    document: {
      getElementById(id) { if (id === 'payload') return { textContent: payload }; return els[id] || (els[id] = makeEl(id)); },
      addEventListener(t, f) { docListeners[t] = f; },
      createElement() { return makeEl(''); },
      body: { appendChild() {} },
      title: '',
    },
    localStorage: { getItem(k) { return store[k] || null; }, setItem(k, v) { store[k] = v; } },
    setTimeout: (f) => f(), clearTimeout() {},
    Blob: class { constructor(parts) { this.text = parts.join(''); } },
    URL: { createObjectURL(b) { const k = 'blob:' + (++nBlob); blobs[k] = b.text; return k; }, revokeObjectURL() {} },
    FileReader: class {},
    JSON, Object, Array, String, Math, Number, Error,
  };
  ctx.window = ctx;
  vm.createContext(ctx);
  for (const s of scripts) {
    if (/application\/json/.test(s.attrs)) continue;
    vm.runInContext(s.body, ctx);
  }
  return { ctx, els, downloads, api: ctx.window.__review, docListeners };
}

test('HTML: script nhúng không lỗi cú pháp (node --check)', () => {
  const r = renderHtml(path.join(FIX, 'merge-plan.json'));
  assert.strictEqual(r.status, 0, r.stderr + r.stdout);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pcv7-js-'));
  scriptsOf(r.html).filter((s) => !/application\/json/.test(s.attrs)).forEach((s, i) => {
    const f = path.join(dir, `s${i}.js`);
    fs.writeFileSync(f, s.body);
    const c = spawnSync(process.execPath, ['--check', f], { encoding: 'utf8' });
    assert.strictEqual(c.status, 0, c.stderr);
  });
  assert.ok(!/\/\*__PAYLOAD__\*\/|\/\*__REVIEW_CORE__\*\//.test(r.html), 'marker chưa được thay');
});

test('HTML: chạy trang trong DOM giả — hiển thị, thao tác, xuất', () => {
  const r = renderHtml(path.join(FIX, 'merge-plan.json'));
  const { els, downloads, api } = runPage(r.html);
  assert.deepStrictEqual(Array.from(api.errors), []);
  assert.match(els.counts.innerHTML, /NEED_CONFIRM 1/);
  assert.match(els.counts.innerHTML, /BLOCKED 2/);
  assert.match(els.fileview.innerHTML, /id="row-K1"/);
  assert.match(els.fileview.innerHTML, /chờ <a data-goto="K2"/);
  assert.match(els.fileview.innerHTML, /class="tok" title="TelEcoCount → FomEcoCnt/);
  assert.match(els.questions.innerHTML, /data-ans="Q1" data-opt="A"/);
  assert.match(els.questions.innerHTML, /đề xuất/);
  assert.match(els.skipped.innerHTML, /ALREADY_IN_TARGET/);
  assert.strictEqual(els.btnDecisions.disabled, false);

  // → K4 khi Q1 chưa trả lời: không áp
  const p0 = api.doAction('K4', 'apply');
  assert.strictEqual(p0.ok, false);
  assert.strictEqual(Object.keys(api.state.decisions.choices).length, 0);

  // trả lời Q1=A → modal liệt kê chunk kéo theo → đồng ý
  api.doAnswer('Q1', 'A');
  assert.match(els.modal.innerHTML, /Kéo theo/);
  api.confirmOk();
  assert.ok(Object.values(api.state.status).every((x) => x.status === 'APPLIED'));
  assert.strictEqual(api.outputText('src/eco.c'), expected('q1a', 'src/eco.c'));
  assert.strictEqual(api.outputText('src/eco.h'), expected('q1a', 'src/eco.h', 'cp932').replace(/\n/g, '\r\n'));

  // ← K6 → modal lùi theo
  api.doAction('K6', 'target');
  assert.match(els.modal.innerHTML, /Lùi theo/);
  api.confirmOk();
  assert.strictEqual(api.state.status.K5.status, 'BLOCKED');

  // xuất decisions.json
  els.btnDecisions.listeners.click();
  const d = JSON.parse(downloads.find((x) => x.name === 'decisions.json').text);
  assert.deepStrictEqual(d, { rt: 'RT9001', answers: { Q1: 'A' }, choices: { K6: 'target' } });

  // file cp932 không có nút tải mà có ghi chú lệnh --apply
  api.state.file = 'src/eco.h';
  api.render();
  assert.match(els.fileview.innerHTML, /--apply/);
  assert.doesNotMatch(els.fileview.innerHTML, /data-dl=/);
});

test('HTML: plan lỗi → banner đỏ, khóa nút xuất; render exit 1', () => {
  const p = loadPlan();
  p.chunks[2].target.text = '    total = page * 3;\n';
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pcv7-bad-'));
  const pp = path.join(dir, 'merge-plan.json');
  fs.writeFileSync(pp, JSON.stringify(p));
  const r = renderHtml(pp);
  assert.strictEqual(r.status, 1);
  const { els } = runPage(r.html);
  assert.match(els.banner.innerHTML, /không qua kiểm tra/);
  assert.match(els.banner.innerHTML, /K3: target.text không khớp/);
  assert.strictEqual(els.btnDecisions.disabled, true);
  assert.strictEqual(els.btnAll.disabled, true);
});

test('HTML: --decisions nạp sẵn vào trang', () => {
  const r = renderHtml(path.join(FIX, 'merge-plan.json'), ['--decisions', path.join(FIX, 'decisions-q1a.json')]);
  assert.strictEqual(r.status, 0, r.stderr);
  const { api } = runPage(r.html);
  assert.strictEqual(api.state.decisions.answers.Q1, 'A');
  assert.strictEqual(api.state.status.K4.status, 'APPLIED');
});
