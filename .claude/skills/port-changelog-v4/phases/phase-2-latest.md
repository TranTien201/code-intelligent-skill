# Phase 2 — Đưa feature lên bản mới nhất (Latest)

Mục tiêu:
- Code của RT lấy ở thời điểm làm RT đã cũ. Sau đó có thể có RT khác sửa tiếp.
- Phase này đưa từng đơn vị của RT lên **trạng thái Latest**, và mang theo **mọi** hàm/biến/macro mà code mới nhất cần.
- Đầu vào: `WORK/phase1/units.md`, các diff ở `WORK/phase1/diff/`.

## Tóm tắt luồng

```text
Với mỗi đơn vị X trong units.md (hàm / macro / biến / kiểu):

Bước 1. Đọc changelog Latest: X có bị "Mod." bởi RT nào về sau không?
Bước 2. Tìm X trong file Latest
        ├─ Thấy ─────────► TH1
        └─ Không thấy ───► TH2

TH1 — Có X ở Latest
  1A. Không có Mod. về sau → KEEP (dùng block Before-After, không kiểm tra thêm) → Bước 3
  1B. Có Mod. về sau       → lấy NGUYÊN X ở Latest (UPDATE_LATEST)                → Bước 3

TH2 — Không có X ở Latest (bị đổi tên hoặc bị xoá)
  Lấy các dòng code đặc trưng của RT trong X → tìm trong file Latest
    ├─ Đúng 1 hàm khớp ≥ 80%     → RENAMED X→Y, lấy nguyên Y → Bước 3
    ├─ ≥ 2 hàm cùng khớp ≥ 80%   → NEED_CONFIRM (liệt kê ứng viên)
    ├─ Khớp 40–80%               → NEED_CONFIRM (có phải đổi tên?)
    └─ Dưới 40% / không thấy     → DELETE, loại X khỏi feature

Bước 3. Khám phá đệ quy (BẮT BUỘC cho mọi đơn vị còn giữ lại)
  Lần theo mọi hàm được gọi và mọi thứ định nghĩa ngoài hàm (biến, macro, kiểu...),
  rồi lần tiếp vào bên trong chúng cho đến hết.
  Mỗi tên: so định nghĩa Latest với Before
    → mới / đã đổi: mang theo, lần tiếp vào trong
    → giống hệt: DEP_EXISTING, dừng

Bước 4. Ghi diff feature mới nhất cho từng file
Bước 5. Report + câu hỏi → DỪNG chờ xác nhận
```

Phần dưới là chi tiết từng bước.

---

## Bước 1 — Đọc changelog Latest

- Với mỗi file trong danh sách Phase 1, mở file đó trong `source/` và đọc khối `Modification:`.
- Tìm entry của RT đang port.
- **Các entry nằm PHÍA TRÊN entry RT là các RT mới hơn.** Xác định theo vị trí trong log, không theo ngày.
- Với mỗi đơn vị X: xem các entry mới hơn có ghi `Mod. X` không.
  - Có: ghi lại mã RT đã sửa, ví dụ "RT2343 Mod".
  - Không: ghi "không có Mod về sau".
- Ví dụ với RT2486:

| Đơn vị | Entry mới hơn có Mod? |
|---|---|
| `ArtLibGetRecipeData` | Có — RT2343 |
| `ArtLibEntryRecipeName` | Có — RT2611 |
| `ArtLibCopyRecipeName` | Có — RT2707 |
| `ArtLibPutOsfData` | Không |

## Bước 2 — Tìm X ở Latest và quyết định

- Tìm **định nghĩa** của X trong cùng file ở `source/` (không phải chỗ gọi X).
  - Hàm: dòng chữ ký hàm có thân `{ ... }`.
  - Macro: `#define X`.
  - Biến / kiểu: dòng khai báo ngoài hàm.

### Trường hợp 1 — Có X ở Latest

- **1A. Không có `Mod.` về sau**
  - Gắn nhãn `KEEP`.
  - Dùng đúng block của X trong diff Before-After. Không gọi `get-diff` để kiểm tra lại.
  - Sang Bước 3.
- **1B. Có `Mod.` về sau**
  - Gắn nhãn `UPDATE_LATEST`, ghi RT nào đã sửa.
  - Lấy **nguyên** X ở Latest. Mọi dòng thêm, sửa, bỏ về sau đều theo Latest, không lọc theo RT.
  - Sang Bước 3.
- **Đơn vị `Del`** (RT đã xoá X):
  - Latest cũng không có X: `DELETE` (giữ việc xoá). Không cần khám phá.
  - Latest **có lại** X: `NEED_CONFIRM`.

### Trường hợp 2 — Không có X ở Latest

