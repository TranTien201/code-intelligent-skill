# Phase 2 — Đưa feature lên bản mới nhất (Latest)

## Mục tiêu

- Code của RT lấy ở thời điểm làm RT (After) đã cũ. Sau đó có thể có RT khác sửa tiếp đúng các đoạn code này.
- Phase này **cập nhật code RT** của từng đơn vị lên trạng thái Latest, và mang theo mọi định nghĩa mà code mới nhất của RT cần.
- Kết quả là **diff (new)**: đầu vào của Phase 3.
- Đầu vào: `WORK/phase1/units.md`, các diff ở `WORK/phase1/diff/`.

## Hiểu đúng trước khi làm

- **Không lấy nguyên hàm ở Latest.** Hàm ở Latest có thể chứa code của feature khác. Chỉ lấy đúng code của RT, ở bản hiện tại của nó.
- **Chỉ cập nhật code RT viết, không đụng code Before.** Trong diff RT, dòng `+` là code RT viết, dòng `-` là code Before mà RT đã thay. Phase này chỉ thay dòng `+` bằng bản Latest. Dòng `-` giữ nguyên, vì Phase 3 cần nó để tìm vị trí trong FOMULAR.
- **Tìm đơn vị theo tên định nghĩa, không tìm đổi tên.** Không thấy đúng tên ở Latest thì loại khỏi feature.

## Từ khóa của Phase này

Các từ dùng chung (RT, đơn vị, bản cắt, hunk, dòng `+` / `-`, diff (new)...) xem trong `SKILL.md`.

### Hai diff của Phase 2

- **Diff RT**: `get-diff(<X>.after.c, <X>.before.c)`. Cho biết RT đã thay đổi gì trong đơn vị X. Lưu ở `<X>.rt.diff`.
  - Ví dụ: dòng `-    return retCode;` và dòng `+    LogPrint("NG"); return retCode;` cho biết RT thêm một lời gọi `LogPrint`.
- **Diff sau RT**: `get-diff(<X>.latest.c, <X>.after.c)`. Cho biết các RT sau đã sửa gì trong đơn vị X. Lưu ở `<X>.ctx.diff`. Chỉ dùng để biết code RT ở Latest nằm đâu và đã đổi gì, **không mang theo**.
  - Ví dụ: hunk `@@ -52,1 +56,2 @@` cho biết dòng 52 của After đã bị sửa thành 2 dòng 56–57 ở Latest.

### Vùng RT và việc cập nhật

- **Vùng RT**: khoảng dòng trong `<X>.after.c` chứa code RT viết của một hunk. Lấy từ số `+c,d` ở dòng `@@` của diff RT: từ dòng `c` đến dòng `c+d−1`.
  - Ví dụ: hunk `@@ -50,3 +50,5 @@` của diff RT → vùng RT là dòng 50–54 của After.
- **Trong vùng / ngoài vùng / vắt qua mép**: vị trí của một hunk của diff sau RT so với vùng RT. Cách xác định ở Bước 4.2.
  - Ví dụ: vùng RT là dòng 50–54. Sửa dòng 52 là trong vùng. Chèn sau dòng 20 là ngoài vùng. Sửa dòng 53–56 là vắt qua mép.
- **Cập nhật code RT**: thay code RT viết (bản After) bằng bản hiện tại của chính đoạn đó ở Latest.
  - Ví dụ: ở After là `LogPrint("NG");`, ở Latest RT sau đổi thành `LogPrint("NG: %d", retCode);` → lấy dòng ở Latest.
- **Độ lệch**: số dòng mà một dòng After bị dời đi khi sang Latest, do các RT sau thêm/bớt dòng **phía trên** nó.
  - Ví dụ: phía trên dòng 50 có một chỗ chèn 4 dòng → độ lệch +4, dòng 50 của After là dòng 54 của Latest.
- **`<X>.feature.c`**: bản cắt Before của X, áp thêm code RT đã cập nhật theo Latest. Có thể hiểu là "X sau khi làm RT, nếu RT được viết hôm nay".

### Trace phụ thuộc

