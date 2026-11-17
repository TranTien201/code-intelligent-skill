# Phase 3 — Merge feature vào FOMULAR

Mục tiêu:
- Đưa feature mới nhất (kết quả Phase 2) vào bản copy của Target (`WORK/target_out/`).
- Kiểm tra danh sách tạm dừng của Phase 2 với FOMULAR. FOMULAR thiếu thứ gì thì mang sang và trace tiếp.
- Giữ lại code riêng của FOMULAR. Chỗ nào không chắc thì hỏi, không ghi đè.
- Đầu vào: `WORK/phase2/diff/`, `WORK/phase2/fn/`, `WORK/phase2/paused.md`, `WORK/phase2/REPORT.md` (đã có câu trả lời của người dùng).

## Tóm tắt luồng

```text
Bước 1. Chuẩn bị: ghép file TELINDY ↔ FOMULAR, copy file Target vào WORK/target_out/

Bước 2. Với mỗi đơn vị X trong diff Phase 2, so 3 phiên bản của X:
          Before (gốc TELINDY) | Latest (kết quả Phase 2) | Target (FOMULAR)
   ├─ Target không có X
   │     ├─ X là mới (Add, DEP_NEW, RENAMED mà Target cũng không có X) → thêm (Bước 4) → MERGED_NEW
   │     ├─ X là DEP_CHANGED                                           → thêm bản Latest → MERGED_DEP
   │     └─ X là sửa hàm có sẵn (KEEP / UPDATE_LATEST)                 → SKIP_NOT_IN_TARGET
   ├─ Target giống Latest  → SKIP_EXISTS
   ├─ Target giống Before  → thay nguyên X bằng bản Latest → MERGED
   └─ Target khác cả hai   → FOMULAR có code riêng
         ├─ phần riêng FOMULAR và phần thay đổi của feature KHÔNG chồng nhau → áp cả hai → MERGED_KEEP_TARGET
         └─ có chồng nhau → NEED_CONFIRM (đưa cả 3 phiên bản), không ghi đè

   Riêng:
   - DELETE  → Target có, giống Before, không còn nơi gọi → xoá → DELETED; còn lại NEED_CONFIRM hoặc SKIP_NOT_IN_TARGET
   - RENAMED → Target còn tên cũ X → thay bằng Y; Target còn nơi khác gọi X → NEED_CONFIRM

Bước 3. Xử lý danh sách tạm dừng (paused.md) — trace tiếp với FOMULAR
   Với mỗi tên T:
   ├─ FOMULAR có T, cùng chữ ký / kiểu / giá trị → dừng hẳn → SKIP_EXISTS
   ├─ FOMULAR có T nhưng khác chữ ký / kiểu / giá trị → NEED_CONFIRM
   └─ FOMULAR KHÔNG có T → lấy T từ Latest mang sang → MERGED_DEP
                          → trace tiếp vào trong T, mỗi tên con lại hỏi: FOMULAR có chưa?
                              có → dừng | không có → mang sang, trace tiếp | khác chữ ký → NEED_CONFIRM

Bước 4. Chèn đơn vị mới vào đúng chỗ (theo symbol neo)
Bước 5. Ghi changelog RT vào Target
Bước 6. Kiểm tra cuối
Bước 7. Report + câu hỏi → DỪNG chờ xác nhận
```

Phần dưới là chi tiết từng bước.

---

## Bước 1 — Chuẩn bị

- Ghép mỗi file TELINDY với file FOMULAR:
  - Tìm theo **cùng đường dẫn tương đối** trong `target/`.
  - Không thấy: tìm theo **cùng tên file** trong toàn bộ `target/`.
  - Có nhiều ứng viên: `NEED_CONFIRM`.
  - Không có file nào:
    - File `added` của RT hoặc file chỉ chứa phụ thuộc mới: tạo file mới theo cùng đường dẫn tương đối, ghi vào report.
    - Trường hợp khác: `SKIP_NO_FILE`, ghi vào "Bỏ qua".
- Copy các file Target liên quan vào `WORK/target_out/`, giữ cấu trúc thư mục. Chỉ sửa trên bản copy.
- Với mỗi đơn vị X, tìm X trong file Target và cắt ra `WORK/phase3/fn/<file>/<X>.target.c` (cách cắt giống Phase 2, Bước 3 "Lưu bản cắt của hàm"). Ghi khoảng dòng.

## Bước 2 — So 3 phiên bản và merge từng đơn vị

- So sánh bằng `get-diff`. Diff trống (hoặc chỉ khác khoảng trắng) nghĩa là giống nhau.
  - `get-diff(<X>.target.c, <X>.latest.c)`: Target có giống Latest không.
  - `get-diff(<X>.target.c, <X>.before.c)`: Target có giống Before không.

### 2.1 Bảng quyết định

