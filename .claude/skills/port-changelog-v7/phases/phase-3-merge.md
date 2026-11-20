# Phase 3 — Lập kế hoạch merge vào FOMULAR

## Mục tiêu và nguyên tắc

- Biến diff (new) thành `WORK/<run-id>/phase3/merge-plan.json` theo `schema/README.md`. `target_out/` và `review.html` do `render_review.py` tạo từ plan; **agent không sửa tay output.**
- Áp mọi thứ độc lập; chỉ giữ chunk có câu hỏi và những gì nối với nó qua `requires`.
- **Before gần giống FOMULAR.** Dòng `-` của diff (new) là code Before, chỉ là manh mối tìm vị trí. Thứ bị thay là **vùng tương ứng trong Target**.
- **Phía `+` chép nguyên văn**, chỉ đổi tên theo `name_map` đã chứng minh. Không tự sửa logic cho hợp FOMULAR.
- **Lệch tên thì merge được, lệch logic thì hỏi.** Tiêu chí `NEED_CONFIRM` ở Bước 3 và Bước 6 là bắt buộc, không nới.
- Đơn vị `MOD` mà Target không có → bỏ (`NOT_IN_TARGET`), không hỏi. Đơn vị `NEW` mà Target không có → thêm.

## Tóm tắt luồng

```text
B1  Chuẩn bị: đọc file theo bảng, ghép file TELINDY ↔ FOMULAR
B2  Cắt đơn vị ở Target + <X>.ctx.diff
B3  Định vị, phân loại từng đoạn thay đổi: CLEAN | ALREADY_IN_TARGET | CONFLICT
B4  Chốt name_map từng file
B5  Tạo chunk
B6  Kiểm phụ thuộc ở Target, ghi requires
B7  Câu hỏi
B8  Ghi merge-plan.json
B9  Ghép target_out (quyết định rỗng) + tạo review.html + changelog
B10 Kiểm tra bằng get_diff, report, cổng → DỪNG
```

## Bước 1 — Chuẩn bị

Đọc: `phase2/diff/<file>.diff` (cả dòng tiêu đề và `Anchor:`), `phase2/fn/` (bản cắt), `phase2/paused.md`, `phase2/REPORT.md` (câu trả lời), `phase2/ledger.md` (dòng cố ý bỏ, không tạo lại). `phase1/diff/` chỉ đọc khi cần context hoặc tìm định nghĩa trong code RT.

- Ghép file: cùng đường dẫn tương đối trong `target/`; không có thì cùng tên file; nhiều ứng viên → `skipped` `QUESTION`.
- Target không có file: `NO_FILE` ở "Bỏ qua". Nếu file chỉ chứa đơn vị mới (cần tạo file mới): tool chưa làm được → ghi `tool-gaps.md`, hỏi người dùng.
- File `deleted` ở Phase 1: không xoá file Target, đưa vào "Cần xác nhận". Ghi encoding từng file Target vào `files`.

## Bước 2 — Cắt đơn vị ở Target

Đọc: diff (new), `target/<file>`, `phase2/fn/<file>/<X>.before.c`.

- Tìm **định nghĩa** X trong file Target đã ghép (như Phase 2, Bước 1). Không có → `NOT_IN_TARGET` (đơn vị `MOD`/`DEL`), không tìm tên khác.
- Cắt theo quy tắc cắt Phase 2 (từ dòng đầu comment đầu hàm) → `phase3/fn/<file>/<X>.target.c`. Ghi khoảng dòng gốc: số dòng trong plan là **số dòng file Target gốc** = dòng bản cắt + (dòng đầu − 1).
- `get_diff(<X>.target.c, <X>.before.c)` → `<X>.ctx.diff`. Chỉ để biết Target lệch Before ở đâu. **Không merge diff này.**

## Bước 3 — Định vị và phân loại

Đọc: diff (new) của X, `<X>.ctx.diff`, `<X>.target.c`, `<X>.before.c`.

### 3a. Định vị từng đoạn thay đổi

- **Vị trí dự kiến** = dòng Before + độ lệch (tổng `+` − `-` của các thay đổi trong `<X>.ctx.diff` nằm hẳn phía trên). Vùng bị sửa giao chính dòng đó: định vị theo nội dung, không cộng độ lệch.
- Tìm theo thứ tự, dừng khi thấy (ghi cách tìm thấy vào `note`):