- **Trace**: lần theo các tên mà code RT dùng tới (hàm, macro, biến, kiểu...) để tìm định nghĩa cần mang theo.
  - Ví dụ: dòng `+` gọi `artLibLinkOnVarSet()` → tìm định nghĩa của hàm này.
- **Phụ thuộc**: đơn vị mà code RT dùng tới nhưng không phải đơn vị của RT.
  - Ví dụ: macro `RCP_BUF_SIZE` được dùng trong dòng `+` của `ArtLibCopyRecipeName`.
- **Đồ mới**: phụ thuộc mà Before chưa có, hoặc đã khác Before.
  - Ví dụ: `artLibLinkOnVarSet` (Before chưa có).
- **Đồ cũ**: phụ thuộc giống hệt Before.
  - Ví dụ: `RcpIfGetAllVari` (giống Before).
- **`paused.md`**: danh sách đồ cũ. Phase 2 không đi sâu vào chúng, Phase 3 kiểm tra với FOMULAR.

## Tóm tắt luồng

```text
Bước 1. Tìm đơn vị X ở Latest (theo tên ĐỊNH NGHĨA, cùng file) và cắt ra file riêng
   ├─ Mod (RT sửa):   Latest không có → DROPPED  | có → cắt before/after/latest → Bước 2
   ├─ Add (RT thêm):  Latest không có → DROPPED  | có → cắt after/latest        → Bước 2
   │                  Latest không còn ai dùng → NOT_PORTED
   └─ Del (RT xoá):   Latest không có → giữ nguyên (toàn bộ là -) | có → NEED_CONFIRM

Bước 2. Lấy diff RT:      get-diff(<X>.after.c, <X>.before.c)  → các vùng RT
Bước 3. Lấy diff sau RT:  get-diff(<X>.latest.c, <X>.after.c)  → các chỗ RT sau đã sửa

Bước 4. Cập nhật code RT của từng vùng RT
   Xét từng hunk của diff sau RT so với vùng RT:
   ├─ Ngoài vùng (kể cả chèn sát mép) → code khác, bỏ qua
   ├─ Trong vùng                      → thay đổi của chính code RT, lấy theo
   └─ Vắt qua mép                     → NEED_CONFIRM
   Kết luận cho vùng RT:
   ├─ Không có hunk nào trong vùng    → KEEP
   ├─ Có hunk trong vùng              → UPDATED: code RT mới = đoạn tương ứng ở Latest
   ├─ Cả vùng bị xoá                  → DROPPED
   └─ Cả vùng bị viết lại / vắt mép   → NEED_CONFIRM

Bước 5. Dựng diff (new) của X:  <X>.feature.c, rồi get-diff(<X>.feature.c, <X>.before.c)

Bước 6. Trace phụ thuộc từ các dòng + của diff (new)
   ├─ Before chưa có                            → DEP_NEW: mang nguyên, trace tiếp
   ├─ Giống hệt Before                          → DEP_PAUSED: ghi paused.md, không đi sâu
   ├─ Khác Before, dòng + dùng tới chỗ đã đổi   → DEP_CHANGED: mang phần đã đổi, trace tiếp
   └─ Khác Before, cách dùng như cũ             → NEED_CONFIRM

Bước 7. Ghi diff (new) cho từng file và paused.md
Bước 8. Report + câu hỏi → DỪNG chờ xác nhận
```

Phần dưới là chi tiết từng bước.

---

## Bước 1 — Tìm đơn vị ở Latest và cắt ra file riêng

### Tìm định nghĩa

- Với mỗi đơn vị X trong `units.md`, tìm **định nghĩa** của X trong cùng file ở `source/`:
  - Hàm: dòng chữ ký có thân `{ ... }`. Chỗ gọi X hoặc prototype của X **không tính**.
  - Macro: `#define X`.
  - Biến, bảng dữ liệu: dòng khai báo ngoài hàm.
  - Kiểu: `struct X { ... }`, `typedef ... X;`, `enum X { ... }`.
- **Không tìm đổi tên.** Không thấy đúng tên X trong file thì coi như không có, không đi tìm hàm khác có code giống.

### Xử lý theo loại đơn vị