| Trường hợp | Xử lý | Kết quả |
|---|---|---|
| Target giống Latest | Không làm gì | `SKIP_EXISTS` |
| Target giống Before | Thay nguyên X bằng bản Latest | `MERGED` |
| Target khác cả Before và Latest | Làm theo mục 2.2 | `MERGED_KEEP_TARGET` hoặc `NEED_CONFIRM` |
| Target không có X, X là `Add` / `DEP_NEW` | Thêm bản Latest (Bước 4) | `MERGED_NEW` |
| Target không có X, X là `DEP_CHANGED` | Vẫn thêm bản Latest, vì code đã merge cần nó | `MERGED_DEP` |
| Target không có X, X là `KEEP` / `UPDATE_LATEST` (sửa hàm có sẵn) | Không merge | `SKIP_NOT_IN_TARGET` |
| Target có X cùng tên nhưng khác chữ ký / kiểu | Không merge | `NEED_CONFIRM` |

### 2.2 Target có code riêng (khác cả Before và Latest)

- Bước 1: `get-diff(<X>.target.c, <X>.before.c)` → phần **riêng của FOMULAR**.
- Bước 2: `get-diff(<X>.latest.c, <X>.before.c)` → phần **thay đổi của feature**.
- Bước 3: so vị trí các block của hai diff (theo số dòng phía Before, tức số dòng ở dòng `@@ -...`).
  - Không có block nào chồng nhau: áp phần thay đổi của feature vào bản Target, giữ nguyên phần riêng của FOMULAR. Ghi rõ đã giữ những gì.
  - Có block chồng nhau: **không ghi đè**. Ghi `NEED_CONFIRM`, đưa cả 3 phiên bản (Before / Latest / Target) của đoạn chồng nhau và đề xuất.

### 2.3 Các nhãn đặc biệt

- **`DELETE`** (đơn vị RT đã xoá):
  - Target không có: `SKIP_NOT_IN_TARGET`.
  - Target có, giống Before, và grep trong `target_out/` không còn nơi nào gọi: xoá. Ghi `DELETED`.
  - Target có code riêng, hoặc còn nơi khác gọi: `NEED_CONFIRM`.
- **`RENAMED` X→Y** (dùng tên Latest là Y):
  - Target có Y: xử lý như bảng 2.1 với Y.
  - Target có X (tên cũ): coi X ở Target là bản Target, so 3 phiên bản như bảng 2.1, kết quả ghi với tên Y.
  - Target còn nơi khác (ngoài phạm vi RT) gọi X: `NEED_CONFIRM`, không tự đổi các nơi gọi đó.
- **`NOT_PORTED`** và `DELETE` do TH2: không làm gì (đã nằm trong "Bỏ qua" của Phase 2).

---

## Bước 3 — Xử lý danh sách tạm dừng (trace tiếp với FOMULAR)

### Hiểu đúng trước khi làm

- Ở Phase 2, những thứ **giống hệt Before** (đồ cũ, có từ trước RT) được **tạm dừng**, không đi sâu. Lý do: nếu đi sâu vào mọi hàm dùng chung thì sẽ lan ra cả source.
- Phase 2 chỉ **đoán** rằng FOMULAR đã có đồ cũ, vì Before là của TELINDY chứ không phải của FOMULAR. Bước này **kiểm tra thật** với FOMULAR.
- Đồ cũ mà feature gọi tới **vẫn là thứ feature cần**. FOMULAR thiếu thì phải mang sang, nếu không code đã merge sẽ lỗi compile.
- Từ bước này, mốc so sánh là **FOMULAR** (`target_out/`), không còn là Before nữa. Câu hỏi ở mỗi tên chỉ là: **"FOMULAR đã có chưa?"**

### Cách làm

- Đọc `WORK/phase2/paused.md`. Với mỗi tên T, tìm định nghĩa của T trong `target_out/` (cùng file trước, sau đó các file `.h` được `#include`, cuối cùng toàn bộ `target_out/`).

| Kết quả | Xử lý | Kết quả ghi |
|---|---|---|
| FOMULAR có T, cùng chữ ký (hàm) / cùng kiểu (biến, struct) / cùng giá trị (macro) | Dừng hẳn. Nếu thân hàm khác thì đó là bản riêng của FOMULAR, giữ nguyên, vì feature không sửa gì T | `SKIP_EXISTS` |
| FOMULAR có T nhưng khác chữ ký / kiểu / giá trị | Không sửa. Đưa bản TELINDY (Latest) và bản FOMULAR để hỏi | `NEED_CONFIRM` |
| FOMULAR không có T | Lấy định nghĩa T ở Latest mang sang (hàm thì lấy cả prototype), chèn theo Bước 4. Rồi **trace tiếp vào trong T** | `MERGED_DEP` |

- **Trace tiếp vào trong T** dùng cùng cách lần theo như Phase 2 Bước 3 (hàm được gọi, biến, macro, kiểu, field...). Chỉ khác ở mốc so sánh. Với mỗi tên con:
  - FOMULAR có, cùng chữ ký / kiểu / giá trị: dừng.
  - FOMULAR không có: mang sang từ Latest, rồi trace tiếp vào trong nó.
  - FOMULAR có nhưng khác chữ ký / kiểu / giá trị: `NEED_CONFIRM`.
