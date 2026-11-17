# Phase 2 — Đưa feature lên bản mới nhất (Latest)

## Mục tiêu

- Code của RT lấy ở thời điểm làm RT đã cũ. Sau đó có thể có RT khác sửa tiếp đúng các đoạn code này.
- Phase này cập nhật **từng block thay đổi (hunk)** của RT lên trạng thái Latest, và mang theo mọi định nghĩa mà code mới nhất của RT cần.
- Kết quả là **diff (new)**: đầu vào của Phase 3.
- Đầu vào: `WORK/phase1/units.md`, các diff ở `WORK/phase1/diff/`.

## Hiểu đúng trước khi làm

- **Không lấy nguyên hàm ở Latest.** Hàm ở Latest có thể chứa logic của feature khác. Chỉ lấy đúng các block logic của RT.
- **Chỉ cập nhật phía `+`.** Mỗi hunk của RT có phía `-` (code Before) và phía `+` (code RT viết). Phase này đi tìm phía `+` trong Latest để lấy bản hiện tại của nó. **Phía `-` là code Before, giữ nguyên, không đụng tới.**
- **Trong block thì lấy, ngoài block thì không:**
  - Code nằm **bên trong** block logic của RT ở Latest (kể cả dòng do RT sau sửa hoặc chèn vào giữa): là logic của feature, lấy theo.
  - Code nằm **bên ngoài** các block của RT: là logic khác, không lấy.
- **Tìm đơn vị theo tên định nghĩa, không tìm đổi tên.** Đơn vị không còn tên đó ở Latest thì loại khỏi feature.
- **"Đơn vị" không chỉ là hàm.** Gồm: hàm và prototype, macro (`#define`), biến global / `static` / `extern`, kiểu (`struct`, `union`, `typedef`, `enum`), bảng dữ liệu / mảng khởi tạo.

## Tóm tắt luồng

```text
Bước 1. Tìm đơn vị ở Latest (theo tên ĐỊNH NGHĨA, cùng file)
   ├─ Đơn vị Mod (RT sửa)
   │     ├─ Latest không có → loại khỏi feature (DROPPED). Không tìm đổi tên
   │     └─ Latest có       → cắt ra <X>.before.c, <X>.after.c, <X>.latest.c → Bước 2
   ├─ Đơn vị Add (RT thêm mới)
   │     ├─ Latest không có              → loại (DROPPED)
   │     ├─ Latest có, không còn ai dùng → NOT_PORTED
   │     └─ Latest có                    → lấy NGUYÊN bản Latest, toàn bộ là + → Bước 6
   └─ Đơn vị Del (RT xoá hẳn) → giữ nguyên, toàn bộ là -

Bước 2. Lấy các hunk của RT:  get-diff(<X>.after.c, <X>.before.c)

Bước 3. Lấy context định vị:  get-diff(<X>.latest.c, <X>.after.c)
   Chỉ để biết đơn vị ở Latest lệch so với After ở đâu. Không phải thứ để mang theo.

Bước 4. Cập nhật phía + của từng hunk
   Tìm block + trong đơn vị Latest → xác định biên (dòng + đầu … dòng + cuối)
   ├─ Block giống nguyên văn       → giữ hunk như cũ                     (KEEP)
   ├─ Block đã bị sửa / chèn thêm  → mọi thứ GIỮA hai biên là + mới      (UPDATED)
   ├─ Không tìm thấy block         → loại hunk                           (DROPPED)
   ├─ Không xác định được biên     → NEED_CONFIRM
   └─ Hunk chỉ có -                → giữ nguyên                          (KEEP)

Bước 5. Dựng diff (new):  <X>.feature.c = bản Before + các hunk đã cập nhật
                          diff (new)    = get-diff(<X>.feature.c, <X>.before.c)

Bước 6. Trace phụ thuộc từ các dòng + của diff (new)
   ├─ Before chưa có                              → DEP_NEW: mang nguyên, trace tiếp
   ├─ Giống hệt Before                            → DEP_PAUSED: ghi paused.md, không đi sâu
   ├─ Khác Before, dòng + dùng tới chỗ đã đổi     → DEP_CHANGED: mang phần đã đổi, trace tiếp
   └─ Khác Before, cách dùng từ dòng + như cũ     → NEED_CONFIRM

Bước 7. Ghi diff (new) cho từng file và paused.md
Bước 8. Report + câu hỏi → DỪNG chờ xác nhận
```