| Loại (cột Add/Mod/Del của `units.md`) | Latest không có X | Latest có X |
|---|---|---|
| `Mod` (RT sửa bên trong) | Loại X khỏi feature. Ghi `DROPPED` vào "Bỏ qua" | Cắt X ra file riêng, sang Bước 2 |
| `Add` (RT thêm mới) | Loại X khỏi feature. Ghi `DROPPED` vào "Bỏ qua" | Cắt X ra file riêng, sang Bước 2. Nếu Latest không còn nơi nào dùng X: ghi `NOT_PORTED` vào "Bỏ qua", dừng xử lý X |
| `Del` (RT xoá hẳn) | Đúng như mong đợi. Giữ nguyên: toàn bộ định nghĩa Before là `-`. Sang Bước 7 | RT sau đã thêm lại X. Ghi `NEED_CONFIRM` |

### Cắt đơn vị ra file riêng

- Cắt nguyên định nghĩa (hàm: theo phạm vi ở `SKILL.md`, gồm cả comment đầu hàm) vào `WORK/phase2/fn/<file>/`. Cắt bản nào tuỳ loại:

| Loại | `<X>.before.c` | `<X>.after.c` | `<X>.latest.c` |
|---|---|---|---|
| `Mod` | Có | Có | Có |
| `Add` | **Không có** (Before chưa có X). Coi như file rỗng | Có | Có |
| `Del` | Có | Không có | Không cắt (chỉ cần biết Latest có X hay không) |

- File cắt ra có dòng đầu là dòng 1. **Từ đây mọi số dòng đều tính bên trong đơn vị**, không tính theo file gốc.
  - Lý do: ở Latest, code nằm phía trên X trong file có thể đã thêm bớt rất nhiều, làm số dòng trong file gốc lệch hẳn. Cắt riêng ra thì các bản của X so được với nhau.
- Ghi khoảng dòng gốc (trong file Before / After / Latest) vào report.

## Bước 2 — Lấy diff RT

- Gọi `get-diff(<X>.after.c, <X>.before.c)`, lưu vào `WORK/phase2/fn/<file>/<X>.rt.diff`.
  - Đơn vị `Add`: không có bản Before, nên cả `<X>.after.c` là một hunk duy nhất toàn dòng `+`. Vùng RT là toàn bộ X (dòng 1 đến dòng cuối).
- Mỗi hunk là một chỗ RT đã thay đổi. Đánh số hunk 1, 2, 3... từ trên xuống.
- Mỗi hunk thuộc một trong ba dạng:

| Dạng hunk | Ý nghĩa | Có vùng RT không |
|---|---|---|
| Có cả dòng `-` và `+` | RT sửa: thay code Before (`-`) bằng code mới (`+`) | Có |
| Chỉ có dòng `+` | RT thêm code mới | Có |
| Chỉ có dòng `-` | RT xoá code Before | **Không**. Không có code RT để cập nhật. Giữ nguyên hunk, bỏ qua Bước 4 |

- Ví dụ một hunk:

```diff
@@ -50,3 +50,5 @@
     retCode = RcpIfGetAllVari(subSystemId, name, &vari);
-    if (retCode != OK) {
-        return retCode;
-    }
+    if (retCode != OK) {
+        LogPrint("GetAllVari NG");
+        artLibSetVarDate(&vari);
+        return retCode;
+    }
```

  - `-50,3`: thay 3 dòng của Before (dòng 50–52).
  - `+50,5`: bằng 5 dòng trong After. **Vùng RT = dòng 50–54 của After.**

## Bước 3 — Lấy diff sau RT

- Gọi `get-diff(<X>.latest.c, <X>.after.c)`, lưu vào `WORK/phase2/fn/<file>/<X>.ctx.diff`.
- Diff này cho biết các RT sau đã sửa những dòng nào của After. Mỗi hunk của nó là một chỗ sửa:
  - Số `-a,b` ở dòng `@@`: chỗ sửa nằm ở dòng nào trong After.
  - Số `+c,d`: chỗ đó ở Latest là những dòng nào.
- **Không mang diff này theo.** Phần lớn nội dung của nó là code của feature khác. Bước 4 chỉ dùng nó để biết vùng RT ở Latest nằm đâu và đã đổi gì.
- Diff trống: X ở Latest giống hệt After. Mọi vùng RT là `KEEP`, sang Bước 5.