- Chỉ xét hai khả năng: **đổi tên** hoặc **bị xoá**.
- Bước 2.1 — Lấy các dòng đặc trưng của RT trong X:
  - X là `Mod`: các dòng `+` của X trong diff Before-After.
  - X là `Add`: toàn bộ thân X ở After.
  - Bỏ các dòng chung chung: `{`, `}`, `return ...;` đơn giản, `break;`, `else`, dòng trống, comment.
  - Ghi danh sách dòng đặc trưng vào report.
- Bước 2.2 — Tìm trong file Latest:
  - So từng dòng sau khi bỏ khoảng trắng thừa.
  - Với mỗi hàm ở Latest có chứa dòng khớp: **tỷ lệ khớp = số dòng đặc trưng tìm thấy trong hàm đó / tổng số dòng đặc trưng**.
- Bước 2.3 — Quyết định:

| Kết quả | Xử lý | Nhãn |
|---|---|---|
| Đúng 1 hàm Y khớp ≥ 80% | Coi X đã đổi tên thành Y. Lấy nguyên Y ở Latest. Sang Bước 3 | `RENAMED` |
| Từ 2 hàm trở lên khớp ≥ 80% | Không tự chọn (có thể hàm bị tách). Liệt kê ứng viên và tỷ lệ | `NEED_CONFIRM` |
| Có hàm khớp 40–80% | Hỏi có phải đổi tên không | `NEED_CONFIRM` |
| Dưới 40% hoặc không thấy | Coi là đã xoá. Loại X khỏi diff feature, không merge sang FOMULAR | `DELETE` |

- X là macro/biến/kiểu không tìm thấy: tìm định nghĩa có cùng giá trị hoặc cùng kiểu trong file Latest. Có thì `NEED_CONFIRM`, không có thì `DELETE`.
- Trong report phải ghi **từng dòng đặc trưng và nó khớp với dòng nào (số dòng) trong hàm ứng viên**, để người duyệt kiểm lại tỷ lệ.

---

## Bước 3 — Khám phá đệ quy (tracing)

- **Bắt buộc** cho mọi đơn vị có nhãn `KEEP`, `UPDATE_LATEST`, `RENAMED`.
- Mục tiêu: lấy ra **đủ mọi thứ** mà code mới nhất của RT cần để chạy đúng trên FOMULAR. Thiếu một thứ là FOMULAR lỗi compile hoặc chạy sai.

### Cần lần theo những gì

- **Hàm được gọi:** hàm X gọi hàm nào thì đọc tiếp hàm đó. Hàm đó lại gọi hàm nào nữa thì đọc tiếp. Cứ thế cho đến hết.
- **Những thứ định nghĩa bên ngoài hàm** mà code dùng tới: biến global / `static` / `extern`, macro, `enum`, `struct` / `typedef` (và field được dùng), prototype.
- **Những thứ mà chính các định nghĩa đó dùng**, ví dụ kích thước mảng là một macro, field có kiểu là một struct khác.

### Mỗi tên tìm được thì xử lý thế nào

- Tìm định nghĩa ở Latest, rồi so với Before:

| Kết quả | Nhãn | Làm gì tiếp |
|---|---|---|
| Before chưa có | `DEP_NEW` | Mang định nghĩa Latest (hàm thì lấy cả prototype). Lần tiếp vào bên trong |
| Before có, Latest đã đổi | `DEP_CHANGED` | Mang bản Latest. Lần tiếp vào phần đã đổi |
| Giống hệt Before | `DEP_EXISTING` | Không cần lần sâu. Phase 3 chỉ kiểm tra Target đã có chưa |
| Không tìm thấy định nghĩa | `UNRESOLVED` | Ghi vào "Cần xác nhận" |
| Thấy ở nhiều chỗ, không biết chỗ nào đúng | `NEED_CONFIRM` | Ghi vào "Cần xác nhận", đưa các vị trí |

### Lưu ý khi lần theo

- Chỉ đi xuôi: từ hàm của RT đi vào bên trong. Không tìm ngược "ai đang gọi hàm này".
- Mỗi tên chỉ xét một lần. Dừng khi không còn tên mới.
- Bỏ qua biến cục bộ, tham số và hàm thư viện chuẩn / hệ thống (`memcpy`, `strcpy`, `printf`...).
- Đừng chỉ đọc các dòng đã thay đổi. Tên nằm ở dòng không đổi vẫn có thể có định nghĩa đã bị RT sau sửa (ví dụ macro đổi giá trị, mảng đổi kích thước).
- Gợi ý: với hàm có ở cả After và Latest, có thể `get-diff` riêng hàm đó để thấy nhanh Latest gọi thêm / bỏ đi những gì, rồi bắt đầu lần theo từ đó.
- Hàm do RT thêm (`Add`) mà ở Latest không còn nơi nào gọi: gắn `NOT_PORTED`, ghi vào "Bỏ qua".
- Toàn bộ code của RT trong hàm không còn ở Latest (có thể RT đã bị gỡ): gắn `NEED_CONFIRM`.
- Phụ thuộc nằm ở file khác: vẫn ghi diff cho file đó ở Bước 4, ghi rõ trong report là file được thêm vì phụ thuộc.
- Không hỏi người dùng chỉ vì Latest gọi thêm hàm hoặc dùng thêm biến mới.