- Mỗi tên chỉ xét một lần, kể cả các tên đã xử lý ở Bước 2. Dừng khi không còn tên mới.
- Bỏ qua biến cục bộ, tham số và hàm thư viện chuẩn / hệ thống.

### Ví dụ

```text
paused.md: RcpIfGetAllVari, RCP_NAME_LEN, rcpVarCheck, LogPrint

 ├─ RcpIfGetAllVari → FOMULAR có, cùng chữ ký        → SKIP_EXISTS (dừng hẳn)
 ├─ LogPrint        → FOMULAR có, thân hàm khác       → SKIP_EXISTS (bản riêng FOMULAR, giữ nguyên)
 ├─ RCP_NAME_LEN    → FOMULAR có nhưng giá trị 16≠32  → NEED_CONFIRM
 └─ rcpVarCheck     → FOMULAR KHÔNG có                → MERGED_DEP, trace tiếp vào trong:
       ├─ rcpVarTbl[]   → FOMULAR không có → MERGED_DEP, trace tiếp vào định nghĩa
       │    └─ RCP_VAR_MAX → FOMULAR có, cùng giá trị → dừng
       └─ LogPrint      → đã xét → bỏ qua
```

---

## Bước 4 — Chèn đơn vị mới vào đúng chỗ

- Áp dụng cho mọi thứ được thêm mới vào Target ở Bước 2 và Bước 3.
- Tìm **symbol neo**: symbol nằm ngay **phía trên** X trong file Latest.
  - Target có neo: chèn X ngay sau neo.
  - Target không có: thử symbol nằm ngay **phía dưới** X ở Latest, chèn X ngay trước nó.
  - Vẫn không có: chèn vào vùng tương ứng:
    - Macro: sau nhóm `#define` cuối cùng ở đầu file.
    - Biến global / static: sau nhóm khai báo biến ở đầu file.
    - Kiểu (`struct`, `typedef`): trong file `.h` tương ứng hoặc nhóm khai báo kiểu ở đầu file.
    - Prototype: trong file `.h` tương ứng hoặc nhóm prototype ở đầu file `.c`.
    - Hàm: cuối file.
- Hàm mới có prototype trong `.h` ở Latest: thêm cả prototype vào `.h` tương ứng của Target.
- Ghi vị trí đã chèn (file, dòng, neo) vào report.

## Bước 5 — Ghi changelog vào Target

- Với mỗi file Target đã sửa, thêm entry RT vào khối `Modification:`.
- Copy entry RT gốc (ngày, người làm, mã RT) từ block changelog trong diff Phase 2.
- **Chỉ liệt kê `Add.` / `Mod.` cho những gì đã thực sự thêm/sửa trong file đó.** Không ghi những mục `SKIP`, `NEED_CONFIRM` chưa trả lời.
- Viết theo đúng định dạng sẵn có của khối `Modification:` trong file Target (độ rộng cột, ký tự `#*/` cuối dòng, vị trí đặt entry).

## Bước 6 — Kiểm tra cuối

- Mọi file ở Phase 1 đều có kết quả cuối: `done`, `skipped` (có lý do) hoặc `blocked` (có lý do).
- Mọi tên trong bảng phụ thuộc Phase 2, trong `paused.md`, và mọi tên mang thêm ở Bước 3 đều có định nghĩa trong `target_out/` (grep lại từng tên).
- Prototype khớp với định nghĩa hàm.
- Không còn nơi nào gọi tới hàm đã xoá.
- Encoding và kiểu xuống dòng của file trong `target_out/` giống file Target gốc.
- Có môi trường build thì compile thử. Không có thì ghi rõ "chưa compile".

## Bước 7 — Report, thông báo và dừng

- Với mỗi file đã sửa: gọi `get-diff(target_out/<file>, target/<file>)`, lưu vào `WORK/phase3/diff/<đường dẫn file>.diff` để người duyệt xem.
- Ghi `WORK/phase3/REPORT.md` theo mẫu trong `SKILL.md`:
  - "Đã xử lý": từng đơn vị, kết quả (`MERGED`, `MERGED_NEW`, `MERGED_KEEP_TARGET`, `MERGED_DEP`, `DELETED`), vị trí trong `target_out/`, ghi chú.
  - "Danh sách tạm dừng": từng tên trong `paused.md` và kết quả kiểm tra với FOMULAR. Với tên được mang sang thì vẽ cây trace tiếp như ví dụ ở Bước 3.
  - "Bỏ qua": các `SKIP` kèm lý do.
  - "Cần xác nhận": kèm 3 phiên bản code khi có chồng nhau, hoặc bản TELINDY và bản FOMULAR khi khác chữ ký / kiểu / giá trị.
  - "Cảnh báo": kết quả kiểm tra cuối, "chưa compile" nếu không build.
- Báo cho người dùng: đường dẫn report, đường dẫn `target_out/`, đường dẫn các diff ở `WORK/phase3/diff/`, số lượng từng kết quả.
- Hỏi người dùng từng mục "Cần xác nhận". Áp dụng câu trả lời vào `target_out/` và cập nhật report.
- Không báo "hoàn tất" khi còn mục chưa được trả lời.