## Bước 4 — Cập nhật code RT của từng vùng RT

### 4.1 Mục tiêu và đầu vào

- **Cập nhật code RT** là thay code RT viết ở After bằng bản hiện tại của chính đoạn code đó ở Latest. Mục tiêu là có "code RT ở Latest" cho từng vùng RT.
- Mỗi đoạn code của RT có ba phiên bản:

| Phiên bản | Là gì | Lấy ở đâu |
|---|---|---|
| Before | Code trước khi làm RT | Dòng `-` của diff RT. **Giữ nguyên** |
| After | Code RT viết, ở thời điểm làm RT | Dòng `+` của diff RT, nằm trong vùng RT |
| Latest | Chính đoạn code đó ở hiện tại | Bước 4 đi tìm. Dùng thay cho bản After |

- Đầu vào cho mỗi vùng RT:
  - Khoảng dòng của vùng RT trong After (Bước 2).
  - Các hunk của diff sau RT (Bước 3).

### 4.2 Xét từng hunk của diff sau RT so với vùng RT

- Mỗi hunk của diff sau RT là một trong hai dạng:
  - **Sửa / xoá dòng After:** có dòng `-`. Các dòng After bị đụng tới là dòng `a` đến dòng `a+b−1`.
  - **Chèn dòng mới:** chỉ có dòng `+`. Nhìn dòng context ngay trên để biết chèn sau dòng After nào.
- Phân loại so với vùng RT (ví dụ vùng RT là dòng 50–54):

| Hunk của diff sau RT | Phân loại | Ví dụ | Xử lý |
|---|---|---|---|
| Các dòng After bị sửa/xoá nằm hẳn trong vùng RT | **Trong vùng** | Sửa dòng 52 | Là thay đổi của chính code RT. Lấy theo |
| Chèn vào **giữa** hai dòng đều thuộc vùng RT | **Trong vùng** | Chèn sau dòng 52 | Lấy theo |
| Các dòng After bị sửa/xoá nằm hẳn ngoài vùng RT | **Ngoài vùng** | Sửa dòng 20 | Code khác. Bỏ qua |
| Chèn ngay **trên dòng đầu** hoặc ngay **dưới dòng cuối** của vùng RT | **Ngoài vùng** | Chèn sau dòng 49, hoặc sau dòng 54 | Code khác, chỉ nằm sát cạnh. Bỏ qua |
| Các dòng After bị sửa/xoá có dòng trong vùng, có dòng ngoài vùng | **Vắt qua mép** | Sửa dòng 53–56 | Không tách được phần nào thuộc RT. `NEED_CONFIRM` |

### 4.3 Kết luận cho vùng RT

| Tình huống | Nhãn | Code RT mới |
|---|---|---|
| Không có hunk nào trong vùng và không có hunk vắt qua mép | `KEEP` | Giữ nguyên code After. Giữ nguyên hunk của diff RT |
| Có hunk trong vùng, không có hunk vắt qua mép, và còn ít nhất một dòng của vùng RT giữ nguyên ở Latest | `UPDATED` | Đoạn Latest từ **mép trên** tới **mép dưới** của vùng (xem 4.4). Gồm cả dòng RT sau sửa và dòng RT sau chèn vào giữa |
| Mọi dòng của vùng RT đều bị xoá, không có gì thay vào | `DROPPED` | Không còn. Loại hunk khỏi feature |
| Mọi dòng của vùng RT đều bị sửa (viết lại hẳn) | `NEED_CONFIRM` | Không đoán. Đưa bản After và bản Latest để hỏi |
| Có hunk vắt qua mép | `NEED_CONFIRM` | Không đoán. Đưa bản After, bản Latest và hunk vắt mép để hỏi |

- Mọi hunk của X đều `DROPPED`: loại X khỏi feature, ghi vào "Bỏ qua".
- Đơn vị `Add`: vùng RT là cả X, nên mọi thay đổi của diff sau RT đều nằm trong vùng. Kết quả chỉ có thể là:
  - Diff sau RT trống: `KEEP`, giữ nguyên diff RT (cả X là dòng `+` như ở After).
  - Diff sau RT có thay đổi: `UPDATED`, code RT mới là toàn bộ `<X>.latest.c`. Report liệt kê các dòng khác After.

