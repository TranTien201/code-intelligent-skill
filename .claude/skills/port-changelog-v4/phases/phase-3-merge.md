# Phase 3 — Merge feature vào FOMULAR

## Mục tiêu

- Đưa diff feature mới nhất (kết quả Phase 2, gọi là **diff (new)**) vào bản copy của Target (`WORK/target_out/`).
- Làm theo **từng block thay đổi (hunk) bên trong đơn vị**, không thay nguyên hàm.
- Thêm vào FOMULAR mọi định nghĩa mà code vừa merge cần nhưng FOMULAR chưa có.

## Hiểu đúng trước khi làm

- **Code Before của TELINDY gần giống code hiện tại của FOMULAR.** Tên hàm giống nhau. Bên trong hàm có thể lệch một chút (tên biến, một vài dòng logic nhỏ). **Lệch tên thì merge được, lệch logic thì phải hỏi** (Bước 4.3).
- **Diff (new) viết theo code Before.** Block `-` là code Before, không phải code FOMULAR. Vì vậy block `-` chỉ là **manh mối để tìm**. Thứ bị thay là **block tương ứng trong hàm FOMULAR**, kể cả khi nó lệch một chút so với block `-`.
- **Phía `+` chép nguyên văn.** Không tự sửa code phía `+` cho hợp với FOMULAR. Ngoại lệ duy nhất: đổi tên theo bảng đổi tên đã chứng minh ở Bước 4.3. Không sửa gì khác.
- **Hai loại đơn vị, hai cách xử lý khác nhau khi FOMULAR không có:**

| Loại | Là gì | FOMULAR không có thì |
|---|---|---|
| Đơn vị **bị sửa** | Có từ Before, RT sửa bên trong (diff có hunk) | **Bỏ**, không merge. Không có gì để sửa |
| Đơn vị **mới** | Toàn bộ là `+` (RT thêm, hoặc phụ thuộc mới tìm ra khi trace) | **Thêm vào**. Code vừa merge gọi tới nó |

- **"Đơn vị" không chỉ là hàm.** Gồm: hàm và prototype, macro (`#define`), biến global / `static` / `extern`, kiểu (`struct`, `union`, `typedef`, `enum`), field của struct, hằng của enum, bảng dữ liệu / mảng khởi tạo, dòng `#include`.

## Từ khóa của Phase này

Các từ dùng chung (RT, đơn vị, bản cắt, hunk, dòng `+` / `-`, diff (new)...) xem trong `SKILL.md`.

### Hai loại đơn vị trong diff (new)