Phần dưới là chi tiết từng bước.

---

## Bước 1 — Tìm đơn vị ở Latest

- Với mỗi đơn vị X trong `units.md`, tìm **định nghĩa** của X trong cùng file ở `source/`:
  - Hàm: dòng chữ ký có thân `{ ... }`. Chỗ gọi X hoặc prototype của X **không tính**.
  - Macro: `#define X`.
  - Biến, bảng dữ liệu: dòng khai báo ngoài hàm.
  - Kiểu: `struct X { ... }`, `typedef ... X;`, `enum X { ... }`.
- Xử lý theo loại đơn vị (cột Add/Mod/Del của `units.md`):

| Loại | Latest không có X | Latest có X |
|---|---|---|
| `Mod` (RT sửa) | Loại X khỏi feature. Ghi `DROPPED` vào "Bỏ qua" | Cắt X ra file riêng (xem dưới), sang Bước 2 |
| `Add` (RT thêm mới) | Loại X khỏi feature. Ghi `DROPPED` | Lấy **nguyên** định nghĩa Latest, toàn bộ là `+`. Sang Bước 6. Nếu Latest không còn nơi nào dùng X: ghi `NOT_PORTED` vào "Bỏ qua" |
| `Del` (RT xoá hẳn) | Đúng như mong đợi. Giữ nguyên: toàn bộ định nghĩa Before là `-` | RT sau đã thêm lại X. Ghi `NEED_CONFIRM` |

- **Không tìm đổi tên.** Không thấy đúng tên X trong file thì coi như không có, không đi tìm hàm khác có code giống.

### Cắt đơn vị ra file riêng

- Cắt nguyên định nghĩa của X (hàm: từ dòng chữ ký tới dấu `}` đóng hàm) ra:
  - `WORK/phase2/fn/<file>/<X>.before.c` (từ Before)
  - `WORK/phase2/fn/<file>/<X>.after.c` (từ After)
  - `WORK/phase2/fn/<file>/<X>.latest.c` (từ Latest)
- File cắt ra có dòng đầu là dòng 1. **Từ đây mọi số dòng đều tính bên trong đơn vị**, không tính theo file gốc.
  - Lý do: ở Latest, code nằm phía trên X trong file có thể đã thêm bớt rất nhiều, làm số dòng trong file gốc lệch hẳn. Cắt riêng ra thì ba bản của X so được với nhau.
- Ghi khoảng dòng gốc (trong file Before / After / Latest) vào report.

### Ghi nhận RT sau đã sửa X

- Đọc khối `Modification:` của file ở `source/`. Các entry nằm **phía trên** entry của RT đang port là các RT mới hơn (xác định theo vị trí, không theo ngày).
- Ghi lại RT nào có `Mod. X`. Thông tin này **chỉ để ghi vào report** cho người duyệt. Việc lấy hay không lấy code do Bước 4 quyết định, không dựa vào changelog.

## Bước 2 — Lấy các hunk của RT

- Gọi `get-diff(<X>.after.c, <X>.before.c)`, lưu vào `WORK/phase2/fn/<file>/<X>.rt.diff`.
- Mỗi block `@@` là một hunk của RT. Đánh số hunk 1, 2, 3... từ trên xuống.
- Mỗi hunk thuộc một trong ba loại: có `-` và `+` (sửa), chỉ có `+` (thêm), chỉ có `-` (xoá).

## Bước 3 — Lấy context định vị