### Lưu bản cắt của hàm

- Với mỗi đơn vị và mỗi phụ thuộc mang theo, cắt phần định nghĩa (hàm: từ dòng chữ ký tới dấu `}` đóng hàm) ra file:
  - `WORK/phase2/fn/<file>/<tên>.before.c` (nếu Before có)
  - `WORK/phase2/fn/<file>/<tên>.after.c` (nếu After có)
  - `WORK/phase2/fn/<file>/<tên>.latest.c` (với `RENAMED`: dùng thân hàm mới)
- Ghi khoảng dòng gốc vào report. Các file này dùng cho Bước 4 và Phase 3.

### Ví dụ

```text
ArtLibCopyRecipeName  (RT2707 Mod về sau → UPDATE_LATEST)
 ├─ artLibLinkOnVarSet()      → Before chưa có → DEP_NEW → đọc tiếp vào trong
 │    ├─ g_varLinkTbl[]       → Before chưa có → DEP_NEW
 │    │    └─ VAR_LINK_MAX    → Before chưa có → DEP_NEW (kích thước mảng)
 │    └─ RcpIfGetAllVari()    → giống Before   → DEP_EXISTING
 └─ RCP_NAME_LEN              → giống Before   → DEP_EXISTING
```

---

## Bước 4 — Ghi diff feature mới nhất

- Mỗi file ghi một diff: `WORK/phase2/diff/<đường dẫn file>.diff`. Đây là đầu vào của Phase 3.
- Diff gồm nhiều block, mỗi đơn vị một block. **Phía trên mỗi block ghi một dòng chú thích:**

```text
### <tên đơn vị> | <nhãn> | Before: <dòng> | Latest: <dòng> | <ghi chú, ví dụ: RT2343 Mod>
```

- Nội dung block theo nhãn:

| Nhãn | Nội dung block |
|---|---|
| `KEEP` | Copy block của đơn vị từ diff Before-After ở Phase 1 |
| `UPDATE_LATEST`, `DEP_CHANGED` | `get-diff(<X>.latest.c, <X>.before.c)` |
| `RENAMED` | `get-diff(<Y>.latest.c, <X>.before.c)` (X là `Add` thì toàn bộ Y là `+`) |
| `DEP_NEW`, đơn vị `Add` | Toàn bộ định nghĩa Latest là `+` |
| `DELETE` của đơn vị `Del` | Toàn bộ định nghĩa Before là `-` |
| `DELETE` do TH2, `NOT_PORTED` | Không có block, chỉ ghi vào report |
| `DEP_EXISTING` | Không có block, chỉ ghi vào bảng phụ thuộc trong report |

- Thêm một block cho entry RT trong khối `Modification:` (lấy từ diff Phase 1), để Phase 3 ghi changelog cho Target.
- File `added` ở Phase 1: toàn bộ nội dung file ở Latest là `+`.
- File `deleted` ở Phase 1: ghi `DELETE` cho cả file.

## Bước 5 — Report, thông báo và dừng

- Ghi `WORK/phase2/REPORT.md` theo mẫu trong `SKILL.md`, thêm các phần sau:
  - **Bảng đơn vị**: đơn vị, nhãn, RT đã sửa về sau, khoảng dòng ở After và Latest.
  - **Cây phụ thuộc**: như ví dụ ở Bước 3.
  - **Bảng phụ thuộc**:

```markdown
| Tên | Loại | Tìm ra từ (hàm nào dùng nó) | Định nghĩa ở Latest (file:dòng) | So với Before | Nhãn |
|---|---|---|---|---|---|
```

  - **TH2**: với mỗi đơn vị không tìm thấy, ghi các dòng đặc trưng, các ứng viên, từng dòng khớp với dòng nào, tỷ lệ khớp và quyết định.
  - **Bỏ qua**: `DELETE`, `NOT_PORTED`, kèm lý do.
  - **Cần xác nhận**: mọi mục `NEED_CONFIRM`, `UNRESOLVED`, tên có nhiều định nghĩa.
- Báo cho người dùng: đường dẫn report, đường dẫn các diff mới nhất, số lượng từng nhãn.
- Hỏi người dùng từng mục "Cần xác nhận". Ghi câu trả lời vào report và cập nhật lại diff ở Bước 4 nếu cần.
- Dừng, chờ người dùng xác nhận rồi mới sang Phase 3.