- **Đơn vị bị sửa**: đơn vị có từ Before, RT sửa bên trong. Trong diff (new), nó có dòng context (code Before giữ nguyên) và các hunk sửa / thêm / xoá dòng.
  - Ví dụ: hàm `ArtLibGetRecipeData` trong diff (new). Code Before vẫn còn, RT thay 3 dòng `-` bằng 5 dòng `+`:

    ```diff
    ### ArtLibGetRecipeData | MOD | UPDATED | Before: 3790 | Latest: 3812
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

- **Đơn vị mới**: đơn vị mà toàn bộ là dòng `+` trong diff (new): không có dòng `-`, không có dòng context. Gồm đơn vị RT thêm và phụ thuộc mới tìm ra khi trace.
  - Ví dụ: hàm `artLibSetVarDate` do RT thêm. Before chưa có nên cả hàm là dòng `+`:

    ```diff
    ### artLibSetVarDate | NEW | KEEP | Before: - | Latest: 4100
    @@ -0,0 +1,6 @@
    +static int artLibSetVarDate(VARI *vari)
    +{
    +    vari->date = RcpGetDate();
    +    g_varLinkTbl[VAR_ID_DATE].updated = TRUE;
    +    return OK;
    +}
    ```

### Tìm vị trí trong FOMULAR

- **Đoạn của FOMULAR**: các dòng trong bản cắt Target ứng với các dòng `-` của một hunk trong diff (new). Có thể lệch một chút so với dòng `-`, ví dụ khác tên biến.
  - Ví dụ: dòng `-` là `retCode = GetVari(subSystemId);`, ở FOMULAR là `retCode = GetVari(subSysId);`.
- **Diff định vị**: `get-diff(<X>.target.c, <X>.before.c)`. Cho biết đơn vị ở FOMULAR khác Before ở đâu. Lưu ở `<X>.ctx.diff`. **Chỉ để tìm vị trí, không merge.**
  - Ví dụ: hunk `@@ -30,4 +30,10 @@` cho biết FOMULAR có thêm 6 dòng riêng quanh dòng 30.
- **Độ lệch**: số dòng mà một dòng Before bị dời đi khi sang FOMULAR, do FOMULAR thêm/bớt dòng **phía trên** nó.
  - Ví dụ: phía trên có 6 dòng riêng của FOMULAR → độ lệch +6.
- **Vị trí dự kiến**: dòng Before cộng độ lệch. Là nơi dự kiến tìm thấy đoạn của FOMULAR.
  - Ví dụ: dòng Before 52, độ lệch +6 → dự kiến ở FOMULAR dòng 58.
- **Kiểu khớp**: mức độ giống của đoạn tìm được, là `EXACT`, `NEAR` hoặc `MOVED` (giải thích trong bảng nhãn của `SKILL.md`).

### Chèn đơn vị mới

- **Symbol neo**: đơn vị đứng ngay trên (hoặc ngay dưới) đơn vị mới trong file Latest. Dùng để chọn chỗ chèn ở Target.
  - Ví dụ: ở Latest, `artLibSetVarDate` nằm ngay sau `ArtLibPutOsfData` → ở Target chèn ngay sau `ArtLibPutOsfData`.

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
   ├─ Block FOMULAR khác logic / đổi tên không chứng minh được → NEED_CONFIRM
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
- **Có định nghĩa X:** cắt nguyên định nghĩa ra `WORK/phase3/fn/<file>/<X>.target.c` (hàm: theo phạm vi ở `SKILL.md`, gồm cả comment đầu hàm). Ghi khoảng dòng gốc trong file Target.
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
- **Độ lệch của một dòng Before** = tổng (số dòng `+` − số dòng `-`) của mọi hunk của `<X>.ctx.diff` nằm **phía trên** dòng đó. Không có hunk nào phía trên thì độ lệch là 0.
- **Vị trí dự kiến ở FOMULAR = dòng Before + độ lệch.**
- Ví dụ:

```text
Hunk của diff (new):  Before dòng 52–55
<X>.ctx.diff có:      @@ -30,4 +30,10 @@   (4 dòng -, 10 dòng +) → độ lệch = 10 − 4 = +6
Vị trí dự kiến:       FOMULAR dòng 58–61
```

### 4.2 Khoanh vùng và tìm theo nội dung

- **Vị trí chỉ để khoanh vùng. Nội dung mới là thứ quyết định.**
- Tìm theo thứ tự, dừng ở bước đầu tiên tìm được:

| Thứ tự | Tìm ở đâu | Tìm gì | Kiểu khớp |
|---|---|---|---|
| 1 | Đúng vị trí dự kiến | Block `-` và các dòng context, giống nguyên văn (bỏ qua khoảng trắng thừa) | `EXACT` |
| 2 | Vùng quanh vị trí dự kiến (10 dòng trên, 10 dòng dưới) | Như trên | `EXACT` |
| 3 | Vùng quanh vị trí dự kiến | Block chỉ khác tên, **đạt đủ điều kiện ở 4.3**. Dùng `<X>.ctx.diff` để xem các dòng `-` đó ở FOMULAR đã thành dòng nào | `NEAR` |
| 4 | Cả đơn vị X | Nguyên văn, hoặc đạt điều kiện ở 4.3, có **đúng một** ứng viên | `MOVED` |

- Không tìm được, hoặc ngoài vùng dự kiến có từ hai ứng viên trở lên: `NEED_CONFIRM`. Đưa block `-`, vị trí dự kiến và các ứng viên.
- Block `-` xuất hiện nhiều lần trong đơn vị (ví dụ nhiều đoạn kiểm tra `retCode` giống nhau): chọn theo vị trí dự kiến và dòng context, **không** lấy chỗ khớp đầu tiên.
- Các hunk trong cùng đơn vị phải giữ **đúng thứ tự trên-dưới** như ở Before. Vị trí tìm được của hunk sau nằm trên hunk trước là dấu hiệu tìm sai: `NEED_CONFIRM`.

### 4.3 Điều kiện "chỉ khác tên" (bắt buộc với `NEAR` và `MOVED`)

- **Khác tên thì merge được. Khác logic thì phải hỏi.** Thêm, bớt hay đổi logic đều phải gắn `NEED_CONFIRM`.
- Áp dụng cho mọi khớp không phải `EXACT`: block FOMULAR thay cho block `-`, và các dòng neo của hunk chỉ có `+`.
- Không đạt dù chỉ một điều kiện thì gắn `NEED_CONFIRM` và không merge.

#### Các điều kiện

1. **So từng token.** Bỏ khoảng trắng và comment, rồi đặt block `-` cạnh block FOMULAR để so từng token theo thứ tự.
2. **Cấu trúc giống hệt.** Cùng số câu lệnh, cùng thứ tự câu lệnh. Từ khoá, toán tử, dấu ngoặc, giá trị literal (số, chuỗi, ký tự) và **tên hàm được gọi** phải giống hệt nhau.
3. **Chỉ được khác ở tên**: biến cục bộ, tham số, biến global, field, macro hoặc hằng enum. Ghi mỗi cặp khác nhau vào **bảng đổi tên** theo dạng `tên Before → tên FOMULAR`.
4. **Nhất quán 1-1.** Trong hunk và các dòng context, một tên Before luôn ứng với đúng một tên FOMULAR, và ngược lại.
5. **Mỗi cặp tên phải được chứng minh là cùng ý nghĩa.** Hai tên chỉ "nghe giống nhau" (ví dụ `idx` và `no`) thì chưa đủ.

| Loại tên | Coi là cùng ý nghĩa khi | Xem ở đâu |
|---|---|---|
| Tham số | Cùng vị trí trong chữ ký hàm và cùng kiểu | Dòng chữ ký trong `<X>.before.c` và `<X>.target.c` |
| Biến cục bộ | Cùng kiểu, **và** lần gán gần nhất phía trên hunk lấy từ cùng một nguồn: cùng hàm được gọi, cùng tham số, hoặc cùng biểu thức / hằng | Dòng khai báo và lệnh gán trong hai bản cắt |
| Biến global / field | Cùng kiểu, **và** được khởi tạo hoặc gán từ cùng một nguồn | Định nghĩa ở source Before và ở `target/` |
| Macro / hằng enum / tên trong biểu thức giá trị | Triển khai ra **cùng một giá trị cuối** | `#define` / `enum` ở source Before và ở `target/` |

