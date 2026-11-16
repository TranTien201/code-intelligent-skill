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
  1A. Không có Mod. về sau → KEEP (dùng block Before-After, không kiểm tra thêm)
                             → Bước 3 khám phá, TẦNG 2
  1B. Có Mod. về sau       → lấy NGUYÊN X ở Latest (UPDATE_LATEST)
                             → Bước 3 khám phá, TẦNG 1

TH2 — Không có X ở Latest (bị đổi tên hoặc bị xoá)
  Lấy các dòng code đặc trưng của RT trong X → tìm trong file Latest
    ├─ Đúng 1 hàm khớp ≥ 80%     → RENAMED X→Y, lấy nguyên Y → Bước 3 khám phá, TẦNG 1
    ├─ ≥ 2 hàm cùng khớp ≥ 80%   → NEED_CONFIRM (liệt kê ứng viên)
    ├─ Khớp 40–80%               → NEED_CONFIRM (có phải đổi tên?)
    └─ Dưới 40% / không thấy     → DELETE, loại X khỏi feature

Bước 3. Khám phá bên trong (BẮT BUỘC cho mọi đơn vị còn giữ lại)
  TẦNG 1 (X có ở cả After và Latest, và đã thay đổi):
    get-diff riêng cho hàm → tên mới (+) điều tra sâu
                           → tên bị bỏ (-) kiểm tra hàm không còn ai gọi
                           → tên ở dòng không đổi: quét nhẹ
  TẦNG 2 (các trường hợp còn lại):
    đọc toàn bộ thân hàm / định nghĩa → điều tra mọi tên
  Điều tra 1 tên: tìm định nghĩa ở Latest → so với Before
    → MỚI / ĐÃ ĐỔI: mang theo, đi tiếp vào bên trong (đệ quy)
    → giống hệt: DEP_EXISTING, dừng
  Dừng khi không còn tên mới.

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

### TH1 — Có X ở Latest

- **1A. Không có `Mod.` về sau**
  - Gắn nhãn `KEEP`.
  - Dùng đúng block của X trong diff Before-After. Không gọi `get-diff` để kiểm tra lại.
  - Sang Bước 3, **tầng 2**.
- **1B. Có `Mod.` về sau**
  - Gắn nhãn `UPDATE_LATEST`, ghi RT nào đã sửa.
  - Lấy **nguyên** X ở Latest. Mọi dòng thêm, sửa, bỏ về sau đều theo Latest, không lọc theo RT.
  - Sang Bước 3, **tầng 1**.
- **Đơn vị `Del`** (RT đã xoá X):
  - Latest cũng không có X: `DELETE` (giữ việc xoá). Không cần khám phá.
  - Latest **có lại** X: `NEED_CONFIRM`.

### TH2 — Không có X ở Latest

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
| Đúng 1 hàm Y khớp ≥ 80% | Coi X đã đổi tên thành Y. Lấy nguyên Y ở Latest. Sang Bước 3, tầng 1 (so Y ở Latest với X ở After) | `RENAMED` |
| Từ 2 hàm trở lên khớp ≥ 80% | Không tự chọn (có thể hàm bị tách). Liệt kê ứng viên và tỷ lệ | `NEED_CONFIRM` |
| Có hàm khớp 40–80% | Hỏi có phải đổi tên không | `NEED_CONFIRM` |
| Dưới 40% hoặc không thấy | Coi là đã xoá. Loại X khỏi diff feature, không merge sang FOMULAR | `DELETE` |

- X là macro/biến/kiểu không tìm thấy: tìm định nghĩa có cùng giá trị hoặc cùng kiểu trong file Latest. Có thì `NEED_CONFIRM`, không có thì `DELETE`.
- Trong report phải ghi **từng dòng đặc trưng và nó khớp với dòng nào (số dòng) trong hàm ứng viên**, để người duyệt kiểm lại tỷ lệ.

---

## Bước 3 — Khám phá bên trong (đệ quy)