| # | Tìm ở đâu | Tìm gì | Cách |
|---|---|---|---|
| 1 | Đúng vị trí dự kiến | Dòng `-` + context, nguyên văn (bỏ khoảng trắng thừa) | `EXACT` |
| 2 | ±10 dòng quanh đó | Như trên | `EXACT` |
| 3 | ±10 dòng quanh đó | Chỉ khác tên, đạt 3c | `NEAR` |
| 4 | Cả đơn vị | Nguyên văn hoặc đạt 3c, **đúng một** ứng viên | `MOVED` |

- Không tìm thấy, hoặc ngoài vùng dự kiến có ≥ 2 ứng viên → `skipped` `QUESTION` (đưa dòng `-`, vị trí dự kiến, ứng viên).
- Dòng `-` lặp nhiều lần trong đơn vị: chọn theo vị trí dự kiến và context, không lấy chỗ đầu tiên.
- Các đoạn trong đơn vị phải giữ thứ tự trên–dưới như Before. Đảo thứ tự → `QUESTION`.
- Đoạn chỉ có `+`: tìm hai neo context (trên, dưới). Không thấy neo → `QUESTION`.

### 3b. Phân loại

| Vùng Target tìm được | Phân loại | Làm gì |
|---|---|---|
| Giống phía `-` (`EXACT`) | `CLEAN` | Chunk, `apply` = phía `+` |
| Giống phía `-` sau đổi tên đã chứng minh (đạt 3c) | `CLEAN` (đổi tên) | Chunk, `apply` = phía `+` đã đổi tên |
| Giống phía `+` (sau đổi tên), không còn phía `-` | `ALREADY_IN_TARGET` | `skipped`; vẫn kiểm phụ thuộc của nó ở Bước 6 |
| Còn lại (không đạt 3c) | `CONFLICT` | Chunk + câu hỏi (Bước 7), `base` = phía `-` |

- `TARGET_EQUIVALENT`: phía `+` (sau đổi tên) đã có nguyên văn trong cùng đơn vị Target nhưng ở chỗ khác, và có cùng tác dụng tại nơi dùng (`detail` ghi vị trí và lý do). Logic viết khác thì là `CONFLICT`, trừ khi người dùng đã xác nhận tương đương.

### 3c. Điều kiện "chỉ khác tên"

Bỏ khoảng trắng và comment, so từng token phía `-` với vùng Target:

1. Cấu trúc giống hệt: cùng số và thứ tự câu lệnh; từ khoá, toán tử, ngoặc, literal (số, chuỗi, ký tự) và **tên hàm được gọi** giống hệt.
2. Chỉ khác ở tên: biến cục bộ, tham số, global, field, macro, hằng enum.
3. Nhất quán 1-1: một tên Before ứng đúng một tên Target và ngược lại (trong đoạn và context).
4. Mỗi cặp tên **chứng minh** được theo bảng ở Bước 4. Nghe giống nhau (`idx`/`no`) là chưa đủ.

Không đạt một điều kiện → `CONFLICT`. Đoạn chỉ `+` mà giữa hai neo Target có dòng riêng → `CONFLICT`.