- Gọi `get-diff(<X>.latest.c, <X>.after.c)`, lưu vào `WORK/phase2/fn/<file>/<X>.ctx.diff`.
- Diff này **chỉ dùng làm context**, trả lời hai câu hỏi:
  - Từ After tới Latest, X đã bị sửa ở những dòng nào, sửa thế nào.
  - Mỗi đoạn của After bị lệch bao nhiêu dòng khi sang Latest.
- **Không mang diff này theo.** Phần lớn nội dung của nó là logic của feature khác.
- Diff trống: X ở Latest giống hệt After. Mọi hunk là `KEEP`, sang Bước 5.

## Bước 4 — Cập nhật phía `+` của từng hunk

### 4.1 Tìm block `+` trong đơn vị Latest

- Thứ đi tìm là **các dòng `+` của hunk** (code RT đã viết), không phải các dòng `-`.
- **Vị trí dự kiến:**
  - Hunk có khoảng dòng phía After, ví dụ dòng 60–64.
  - Trong `<X>.ctx.diff`, mỗi block `@@ -a,b +c,d @@` làm phần phía dưới nó lệch đi: **độ lệch = (c + d) − (a + b)**.
  - Vị trí dự kiến ở Latest = dòng After + độ lệch của block gần nhất nằm phía trên. Không có block nào phía trên thì độ lệch là 0.
- **Vị trí chỉ để khoanh vùng. Nội dung mới là thứ quyết định.** Tìm theo thứ tự, dừng ở bước đầu tiên tìm được:

| Thứ tự | Tìm ở đâu | Tìm gì |
|---|---|---|
| 1 | Đúng vị trí dự kiến | Các dòng `+`, giống nguyên văn (bỏ qua khoảng trắng thừa) |
| 2 | Vùng quanh vị trí dự kiến (10 dòng trên, 10 dòng dưới) | Như trên |
| 3 | Vùng quanh vị trí dự kiến | Các dòng gần giống: cùng câu lệnh, chỉ khác tên biến / tham số / hằng số / comment. Dùng `<X>.ctx.diff` để xem dòng `+` đó ở Latest đã thành dòng nào |
| 4 | Cả đơn vị X | Nguyên văn hoặc gần giống, có **đúng một** ứng viên |

- Các dòng `+` xuất hiện nhiều lần trong đơn vị: chọn theo vị trí dự kiến và các dòng context xung quanh, **không** lấy chỗ khớp đầu tiên.
- Ngoài vùng dự kiến có từ hai ứng viên trở lên: `NEED_CONFIRM`.

### 4.2 Xác định biên của block

- **Biên trên:** dòng ở Latest ứng với dòng `+` **đầu tiên** của hunk.
- **Biên dưới:** dòng ở Latest ứng với dòng `+` **cuối cùng** của hunk.
- Dòng biên đã bị sửa: dòng thay thế nó ở Latest (xem trong `<X>.ctx.diff`) là biên.
- Dòng biên đã bị xoá hẳn: lấy dòng `+` kế tiếp phía trong còn tìm thấy làm biên.
- Ghi `NEED_CONFIRM` khi không tách được rõ dòng nào thuộc block, ví dụ một block thay đổi của `<X>.ctx.diff` vắt qua biên (vừa sửa dòng biên vừa thêm dòng mới ở phía ngoài).

### 4.3 Kết quả của từng hunk

| Tình huống | Xử lý | Nhãn |
|---|---|---|
| Các dòng giữa hai biên giống nguyên văn phía `+` của hunk | Giữ hunk như cũ | `KEEP` |
| Các dòng giữa hai biên đã khác (RT sau sửa dòng, chèn dòng, bỏ dòng) | **Mọi dòng nằm giữa hai biên ở Latest** là phía `+` mới. Không hỏi | `UPDATED` |
| Không tìm thấy dòng `+` nào của hunk ở Latest | Logic này đã bị gỡ hoặc viết lại hẳn. Loại hunk | `DROPPED` |
| Hunk chỉ có `-` | Không có `+` để cập nhật. Giữ nguyên | `KEEP` |
| Không xác định được vị trí hoặc biên | Không đoán | `NEED_CONFIRM` |

