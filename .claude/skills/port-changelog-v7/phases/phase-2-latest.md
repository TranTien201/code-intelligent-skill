# Phase 2 — Đưa code RT lên Latest

## Mục tiêu

- Code RT ở After đã cũ; các RT sau có thể đã sửa tiếp. Phase này thay **code RT viết** bằng bản hiện tại của chính nó ở Latest, và mang theo mọi định nghĩa mà code đó cần.
- Kết quả: **diff (new)** từng file, `paused.md`, `ledger.md`. Không quyết định cách merge vào Target.
- **Chỉ thay dòng `+` của diff RT.** Dòng `-` (code Before) giữ nguyên vì Phase 3 dùng nó để tìm vị trí trong FOMULAR.

## Từ khóa của Phase này

- **Diff RT**: `get_diff(<X>.after.c, <X>.before.c)` → `<X>.rt.diff`. RT đã đổi gì trong X.
- **Diff sau RT**: `get_diff(<X>.latest.c, <X>.after.c)` → `<X>.ctx.diff`. RT sau đã đổi gì. **Chỉ để định vị, không mang theo.**
- **Vùng RT**: khoảng dòng `+` liên tiếp trong `<X>.after.c`. Đếm dòng After: context và `+` tăng bộ đếm, `-` không tăng. Header `+c,d` có cả context, không phải toàn bộ là code RT.
- **Độ lệch**: tổng (`+` − `-`) của mọi thay đổi của diff sau RT nằm **phía trên** một dòng After. Dòng After `n` không bị sửa ở Latest là `n + độ lệch`.
- **`<X>.feature.c`**: `<X>.before.c` + code RT đã cập nhật theo Latest ("X nếu RT được viết hôm nay").
- **Đồ mới / đồ cũ**: phụ thuộc mà Before chưa có hoặc đã khác / giống hệt Before.

## Tóm tắt luồng

```text
B1 Tìm X ở Latest theo tên định nghĩa, cắt before/after/latest (từ dòng đầu comment đầu hàm)
B2 Diff RT → vùng RT
B3 Diff sau RT → chỗ RT sau đã sửa
B4 Mỗi vùng RT: KEEP | UPDATED | DROPPED | NEED_CONFIRM
B5 Dựng <X>.feature.c, diff (new) của X
B6 Trace phụ thuộc: DEP_NEW | DEP_CHANGED | DEP_PAUSED | NEED_CONFIRM | UNRESOLVED
B7 Ghi diff (new) từng file (tiêu đề có Anchor:) + paused.md
B8 Rà độ phủ P1→P2 → ledger.md, CHƯA XÉT = 0
B9 Report + cổng + câu hỏi → DỪNG
```

## Bước 1 — Tìm đơn vị ở Latest và cắt

Đọc: `phase1/units.md`, `source/`, `request/`.

- Tìm **định nghĩa** của X trong cùng file ở `source/`: hàm có thân `{}` (chỗ gọi, prototype không tính); `#define X`; khai báo biến/bảng ngoài hàm; `struct X`, `typedef … X;`, `enum`. Không thấy đúng tên → coi như không có.

| Loại | Latest không có X | Latest có X |
|---|---|---|
| `Mod` | `DROPPED`, ghi "Bỏ qua" | Cắt before/after/latest |
| `Add` | `DROPPED` | Cắt after/latest. Latest không còn ai dùng X → `NOT_PORTED`, dừng X |
| `Del` | Đúng mong đợi: toàn bộ Before là `-` | RT sau đã thêm lại → `NEED_CONFIRM` |

- Cắt vào `WORK/<run-id>/phase2/fn/<file>/<X>.{before,after,latest}.c`. Đơn vị `Add` không có `before.c` (coi như rỗng). Từ đây số dòng tính trong bản cắt. Ghi khoảng dòng gốc vào report.

### Quy tắc cắt (bắt buộc)