- **Bắt buộc** cho mọi đơn vị có nhãn `KEEP`, `UPDATE_LATEST`, `RENAMED`.
- Mục đích: code mới nhất có thể gọi thêm hàm khác, dùng thêm biến global, macro, kiểu. Phải mang theo đủ, nếu không FOMULAR sẽ lỗi compile hoặc chạy sai.

### 3.1 Chọn tầng

| Đơn vị cần khám phá | Tầng |
|---|---|
| 1B — `UPDATE_LATEST` | Tầng 1 |
| TH2 — `RENAMED` (Y ở Latest, X ở After) | Tầng 1 |
| 1A — `KEEP` | Tầng 2 (trên thân hàm ở After) |
| Hàm mới tìm ra trong lúc khám phá (Before chưa có) | Tầng 2 |
| Macro / biến / kiểu | Tầng 2 (trên phần định nghĩa) |

### 3.2 Cắt hàm ra file riêng

- Copy thân hàm (từ dòng chữ ký tới dấu `}` đóng hàm, kèm comment ngay phía trên nếu có) ra file:
  - `WORK/phase2/fn/<file>/<X>.before.c` (nếu Before có)
  - `WORK/phase2/fn/<file>/<X>.after.c`
  - `WORK/phase2/fn/<file>/<X>.latest.c` (với `RENAMED`: dùng thân Y)
- Ghi khoảng dòng gốc của từng bản vào report.

### 3.3 Tầng 1 — Dùng diff của riêng hàm

- Bước 1: gọi `get-diff(<X>.latest.c, <X>.after.c)`, lưu vào `WORK/phase2/fn/<file>/<X>.diff`.
- Bước 2: lấy **tên mới** từ dòng `+` (tên không có trong bản After).
  - Mỗi tên mới: điều tra theo mục 3.5.
- Bước 3: lấy **tên bị bỏ** từ dòng `-` (tên không còn trong bản Latest).
  - Nếu tên bị bỏ là hàm do RT thêm (`Add`): grep trong `source/` xem còn nơi nào gọi (bỏ qua định nghĩa, prototype, comment changelog).
  - Không còn nơi nào gọi: gắn `NOT_PORTED`, ghi vào "Bỏ qua".
  - Còn nơi gọi: giữ lại như bình thường.
- Bước 4: **quét nhẹ** các tên ở dòng không đổi.
  - Chỉ tìm định nghĩa ở Latest và so với Before.
  - Giống nhau: `DEP_EXISTING`, không đi sâu.
  - Khác nhau (ví dụ macro đổi giá trị, mảng đổi kích thước): `DEP_CHANGED`, điều tra theo mục 3.5.
- Bước 5: nếu **toàn bộ** dòng đặc trưng của RT trong X không còn trong bản Latest (có thể RT đã bị gỡ): ghi `NEED_CONFIRM`.

### 3.4 Tầng 2 — Đọc toàn bộ thân hàm / định nghĩa

- Liệt kê **mọi tên** được dùng, rồi điều tra từng tên theo mục 3.5.
- Cách nhận biết tên:
  - Tên đứng trước dấu `(` (trừ `if`, `for`, `while`, `switch`, `sizeof`, `return`): hàm hoặc macro dạng hàm. Grep `#define <tên>` để phân biệt.
  - Tên không khai báo trong hàm và không phải tham số: biến global, `static`, `extern`.
  - Tên viết hoa toàn bộ: macro hoặc giá trị `enum`.
  - `x.field`, `p->field`: field của struct. Xác định kiểu của `x`/`p`, rồi tìm struct và field đó.
  - Kiểu dùng trong khai báo, ép kiểu: `typedef`, `struct`, `enum`.
  - Tên hàm dùng như giá trị (gán cho con trỏ hàm, đưa vào bảng): vẫn tính là phụ thuộc.
- Bỏ qua:
  - Biến cục bộ, tham số của hàm.
  - Từ khoá C.
  - Hàm thư viện chuẩn (`memcpy`, `strcpy`, `memset`, `printf`...).