- Dòng mới nằm **ngay trên biên trên** hoặc **ngay dưới biên dưới** là ngoài block: không lấy.
- Mọi hunk của X đều `DROPPED`: loại X khỏi feature, ghi vào "Bỏ qua".
- Ví dụ:

```text
Hunk của RT (phía +):                  Ở Latest:
  if (retCode != OK) {                   if (retCode != OK) {                  ← biên trên
      LogPrint("GetAllVari NG");             LogPrint("NG: %d", retCode);      ← RT sau sửa dòng   → lấy
      artLibSetVarDate(&vari);               artLibClearCache(subSystemId);    ← RT sau chèn giữa  → lấy
      return retCode;                        artLibSetVarDate(&vari);
  }                                          return retCode;
                                         }                                     ← biên dưới
                                         artLibNotify(subSystemId);            ← ngoài block       → KHÔNG lấy
→ UPDATED: phía + mới là 6 dòng từ biên trên tới biên dưới.
```

### 4.4 Biến cục bộ và tham số mà phía `+` mới dùng

- Với mỗi hunk `UPDATED`, xem phía `+` mới có dùng biến cục bộ hoặc tham số nào **không có trong `<X>.before.c` và không có trong các hunk của RT**.
- **Biến cục bộ:** mang theo dòng khai báo của nó ở Latest, thành một hunk chỉ có `+`. Đặt ngay sau dòng khai báo đứng trước nó ở Latest mà Before cũng có.
  - Chỉ mang dòng khai báo. Các dòng khác ngoài block có dùng biến đó là logic khác, không lấy.
  - Dòng khai báo có dùng tên khác (ví dụ `int retryCnt = RETRY_MAX;`): tên đó được trace ở Bước 6.
- **Tham số mới của X** (chữ ký của X ở Latest đã đổi): ghi `NEED_CONFIRM`. Đổi chữ ký kéo theo mọi nơi gọi X, không tự quyết.

## Bước 5 — Dựng diff (new)

- Dựng `WORK/phase2/fn/<file>/<X>.feature.c`:
  - Bắt đầu từ `<X>.before.c`.
  - Áp các hunk `KEEP` và `UPDATED` (phía `-` giữ nguyên, phía `+` là bản đã cập nhật). Áp từ dưới lên trên để không làm lệch vị trí các hunk chưa áp.
  - Thêm các hunk khai báo biến ở mục 4.4.
  - Không áp hunk `DROPPED` và `NEED_CONFIRM` chưa trả lời.
- Gọi `get-diff(<X>.feature.c, <X>.before.c)`. Đây là **diff (new)** của X.
  - Số dòng trong diff là số dòng bên trong đơn vị.
  - Context của diff là code Before. Phase 3 dùng context này để định vị trong FOMULAR, vì FOMULAR gần giống Before.
- Kiểm tra nhanh: nếu mọi hunk của X là `KEEP` thì `<X>.feature.c` phải giống hệt `<X>.after.c`.

---

## Bước 6 — Trace phụ thuộc

- Mục tiêu: lấy ra **đủ mọi thứ** mà code mới nhất của feature cần. Thiếu một thứ là FOMULAR lỗi compile hoặc chạy sai.

### Xuất phát từ đâu

- Các dòng `+` của diff (new) (Bước 5).
- Toàn bộ định nghĩa của các đơn vị mới (đơn vị `Add` ở Bước 1, và các `DEP_NEW` tìm ra trong lúc trace).
- **Không** trace từ các dòng context hay từ phần còn lại của hàm Latest. Những dòng đó không phải code của feature.

### Cần lần theo những gì

