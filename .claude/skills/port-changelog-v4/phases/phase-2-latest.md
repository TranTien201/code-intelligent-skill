# Phase 2 — Đưa feature lên bản mới nhất (Latest)

## Mục tiêu:
- Code của RT lấy ở thời điểm làm RT đã cũ. Sau đó có thể có RT khác sửa tiếp.
- Phase này đưa từng đơn vị của RT lên **trạng thái Latest**, và mang theo **mọi** hàm/biến/macro mà code mới nhất cần.
- Đầu vào: `WORK/phase1/units.md`, các diff ở `WORK/phase1/diff/`.

## Tóm tắt luồng

```markdown
Với mỗi đơn vị X trong units.md (hàm / macro / biến):

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
  Lần theo mọi hàm được gọi và mọi thứ định nghĩa ngoài hàm (biến, macro, kiểu...).
  Mỗi tên: so định nghĩa ở Latest với ở Before (TELINDY trước khi có RT)
    → Before chưa có, hoặc Latest đã sửa: ĐỒ MỚI → mang theo (DEP_NEW / DEP_CHANGED), đi tiếp vào trong
    → Giống hệt Before: ĐỒ CŨ → TẠM DỪNG (DEP_PAUSED), không đi sâu, ghi vào paused.md
  Đồ cũ chỉ tạm dừng, không phải bỏ: Phase 3 kiểm tra với FOMULAR, thiếu thì mang sang và trace tiếp.

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
### Trường hợp 2 — Không có X ở Latest

- Chỉ xét hai khả năng: **đổi tên** hoặc **bị xoá**.
- X là đơn vị `Del` (chính RT đã xoá X): Latest không có X là đúng. Gắn `DELETE` luôn, không cần tìm đổi tên. Ở đây `DELETE` nghĩa là **giữ việc xoá**: Phase 3 sẽ xoá X ở Target.
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
- Mục tiêu: lấy ra **đủ mọi thứ mới** mà code mới nhất của RT cần. Thiếu một thứ là FOMULAR lỗi compile hoặc chạy sai.

### Hiểu đúng trước khi làm

- **Trace xuôi vẫn có thể lan ra cả source.** Hàm của RT gọi hàm dùng chung (ví dụ `RcpIfGetAllVari`, `LogPrint`). Hàm dùng chung lại gọi tiếp module khác, rồi tới tầng OS, driver... Nếu cứ đi tới cùng thì gần như phải đọc hết source, và còn mang các hàm dùng chung của TELINDY đè lên bản riêng của FOMULAR.
- **Vì vậy cần biết chỗ nào được dừng.** Câu hỏi ở mỗi tên là: "Đây là **đồ mới** của feature, hay là **đồ cũ** mà feature chỉ dựa vào?"
- **Mốc để phân biệt là Before** (source TELINDY ngay trước khi làm RT):
  - Không có ở Before, hoặc Latest đã sửa khác Before: là **đồ mới** (do RT này hoặc RT sau thêm/sửa). Phải mang theo và đi tiếp vào trong.
  - Giống hệt Before: là **đồ cũ**, có từ trước RT. Feature không sửa gì nó, chỉ gọi tới nó.
- **Không so với After.** After đã chứa code của chính RT. So với After thì những thứ RT thêm vào sẽ trông như "đồ cũ" và bị bỏ sót.
- **Đồ cũ thì TẠM DỪNG, không phải BỎ.** Before là của TELINDY, không phải của FOMULAR. FOMULAR thường đã có đồ cũ, nhưng **không chắc chắn**. Vì vậy:
  - Phase 2 ghi đồ cũ vào **danh sách tạm dừng** (`DEP_PAUSED`) và không đi sâu vào nó.
  - Phase 3 mới kiểm tra danh sách này với FOMULAR. FOMULAR thiếu thứ nào thì mang sang và trace tiếp vào trong thứ đó.
  - Nhờ vậy: không phải đọc cả source, mà cũng không sót.

### Cần lần theo những gì

- **Hàm được gọi:** hàm X gọi hàm nào thì xét hàm đó. Nếu là đồ mới thì đọc tiếp vào trong, nó gọi hàm nào nữa thì xét tiếp. Cứ thế cho đến hết.
- **Những thứ định nghĩa bên ngoài hàm** mà code dùng tới: biến global / `static` / `extern`, macro, `enum`, `struct` / `typedef` (và field được dùng), prototype.
- **Những thứ mà chính các định nghĩa đó dùng**, ví dụ kích thước mảng là một macro, field có kiểu là một struct khác.

### Mỗi tên tìm được thì xử lý thế nào

- Tìm định nghĩa ở Latest, rồi so với Before:

| Kết quả | Nhãn | Làm gì tiếp |
|---|---|---|
| Before chưa có | `DEP_NEW` | Mang định nghĩa Latest (hàm thì lấy cả prototype). Đi tiếp vào bên trong |
| Before có, Latest đã sửa khác | `DEP_CHANGED` | Mang bản Latest. Đi tiếp vào bên trong |
| Giống hệt Before | `DEP_PAUSED` | **Tạm dừng**, không đi sâu. Ghi vào danh sách tạm dừng cho Phase 3 |
| Không tìm thấy định nghĩa | `UNRESOLVED` | Ghi vào "Cần xác nhận" |
| Thấy ở nhiều chỗ, không biết chỗ nào đúng | `NEED_CONFIRM` | Ghi vào "Cần xác nhận", đưa các vị trí |

### Lưu ý khi lần theo

- Chỉ đi xuôi: từ hàm của RT đi vào bên trong. Không tìm ngược "ai đang gọi hàm này".
- Mỗi tên chỉ xét một lần. Dừng khi không còn tên mới.
- Bỏ qua biến cục bộ, tham số và hàm thư viện chuẩn / hệ thống (`memcpy`, `strcpy`, `printf`...).
- Đừng chỉ đọc các dòng đã thay đổi. Tên nằm ở dòng không đổi vẫn có thể có định nghĩa đã bị RT sau sửa (ví dụ macro đổi giá trị, mảng đổi kích thước). Trường hợp đó là `DEP_CHANGED`, không phải `DEP_PAUSED`.
- Gợi ý: với hàm có ở cả After và Latest, có thể `get-diff` riêng hàm đó để thấy nhanh Latest gọi thêm / bỏ đi những gì, rồi bắt đầu lần theo từ đó.
- Hàm do RT thêm (`Add`) mà ở Latest không còn nơi nào gọi: gắn `NOT_PORTED`, ghi vào "Bỏ qua".
- Toàn bộ code của RT trong hàm không còn ở Latest (có thể RT đã bị gỡ): gắn `NEED_CONFIRM`.
- Phụ thuộc nằm ở file khác: vẫn ghi diff cho file đó ở Bước 4, ghi rõ trong report là file được thêm vì phụ thuộc.
- Không hỏi người dùng chỉ vì Latest gọi thêm hàm hoặc dùng thêm biến mới.

### Ghi danh sách tạm dừng

- Lưu vào `WORK/phase2/paused.md`. Đây là đầu vào của Phase 3 (Bước 3):

```markdown
| Tên | Loại | Tìm ra từ (hàm nào dùng nó) | Định nghĩa ở Latest (file:dòng) | Chữ ký / kiểu / giá trị |
|---|---|---|---|---|
| RcpIfGetAllVari | hàm | artLibLinkOnVarSet | src/rcpif.c:820 | int RcpIfGetAllVari(int, char*, char*, int*, VARI**) |
| RCP_NAME_LEN | macro | ArtLibCopyRecipeName | inc/rcp.h:45 | 32 |
```

- Cột "Chữ ký / kiểu / giá trị" giúp Phase 3 so nhanh với FOMULAR mà không phải mở lại file.

### Lưu bản cắt của hàm

- Với mỗi đơn vị và mỗi phụ thuộc mang theo (`DEP_NEW`, `DEP_CHANGED`), cắt phần định nghĩa (hàm: từ dòng chữ ký tới dấu `}` đóng hàm) ra file:
  - `WORK/phase2/fn/<file>/<tên>.before.c` (nếu Before có)
  - `WORK/phase2/fn/<file>/<tên>.after.c` (nếu After có)
  - `WORK/phase2/fn/<file>/<tên>.latest.c` (với `RENAMED`: dùng thân hàm mới)
- Ghi khoảng dòng gốc vào report. Các file này dùng cho Bước 4 và Phase 3.

### Ví dụ

```text
ArtLibCopyRecipeName  (RT2707 Mod về sau → UPDATE_LATEST)
 ├─ artLibLinkOnVarSet()      → Before chưa có     → DEP_NEW → đi tiếp vào trong
 │    ├─ g_varLinkTbl[]       → Before chưa có     → DEP_NEW → đi tiếp vào định nghĩa
 │    │    └─ VAR_LINK_MAX    → Before chưa có     → DEP_NEW (kích thước mảng)
 │    └─ RcpIfGetAllVari()    → giống hệt Before   → DEP_PAUSED (không mở ra đọc)
 ├─ RCP_BUF_SIZE              → Latest đổi 256→512 → DEP_CHANGED
 └─ RCP_NAME_LEN              → giống hệt Before   → DEP_PAUSED

Danh sách tạm dừng gửi sang Phase 3: RcpIfGetAllVari, RCP_NAME_LEN
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
| `DEP_PAUSED` | Không có block, chỉ ghi vào `WORK/phase2/paused.md` |

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

  - **Danh sách tạm dừng**: copy bảng từ `paused.md`, ghi rõ "Phase 3 sẽ kiểm tra với FOMULAR".
  - **TH2**: với mỗi đơn vị không tìm thấy, ghi các dòng đặc trưng, các ứng viên, từng dòng khớp với dòng nào, tỷ lệ khớp và quyết định.
  - **Bỏ qua**: `DELETE`, `NOT_PORTED`, kèm lý do.
  - **Cần xác nhận**: mọi mục `NEED_CONFIRM`, `UNRESOLVED`, tên có nhiều định nghĩa.
- Báo cho người dùng: đường dẫn report, đường dẫn các diff mới nhất, số lượng từng nhãn.
- Hỏi người dùng từng mục "Cần xác nhận". Ghi câu trả lời vào report và cập nhật lại diff ở Bước 4 nếu cần.
- Dừng, chờ người dùng xác nhận rồi mới sang Phase 3.