- Nếu nguồn của một tên lại là một biến khác, kiểm tiếp biến đó theo cùng bảng. Kiểm tối đa 3 cấp. Quá 3 cấp thì không đạt.
- Không tìm được nguồn, nguồn khác nhau, hoặc chỉ đoán theo tên thì **không đạt**.

#### Đạt hết các điều kiện

- Ghi kiểu khớp `NEAR` (hoặc `MOVED`) và merge.
- **Đổi tên phía `+` theo bảng đổi tên.** Chỉ thay đúng các tên có trong bảng, thay nguyên token (không thay chuỗi con). Mọi thứ khác giữ nguyên văn.
- Dòng `+` có thể dùng một tên biến cục bộ / tham số của Before mà không nằm trong block `-`. Nếu FOMULAR không có tên đó, tìm tên tương ứng ở FOMULAR qua `<X>.ctx.diff` rồi chứng minh theo bảng trên. Chứng minh được thì thêm vào bảng đổi tên. Không chứng minh được thì gắn `NEED_CONFIRM` cho cả hunk.
- Biến mới mà phía `+` tự khai báo thì giữ nguyên tên.

```text
diff (new):    - retCode = GetX(idx);
               + retCode = GetXWithMode(idx, MODE_A);
FOMULAR:         ret = GetX(no);
Bảng đổi tên:    retCode → ret   (cùng kiểu INT, cùng gán từ GetX)
                 idx     → no    (cùng là tham số thứ 1, kiểu UINT)
Áp vào:          ret = GetXWithMode(no, MODE_A);
```