- **Hàm được gọi.**
- **Những thứ định nghĩa bên ngoài hàm:** biến global / `static` / `extern`, macro, `enum`, `struct` / `typedef` (và field được dùng), bảng dữ liệu, prototype.
- **Những thứ mà chính các định nghĩa đó dùng**, ví dụ kích thước mảng là một macro, field có kiểu là một struct khác.
- Bỏ qua biến cục bộ, tham số (đã xử lý ở mục 4.4) và hàm thư viện chuẩn / hệ thống (`memcpy`, `strcpy`, `printf`...).

### Mỗi tên tìm được thì xử lý thế nào

- Tìm định nghĩa ở Latest, rồi so với **Before** (source TELINDY ngay trước khi làm RT):

| Kết quả | Nhãn | Làm gì tiếp |
|---|---|---|
| Before chưa có | `DEP_NEW` | Mang **nguyên** định nghĩa Latest, toàn bộ là `+` (hàm thì lấy cả prototype). Trace tiếp vào bên trong |
| Giống hệt Before | `DEP_PAUSED` | **Tạm dừng**, không đi sâu. Ghi vào `paused.md` cho Phase 3 |
| Khác Before, và dòng `+` **dùng tới chỗ đã đổi** | `DEP_CHANGED` | Mang phần đã đổi (xem bảng dưới). Trace tiếp vào phần đó |
| Khác Before, nhưng dòng `+` dùng nó **đúng như cách cũ** (chỉ thân hàm đổi) | `NEED_CONFIRM` | Đưa diff Before–Latest của định nghĩa và RT đã sửa nó. Chưa mang, chưa ghi vào `paused.md` |
| Không tìm thấy định nghĩa | `UNRESOLVED` | Ghi vào "Cần xác nhận" |
| Thấy ở nhiều chỗ, không biết chỗ nào đúng | `NEED_CONFIRM` | Ghi vào "Cần xác nhận", đưa các vị trí |

- **Không so với After.** After đã chứa code của chính RT. So với After thì những thứ RT thêm vào sẽ trông như "đồ cũ" và bị bỏ sót.
- File chứa định nghĩa không có trong `request/Before/` (không so được): ghi `DEP_PAUSED`, ghi chú "không có bản Before để so". Phase 3 sẽ kiểm tra với FOMULAR.

### `DEP_CHANGED` — mang phần nào

| Chỗ đã đổi mà dòng `+` dùng tới | Mang gì |
|---|---|
| Giá trị macro, kích thước mảng, kiểu của biến | Định nghĩa mới ở Latest |
| Field mới của struct, hằng mới của enum, phần tử mới của bảng dữ liệu | Chỉ đúng field / hằng / phần tử đó (một hunk `+`), không lấy các thay đổi khác của định nghĩa |
| Chữ ký hàm (thêm bớt tham số, đổi kiểu trả về) | Toàn bộ khác biệt Before–Latest của hàm đó, vì không tách riêng được. Ghi rõ trong report: có thể kèm logic của RT khác |

- Cắt bản Before và bản Latest của định nghĩa ra `WORK/phase2/fn/` và dựng diff như Bước 5.

### Vì sao tạm dừng ở đồ cũ (`DEP_PAUSED`)

- Hàm dùng chung (ví dụ `RcpIfGetAllVari`) lại gọi tiếp module khác, rồi tới tầng OS, driver... Đi tới cùng thì gần như phải đọc hết source.
- Đồ cũ có từ trước RT. Feature không sửa gì nó, chỉ dùng tới nó. FOMULAR thường đã có sẵn.
- **Tạm dừng, không phải bỏ.** Before là của TELINDY, không phải của FOMULAR. Phase 3 kiểm tra danh sách này với FOMULAR, thiếu thứ nào thì mang sang và trace tiếp vào trong thứ đó.

### Lưu ý khi lần theo

