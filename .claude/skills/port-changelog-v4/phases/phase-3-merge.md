# Phase 3 — Merge feature vào FOMULAR

## Mục tiêu

- Đưa diff feature mới nhất (kết quả Phase 2, gọi là **diff (new)**) vào bản copy của Target (`WORK/target_out/`).
- Làm theo **từng block thay đổi (hunk) bên trong đơn vị**, không thay nguyên hàm.
- Thêm vào FOMULAR mọi định nghĩa mà code vừa merge cần nhưng FOMULAR chưa có.

## Hiểu đúng trước khi làm

- **Code Before của TELINDY gần giống code hiện tại của FOMULAR.** Tên hàm giống nhau. Bên trong hàm có thể lệch một chút (tên biến, một vài dòng logic nhỏ).
- **Diff (new) viết theo code Before.** Block `-` là code Before, không phải code FOMULAR. Vì vậy block `-` chỉ là **manh mối để tìm**. Thứ bị thay là **block tương ứng trong hàm FOMULAR**, kể cả khi nó lệch một chút so với block `-`.
- **Phía `+` chép nguyên văn.** Không tự sửa code phía `+` cho hợp với FOMULAR.
- **Hai loại đơn vị, hai cách xử lý khác nhau khi FOMULAR không có:**

| Loại | Là gì | FOMULAR không có thì |
|---|---|---|
| Đơn vị **bị sửa** | Có từ Before, RT sửa bên trong (diff có hunk) | **Bỏ**, không merge. Không có gì để sửa |
| Đơn vị **mới** | Toàn bộ là `+` (RT thêm, hoặc phụ thuộc mới tìm ra khi trace) | **Thêm vào**. Code vừa merge gọi tới nó |

- **"Đơn vị" không chỉ là hàm.** Gồm: hàm và prototype, macro (`#define`), biến global / `static` / `extern`, kiểu (`struct`, `union`, `typedef`, `enum`), field của struct, hằng của enum, bảng dữ liệu / mảng khởi tạo, dòng `#include`.

## Đầu vào (từ Phase 2)

| Đầu vào | Nội dung |
|---|---|
| `WORK/phase2/diff/<file>.diff` | Diff (new). Mỗi đơn vị một block. Số dòng trong hunk là số dòng **bên trong đơn vị** (dòng đầu của đơn vị là dòng 1), phía `-` tính theo bản Before |
| `WORK/phase2/fn/<file>/<X>.before.c` | Đơn vị X cắt ra từ Before |
| `WORK/phase2/fn/<file>/<X>.latest.c` | Định nghĩa ở Latest của các đơn vị mới |
| `WORK/phase2/paused.md` | Phụ thuộc cũ (giống hệt Before), chưa kiểm tra với FOMULAR |
| `WORK/phase2/REPORT.md` | Đã có câu trả lời của người dùng |

## Tóm tắt luồng

```text
Bước 1. Chuẩn bị: ghép file TELINDY ↔ FOMULAR, copy file Target vào WORK/target_out/

Bước 2. Tìm đơn vị bị sửa ở FOMULAR (theo tên ĐỊNH NGHĨA, không phải chỗ gọi)
   ├─ Không có → bỏ toàn bộ diff của đơn vị đó → SKIP_NOT_IN_TARGET
   └─ Có       → cắt ra <X>.target.c

Bước 3. Lấy context định vị: get-diff(<X>.target.c, <X>.before.c)
   Chỉ để biết đơn vị ở FOMULAR lệch so với Before ở đâu. Không phải thứ để merge.

Bước 4. Áp từng hunk của diff (new)
   Tính vị trí dự kiến → khoanh vùng → tìm theo nội dung
   ├─ Hunk có - và +  → tìm block của FOMULAR ứng với block - → thay bằng phía +
   ├─ Hunk chỉ có +   → tìm điểm chèn theo dòng context       → chèn phía +
   ├─ Hunk chỉ có -   → tìm block của FOMULAR                 → xoá
   ├─ FOMULAR đã có sẵn phía +                                → SKIP_EXISTS
   └─ Không xác định được vị trí                              → NEED_CONFIRM, làm tiếp hunk khác

Bước 5. Thêm đơn vị mới (toàn +): FOMULAR chưa có thì chèn theo symbol neo

Bước 6. Kiểm tra paused.md với FOMULAR: thiếu thì mang sang và trace tiếp

Bước 7. Ghi changelog RT vào Target
Bước 8. Kiểm tra cuối
Bước 9. Report + câu hỏi → DỪNG chờ xác nhận
```