#### Ví dụ

| # | Block `-` (Before) | Block FOMULAR | Kết quả | Lý do |
|---|---|---|---|---|
| 1 | `retCode = GetX(idx);` | `ret = GetX(no);`, trong đó `idx` và `no` đều là tham số thứ 1, kiểu `UINT` | `NEAR`, merge | Chỉ khác tên, cả hai cặp đã chứng minh được |
| 2 | `retCode = GetX(idx);` | `ret = GetX(no);`, trong đó `idx` là tham số, còn `no = GetCurNo();` | `NEED_CONFIRM` | `idx` và `no` khác nguồn |
| 3 | `retCode = GetX(idx);`, với `idx = RCP_ID;` và `#define RCP_ID 3` | `ret = GetX(ID);`, với `#define ID 3` | `NEAR`, merge | Cùng giá trị cuối là 3 |
| 4 | Như #3 | `ret = GetX(ID);`, với `#define ID 5` | `NEED_CONFIRM` | Khác giá trị |
| 5 | `if (cnt > 5)` | `if (cnt > 10)` | `NEED_CONFIRM` | Khác literal |
| 6 | `if (a && b)` | `if (a \|\| b)` | `NEED_CONFIRM` | Khác toán tử |
| 7 | `GetX(idx);` | `GetXEx(idx);` | `NEED_CONFIRM` | Gọi hàm khác |
| 8 | `Init(); Run();` | `Init(); if (IsFom()) { Adj(); } Run();` | `NEED_CONFIRM` | FOMULAR có thêm logic |
| 9 | `Clear(buf); Send(buf);` | `Send(buf);` | `NEED_CONFIRM` | FOMULAR thiếu logic |
| 10 | `a = 1; b = 2;` | `b = 2; a = 1;` | `NEED_CONFIRM` | Đổi thứ tự câu lệnh |
| 11 | `retCode = GetX(i); if (retCode)` | `ret = GetX(i); if (retCode)` | `NEED_CONFIRM` | Đổi tên không nhất quán: `retCode` vừa thành `ret` vừa giữ nguyên |
| 12 | Hunk chỉ có `+`, chèn giữa `Init();` và `Run();` | `Init(); Log(); Run();` | `NEED_CONFIRM` | FOMULAR có logic riêng giữa hai neo |

### 4.4 Xử lý theo loại hunk

| Loại hunk | Cách làm |
|---|---|
| Có `-` và `+` (sửa) | Xác định block của FOMULAR ứng với block `-`. Thay **block của FOMULAR** bằng phía `+` |
| Chỉ có `+` (thêm) | Lấy dòng context ngay trên và ngay dưới của hunk làm neo, tìm hai neo đó ở FOMULAR theo 4.1 và 4.2. Chèn phía `+` vào giữa |
| Chỉ có `-` (xoá) | Xác định block của FOMULAR ứng với block `-`. Xoá block đó |