- Chỉ đi xuôi: từ code của feature đi vào bên trong. Không tìm ngược "ai đang gọi hàm này".
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
ArtLibCopyRecipeName — hunk 2/3 UPDATED, các dòng + mới dùng:
 ├─ artLibLinkOnVarSet()      → Before chưa có               → DEP_NEW → trace tiếp vào trong
 │    ├─ g_varLinkTbl[]       → Before chưa có               → DEP_NEW → trace tiếp vào định nghĩa
 │    │    └─ VAR_LINK_MAX    → Before chưa có               → DEP_NEW (kích thước mảng)
 │    └─ RcpIfGetAllVari()    → giống hệt Before             → DEP_PAUSED (không mở ra đọc)
 ├─ RCP_BUF_SIZE              → Latest đổi 256→512, + dùng   → DEP_CHANGED
 ├─ LogPrint()                → thân hàm đổi, cách gọi như cũ → NEED_CONFIRM
 └─ RCP_NAME_LEN              → giống hệt Before             → DEP_PAUSED

Danh sách tạm dừng gửi sang Phase 3: RcpIfGetAllVari, RCP_NAME_LEN
```

---

## Bước 7 — Ghi diff (new) cho từng file

- Mỗi file ghi một diff: `WORK/phase2/diff/<đường dẫn file>.diff`. Đây là đầu vào của Phase 3.
- Diff gồm nhiều block, mỗi đơn vị một block. **Phía trên mỗi block ghi một dòng chú thích:**

```text
### <tên đơn vị> | <MOD / NEW / DEL> | <nhãn> | Before: <dòng trong file> | Latest: <dòng trong file> | <ghi chú, ví dụ: RT2611 Mod>
```

- Nội dung block theo loại:

| Loại | Gồm những đơn vị nào | Nội dung block |
|---|---|---|
| `MOD` (đơn vị bị sửa) | Đơn vị `Mod` của RT, `DEP_CHANGED` | `get-diff(<X>.feature.c, <X>.before.c)` (Bước 5). Số dòng tính bên trong đơn vị |
| `NEW` (đơn vị mới) | Đơn vị `Add` của RT, `DEP_NEW` | Toàn bộ định nghĩa Latest là `+` |
| `DEL` (đơn vị bị xoá) | Đơn vị `Del` của RT | Toàn bộ định nghĩa Before là `-` |

- Không có block cho: `DROPPED`, `NOT_PORTED` (chỉ ghi vào report), `DEP_PAUSED` (chỉ ghi vào `paused.md`), `NEED_CONFIRM` chưa trả lời.
- Thêm một block cho entry RT trong khối `Modification:` (lấy từ diff Phase 1), để Phase 3 ghi changelog cho Target.
- File `added` ở Phase 1: toàn bộ nội dung file ở Latest là `+`.
- File `deleted` ở Phase 1: ghi một dòng chú thích `DEL` cho cả file.

## Bước 8 — Report, thông báo và dừng

- Ghi `WORK/phase2/REPORT.md` theo mẫu trong `SKILL.md`, thêm các phần sau:
  - **Bảng đơn vị**: đơn vị, loại (`Add` / `Mod` / `Del`), có ở Latest không, RT sau đã sửa, khoảng dòng trong file ở Before / After / Latest.
  - **Bảng hunk** (mọi hunk của mọi đơn vị `Mod`):

```markdown
| File | Đơn vị | Hunk | Loại | Dòng After | Dòng ở Latest | Nhãn | Ghi chú |
|---|---|---|---|---|---|---|---|
| src/artlib.c | ArtLibGetRecipeData | 2/3 | sửa | 60–64 | 71–76 | UPDATED | RT sau sửa 1 dòng, chèn 1 dòng giữa block |
```

  - **Chi tiết hunk `UPDATED`**: với mỗi hunk, trích phía `+` ở After và phía `+` mới ở Latest, đánh dấu dòng nào do RT sau sửa hoặc chèn. Kèm các dòng khai báo biến mang theo (mục 4.4).
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
  - Phụ thuộc bị sửa thân, người dùng trả lời "mang theo": xử lý như `DEP_CHANGED`. Trả lời "không mang": ghi vào `paused.md`.
- Dừng, chờ người dùng xác nhận rồi mới sang Phase 3.