### 4.4 Tìm đoạn Latest của vùng RT (cho `UPDATED`)

- **Độ lệch của một dòng After** = tổng (số dòng `+` − số dòng `-`) của mọi hunk của diff sau RT nằm **phía trên** dòng đó.
- **Dòng After không bị sửa** ở dòng `n` thì ở Latest là dòng `n + độ lệch`.
- **Mép trên** (dòng đầu của đoạn Latest):
  - Dòng đầu vùng RT không bị sửa: là dòng tương ứng của nó ở Latest.
  - Dòng đầu vùng RT bị sửa: là dòng `c` (dòng đầu phía `+c,d`) của hunk đã sửa nó.
  - Dòng đầu vùng RT bị xoá hẳn: lấy dòng kế tiếp phía trong vùng còn ở Latest.
- **Mép dưới** (dòng cuối của đoạn Latest): làm tương tự với dòng cuối vùng RT. Bị sửa thì lấy dòng `c+d−1` của hunk đã sửa nó.
- Ví dụ:

```text
Vùng RT: After dòng 50–54 (hunk 2 của diff RT)

Diff sau RT có 3 hunk:
  (1) chèn 4 dòng sau dòng 20             → ngoài vùng → bỏ qua
  (2) @@ -52,1 +56,2 @@ sửa dòng 52 → 2 dòng → trong vùng → lấy theo

  (3) chèn 1 dòng sau dòng 54             → sát mép dưới, ngoài vùng → bỏ qua

Mép trên: dòng 50 không bị sửa. Phía trên có hunk (1): +4 → Latest dòng 54
Mép dưới: dòng 54 không bị sửa. Phía trên có (1): +4 và (2): +2−1 = +1 → Latest dòng 59

Kết quả: UPDATED. Code RT mới = Latest dòng 54–59
  54  if (retCode != OK) {                       ← dòng 50 của After
  55      LogPrint("GetAllVari NG");             ← dòng 51
  56      artLibClearCache(subSystemId);         ← dòng 52 `artLibSetVarDate(&vari);`
  57      artLibSetVarDate(&vari, TRUE);            bị RT sau sửa thành 2 dòng này
  58      return retCode;                        ← dòng 53
  59  }                                          ← dòng 54
  60  artLibNotify(subSystemId);                 ← hunk (3), ngoài vùng, KHÔNG lấy
```

### 4.5 Biến cục bộ và tham số mà code RT mới dùng

- Với mỗi vùng `UPDATED`, xem code RT mới có dùng biến cục bộ hoặc tham số nào **không có trong `<X>.before.c` và không có trong code RT ở After**.
- **Biến cục bộ:** mang theo dòng khai báo của nó ở Latest, thành một hunk chỉ có dòng `+`. Đặt ngay sau dòng khai báo đứng trước nó ở Latest mà Before cũng có.
  - Chỉ mang dòng khai báo. Các dòng khác ngoài vùng RT có dùng biến đó là code khác, không lấy.
  - Dòng khai báo có dùng tên khác (ví dụ `int retryCnt = RETRY_MAX;`): tên đó được trace ở Bước 6.
  - Ví dụ: code RT mới có `LogPrint("NG: retry=%d", retryCnt);`, mà `int retryCnt = 0;` khai báo ở đầu hàm, ngoài vùng RT → mang theo dòng `int retryCnt = 0;`.
- **Tham số mới của X** (chữ ký của X ở Latest đã đổi): ghi `NEED_CONFIRM`. Đổi chữ ký kéo theo mọi nơi gọi X, không tự quyết.

## Bước 5 — Dựng diff (new)