Phần dưới là chi tiết từng bước.

---

## Bước 1 — Chuẩn bị

- Ghép mỗi file TELINDY với file FOMULAR:
  - Tìm theo **cùng đường dẫn tương đối** trong `target/`.
  - Không thấy: tìm theo **cùng tên file** trong toàn bộ `target/`.
  - Có nhiều ứng viên: `NEED_CONFIRM`.
  - Không có file nào:
    - File chỉ chứa đơn vị mới (file `added` của RT, hoặc file chỉ có phụ thuộc mới): tạo file mới theo cùng đường dẫn tương đối, ghi vào report.
    - Trường hợp khác: `SKIP_NO_FILE`, ghi vào "Bỏ qua".
- File `deleted` ở Phase 1: không tự xoá file ở Target. Ghi `NEED_CONFIRM`.
- Copy các file Target liên quan vào `WORK/target_out/`, giữ cấu trúc thư mục. **Chỉ sửa trên bản copy.**

## Bước 2 — Tìm đơn vị bị sửa ở FOMULAR

- Với mỗi đơn vị bị sửa X trong diff (new), tìm **định nghĩa** của X trong file Target đã ghép:
  - Hàm: dòng chữ ký có thân `{ ... }`. Chỗ gọi X hoặc prototype của X **không tính**.
  - Macro: `#define X`.
  - Biến, bảng dữ liệu: dòng khai báo ngoài hàm.
  - Kiểu: `struct X { ... }`, `typedef ... X;`, `enum X { ... }`.
- **Không có định nghĩa X:** bỏ toàn bộ diff của X. Ghi `SKIP_NOT_IN_TARGET` vào "Bỏ qua". Không hỏi người dùng, không đi tìm tên khác.
- **Có định nghĩa X:** cắt nguyên định nghĩa ra `WORK/phase3/fn/<file>/<X>.target.c` (hàm: từ dòng chữ ký tới dấu `}` đóng hàm). Ghi khoảng dòng gốc trong file Target.
  - File cắt ra có dòng đầu là dòng 1, giống cách cắt `<X>.before.c` ở Phase 2. Nhờ vậy số dòng của hai bản so được với nhau, không bị ảnh hưởng bởi code nằm phía trên đơn vị trong file gốc.

## Bước 3 — Lấy context định vị

- Gọi `get-diff(<X>.target.c, <X>.before.c)`, lưu vào `WORK/phase3/fn/<file>/<X>.ctx.diff`.
- Diff này **chỉ dùng làm context**, trả lời hai câu hỏi:
  - Đơn vị ở FOMULAR khác Before ở những dòng nào, khác thế nào (đổi tên biến, thêm bớt dòng...).
  - Mỗi đoạn của Before bị lệch bao nhiêu dòng khi sang FOMULAR.
- **Không merge diff này.** Nó không phải thay đổi của feature.
- Diff trống: X ở FOMULAR giống hệt Before. Mọi hunk áp đúng số dòng, không cần tìm.

## Bước 4 — Áp từng hunk của diff (new)

Làm trên bản copy `WORK/phase3/fn/<file>/<X>.merged.c` (ban đầu copy từ `<X>.target.c`).

### 4.1 Tính vị trí dự kiến

- Mỗi hunk của diff (new) có khoảng dòng phía Before, ví dụ dòng 52–55.
- Trong `<X>.ctx.diff`, mỗi block `@@ -a,b +c,d @@` làm phần phía dưới nó lệch đi: **độ lệch = (c + d) − (a + b)**.
- **Vị trí dự kiến ở FOMULAR = dòng Before + độ lệch của block gần nhất nằm phía trên.** Không có block nào phía trên thì độ lệch là 0.
- Ví dụ:

```text
Hunk của diff (new):  Before dòng 52–55
<X>.ctx.diff có:      @@ -30,4 +30,10 @@   → độ lệch = (30+10) − (30+4) = +6
Vị trí dự kiến:       FOMULAR dòng 58–61
```

### 4.2 Khoanh vùng và tìm theo nội dung

- **Vị trí chỉ để khoanh vùng. Nội dung mới là thứ quyết định.**
- Tìm theo thứ tự, dừng ở bước đầu tiên tìm được:

| Thứ tự | Tìm ở đâu | Tìm gì | Kiểu khớp |
|---|---|---|---|
| 1 | Đúng vị trí dự kiến | Block `-` và các dòng context, giống nguyên văn (bỏ qua khoảng trắng thừa) | `EXACT` |
| 2 | Vùng quanh vị trí dự kiến (10 dòng trên, 10 dòng dưới) | Như trên | `EXACT` |
| 3 | Vùng quanh vị trí dự kiến | Block gần giống: cùng câu lệnh, cùng thứ tự, chỉ khác tên biến / tham số / hằng số / comment. Dùng `<X>.ctx.diff` để xem các dòng `-` đó ở FOMULAR đã thành dòng nào | `NEAR` |
| 4 | Cả đơn vị X | Nguyên văn hoặc gần giống, có **đúng một** ứng viên | `MOVED` |

- Không tìm được, hoặc ngoài vùng dự kiến có từ hai ứng viên trở lên: `NEED_CONFIRM`. Đưa block `-`, vị trí dự kiến và các ứng viên.
- Block `-` xuất hiện nhiều lần trong đơn vị (ví dụ nhiều đoạn kiểm tra `retCode` giống nhau): chọn theo vị trí dự kiến và dòng context, **không** lấy chỗ khớp đầu tiên.
- Các hunk trong cùng đơn vị phải giữ **đúng thứ tự trên-dưới** như ở Before. Vị trí tìm được của hunk sau nằm trên hunk trước là dấu hiệu tìm sai: `NEED_CONFIRM`.

### 4.3 Xử lý theo loại hunk

| Loại hunk | Cách làm |
|---|---|
| Có `-` và `+` (sửa) | Xác định block của FOMULAR ứng với block `-`. Thay **block của FOMULAR** bằng phía `+` |
| Chỉ có `+` (thêm) | Lấy dòng context ngay trên và ngay dưới của hunk làm neo, tìm hai neo đó ở FOMULAR theo 4.1 và 4.2. Chèn phía `+` vào giữa |
| Chỉ có `-` (xoá) | Xác định block của FOMULAR ứng với block `-`. Xoá block đó |

- **Trước khi áp, kiểm tra FOMULAR đã có sẵn chưa:** tại vị trí dự kiến đã có đúng phía `+` (và không còn block `-`) thì ghi `SKIP_EXISTS`, không làm gì.
- **Hunk chỉ có `+` mà giữa hai neo FOMULAR có thêm dòng riêng:** chèn ngay sau neo trên, ghi kiểu khớp `NEAR` và ghi rõ trong report.
- **Khớp `NEAR` hoặc `MOVED`:** vẫn thay, nhưng report phải trích cả ba đoạn (block `-` gốc, block thực tế của FOMULAR, phía `+` đã thay vào) để người duyệt kiểm.
- **Không tự thay, ghi `NEED_CONFIRM`** khi:
  - Block của FOMULAR có **thêm câu lệnh riêng** mà Before không có (thay vào sẽ làm mất logic riêng của FOMULAR).
  - Block của FOMULAR thiếu phần lớn các dòng của block `-`, hoặc không xác định được dòng đầu và dòng cuối của block.
  - Neo của hunk chỉ có `+` không tìm thấy ở FOMULAR.
- Một hunk bị `NEED_CONFIRM` không dừng các hunk khác. Làm tiếp phần còn lại.

### 4.4 Ghép lại vào file

- Áp các hunk của một đơn vị **từ dưới lên trên**, để việc thêm bớt dòng không làm lệch vị trí các hunk chưa áp.
- Xong một đơn vị: tìm lại định nghĩa X trong `target_out/<file>` theo tên, thay nguyên khoảng dòng đó bằng nội dung `<X>.merged.c`.
- Kết quả ghi cho từng hunk đã áp: `MERGED`, kèm loại hunk (sửa / thêm / xoá) và kiểu khớp.

### 4.5 Đơn vị bị RT xoá hẳn

- Áp dụng khi diff (new) ghi cả đơn vị X là `-` (RT đã xoá X):
  - Target không có X: `SKIP_NOT_IN_TARGET`.
  - Target có X, giống Before, và grep trong `target_out/` không còn nơi nào dùng X: xoá. Ghi `DELETED`.
  - Target có X khác Before, hoặc còn nơi khác dùng X: `NEED_CONFIRM`.

---

## Bước 5 — Thêm đơn vị mới

- Áp dụng cho các đơn vị toàn `+` trong diff (new): đơn vị RT thêm và phụ thuộc mới tìm ra khi trace ở Phase 2.
- Tìm định nghĩa cùng tên trong `target_out/` (cùng file trước, sau đó các file `.h` được `#include`, cuối cùng toàn bộ `target_out/`):