- Bản cắt hàm **bắt đầu ở dòng đầu tiên của comment đầu hàm**, kết thúc ở `}` đóng hàm.
- Đi ngược từ chữ ký lên qua **mọi** dòng comment, kể cả dòng kẻ `/*#----#*/` và hộp mô tả. Dừng khi gặp dòng code, 2 dòng trống liên tiếp hoặc `}` của đơn vị trước.
- Tự kiểm: dòng ngay trên điểm bắt đầu phải là code, `}`, hoặc dòng trống; **không được là comment**.
- Kiểm tra bản cắt không dừng ở `}` của khối con và không ăn sang đơn vị kế tiếp (xét comment, chuỗi, `#if`).

Ví dụ (RT1234): helper `libLinkVarSet` ở Latest có comment đầu hàm bắt đầu dòng 1200, `}` ở dòng 1255. Đúng: `1200-1255`. Lần chạy trước cắt từ 1212 (dòng kẻ cuối của hộp comment) → mất 11 dòng comment đầu hàm, Phase 3 chèn hàm thiếu comment.

## Bước 2 — Diff RT

Đọc: `<X>.after.c`, `<X>.before.c`.

- `get_diff(<X>.after.c, <X>.before.c)` → `<X>.rt.diff`. Đơn vị `Add`: cả `after.c` là một hunk `+`, vùng RT là toàn bộ X.
- Hunk có `-` và `+`: RT sửa, có vùng RT. Chỉ `+`: RT thêm, có vùng RT. Chỉ `-`: RT xoá, không có vùng RT, giữ nguyên hunk, bỏ qua Bước 4.

## Bước 3 — Diff sau RT

Đọc: `<X>.latest.c`, `<X>.after.c`.

- `get_diff(<X>.latest.c, <X>.after.c)` → `<X>.ctx.diff`. Đọc từng dòng để tách thay đổi thực (context tăng cả hai bộ đếm, `-` chỉ tăng After, `+` chỉ tăng Latest).
- Diff trống: mọi vùng RT là `KEEP`.

## Bước 4 — Cập nhật từng vùng RT

Đọc: `<X>.rt.diff` (vùng RT), `<X>.ctx.diff`.

Xét từng thay đổi thực của diff sau RT so với vùng RT (ví dụ vùng RT = After 50–54):

| Thay đổi của diff sau RT | Phân loại | Xử lý |
|---|---|---|
| Sửa/xoá dòng nằm hẳn trong vùng (sửa dòng 52) | Trong vùng | Lấy theo |
| Chèn giữa hai dòng đều trong vùng (sau dòng 52) | Trong vùng | Lấy theo |
| Sửa/xoá dòng nằm hẳn ngoài vùng (dòng 20) | Ngoài vùng | Bỏ qua |
| Chèn sát mép (sau dòng 49 hoặc sau dòng 54) | Ngoài vùng | Bỏ qua |
| Sửa/xoá có dòng trong và ngoài vùng (53–56) | Vắt qua mép | `NEED_CONFIRM` |

| Kết luận cho vùng RT | Nhãn | Code RT mới |
|---|---|---|
| Không có thay đổi trong vùng, không vắt mép | `KEEP` | Code After |
| Có thay đổi trong vùng, không vắt mép, còn ít nhất 1 dòng giữ nguyên | `UPDATED` | Đoạn Latest từ mép trên tới mép dưới |
| Mọi dòng bị xoá | `DROPPED` | Không còn |
| Mọi dòng bị viết lại, hoặc có vắt mép | `NEED_CONFIRM` | Không đoán; đưa After, Latest để hỏi |

- **Mép trên**: dòng đầu vùng không bị sửa → `dòng + độ lệch`; bị sửa → dòng `+` thực đầu tiên của cụm thay thế; bị xoá → dòng kế tiếp trong vùng còn ở Latest. **Mép dưới** làm tương tự với dòng cuối.
- Ví dụ: vùng After 50–54; diff sau RT: (1) chèn 4 dòng sau dòng 20, (2) `@@ -52,1 +56,2 @@`, (3) chèn sau dòng 54. Mép trên 50+4 = 54; mép dưới 54+4+1 = 59. Kết quả `UPDATED`, code RT mới = Latest 54–59; (1), (3) ngoài vùng, không lấy.
- Đơn vị `Add`: diff sau RT trống → `KEEP`; có thay đổi → `UPDATED`, code mới = toàn bộ `latest.c`.