- Dựng `WORK/phase2/fn/<file>/<X>.feature.c`:
  - Bắt đầu từ `<X>.before.c` (đơn vị `Add`: bắt đầu từ file rỗng).
  - Với mỗi hunk của diff RT, thay dòng `-` bằng code RT: bản After nếu `KEEP`, bản Latest nếu `UPDATED`. Áp từ dưới lên trên để không làm lệch vị trí các hunk chưa áp.
  - Hunk chỉ có dòng `-`: áp như cũ (xoá các dòng đó).
  - Thêm các dòng khai báo biến ở mục 4.5.
  - Không áp hunk `DROPPED` và hunk `NEED_CONFIRM` chưa trả lời: chỗ đó giữ nguyên code Before.
- Gọi `get-diff(<X>.feature.c, <X>.before.c)`. Đây là **diff (new)** của X.
  - Số dòng trong diff là số dòng bên trong đơn vị.
  - Code xung quanh (context) của diff là code Before. Phase 3 dùng nó để tìm vị trí trong FOMULAR, vì FOMULAR gần giống Before.
- Kiểm tra nhanh: nếu mọi hunk của X là `KEEP` thì `<X>.feature.c` phải giống hệt `<X>.after.c`.

---

## Bước 6 — Trace phụ thuộc

- Mục tiêu: lấy ra **đủ mọi thứ** mà code mới nhất của RT cần. Thiếu một thứ là FOMULAR lỗi compile hoặc chạy sai.

### Xuất phát từ đâu

- Các dòng `+` của diff (new) (Bước 5).
- Toàn bộ định nghĩa của các đồ mới tìm ra trong lúc trace (`DEP_NEW`).
- **Không** trace từ dòng context hay từ phần còn lại của hàm Latest. Những dòng đó không phải code của RT.

### Cần lần theo những gì

- **Hàm được gọi.**
- **Những thứ định nghĩa bên ngoài hàm:** biến global / `static` / `extern`, macro, `enum`, `struct` / `typedef` (và field được dùng), bảng dữ liệu, prototype.
- **Những thứ mà chính các định nghĩa đó dùng**, ví dụ kích thước mảng là một macro, field có kiểu là một struct khác.
- Bỏ qua biến cục bộ, tham số (đã xử lý ở mục 4.5) và hàm thư viện chuẩn / hệ thống (`memcpy`, `strcpy`, `printf`...).

### Mỗi tên tìm được thì xử lý thế nào

- Tìm định nghĩa ở Latest, rồi so với **Before** (source TELINDY ngay trước khi làm RT):

| Kết quả | Nhãn | Làm gì tiếp |
|---|---|---|
| Before chưa có | `DEP_NEW` | Mang **nguyên** định nghĩa Latest, toàn bộ là `+` (hàm thì lấy cả prototype). Trace tiếp vào bên trong |
| Giống hệt Before | `DEP_PAUSED` | **Tạm dừng**, không đi sâu. Ghi vào `paused.md` cho Phase 3 |
| Khác Before, và dòng `+` **dùng tới chỗ đã đổi** | `DEP_CHANGED` | Mang phần đã đổi (xem bảng dưới). Trace tiếp vào phần đó |
| Khác Before, nhưng dòng `+` dùng nó **đúng như cách cũ** (chỉ thân hàm đổi) | `NEED_CONFIRM` | Đưa diff Before–Latest của định nghĩa để hỏi. Chưa mang, chưa ghi vào `paused.md` |
| Không tìm thấy định nghĩa | `UNRESOLVED` | Ghi vào "Cần xác nhận" |
| Thấy ở nhiều chỗ, không biết chỗ nào đúng | `NEED_CONFIRM` | Ghi vào "Cần xác nhận", đưa các vị trí |

- **Không so với After.** After đã chứa code của chính RT. So với After thì những thứ RT thêm vào sẽ trông như "đồ cũ" và bị bỏ sót.
- File chứa định nghĩa không có trong `request/Before/` (không so được): ghi `DEP_PAUSED`, ghi chú "không có bản Before để so". Phase 3 sẽ kiểm tra với FOMULAR.

### `DEP_CHANGED` — mang phần nào