- **Trước khi áp, kiểm tra FOMULAR đã có sẵn chưa:** tại vị trí dự kiến đã có đúng phía `+` (và không còn block `-`) thì ghi `SKIP_EXISTS`, không làm gì.
- **Hunk chỉ có `+` mà giữa hai neo FOMULAR có thêm dòng riêng:** `NEED_CONFIRM`, vì FOMULAR có logic riêng giữa hai neo (ví dụ 12 ở 4.3).
- **Khớp `NEAR` hoặc `MOVED`:** chỉ thay khi đạt 4.3. Report trích block `-` gốc, block thực tế của FOMULAR, bảng đổi tên kèm bằng chứng của từng cặp, và phía `+` sau khi đổi tên, để người duyệt kiểm.
- **Không tự thay, ghi `NEED_CONFIRM`** khi:
  - Block của FOMULAR **không đạt 4.3**: thêm, thiếu hoặc đổi logic so với block `-` (thay vào sẽ làm mất logic riêng của FOMULAR), hoặc có cặp tên không chứng minh được cùng ý nghĩa.
  - Block của FOMULAR thiếu phần lớn các dòng của block `-`, hoặc không xác định được dòng đầu và dòng cuối của block.
  - Neo của hunk chỉ có `+` không tìm thấy ở FOMULAR.
- **Không áp K và logic liên quan tới K.** Logic không liên quan vẫn áp (4.5). Chỗ không áp giữ nguyên code Target cho tới khi người dùng trả lời.
- Một hunk bị `NEED_CONFIRM` không dừng các hunk khác. Làm tiếp phần còn lại.

### 4.5 Một phần của hunk cần xác nhận

- Trong hunk, logic nào cần `NEED_CONFIRM` thì gọi là **K**.
- Xét các logic **nằm dưới K, trong cùng hunk**:
  - **Liên quan tới K** (dùng biến mà K ghi hoặc kiểm tra, hoặc nằm trong `if` / vòng lặp mà K sửa): không merge, gắn `NEED_CONFIRM` với lý do "chờ xác nhận K".
  - **Không liên quan tới K**, và tự nó đạt 4.3: merge như bình thường.
- Không chắc có liên quan hay không thì coi là liên quan.

Ví dụ:

```text
-    if (retCode != OK) {                     K   FOMULAR có thêm `|| IsFom()`   → NEED_CONFIRM
+    if (retCode != OK && retCode != WARN) {
         return retCode;
     }
+    if (retCode == WARN) { cnt = 0; }            dùng retCode mà K kiểm tra      → NEED_CONFIRM, chờ K
-    len = 10;                                    không liên quan K               → MERGED
+    len = RCP_NAME_LEN;
```

### 4.6 Ghép lại vào file

- Áp các hunk của một đơn vị **từ dưới lên trên**, để việc thêm bớt dòng không làm lệch vị trí các hunk chưa áp.
- Xong một đơn vị: tìm lại định nghĩa X trong `target_out/<file>` theo tên, thay nguyên khoảng dòng đó bằng nội dung `<X>.merged.c`.
- Kết quả ghi cho từng hunk đã áp: `MERGED`, kèm loại hunk (sửa / thêm / xoá) và kiểu khớp.

### 4.7 Đơn vị bị RT xoá hẳn

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
| FOMULAR không có T (macro, biến, kiểu) | Lấy định nghĩa T ở Latest mang sang, chèn theo Bước 5. Rồi **trace tiếp vào trong T** | `MERGED_DEP` |
| FOMULAR không có T (hàm), code RT (`WORK/phase1/diff/*.diff`) có định nghĩa T | Lấy định nghĩa T ở Latest mang sang, chèn theo Bước 5. Rồi **trace tiếp vào trong T** | `MERGED_DEP` |
| FOMULAR không có T (hàm), code RT cũng không có định nghĩa T | Không mang sang, kể cả khi Latest có. Không trace vào trong T. Lý do: "Cần khách hàng cung cấp source của function này" | `NEED_CONFIRM` |

- **Trace tiếp vào trong T:** lần theo mọi tên mà định nghĩa của T dùng tới (hàm được gọi, biến, macro, kiểu, field, kích thước mảng...). Với mỗi tên con, hỏi cùng câu hỏi: **FOMULAR đã có chưa?**
  - Có, cùng chữ ký / kiểu / giá trị: dừng.
  - Không có: xử lý theo đúng bảng trên. Hàm thì tìm định nghĩa trong code RT trước khi mang sang.
  - Có nhưng khác: `NEED_CONFIRM`.