| # | Phía `-` (Before) | Target | Kết quả | Lý do |
|---|---|---|---|---|
| 1 | `retCode = GetX(idx);` | `ret = GetX(no);` (`idx`, `no` đều tham số #1, `UINT`) | `CLEAN` đổi tên | Cặp tên chứng minh được |
| 2 | `retCode = GetX(idx);` | `ret = GetX(no);`, `no = GetCurNo();` | `CONFLICT` | Khác nguồn |
| 3 | `GetX(idx)`, `idx = ITEM_ID`, `#define ITEM_ID 3` | `GetX(ID)`, `#define ID 3` | `CLEAN` đổi tên | Cùng giá trị cuối |
| 4 | Như #3 | `#define ID 5` | `CONFLICT` | Khác giá trị |
| 5 | `if (cnt > 5)` | `if (cnt > 10)` | `CONFLICT` | Khác literal |
| 6 | `if (a && b)` | `if (a \|\| b)` | `CONFLICT` | Khác toán tử |
| 7 | `GetX(idx);` | `GetXEx(idx);` | `CONFLICT` | Gọi hàm khác |
| 8 | `Init(); Run();` | `Init(); if (IsFom()) { Adj(); } Run();` | `CONFLICT` | FOMULAR có thêm logic |
| 9 | `Clear(buf); Send(buf);` | `Send(buf);` | `CONFLICT` | FOMULAR thiếu logic |
| 10 | `a = 1; b = 2;` | `b = 2; a = 1;` | `CONFLICT` | Đổi thứ tự |
| 11 | `retCode = GetX(i); if (retCode)` | `ret = GetX(i); if (retCode)` | `CONFLICT` | Đổi tên không nhất quán |
| 12 | Chỉ `+`, chèn giữa `Init();` và `Run();` | `Init(); Log(); Run();` | `CONFLICT` | Logic riêng giữa hai neo |

- Target thiếu phần lớn dòng `-` hoặc không xác định được dòng đầu/cuối vùng → `CONFLICT`.

### 3d. Đơn vị `NEW` và `DEL`

| Trường hợp | Làm gì |
|---|---|
| `NEW`, Target chưa có tên này (cùng file, header được include, cả Target) | Chunk chèn tại neo (Bước 5) |
| `NEW`, Target có, giống Latest | `skipped` `ALREADY_IN_TARGET` |
| `NEW`, Target có nhưng khác | `CONFLICT`: chunk thay định nghĩa Target bằng Latest + câu hỏi |
| `DEL`, Target không có X | `NOT_IN_TARGET` |
| `DEL`, Target có X giống Before, không còn chỗ dùng | Chunk `apply` = `""` |
| `DEL`, Target có X khác Before hoặc còn chỗ dùng | Chunk `apply` = `""` + câu hỏi |

## Bước 4 — Chốt `name_map`

Đọc: `<X>.before.c`, `<X>.target.c`, định nghĩa ở `request/Before/` và `target/`.

- Lập `name_map` **một lần cho mỗi file**, gồm mọi cặp đã chứng minh ở Bước 3 và mọi tên Before khác mà các dòng `+` dùng (Target không có tên đó → tìm tên tương ứng qua `<X>.ctx.diff`).
- Mỗi cặp `{from, to, proof}` phải đạt bảng sau:

| Loại tên | Cùng ý nghĩa khi | Xem ở đâu |
|---|---|---|
| Tham số | Cùng vị trí trong chữ ký và cùng kiểu | Chữ ký trong `before.c` và `target.c` |
| Biến cục bộ | Cùng kiểu **và** lần gán gần nhất phía trên lấy từ cùng nguồn (cùng hàm gọi, cùng tham số, cùng biểu thức/hằng) | Khai báo và lệnh gán trong hai bản cắt |
| Global / field | Cùng kiểu **và** khởi tạo/gán từ cùng nguồn | Định nghĩa ở Before và `target/` |
| Macro / hằng enum | Ra cùng một giá trị cuối | `#define`/`enum` ở Before và `target/` |

- Nguồn lại là một biến khác: kiểm tiếp biến đó, **tối đa 3 cấp**. Quá 3 cấp, không tìm được nguồn, nguồn khác, hoặc chỉ đoán theo tên → không đạt.
- **Ứng viên theo kiểu viết**: hai tên giống nhau khi bỏ `_` và không phân biệt hoa thường (`name_new` / `nameNew`) chỉ là **ứng viên để kiểm**, không được dùng khi chưa chứng minh.
- Tên do chính RT khai báo mới (dòng `+` có khai báo) giữ nguyên, không đưa vào `name_map`.
- Không chứng minh được → chunk dùng tên đó là `CONFLICT` + câu hỏi (cặp tên đề xuất ghi trong `evidence`).
- Áp `name_map` theo **token** (không thay chuỗi con) cho mọi `apply`. Ghi `proof` có tên đơn vị nếu là biến cục bộ.

Ví dụ: `{"from": "name_new", "to": "nameNew", "proof": "biến cục bộ LibCopyItem; cùng kiểu text[NAME_LEN]; cùng gán từ strcpy(…, itemName) dòng Before 41 / Target 44"}`.

## Bước 5 — Tạo chunk

Đọc: kết quả Bước 3–4, `target/<file>`.

- Mặc định mỗi đoạn thay đổi `CLEAN`/`CONFLICT` là một chunk. **Một chunk = một vùng liên tục của Target gốc.** Các chunk cùng file không chồng nhau.
- Giữ chung một chunk khi tách ra sẽ không tự đứng được (ngoặc `if {…}` mở ở đoạn này, đóng ở đoạn kia; một câu lệnh nhiều dòng). Tách tại dòng context khi mỗi phần tự đứng được.
- `target.text` = **nguyên văn** dòng `start..end` của Target gốc (đọc theo encoding của file, mỗi dòng kết thúc `\n`). Không gõ lại bằng tay.
- `apply` = code RT (phía `+` của diff (new)) đã áp `name_map`. Không có phương án lai nên **không ghi `rt`**. `base` = phía `-` khi chunk có câu hỏi hoặc Target khác Before.
- Đoạn chỉ `+`: chunk thay một dòng neo bằng "dòng neo + code mới" (hoặc "code mới + dòng neo").
- **Đơn vị `NEW`**: tìm dòng theo `Anchor:` trong Target (phải duy nhất).
  - `trước "L"`: `target` = dòng L; `apply` = code mới + dòng L.
  - `sau "L"` / `sau đơn vị Y`: `target` = dòng L / dòng cuối của Y; `apply` = dòng đó + code mới.
  - Giữ dòng trống ngăn cách như ở Latest. Hai thứ cùng một neo → gộp một chunk.
  - Target không có neo: chèn sau đơn vị đứng ngay trên ở Latest, hoặc trước đơn vị ngay dưới; vẫn không có thì theo loại (macro/global/kiểu/prototype: cuối nhóm cùng loại đầu file hoặc trong `.h`; `#include`: cuối nhóm include; hàm: cuối file). Ghi neo đã dùng vào `note`.

Ví dụ: helper `libLinkVarSet` có `Anchor: trước "/** EOF **/"`; Target dòng 270 là `/** EOF **/` → `target` = `{270, 270, "/** EOF **/\n"}`, `apply` = toàn bộ helper (từ dòng đầu comment) + dòng trống + `/** EOF **/\n`.

## Bước 6 — Phụ thuộc ở Target và `requires`

Đọc: `phase2/paused.md`, dòng `+` của các chunk, `target/`, `phase1/diff/` (định nghĩa trong code RT).

### 6a. Kiểm từng tên T (trong `paused.md` và tên các chunk dùng)

Tìm trong Target (cùng file, header được include, cả Target):

| Kết quả | Làm gì |
|---|---|
| Target có T, cùng chữ ký/kiểu/giá trị | Dừng. Giữ thân Target; không port khác biệt không thuộc feature |
| Target có T nhưng khác chữ ký/kiểu/giá trị | `NEED_CONFIRM`: câu hỏi trên chunk dùng T |
| Target không có T (macro, biến, kiểu) | Tạo chunk mang định nghĩa Latest (chèn như Bước 5). Trace tiếp vào trong T |
| Target không có T (hàm), code RT (`phase1/diff/`) có định nghĩa T | Tạo chunk mang định nghĩa Latest. Trace tiếp vào trong T |
| Target không có T (hàm), code RT không có định nghĩa T | Không mang, không trace vào T. `NEED_CONFIRM` "Cần khách hàng cung cấp source của function này", câu hỏi trên chunk **gọi** T |

- Trace vào T: mỗi tên con hỏi lại "Target có chưa?" theo cùng bảng. Mỗi định nghĩa xét một lần, ghi mọi chỗ dùng. Bỏ qua biến cục bộ, tham số, hàm thư viện chuẩn.
- Feature cần hợp đồng cụ thể (output qua con trỏ, ownership, side effect) mà chưa đủ bằng chứng ở Target → câu hỏi; không thay thân hàm Target.

### 6b. Ghi `requires`

- `X requires Y` khi X **dùng** thứ Y tạo ra: biến Y khai báo, hàm/prototype Y định nghĩa, giá trị/buffer Y gán hoặc cấp phát. Hoặc cùng ý đồ: `why` phải nêu cụ thể (ví dụ "giải phóng buffer do K2 cấp phát").
- Chiều luôn **chỗ dùng → chỗ định nghĩa**. Xuyên hunk, xuyên file.
- Mọi `why` nêu tên symbol/giá trị cụ thể. Không ghi "liên quan", "cùng hunk".
- **Không tạo cạnh** vì nằm gần, cùng hunk, cùng hàm, hay nằm dưới chunk có câu hỏi.
- Chunk không có cạnh nào tới chunk bị giữ thì được áp. Trạng thái `BLOCKED`/`FOLLOW` do tool tính (`schema/README.md` §4).

### Ví dụ (rút gọn)

```text
K1 LibCopyItem  khai báo nameNew, value_new
K2 LibCopyItem  nhánh mới: IfGetAllForce(...) rồi libLinkVarSet(...)
                         requires K1 (dùng nameNew, value_new), K3 (gọi helper), K4 (prototype)
K3 libLinkVarSet    helper mới, chèn trước "/** EOF **/"
K4 prototype libLinkVarSet
K5 LibCopyItem  MemRelease(value_new)   requires K2 (giải phóng buffer K2 cấp phát)
K6 LibCopyItem  case mới trong switch, không dùng gì của K1–K5 → không requires
Q1 IfGetAllForce: Target không có, code RT không có → "Cần khách hàng cung cấp source", chunks [K2]
```

| Q1 | K2 | K5 | K1, K3, K4 | K6 |
|---|---|---|---|---|
| Chưa trả lời | NEED_CONFIRM | BLOCKED (chờ K2) | FOLLOW | APPLIED |
| Chọn áp | APPLIED | APPLIED | APPLIED (kéo theo) | APPLIED |
| Chọn giữ Target | KEPT | BLOCKED | FOLLOW | APPLIED |

Sai đã gặp: chặn K1, K4, K6 vì nằm gần K2; ghi "K3 requires K2" (ngược chiều: helper không dùng gì của chỗ gọi).

## Bước 7 — Câu hỏi

Đọc: các chunk `CONFLICT` và `NEED_CONFIRM` của Bước 3–6.

- **Một câu hỏi cho một quyết định K.** Không hỏi lại cho chunk phụ thuộc (chúng tự thành `BLOCKED`/`FOLLOW`). Một chunk thuộc tối đa một câu hỏi.
- `text`: file, đơn vị, khác biệt cụ thể. `evidence`: vị trí, kết quả tìm kiếm, cặp tên chưa chứng minh.
- `options`: hai phương án, mỗi `label` nói rõ hệ quả:
  - **Áp** (`apply` = các chunk của câu hỏi): chunk nào sẽ được kéo theo qua `requires`, phụ thuộc nào còn thiếu, hành vi/logic FOMULAR nào bị thay.
  - **Giữ Target** (`apply` = `[]`): logic Target nào được giữ, phần feature nào chưa port.
- **Không tự tạo phương án lai** bằng cách chèn mọi phần khớp được. Chỉ khi người dùng tự yêu cầu sửa khác RT: `apply` = code người dùng duyệt, `rt` = code RT.
- `recommended`: tuỳ chọn, chỉ khi có lý do rõ.
- Vấn đề không gắn được chunk (không định vị được, file mơ hồ) → `skipped` `QUESTION`, câu hỏi trong `detail`; hỏi trong report.

## Bước 8 — Ghi `merge-plan.json`

Đọc: `schema/README.md`, `schema/merge-plan.schema.json`.

- Ghi đúng trường của schema. `src` chỉ hunk nguồn, ví dụ `P2 LibCopyItem -60,24 +67,81 (dòng +180..+226)`.
- Không ghi trạng thái vào plan; tool tự tính.

## Bước 9 — Ghép output và tạo trang duyệt

- Tạo `phase3/decisions.empty.json`: `{"rt": "<RT>", "answers": {}, "choices": {}}`.
- Chạy lệnh ghép (`SKILL.md`) với `--decisions WORK/<run-id>/phase3/decisions.empty.json --allow-pending`. Câu hỏi chưa trả lời giữ Target; chunk độc lập được áp. Lệnh in dòng `Trạng thái:` và từng chunk bị giữ kèm lý do: đó là nguồn cho mọi bảng trạng thái.
- **Changelog Target** (mỗi file có chunk APPLIED): một chunk `unit: "Modification"` trên khối `Modification:` của Target.
  - Copy ngày, người làm, mã RT từ phần `### Modification` của diff (new).
  - Chỉ liệt kê `Add.`/`Mod.` cho đơn vị có ít nhất một chunk APPLIED trong file đó. Không ghi phần bỏ qua, phần đang chờ.
  - Theo đúng định dạng khối `Modification:` của file Target (độ rộng cột, `#*/` cuối dòng, vị trí entry mới).
  - Sau mỗi lần `--apply`, cập nhật chunk này theo trạng thái tính được; file không còn chunk APPLIED nào khác → xoá chunk changelog. Ghép lại.
- Tạo `phase3/review.html` bằng lệnh tạo trang.
- Tool báo lỗi dữ liệu → sửa plan, chạy lại. Tool crash → `tool-gaps.md` (xem `SKILL.md`).

## Bước 10 — Kiểm tra, report, cổng

**10a. Plan khớp Target.** Tạo `phase3/decisions.all_target.json` (mọi chunk `choices` = `target`), ghép ra `WORK/<run-id>/phase3/check_all_target/`. Với mỗi file: `get_diff(check_all_target/<file>, target/<file>)` phải **trống**. Tool không báo lỗi kiểm tra nào (`schema/README.md` §6).

**10b. Output ↔ chunk.** Với mỗi file: `get_diff(target_out/<file>, target/<file>)` → `phase3/diff/<file>.diff`.
- Mỗi chunk APPLIED nằm trong đúng một hunk; mỗi hunk chứa ít nhất một chunk APPLIED (chunk APPLIED liền nhau có thể chung hunk). Hunk không có chunk, hoặc chunk APPLIED không thấy trong diff → sai, sửa plan.

**10c. Độ phủ P2→P3.** Bảng: mỗi hunk của diff (new) (trừ phần `Modification`) → chunk `K…`, hoặc `skipped` (lý do), hoặc `NOT_IN_TARGET`/`NO_FILE` ở "Bỏ qua". Mỗi tên trong `paused.md` → "Target có" / chunk / câu hỏi.

**Report** `phase3/REPORT.md` theo `templates/report.md`, thêm:
- Bảng trạng thái chunk **lấy từ kết quả tool** (không tự viết): `| K | File | Đơn vị | Tóm tắt | Trạng thái | Chờ chunk / câu hỏi |`.
- `name_map` từng file kèm `proof`.
- Câu hỏi: id, chunk, bằng chứng, hệ quả từng phương án.
- Kết quả kiểm `paused.md` (Bước 6a), đơn vị mới đã chèn (neo, dòng Target).
- Đường dẫn `review.html`, `target_out/`, `phase3/diff/`.

**Cổng Phase 3:**

| # | Kiểm tra | Đạt khi |
|---|---|---|
| 1 | 10a: file có diff khác trống khi giữ toàn Target; lỗi kiểm tra của tool | `0` và `0` |
| 2 | 10b: hunk không có chunk / chunk APPLIED không có trong diff | `0` / `0` |
| 3 | 10c: hunk diff (new) có nơi nhận | `N/N` |
| 4 | `from` trong `name_map` còn sót trong `apply` của chunk cùng file (grep theo token) | `0` |
| 5 | Ứng viên theo kiểu viết chưa chứng minh mà đã dùng | `0` |
| 6 | `requires` có `why` nêu symbol/giá trị cụ thể | `n/n` |
| 7 | `requires` ngược chiều (định nghĩa → chỗ dùng) | `0` |
| 8 | Câu hỏi "cần source" đặt trên chunk **gọi** hàm thiếu, không đặt trên khai báo/helper/prototype | `n/n` |
| 9 | Đơn vị NEW có chunk chèn tại neo hoặc có trong `skipped` | `n/n` |
| 10 | Câu hỏi có đủ 2 phương án, mỗi chunk thuộc ≤ 1 câu hỏi | `n/n` |
| 11 | Encoding/xuống dòng `target_out` giống Target | `n/n` file |
| 12 | Chunk changelog chỉ liệt kê đơn vị có chunk APPLIED; file không có chunk APPLIED thì không có chunk changelog | `n/n` file |

- Không có môi trường build: ghi "chưa compile" ở Cảnh báo.
- Báo người dùng: số chunk theo trạng thái, số câu hỏi, đường dẫn `review.html`. Câu hỏi `skipped` `QUESTION` trả lời trong chat; trả lời xong quay lại Bước 3. Dừng, sang Phase 4.