| Chỗ đã đổi mà dòng `+` dùng tới | Mang gì | Ví dụ |
|---|---|---|
| Giá trị macro, kích thước mảng, kiểu của biến | Định nghĩa mới ở Latest | `RCP_BUF_SIZE` đổi 256→512 |
| Field mới của struct, hằng mới của enum, phần tử mới của bảng dữ liệu | Chỉ đúng field / hằng / phần tử đó (một hunk `+`), không lấy các thay đổi khác của định nghĩa | Dòng `+` dùng `rcp->varDate`, field `varDate` mới thêm vào struct |
| Chữ ký hàm (thêm bớt tham số, đổi kiểu trả về) | Toàn bộ khác biệt Before–Latest của hàm đó, vì không tách riêng được. Ghi rõ trong report: có thể kèm code của RT khác | Dòng `+` gọi `RcpIfGetAllVari(id, name, &vari, flag)`, tham số `flag` mới thêm |

- Cắt bản Before và bản Latest của định nghĩa ra `WORK/phase2/fn/` và dựng diff như Bước 5.

### Vì sao tạm dừng ở đồ cũ (`DEP_PAUSED`)

- Hàm dùng chung (ví dụ `RcpIfGetAllVari`) lại gọi tiếp module khác, rồi tới tầng OS, driver... Đi tới cùng thì gần như phải đọc hết source.
- Đồ cũ có từ trước RT. Feature không sửa gì nó, chỉ dùng tới nó. FOMULAR thường đã có sẵn.
- **Tạm dừng, không phải bỏ.** Before là của TELINDY, không phải của FOMULAR. Phase 3 kiểm tra danh sách này với FOMULAR, thiếu thứ nào thì mang sang và trace tiếp vào trong thứ đó.

### Lưu ý khi lần theo

- Chỉ đi xuôi: từ code của RT đi vào bên trong. Không tìm ngược "ai đang gọi hàm này".
- Mỗi tên chỉ xét một lần. Dừng khi không còn tên mới.
- Phụ thuộc nằm ở file khác: vẫn ghi diff cho file đó ở Bước 7, ghi rõ trong report là file được thêm vì phụ thuộc.
- Không hỏi người dùng chỉ vì code mới gọi thêm hàm hoặc dùng thêm biến mới.

### Ghi danh sách tạm dừng

- Lưu vào `WORK/phase2/paused.md`. Đây là đầu vào của Phase 3:

```markdown
| Tên | Loại | Tìm ra từ (đơn vị nào dùng nó) | Định nghĩa ở Latest (file:dòng) | Chữ ký / kiểu / giá trị |
|---|---|---|---|---|
| RcpIfGetAllVari | hàm | artLibLinkOnVarSet | src/rcpif.c:820 | int RcpIfGetAllVari(int, char*, char*, int*, VARI**) |
| RCP_NAME_LEN | macro | ArtLibCopyRecipeName | inc/rcp.h:45 | 32 |
```

- Cột "Chữ ký / kiểu / giá trị" giúp Phase 3 so nhanh với FOMULAR mà không phải mở lại file.

### Ví dụ

```text
ArtLibCopyRecipeName — hunk 2/3 UPDATED, các dòng + của diff (new) dùng:
 ├─ artLibLinkOnVarSet()      → Before chưa có                → DEP_NEW → trace tiếp vào trong
 │    ├─ g_varLinkTbl[]       → Before chưa có                → DEP_NEW → trace tiếp vào định nghĩa
 │    │    └─ VAR_LINK_MAX    → Before chưa có                → DEP_NEW (kích thước mảng)
 │    └─ RcpIfGetAllVari()    → giống hệt Before              → DEP_PAUSED (không mở ra đọc)
 ├─ RCP_BUF_SIZE              → Latest đổi 256→512, dòng + dùng → DEP_CHANGED
 ├─ LogPrint()                → thân hàm đổi, cách gọi như cũ → NEED_CONFIRM
 └─ RCP_NAME_LEN              → giống hệt Before              → DEP_PAUSED

Danh sách tạm dừng gửi sang Phase 3: RcpIfGetAllVari, RCP_NAME_LEN
```

---

## Bước 7 — Ghi diff (new) cho từng file

- Mỗi file ghi một diff: `WORK/phase2/diff/<đường dẫn file>.diff`. Đây là đầu vào của Phase 3.
- Diff gồm nhiều phần, mỗi đơn vị một phần. **Phía trên mỗi phần ghi một dòng chú thích:**