### Biến cục bộ và tham số mới

- Code RT mới dùng biến cục bộ không có trong `before.c` và không có trong code RT ở After: mang dòng khai báo ở Latest thành hunk `+`, đặt sau dòng khai báo đứng trước nó mà Before cũng có.
- Không tự mang lệnh gán ngoài vùng RT. Nếu thiếu nguồn giá trị: `NEED_CONFIRM` cho phần dùng giá trị đó; phần độc lập vẫn tiếp tục.
- Chữ ký X ở Latest có tham số mới: `NEED_CONFIRM` (kéo theo mọi nơi gọi X).

## Bước 5 — Dựng Feature và diff (new) của đơn vị

Đọc: `<X>.before.c`, `<X>.rt.diff`, kết luận Bước 4.

- Từ `<X>.before.c` (đơn vị `Add`: file rỗng), áp từ dưới lên: mỗi hunk của diff RT thay dòng `-` bằng code After (`KEEP`) hoặc Latest (`UPDATED`); hunk chỉ `-` áp như cũ; thêm khai báo biến ở Bước 4. Không áp hunk `DROPPED` và `NEED_CONFIRM` chưa trả lời.
- Ghi `<X>.feature.c`. Mọi vùng là `KEEP` thì `feature.c` phải giống hệt `after.c`.
- Diff (new) của X: `get_diff(<X>.feature.c, <X>.before.c)`. Context là code Before, Phase 3 dùng để tìm vị trí ở FOMULAR.

## Bước 6 — Trace phụ thuộc

Đọc: dòng `+` của diff (new), định nghĩa ở `source/` và `request/Before/`.

- Xuất phát từ dòng `+` của diff (new) và toàn bộ định nghĩa `DEP_NEW` tìm được. Không trace từ context hay phần còn lại của hàm Latest. Chỉ đi xuôi vào trong, không tìm ngược ai gọi.
- Lần theo: hàm được gọi; biến global/static/extern, macro, `enum`, `struct`/`typedef` (và field dùng tới), bảng dữ liệu, prototype; cả những thứ mà các định nghĩa đó dùng. Bỏ qua biến cục bộ, tham số, hàm thư viện chuẩn.
- So định nghĩa ở Latest với **Before** (không so với After: After đã có code RT):

| Kết quả | Nhãn | Làm gì |
|---|---|---|
| Before chưa có | `DEP_NEW` | Mang nguyên định nghĩa Latest (hàm: cả prototype), cắt theo quy tắc Bước 1. Trace tiếp |
| Giống hệt Before | `DEP_PAUSED` | Ghi `paused.md`, không đi sâu |
| Không có bản Before để so | `DEP_PAUSED` | Ghi `paused.md`, ghi chú "không có Before" |
| Khác Before, dòng `+` dùng chỗ đã đổi | `DEP_CHANGED` | Mang phần đã đổi (bảng dưới). Trace tiếp |
| Khác Before, dòng `+` dùng như cũ (chỉ thân đổi) | `NEED_CONFIRM` | Đưa diff Before–Latest của định nghĩa để hỏi |
| Không tìm thấy định nghĩa | `UNRESOLVED` | "Cần xác nhận" |
| Nhiều định nghĩa, không biết chỗ nào đúng | `NEED_CONFIRM` | Đưa các vị trí |

| Chỗ đổi mà dòng `+` dùng | Mang gì (`DEP_CHANGED`) |
|---|---|
| Giá trị macro, kích thước mảng, kiểu biến | Định nghĩa mới ở Latest |
| Field / hằng enum / phần tử bảng mới | Chỉ đúng phần đó (hunk `+`) |
| Chữ ký hàm | Toàn bộ khác biệt Before–Latest của hàm; ghi rõ có thể kèm code RT khác |