- Mỗi tên chỉ xét một lần, kể cả các tên đã xử lý ở Bước 4 và Bước 5. Dừng khi không còn tên mới.
- Bỏ qua biến cục bộ, tham số và hàm thư viện chuẩn / hệ thống (`memcpy`, `strcpy`, `printf`...).

### Ví dụ

```text
paused.md: RcpIfGetAllVari, RCP_NAME_LEN, rcpVarCheck, LogPrint

 ├─ RcpIfGetAllVari → FOMULAR có, cùng chữ ký        → SKIP_EXISTS
 ├─ LogPrint        → FOMULAR có, thân hàm khác       → SKIP_EXISTS (bản riêng FOMULAR, giữ nguyên)
 ├─ RCP_NAME_LEN    → FOMULAR có nhưng giá trị 16≠32  → NEED_CONFIRM
 └─ rcpVarCheck     → FOMULAR KHÔNG có, code RT có (artrcp.c.diff:45) → MERGED_DEP, trace tiếp vào trong:
       ├─ rcpVarTbl[]   → FOMULAR không có → MERGED_DEP, trace tiếp vào định nghĩa
       │    └─ RCP_VAR_MAX → FOMULAR có, cùng giá trị → dừng
       ├─ rcpVarSub()   → FOMULAR không có, code RT không có → NEED_CONFIRM: cần khách hàng cung cấp source
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
  - Thiếu: ghi vào "Cảnh báo". Trường hợp hay gặp: dòng `+` còn dùng tên TELINDY mà bảng đổi tên ở Bước 4.3 bỏ sót. **Không tự sửa**, để người duyệt quyết.
- Mọi tên trong `paused.md` và mọi tên mang thêm ở Bước 6 đều có định nghĩa trong `target_out/`.
- Prototype khớp với định nghĩa hàm.
- Mỗi hàm đã thêm hoặc sửa: comment đầu hàm trong `target_out/` khớp với diff Phase 1 (đủ các dòng Function / Summary / Argument / Return).
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

  - **Chi tiết khớp `NEAR` / `MOVED`**: với mỗi hunk, trích block `-` gốc, block thực tế của FOMULAR, phía `+` đã thay vào (sau khi đổi tên), và bảng đổi tên:

```markdown
| Tên Before | Tên FOMULAR | Loại | Bằng chứng (file:dòng của nguồn / giá trị) |
|---|---|---|---|
| idx | no | tham số | thứ 1, kiểu UINT: before.c:1, target.c:1 |
```

  - **Đơn vị mới đã thêm**: tên, loại, lấy từ đâu ở Latest, chèn ở đâu (file, dòng, neo), được kéo theo từ đơn vị nào.
  - **Danh sách tạm dừng**: từng tên trong `paused.md` và kết quả kiểm tra. Với hàm không có ở FOMULAR, ghi thêm: gọi từ đâu (file:dòng) và kết quả tìm ở code RT (file diff:dòng, hoặc "không có"). Tên được mang sang thì vẽ cây trace tiếp như ví dụ ở Bước 6.
  - **Bỏ qua**: các `SKIP` kèm lý do.
  - **Cần xác nhận**: kèm block `-`, vị trí dự kiến, các ứng viên; hoặc bản Latest và bản FOMULAR khi khác chữ ký / kiểu / giá trị.
  - **Cảnh báo**: kết quả kiểm tra cuối, tên chưa có định nghĩa, "chưa compile" nếu không build.
- Báo cho người dùng: đường dẫn report, đường dẫn `target_out/`, đường dẫn các diff ở `WORK/phase3/diff/`, số lượng từng kết quả.
- Hỏi người dùng từng mục "Cần xác nhận". Áp dụng câu trả lời vào `target_out/` và cập nhật report.
- Không báo "hoàn tất" khi còn mục chưa được trả lời.