```text
### <tên đơn vị> | <MOD / NEW / DEL> | <nhãn> | Before: <dòng trong file> | Latest: <dòng trong file> | <ghi chú>
```

- Nội dung phần theo loại:

| Loại | Gồm những đơn vị nào | Nội dung phần |
|---|---|---|
| `MOD` (đơn vị bị sửa) | Đơn vị `Mod` của RT, `DEP_CHANGED` | `get-diff(<X>.feature.c, <X>.before.c)` (Bước 5). Số dòng tính bên trong đơn vị |
| `NEW` (đơn vị mới) | Đơn vị `Add` của RT, `DEP_NEW` | Toàn bộ `<X>.feature.c` là dòng `+` |
| `DEL` (đơn vị bị xoá) | Đơn vị `Del` của RT | Toàn bộ `<X>.before.c` là dòng `-` |

- Không có phần cho: `DROPPED`, `NOT_PORTED` (chỉ ghi vào report), `DEP_PAUSED` (chỉ ghi vào `paused.md`), `NEED_CONFIRM` chưa trả lời.
- Thêm một phần cho entry RT trong khối `Modification:` (lấy từ diff Phase 1), để Phase 3 ghi changelog cho Target.
- File `added` ở Phase 1: toàn bộ nội dung file ở Latest là `+`.
- File `deleted` ở Phase 1: ghi một dòng chú thích `DEL` cho cả file.

## Bước 8 — Report, thông báo và dừng

- Ghi `WORK/phase2/REPORT.md` theo mẫu trong `SKILL.md`, thêm các phần sau:
  - **Bảng đơn vị**: đơn vị, loại (`Add` / `Mod` / `Del`), có ở Latest không, khoảng dòng trong file ở Before / After / Latest, **RT sau đã sửa đơn vị**.
    - Cột "RT sau đã sửa": đọc khối `Modification:` của file ở `source/`. Các entry nằm **phía trên** entry của RT đang port là các RT mới hơn (xác định theo vị trí, không theo ngày). Ghi các RT có `Mod. X`.
    - Cột này **chỉ để người duyệt tham khảo**. Nó không ảnh hưởng tới việc lấy hay không lấy code; việc đó do Bước 4 quyết định.
  - **Bảng vùng RT** (mọi vùng RT của mọi đơn vị):

```markdown
| File | Đơn vị | Hunk | Vùng RT (After) | Đoạn ở Latest | Nhãn | Ghi chú |
|---|---|---|---|---|---|---|
| src/artlib.c | ArtLibGetRecipeData | 2/3 | 50–54 | 54–59 | UPDATED | dòng 52 bị sửa thành 2 dòng |
```

  - **Chi tiết vùng `UPDATED`**: trích code RT ở After và code RT mới ở Latest, đánh dấu dòng nào bị sửa hoặc chèn. Kèm các dòng khai báo biến mang theo (mục 4.5).
  - **Cây phụ thuộc**: như ví dụ ở Bước 6.
  - **Bảng phụ thuộc**:

```markdown
| Tên | Loại | Tìm ra từ (đơn vị nào dùng nó) | Định nghĩa ở Latest (file:dòng) | So với Before | Nhãn |
|---|---|---|---|---|---|
```

  - **Danh sách tạm dừng**: copy bảng từ `paused.md`, ghi rõ "Phase 3 sẽ kiểm tra với FOMULAR".
  - **Bỏ qua**: đơn vị và hunk `DROPPED`, `NOT_PORTED`, kèm lý do.
  - **Cần xác nhận**: mọi mục `NEED_CONFIRM`, `UNRESOLVED`.
- Báo cho người dùng: đường dẫn report, đường dẫn các diff (new), số lượng từng nhãn.
- Hỏi người dùng từng mục "Cần xác nhận". Ghi câu trả lời vào report và cập nhật lại diff (new), `paused.md` nếu cần:
  - Phụ thuộc chỉ đổi thân hàm, người dùng trả lời "mang theo": xử lý như `DEP_CHANGED`. Trả lời "không mang": ghi vào `paused.md`.
- Dừng, chờ người dùng xác nhận rồi mới sang Phase 3.