- Mỗi định nghĩa trace một lần nhưng ghi mọi chỗ dùng. Phụ thuộc ở file khác: vẫn ghi diff cho file đó ở Bước 7.
- `DEP_NEW` cần **neo** như đơn vị `Add`: dòng liền trước / liền sau định nghĩa trong file Latest (cách ghi ở Phase 1, Bước 4).
- `paused.md`:

```markdown
| Tên | Loại | Dùng ở (đơn vị:dòng trong feature.c) | Định nghĩa ở Latest (file:dòng) | Chữ ký / kiểu / giá trị | So với Before |
|---|---|---|---|---|---|
| IfGetAll | hàm | libLinkVarSet:21 | src/itemif.c:820 | int IfGetAll(int, char*, VARI**) | giống |
```

## Bước 7 — Ghi diff (new) từng file

Đọc: diff (new) từng đơn vị, `phase1/units.md` (neo), `phase1/diff/` (entry RT).

- Một file `WORK/<run-id>/phase2/diff/<file>.diff`, mỗi đơn vị một phần. Trên mỗi phần một dòng tiêu đề:

```text
### <tên> | <MOD|NEW|DEL> | <nhãn> | Before: <dòng> | Latest: <dòng> | Anchor: <neo hoặc -> | <ghi chú>
```

  Ví dụ: `### libLinkVarSet | NEW | KEEP | Before: - | Latest: 1200-1255 | Anchor: trước "/** EOF **/" | Add helper`

| Loại | Gồm | Nội dung phần | `Anchor:` |
|---|---|---|---|
| `MOD` | Đơn vị `Mod`, `DEP_CHANGED` | `get_diff(<X>.feature.c, <X>.before.c)` | `-` |
| `NEW` | Đơn vị `Add`, `DEP_NEW` | Toàn bộ `<X>.feature.c` là `+` | **Bắt buộc** |
| `DEL` | Đơn vị `Del` | Toàn bộ `<X>.before.c` là `-` | `-` |

- Khoảng `Latest:` phải đúng bằng khoảng của bản cắt Latest (Bước 1).
- Không có phần cho `DROPPED`, `NOT_PORTED`, `DEP_PAUSED`, `NEED_CONFIRM` chưa trả lời.
- Thêm một phần `### Modification | …` chứa entry RT (từ diff Phase 1) để Phase 3 ghi changelog Target.
- File `added`: toàn bộ file Latest là `+`. File `deleted`: một dòng tiêu đề `DEL` cho cả file.

## Bước 8 — Rà độ phủ P1→P2

Đọc: `<X>.feature.c`, `<X>.after.c`, `phase1/diff/<file>.diff`.

Mục đích: không dòng RT nào mất mà không có lý do.

- Đơn vị `Mod`: `get_diff(<X>.feature.c, <X>.after.c)`. Đơn vị `Add`: cắt khối `+` của đơn vị từ diff Phase 1 ra `<X>.p1.c`, rồi `get_diff(<X>.feature.c, <X>.p1.c)`. (`DEP_NEW` không có dòng RT, không rà.)
- Đơn vị `DROPPED` / `NOT_PORTED` cả đơn vị: một dòng ledger `DROPPED_IN_LATEST` cho cả khoảng dòng.
- Mọi dòng `-` của diff này là dòng RT có ở After mà Feature không có. Mỗi dòng phải:
  - **Sửa** (đưa lại vào Feature, dựng lại diff (new)) nếu bị mất do nhầm, hoặc
  - **Ghi `ledger.md`** với đúng một mã lý do:

| Mã | Khi nào |
|---|---|
| `DROPPED_IN_LATEST` | Dòng thuộc vùng RT bị RT sau xoá (Bước 4) |
| `REPLACED_BY_LATEST` | Dòng thuộc vùng `UPDATED`, bản Latest đã thay nó |
| `NOT_RT` | Dòng không phải code RT (ví dụ thay đổi `UNEXPLAINED` người dùng xác nhận không thuộc RT) |
| `CHANGELOG_ONLY` | Dòng thuộc khối `Modification:` (đi theo phần `Modification`) |
| `USER_DECISION` | Người dùng đã trả lời bỏ (ghi số câu hỏi) |

