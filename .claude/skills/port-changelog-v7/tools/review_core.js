/* review_core.js — logic thuần (không DOM) cho UI duyệt merge-plan.json (Phase 4, port-changelog-v7).
 *
 * Hợp đồng: ../schema/README.md (mục 4: trạng thái + ghép output, mục 4b: thao tác, mục 6: kiểm tra).
 * Chạy được cả khi nhúng vào trang HTML lẫn qua require() trong Node.
 * Bản Python tương đương nằm trong render_review.py (validate / compute_status / build_file);
 * hai bản phải giữ giống hệt nhau — tests/test_render_review.py so sánh chúng.
 *
 * API chính:
 *   validate(plan, files)            -> string[]
 *   computeStatus(plan, decisions)   -> { [chunkId]: { status, choice, by } }
 *   build(plan, files, decisions)    -> { [path]: text }
 *   closure(plan, chunkId)           -> string[]   (bao đóng requires, không gồm chính nó)
 *   dependents(plan, chunkId)        -> string[]   (bao đóng ngược)
 * Phụ trợ cho UI: buildFile, previewAction, previewAnswer, normalizeDecisions, splitLines, questionOf.
 */
(function (root) {
  'use strict';

  var CHOICE_VALUES = ['target', 'apply', 'rt'];

  function hasOwn(o, k) {
    return o !== null && typeof o === 'object' && Object.prototype.hasOwnProperty.call(o, k);
  }

  /** Tách text thành mảng dòng (không kèm '\n'). '' -> []. Dòng cuối không có '\n' vẫn là một dòng. */
  function splitLines(text) {
    if (text === '' || text === null || text === undefined) return [];
    var parts = String(text).split('\n');
    if (parts[parts.length - 1] === '') parts.pop();
    return parts;
  }

  function chunksOf(plan) {
    return (plan && Array.isArray(plan.chunks)) ? plan.chunks : [];
  }
  function questionsOf(plan) {
    return (plan && Array.isArray(plan.questions)) ? plan.questions : [];
  }
  function filesOf(plan) {
    return (plan && plan.files && typeof plan.files === 'object') ? plan.files : {};
  }

  /** Map id -> chunk (lần xuất hiện đầu tiên). */
  function chunkIndex(plan) {
    var m = {};
    chunksOf(plan).forEach(function (c) {
      if (c && typeof c.id === 'string' && !hasOwn(m, c.id)) m[c.id] = c;
    });
    return m;
  }

  /** Map chunkId -> câu hỏi đầu tiên chứa chunk đó. */
  function questionMap(plan) {
    var m = {};
    questionsOf(plan).forEach(function (q) {
      (Array.isArray(q.chunks) ? q.chunks : []).forEach(function (k) {
        if (!hasOwn(m, k)) m[k] = q;
      });
    });
    return m;
  }

  function questionOf(plan, chunkId) {
    var m = questionMap(plan);
    return hasOwn(m, chunkId) ? m[chunkId] : null;
  }

  function requiresIds(chunk) {
    var out = [];
    (Array.isArray(chunk.requires) ? chunk.requires : []).forEach(function (r) {
      if (r && typeof r.chunk === 'string' && out.indexOf(r.chunk) < 0) out.push(r.chunk);
    });
    return out;
  }

  /** Map chunkId -> các chunk requires trực tiếp tới nó (theo thứ tự plan). */
  function reverseIndex(plan) {
    var idx = chunkIndex(plan);
    var rev = {};
    Object.keys(idx).forEach(function (k) { rev[k] = []; });
    Object.keys(idx).forEach(function (k) {
      requiresIds(idx[k]).forEach(function (r) {
        if (hasOwn(rev, r) && rev[r].indexOf(k) < 0) rev[r].push(k);
      });
    });
    return rev;
  }

  // ------------------------------------------------------------------ mục 6: kiểm tra

  function validate(plan, files) {
    var errs = [];
    files = files || {};
    var pfiles = filesOf(plan);
    var fileKeys = Object.keys(pfiles);
    var lineCache = {};

    fileKeys.forEach(function (k) {
      if (typeof files[k] !== 'string') {
        errs.push('File "' + k + '" có trong plan.files nhưng không có nội dung Target');
      } else {
        lineCache[k] = splitLines(files[k]);
      }
    });

    var seen = {};
    chunksOf(plan).forEach(function (c) {
      if (hasOwn(seen, c.id)) errs.push('Trùng id chunk ' + c.id);
      seen[c.id] = true;
    });
    var qseen = {};
    questionsOf(plan).forEach(function (q) {
      if (hasOwn(qseen, q.id)) errs.push('Trùng id câu hỏi ' + q.id);
      qseen[q.id] = true;
    });

    // 1, 2, 4, 7 theo từng chunk
    var ranges = {}; // file -> [{s, e, id}]
    chunksOf(plan).forEach(function (c) {
      var id = c.id;
      if (!hasOwn(pfiles, c.file)) {
        errs.push(id + ': file "' + c.file + '" không có trong plan.files');
      } else {
        var t = c.target || {};
        var s = t.start, e = t.end;
        var lines = lineCache[c.file];
        if (lines) {
          var n = lines.length;
          if (!(Number.isInteger(s) && Number.isInteger(e) && s >= 1 && s <= e && e <= n)) {
            errs.push(id + ': khoảng dòng ' + s + '-' + e + ' không hợp lệ (' + c.file + ' có ' + n + ' dòng)');
          } else {
            (ranges[c.file] = ranges[c.file] || []).push({ s: s, e: e, id: id });
            var want = lines.slice(s - 1, e);
            var got = splitLines(typeof t.text === 'string' ? t.text : '');
            var textOk = typeof t.text === 'string' && t.text.slice(-1) === '\n' &&
              want.length === got.length && want.every(function (l, i) { return l === got[i]; });
            if (!textOk) {
              var i = 0;
              while (i < want.length && i < got.length && want[i] === got[i]) i++;
              var at = (i < want.length || i < got.length) ? (s + i) : e;
              errs.push(id + ': target.text không khớp Target dòng ' + s + '-' + e + ' (lệch từ dòng ' + at + ')');
            }
          }
        }
      }
      if (typeof c.rt === 'string' && c.rt === c.apply) {
        errs.push(id + ': rt giống hệt apply (chỉ ghi rt khi khác apply)');
      }
    });

    // 3: chồng range trong cùng file
    fileKeys.forEach(function (f) {
      var rs = (ranges[f] || []).slice().sort(function (a, b) { return a.s - b.s || a.e - b.e; });
      for (var i = 1; i < rs.length; i++) {
        var a = rs[i - 1], b = rs[i];
        if (b.s <= a.e) {
          errs.push(f + ': ' + a.id + ' (' + a.s + '-' + a.e + ') chồng lên ' + b.id + ' (' + b.s + '-' + b.e + ')');
        }
      }
    });

    // 5: tham chiếu
    chunksOf(plan).forEach(function (c) {
      (Array.isArray(c.requires) ? c.requires : []).forEach(function (r) {
        if (!hasOwn(seen, r.chunk)) errs.push(c.id + ': requires trỏ tới chunk không tồn tại ' + r.chunk);
      });
    });
    questionsOf(plan).forEach(function (q) {
      var qc = Array.isArray(q.chunks) ? q.chunks : [];
      qc.forEach(function (k) {
        if (!hasOwn(seen, k)) errs.push(q.id + ': chunks trỏ tới chunk không tồn tại ' + k);
      });
      (Array.isArray(q.options) ? q.options : []).forEach(function (o) {
        (Array.isArray(o.apply) ? o.apply : []).forEach(function (k) {
          if (!hasOwn(seen, k)) errs.push(q.id + '/' + o.id + ': apply trỏ tới chunk không tồn tại ' + k);
          else if (qc.indexOf(k) < 0) errs.push(q.id + '/' + o.id + ': apply có ' + k + ' không thuộc chunks của câu hỏi');
        });
      });
    });

    // 6: một chunk thuộc tối đa một câu hỏi
    var owner = {};
    questionsOf(plan).forEach(function (q) {
      var mine = {};
      (Array.isArray(q.chunks) ? q.chunks : []).forEach(function (k) {
        if (hasOwn(mine, k)) return;
        mine[k] = true;
        if (hasOwn(owner, k)) errs.push(k + ' thuộc hai câu hỏi: ' + owner[k] + ', ' + q.id);
        else owner[k] = q.id;
      });
    });

    return errs;
  }

  // ------------------------------------------------------------------ mục 4: trạng thái

  function normalizeDecisions(plan, decisions) {
    var d = decisions || {};
    var answers = {}, choices = {};
    var idx = chunkIndex(plan);
    if (d.answers && typeof d.answers === 'object') {
      questionsOf(plan).forEach(function (q) {
        var a = d.answers[q.id];
        if (typeof a === 'string' && (q.options || []).some(function (o) { return o.id === a; })) answers[q.id] = a;
      });
    }
    if (d.choices && typeof d.choices === 'object') {
      Object.keys(d.choices).forEach(function (k) {
        if (hasOwn(idx, k) && CHOICE_VALUES.indexOf(d.choices[k]) >= 0) choices[k] = d.choices[k];
      });
    }
    var out = { rt: (plan && plan.rt) || d.rt || '', answers: answers, choices: choices };
    return out;
  }

  function computeStatus(plan, decisions) {
    var dec = normalizeDecisions(plan, decisions);
    var idx = chunkIndex(plan);
    var ids = Object.keys(idx);
    var qmap = questionMap(plan);
    var rev = reverseIndex(plan);
    var st = {}, choice = {}, by = {};

    // Bước 1: ý muốn
    ids.forEach(function (k) {
      var c = idx[k];
      var q = hasOwn(qmap, k) ? qmap[k] : null;
      by[k] = [];
      if (hasOwn(dec.choices, k)) {
        var v = dec.choices[k];
        if (v === 'rt' && typeof c.rt !== 'string') v = 'apply';
        choice[k] = v;
        st[k] = v === 'target' ? 'KEPT' : 'APPLIED';
      } else if (q && hasOwn(dec.answers, q.id)) {
        var opt = null;
        (q.options || []).forEach(function (o) { if (!opt && o.id === dec.answers[q.id]) opt = o; });
        var on = (opt.apply || []).indexOf(k) >= 0;
        choice[k] = on ? 'apply' : 'target';
        st[k] = on ? 'APPLIED' : 'KEPT';
      } else if (q) {
        choice[k] = 'target';
        st[k] = 'NEED_CONFIRM';
        by[k] = [q.id];
      } else {
        choice[k] = 'apply';
        st[k] = 'APPLIED';
      }
    });

    // Bước 2: hạ cấp theo từng vòng đồng bộ (mỗi vòng xét trên trạng thái của vòng trước)
    var changed = true;
    while (changed) {
      changed = false;
      var next = {};
      ids.forEach(function (k) { next[k] = st[k]; });
      ids.forEach(function (k) {
        if (st[k] !== 'APPLIED') return;
        var reqs = requiresIds(idx[k]).filter(function (r) { return hasOwn(idx, r); });
        var blocked = reqs.some(function (r) { return st[r] !== 'APPLIED'; });
        if (blocked) {
          next[k] = 'BLOCKED';
          changed = true;
          return;
        }
        var deps = rev[k];
        if (!hasOwn(dec.choices, k) && !hasOwn(qmap, k) && deps.length > 0 &&
            deps.every(function (d) { return st[d] !== 'APPLIED'; })) {
          next[k] = 'FOLLOW';
          changed = true;
        }
      });
      st = next;
    }

    var out = {};
    ids.forEach(function (k) {
      var s = st[k];
      var b = by[k];
      var ch = choice[k];
      if (s === 'BLOCKED') {
        ch = 'target';
        // Chunk chặn = requires chưa APPLIED. Bỏ các requires đang FOLLOW: chúng chỉ bị hạ vì
        // chính chunk này bị giữ, không phải nguyên nhân (nguyên nhân thật luôn còn ít nhất một).
        b = requiresIds(idx[k]).filter(function (r) {
          return hasOwn(idx, r) && st[r] !== 'APPLIED' && st[r] !== 'FOLLOW';
        });
      } else if (s === 'FOLLOW') {
        ch = 'target';
        b = rev[k].slice();
      }
      out[k] = { status: s, choice: ch, by: b };
    });
    return out;
  }

  // ------------------------------------------------------------------ mục 4 bước 3: ghép output

  function replacementText(chunk, choice) {
    if (choice === 'rt' && typeof chunk.rt === 'string') return chunk.rt;
    if (choice === 'apply' || choice === 'rt') return typeof chunk.apply === 'string' ? chunk.apply : '';
    return null; // target: giữ nguyên dòng gốc
  }

  /**
   * Ghép một file. Trả về { text, lines, regions }:
   *   lines   = các dòng output (không kèm '\n')
   *   regions = [{ chunk, start, end, origStart, origEnd }] — start/end là số dòng output (tính từ 1);
   *             vùng rỗng (apply = "") có end = start - 1.
   * Output dùng '\n'. Kiểu "dòng cuối có/không có '\n'" giữ như Target gốc.
   */
  function buildFile(plan, key, text, status) {
    var lines = splitLines(text);
    var finalNL = text === '' || String(text).slice(-1) === '\n';
    var list = chunksOf(plan).filter(function (c) {
      return c.file === key && c.target && Number.isInteger(c.target.start) && Number.isInteger(c.target.end);
    }).map(function (c, i) { return { c: c, i: i }; });
    list.sort(function (a, b) { return a.c.target.start - b.c.target.start || a.i - b.i; });
    var out = [];
    var regions = [];
    var pos = 0;
    list.forEach(function (it) {
      var c = it.c;
      var s = c.target.start - 1, e = c.target.end;
      if (s < pos || s < 0 || e > lines.length || e <= s) return; // range lỗi: bỏ qua (validate đã báo)
      for (var i = pos; i < s; i++) out.push(lines[i]);
      var regStart = out.length + 1;
      var stc = status && hasOwn(status, c.id) ? status[c.id] : null;
      var rep = replacementText(c, stc ? stc.choice : 'target');
      if (rep === null) {
        for (var j = s; j < e; j++) out.push(lines[j]);
      } else {
        splitLines(rep).forEach(function (l) { out.push(l); });
      }
      regions.push({ chunk: c.id, start: regStart, end: out.length, origStart: s + 1, origEnd: e });
      pos = e;
    });
    for (var k = pos; k < lines.length; k++) out.push(lines[k]);
    var result = out.join('\n') + (out.length > 0 && finalNL ? '\n' : '');
    return { text: result, lines: out, regions: regions };
  }

  function build(plan, files, decisions) {
    files = files || {};
    var status = computeStatus(plan, decisions);
    var res = {};
    Object.keys(filesOf(plan)).forEach(function (key) {
      if (typeof files[key] !== 'string') return;
      res[key] = buildFile(plan, key, files[key], status).text;
    });
    return res;
  }

  // ------------------------------------------------------------------ đồ thị requires

  function bfs(start, next) {
    var seen = {}, out = [], queue = [start];
    seen[start] = true;
    while (queue.length) {
      var cur = queue.shift();
      next(cur).forEach(function (n) {
        if (hasOwn(seen, n)) return;
        seen[n] = true;
        out.push(n);
        queue.push(n);
      });
    }
    return out;
  }

  function closure(plan, chunkId) {
    var idx = chunkIndex(plan);
    return bfs(chunkId, function (k) {
      return hasOwn(idx, k) ? requiresIds(idx[k]).filter(function (r) { return hasOwn(idx, r); }) : [];
    });
  }

  function dependents(plan, chunkId) {
    var rev = reverseIndex(plan);
    return bfs(chunkId, function (k) { return hasOwn(rev, k) ? rev[k] : []; });
  }

  // ------------------------------------------------------------------ mục 4b: thao tác UI

  function cloneDecisions(plan, decisions) {
    var d = normalizeDecisions(plan, decisions);
    return { rt: d.rt, answers: Object.assign({}, d.answers), choices: Object.assign({}, d.choices) };
  }

  function diffStatus(before, after) {
    var changes = [];
    Object.keys(after).forEach(function (k) {
      var a = before[k] || {}, b = after[k];
      if (a.status !== b.status || a.choice !== b.choice) {
        changes.push({ chunk: k, from: a.status, to: b.status, fromChoice: a.choice, toChoice: b.choice });
      }
    });
    return changes;
  }

  /**
   * Xem trước một thao tác trên chunk.
   * action: 'apply' (→) | 'rt' | 'target' (←) | 'reset' (bỏ chọn tay)
   * Trả về { ok, question, decisions, changes }.
   *   ok=false + question=<id câu hỏi>: bao đóng (hoặc chính chunk) thuộc câu hỏi chưa trả lời — không áp.
   *   changes: các chunk đổi trạng thái/lựa chọn (gồm cả chính chunk).
   */
  function previewAction(plan, decisions, chunkId, action) {
    var dec = cloneDecisions(plan, decisions);
    var before = computeStatus(plan, dec);
    if (action === 'apply' || action === 'rt') {
      var qmap = questionMap(plan);
      var cl = closure(plan, chunkId);
      var all = [chunkId].concat(cl);
      for (var i = 0; i < all.length; i++) {
        var q = hasOwn(qmap, all[i]) ? qmap[all[i]] : null;
        if (q && !hasOwn(dec.answers, q.id)) {
          return { ok: false, question: q.id, chunk: all[i], reason: 'unanswered', decisions: dec, changes: [] };
        }
        // Câu hỏi đã trả lời "giữ Target" cho chunk này (và không có chọn tay áp): không ghi đè âm thầm,
        // người duyệt phải đổi câu trả lời trước.
        if (q && i > 0 && dec.choices[all[i]] !== 'apply' && dec.choices[all[i]] !== 'rt') {
          var opt = null;
          for (var j = 0; j < q.options.length; j++) if (q.options[j].id === dec.answers[q.id]) opt = q.options[j];
          if (opt && opt.apply.indexOf(all[i]) < 0) {
            return { ok: false, question: q.id, chunk: all[i], reason: 'answered-keep', decisions: dec, changes: [] };
          }
        }
      }
      dec.choices[chunkId] = action;
      cl.forEach(function (k) {
        if (dec.choices[k] !== 'apply' && dec.choices[k] !== 'rt') dec.choices[k] = 'apply';
      });
    } else if (action === 'target') {
      dec.choices[chunkId] = 'target';
    } else if (action === 'reset') {
      delete dec.choices[chunkId];
    } else {
      throw new Error('Thao tác không hợp lệ: ' + action);
    }
    var after = computeStatus(plan, dec);
    return { ok: true, question: null, decisions: dec, changes: diffStatus(before, after) };
  }

  /** Xem trước việc trả lời (optionId) hoặc bỏ trả lời (optionId = null) câu hỏi. */
  function previewAnswer(plan, decisions, questionId, optionId) {
    var dec = cloneDecisions(plan, decisions);
    var before = computeStatus(plan, dec);
    if (optionId === null || optionId === undefined) delete dec.answers[questionId];
    else dec.answers[questionId] = optionId;
    var after = computeStatus(plan, dec);
    return { ok: true, question: null, decisions: dec, changes: diffStatus(before, after) };
  }

  var api = {
    validate: validate,
    computeStatus: computeStatus,
    build: build,
    closure: closure,
    dependents: dependents,
    buildFile: buildFile,
    splitLines: splitLines,
    normalizeDecisions: normalizeDecisions,
    previewAction: previewAction,
    previewAnswer: previewAnswer,
    questionOf: questionOf,
    reverseIndex: reverseIndex
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.ReviewCore = api;
})(typeof window !== 'undefined' ? window : this);