| Kết quả | Xử lý | Kết quả ghi |
|---|---|---|
| FOMULAR chưa có | Thêm định nghĩa Latest, chèn theo quy tắc bên dưới. Hàm thì thêm cả prototype | `MERGED_NEW` |
| FOMULAR đã có, giống | Không làm gì | `SKIP_EXISTS` |
| FOMULAR đã có nhưng khác | Không sửa. Đưa bản Latest và bản FOMULAR để hỏi | `NEED_CONFIRM` |

- **Thêm vào bên trong định nghĩa đã có** (field mới của struct, hằng mới của enum, phần tử mới của bảng dữ liệu): đây là hunk chỉ có `+` của một đơn vị bị sửa. Xử lý theo Bước 4, không thay cả định nghĩa.

### Chèn vào đâu

- Tìm **symbol neo**: symbol nằm ngay **phía trên** đơn vị trong file Latest.
  - Target có neo: chèn ngay sau neo.
  - Target không có: thử symbol nằm ngay **phía dưới** ở Latest, chèn ngay trước nó.
  - Vẫn không có: chèn vào vùng tương ứng:
    - Macro: sau nhóm `#define` cuối cùng ở đầu file.
    - Biến global / static, bảng dữ liệu: sau nhóm khai báo biến ở đầu file.
    - Kiểu (`struct`, `typedef`, `enum`): trong file `.h` tương ứng hoặc nhóm khai báo kiểu ở đầu file.
    - Prototype: trong file `.h` tương ứng hoặc nhóm prototype ở đầu file `.c`.
    - `#include`: cuối nhóm `#include` của file.
    - Hàm: cuối file.
- Ghi vị trí đã chèn (file, dòng, neo) vào report.

---

## Bước 6 — Kiểm tra danh sách tạm dừng (`paused.md`)

### Vì sao cần bước này

- Phase 2 chỉ trace sâu vào **đồ mới**. Gặp **đồ cũ** (định nghĩa giống hệt Before) thì tạm dừng và ghi vào `paused.md`, để không phải đọc lan ra cả source.
- Before là code của TELINDY. "Có ở Before" thường là "có ở FOMULAR", nhưng **không chắc chắn**.
- Đồ cũ mà code vừa merge dùng tới **vẫn là thứ feature cần**. FOMULAR thiếu thì lỗi compile. Bước này kiểm tra thật với FOMULAR.

### Cách làm

- Với mỗi tên T trong `paused.md`, tìm định nghĩa của T trong `target_out/` (cùng file trước, sau đó các file `.h` được `#include`, cuối cùng toàn bộ `target_out/`):

| Kết quả | Xử lý | Kết quả ghi |
|---|---|---|
| FOMULAR có T, cùng chữ ký (hàm) / cùng kiểu (biến, struct) / cùng giá trị (macro) | Dừng. Thân hàm khác cũng giữ nguyên, vì feature không sửa gì T | `SKIP_EXISTS` |
| FOMULAR có T nhưng khác chữ ký / kiểu / giá trị | Không sửa. Đưa bản Latest và bản FOMULAR để hỏi | `NEED_CONFIRM` |
| FOMULAR không có T | Lấy định nghĩa T ở Latest mang sang, chèn theo Bước 5. Rồi **trace tiếp vào trong T** | `MERGED_DEP` |

- **Trace tiếp vào trong T:** lần theo mọi tên mà định nghĩa của T dùng tới (hàm được gọi, biến, macro, kiểu, field, kích thước mảng...). Với mỗi tên con, hỏi cùng câu hỏi: **FOMULAR đã có chưa?**
  - Có, cùng chữ ký / kiểu / giá trị: dừng.
  - Không có: mang sang từ Latest, rồi trace tiếp vào trong nó.
  - Có nhưng khác: `NEED_CONFIRM`.
- Mỗi tên chỉ xét một lần, kể cả các tên đã xử lý ở Bước 4 và Bước 5. Dừng khi không còn tên mới.
- Bỏ qua biến cục bộ, tham số và hàm thư viện chuẩn / hệ thống (`memcpy`, `strcpy`, `printf`...).

### Ví dụ

```text
paused.md: RcpIfGetAllVari, RCP_NAME_LEN, rcpVarCheck, LogPrint

 ├─ RcpIfGetAllVari → FOMULAR có, cùng chữ ký        → SKIP_EXISTS
 ├─ LogPrint        → FOMULAR có, thân hàm khác       → SKIP_EXISTS (bản riêng FOMULAR, giữ nguyên)
 ├─ RCP_NAME_LEN    → FOMULAR có nhưng giá trị 16≠32  → NEED_CONFIRM
 └─ rcpVarCheck     → FOMULAR KHÔNG có                → MERGED_DEP, trace tiếp vào trong:
       ├─ rcpVarTbl[]   → FOMULAR không có → MERGED_DEP, trace tiếp vào định nghĩa
       │    └─ RCP_VAR_MAX → FOMULAR có, cùng giá trị → dừng
       └─ LogPrint      → đã xét → bỏ qua
```