- Không tự đặt lý do khác. Không mã nào đúng → đó là lỗi → sửa.
- Dòng `+` của diff này phải giải thích được bằng vùng `UPDATED` hoặc khai báo mang theo (Bước 4). Không giải thích được (ví dụ dòng Before mà RT đã xoá vẫn còn trong Feature) → lỗi, sửa.
- Khối `Modification:`: dòng `+` của entry RT ở diff Phase 1 ghi **một** dòng ledger `CHANGELOG_ONLY` (khoảng dòng), sau khi kiểm chúng có đủ trong phần `### Modification` của diff (new).
- **Tổng dòng RT** = mọi dòng `+` của diff Phase 1.

Ví dụ: diff rà của `libLinkVarSet` có 11 dòng `-` là comment đầu hàm. Không mã nào đúng → lỗi cắt → cắt lại từ dòng đầu comment, dựng lại diff (new), chạy lại rà.

`ledger.md`:

```markdown
| File | Đơn vị | Dòng After | Nội dung (rút gọn) | Mã | Chi tiết |
|---|---|---|---|---|---|
| src/item.c | LibCopyItem | 212 | LogPrint("NG"); | REPLACED_BY_LATEST | Latest 230: LogPrint("NG: %d", ret); |

Tổng dòng RT: 180 | Có trong Feature: 171 | Có lý do: 9 | Đã sửa: 0 | CHƯA XÉT: 0
```

## Bước 9 — Report, cổng, câu hỏi

Đọc: kết quả Bước 1–8, khối `Modification:` ở `source/`.

- Ghi `phase2/REPORT.md` theo `templates/report.md`, thêm:
  - Bảng đơn vị: loại, có ở Latest không, khoảng dòng Before/After/Latest, **RT sau đã sửa** (entry phía trên RT trong `source/` có `Mod. X`; chỉ để tham khảo).
  - Bảng vùng RT: `| File | Đơn vị | Hunk | Vùng RT (After) | Đoạn Latest | Nhãn | Ghi chú |`; trích code After/Latest cho vùng `UPDATED`.
  - Cây phụ thuộc và bảng phụ thuộc (tên, loại, dùng ở, định nghĩa Latest, so với Before, nhãn); copy `paused.md`.
  - Độ phủ: dòng tổng kết của `ledger.md`.
- **Cổng Phase 2:**

| # | Kiểm tra | Đạt khi |
|---|---|---|
| 1 | Đơn vị trong `units.md` đã xử lý (cắt / `DROPPED` / `NOT_PORTED` / `Del`) | `n/n` |
| 2 | Bản cắt hàm: dòng ngay trên điểm bắt đầu không phải comment | `n/n` |
| 3 | Phần `NEW` có `Anchor:` khác `-` | `n/n` |
| 4 | Khoảng `Latest:` ở tiêu đề = khoảng bản cắt | `n/n` |
| 5 | Độ phủ: dòng RT = có trong Feature + có lý do + đã sửa | `CHƯA XÉT = 0` |
| 6 | Dòng `paused.md` = số `DEP_PAUSED` | Bằng nhau |
| 7 | Đơn vị chỉ `KEEP`: `feature.c` giống hệt `after.c` | `n/n` |
| 8 | Câu hỏi đã trả lời | Tất cả, trước khi sang Phase 3 |

- Báo người dùng: report, diff (new), số lượng từng nhãn. Hỏi từng mục "Cần xác nhận".
- Sau mỗi câu trả lời: ghi vào report, cập nhật Feature, diff (new), `paused.md`, `ledger.md` (`USER_DECISION`), chạy lại Bước 8 và cổng. Ví dụ: phụ thuộc chỉ đổi thân, trả lời "mang" → xử lý như `DEP_CHANGED`; "không mang" → ghi `paused.md`.
- Dừng chờ xác nhận rồi mới sang Phase 3.