### 3.5 Điều tra một tên T (dùng chung cho cả 2 tầng)

```text
tên T
 ├─ Đã xét rồi? → bỏ qua
 ├─ Tìm định nghĩa ở Latest: cùng file → file .h được #include → toàn bộ source/
 │    ├─ Không thấy        → UNRESOLVED → NEED_CONFIRM
 │    └─ Thấy ở nhiều chỗ  → NEED_CONFIRM (đưa các vị trí)
 └─ So với Before (cùng tên, cùng file):
      ├─ Before chưa có    → DEP_NEW
      │                       mang định nghĩa Latest (hàm thì lấy cả prototype ở .h)
      │                       hàm → TẦNG 2 trên thân T
      │                       biến/kiểu → TẦNG 2 trên định nghĩa (macro kích thước, kiểu field...)
      ├─ Before có, khác   → DEP_CHANGED
      │                       mang bản Latest
      │                       hàm → TẦNG 1 (get-diff T ở Latest với T ở Before)
      └─ Giống hệt Before  → DEP_EXISTING, dừng (Phase 3 chỉ kiểm tra Target có T chưa)
```

- **Chỉ đi xuôi:** từ hàm của RT đi vào các hàm/biến nó dùng, rồi đi tiếp vào trong các hàm đó. Không tìm ngược "ai đang dùng hàm này".
- **Điểm dừng:**
  - Mỗi tên chỉ xét một lần.
  - Tên `DEP_EXISTING` thì không đi sâu.
  - Tên không có trong `source/` (thư viện hệ thống) thì dừng.
  - Dừng khi không còn tên mới.
- Phụ thuộc nằm ở file khác (không có trong danh sách Phase 1): vẫn ghi diff cho file đó ở Bước 4, ghi rõ trong report là file được thêm vì phụ thuộc.
- Không hỏi người dùng chỉ vì Latest gọi thêm hàm hoặc dùng thêm biến mới.

### 3.6 Ví dụ

```text
ArtLibCopyRecipeName  (RT2486 Mod, RT2707 Mod về sau → 1B → tầng 1)
 ├─ + artLibLinkOnVarSet()     → Before chưa có → DEP_NEW → tầng 2
 │    ├─ g_varLinkTbl[]        → Before chưa có → DEP_NEW → tầng 2 trên định nghĩa
 │    │    └─ VAR_LINK_MAX     → Before chưa có → DEP_NEW
 │    └─ RcpIfGetAllVari()     → giống Before   → DEP_EXISTING
 └─ (quét nhẹ) RCP_NAME_LEN    → giống Before   → DEP_EXISTING

ArtLibPutOsfData  (không có Mod về sau → 1A → KEEP → tầng 2)
 └─ ... điều tra mọi tên trong thân hàm như trên
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
  - **Cây phụ thuộc**: như ví dụ ở mục 3.6.
  - **Bảng phụ thuộc**:

```markdown
| Tên | Loại | Tìm ra từ | Nguồn (tầng 1 mới / tầng 1 bỏ / quét nhẹ / tầng 2) | Định nghĩa ở Latest (file:dòng) | So với Before | Nhãn |
|---|---|---|---|---|---|---|
```

  - **TH2**: với mỗi đơn vị không tìm thấy, ghi các dòng đặc trưng, các ứng viên, từng dòng khớp với dòng nào, tỷ lệ khớp và quyết định.
  - **Bỏ qua**: `DELETE`, `NOT_PORTED`, kèm lý do.
  - **Cần xác nhận**: mọi mục `NEED_CONFIRM`, `UNRESOLVED`, tên có nhiều định nghĩa.
- Báo cho người dùng: đường dẫn report, đường dẫn các diff mới nhất, số lượng từng nhãn.
- Hỏi người dùng từng mục "Cần xác nhận". Ghi câu trả lời vào report và cập nhật lại diff ở Bước 4 nếu cần.
- Dừng, chờ người dùng xác nhận rồi mới sang Phase 3.