---

## Bước 7 — Ghi changelog vào Target

- Với mỗi file Target đã sửa, thêm entry RT vào khối `Modification:`.
- Copy entry RT gốc (ngày, người làm, mã RT) từ block changelog trong diff (new).
- **Chỉ liệt kê `Add.` / `Mod.` cho những gì đã thực sự thêm/sửa trong file đó.** Không ghi những mục `SKIP`, `NEED_CONFIRM` chưa trả lời.
- Viết theo đúng định dạng sẵn có của khối `Modification:` trong file Target (độ rộng cột, ký tự `#*/` cuối dòng, vị trí đặt entry).

## Bước 8 — Kiểm tra cuối

- Mọi file ở Phase 1 đều có kết quả cuối: `done`, `skipped` (có lý do) hoặc `blocked` (có lý do).
- Mọi hunk của diff (new) đều có kết quả: `MERGED`, `SKIP_EXISTS`, `SKIP_NOT_IN_TARGET` hoặc `NEED_CONFIRM`.
- **Mọi tên dùng trong các dòng `+` đã merge đều có định nghĩa hoặc khai báo ở FOMULAR** (grep lại từng tên trong `target_out/`, biến cục bộ và tham số thì xem trong chính hàm đó).
  - Thiếu: ghi vào "Cảnh báo". Trường hợp hay gặp: dòng `+` dùng tên biến của TELINDY, còn hàm FOMULAR đặt tên khác. **Không tự sửa**, để người duyệt quyết.
- Mọi tên trong `paused.md` và mọi tên mang thêm ở Bước 6 đều có định nghĩa trong `target_out/`.
- Prototype khớp với định nghĩa hàm.
- Không còn nơi nào dùng đơn vị đã xoá.
- Encoding và kiểu xuống dòng của file trong `target_out/` giống file Target gốc.
- Có môi trường build thì compile thử. Không có thì ghi rõ "chưa compile".

## Bước 9 — Report, thông báo và dừng

- Với mỗi file đã sửa: gọi `get-diff(target_out/<file>, target/<file>)`, lưu vào `WORK/phase3/diff/<đường dẫn file>.diff` để người duyệt xem.
- Ghi `WORK/phase3/REPORT.md` theo mẫu trong `SKILL.md`, thêm các phần sau:
  - **Bảng hunk** (mọi hunk của mọi đơn vị bị sửa):

```markdown
| File | Đơn vị | Hunk | Loại | Dòng Before | Dòng dự kiến | Dòng thực tế ở FOMULAR | Kiểu khớp | Kết quả |
|---|---|---|---|---|---|---|---|---|
| src/artlib.c | ArtLibGetRecipeData | 2/3 | sửa | 52–55 | 58–61 | 58–61 | NEAR | MERGED |
```

  - **Chi tiết khớp `NEAR` / `MOVED`**: với mỗi hunk, trích block `-` gốc, block thực tế của FOMULAR và phía `+` đã thay vào.
  - **Đơn vị mới đã thêm**: tên, loại, lấy từ đâu ở Latest, chèn ở đâu (file, dòng, neo), được kéo theo từ đơn vị nào.
  - **Danh sách tạm dừng**: từng tên trong `paused.md` và kết quả kiểm tra. Tên được mang sang thì vẽ cây trace tiếp như ví dụ ở Bước 6.
  - **Bỏ qua**: các `SKIP` kèm lý do.
  - **Cần xác nhận**: kèm block `-`, vị trí dự kiến, các ứng viên; hoặc bản Latest và bản FOMULAR khi khác chữ ký / kiểu / giá trị.
  - **Cảnh báo**: kết quả kiểm tra cuối, tên chưa có định nghĩa, "chưa compile" nếu không build.
- Báo cho người dùng: đường dẫn report, đường dẫn `target_out/`, đường dẫn các diff ở `WORK/phase3/diff/`, số lượng từng kết quả.
- Hỏi người dùng từng mục "Cần xác nhận". Áp dụng câu trả lời vào `target_out/` và cập nhật report.
- Không báo "hoàn tất" khi còn mục chưa được trả lời.
