---
name: port-changelog-v4
description: Quy trình chuyển một chức năng (mã RT) từ máy TELINDY sang máy FOMULAR
---

# Port RT từ TELINDY sang FOMULAR

## Bài toán

- **RT** là mã yêu cầu thay đổi của khách, ví dụ `RT2486`. Một RT tương ứng với một chức năng mới hoặc một lần sửa code.
- Khách hàng không dùng git. Mỗi lần làm một RT, họ ghi một entry vào khối `Modification:` ở đầu file sửa, ví dụ:

```text
/*#         2018/08/31  Y.Kaneko (TTS-X)     RT2486                         #*/
/*#                     Add. artLibSetVarDate()                             #*/
/*#                     Mod. ArtLibGetRecipeData()                          #*/
/*#                          ArtLibPutOsfData()                             #*/
```

- Entry gồm: ngày, người làm, mã RT, rồi danh sách `Add.` (thêm) / `Mod.` (sửa) các hàm, biến, macro. Entry mới nhất nằm trên cùng.
- Khách đưa source của RT ở thời điểm làm RT (Before / After). Sau đó nhiều RT khác đã sửa tiếp các hàm này.
- Việc cần làm (**port một RT**): lấy chức năng của RT **ở trạng thái mới nhất (Latest)** rồi merge vào máy FOMULAR.

## Đầu vào

- `request/Before/`: source TELINDY **trước** khi làm RT (nhiều file).
- `request/After/`: source TELINDY **sau** khi làm RT (nhiều file).
- `source/`: source TELINDY mới nhất (Latest). Đã có RT này và mọi RT về sau.
- `target/`: source FOMULAR mới nhất (Target). Nơi cần merge RT vào.
- `WORK/`: thư mục ghi kết quả.

## Từ khóa dùng chung

Các từ dưới đây dùng ở mọi Phase, mỗi từ chỉ mang đúng một nghĩa. Từ riêng của từng Phase nằm ở đầu file hướng dẫn của Phase đó.

### RT và changelog

- **RT**: mã yêu cầu thay đổi của khách. Mỗi RT ghi một entry trong khối `Modification:`.
  - Ví dụ: `RT2486`. Mã có thể có hậu tố, `RT2486:V806-0001` vẫn là RT2486.
- **Entry RT**: các dòng của một RT trong khối `Modification:`.
  - Ví dụ: 4 dòng `2018/08/31 ... RT2486`, `Add. artLibSetVarDate()`, `Mod. ArtLibGetRecipeData()`, `ArtLibPutOsfData()`.
- **RT sau**: RT được làm sau RT đang port. Entry của nó nằm **phía trên** entry của RT đang port.
  - Ví dụ: đang port RT2486, entry RT2707 nằm phía trên → RT2707 là RT sau.
- **Feature**: toàn bộ code mà RT đang port đã thêm, sửa, xoá.

### Đơn vị

- **Đơn vị** là một định nghĩa hoàn chỉnh, có tên riêng, nằm ở cấp file (không nằm bên trong hàm). Skill tìm, cắt, so sánh và merge code theo đơn vị.
- Mỗi đơn vị có **tên** (dùng để tìm ở Latest / Target và đặt tên bản cắt) và **phạm vi** (từ dòng nào tới dòng nào là của nó).
- Có 7 loại đơn vị:

1. **Hàm**: phạm vi từ dòng chữ ký tới dấu `}` đóng hàm. Tên là tên hàm.

   ```c
   int ArtLibGetRecipeData(int subSystemId, char *name)
   {
       int retCode;
       retCode = RcpIfGetAllVari(subSystemId, name, &vari);
       return retCode;
   }
   ```

2. **Prototype**: khai báo hàm không có thân, kết thúc bằng `;`. Thường ở file `.h` hoặc đầu file `.c`. Tên là tên hàm.

   ```c
   int artLibSetVarDate(VARI *vari);
   ```

3. **Macro**: dòng `#define`. Macro nhiều dòng (nối bằng `\`) thì phạm vi gồm mọi dòng nối. Tên là tên macro.

   ```c
   #define RCP_BUF_SIZE        512
   #define RCP_IS_VALID(id)    ((id) >= 0 && (id) < RCP_MAX)
   ```

4. **Biến global / static / extern**: khai báo biến ngoài mọi hàm. Tên là tên biến.

   ```c
   static int  g_recipeCnt = 0;
   extern char g_recipeName[RCP_NAME_LEN];
   ```

5. **Bảng dữ liệu**: mảng có giá trị khởi tạo. Phạm vi từ dòng khai báo tới dấu `};`. Tên là tên mảng.

   ```c
   static const VAR_LINK g_varLinkTbl[VAR_LINK_MAX] = {
       { VAR_ID_DATE,  artLibSetVarDate },
       { VAR_ID_NAME,  artLibSetVarName },
   };
   ```

6. **Kiểu `struct` / `union` / `typedef`**: phạm vi từ dòng `struct` / `typedef` tới dấu `;` cuối. Tên là tên kiểu (với `typedef` thì là tên đứng cuối).

   ```c
   typedef struct {
       int   id;
       char  name[RCP_NAME_LEN];
       DATE  varDate;
   } RECIPE_INFO;
   ```

7. **`enum`**: phạm vi từ dòng `enum` tới dấu `;` cuối. Tên là tên enum (hoặc tên `typedef`).

   ```c
   typedef enum {
       VAR_ID_DATE = 0,
       VAR_ID_NAME,
       VAR_ID_MAX
   } VAR_ID;
   ```

- **Phần bên trong đơn vị** không phải đơn vị riêng: không tìm, không cắt riêng. RT thêm, sửa hoặc xoá chúng thì đó là một hunk bên trong đơn vị chứa chúng.
  - Ví dụ: field `varDate` của struct `RECIPE_INFO`, hằng `VAR_ID_NAME` của enum `VAR_ID`, phần tử `{ VAR_ID_DATE, artLibSetVarDate }` của bảng `g_varLinkTbl[]`, câu lệnh `retCode = RcpIfGetAllVari(...);` trong hàm `ArtLibGetRecipeData`.
  - Ví dụ: RT thêm field `varDate` vào `RECIPE_INFO`. Đơn vị là `RECIPE_INFO` (loại `Mod`), dòng `DATE varDate;` là một hunk chỉ có dòng `+` bên trong nó. Không tạo đơn vị `varDate` riêng.

  ```diff
   typedef struct {
       int   id;
       char  name[RCP_NAME_LEN];
  +    DATE  varDate;
   } RECIPE_INFO;
  ```

- **Không phải đơn vị**: biến cục bộ, tham số hàm, comment, khối `Modification:`. Dòng `#include` cũng không phải đơn vị, nhưng có thể phải thêm vào Target khi mang một định nghĩa từ header khác sang (Phase 3).
  - Ví dụ: trong hàm `ArtLibGetRecipeData` ở trên, `int retCode;` là biến cục bộ, `subSystemId` và `name` là tham số. Chúng là phần của hàm, không tìm hay cắt riêng.
  - Ví dụ: `/* Get All Variable Data */` là comment; `#include "rcpif.h"` là dòng include. Cả hai không phải đơn vị.
- **Đơn vị `Add` / `Mod` / `Del`**: đơn vị RT thêm mới / RT sửa bên trong / RT xoá hẳn. Xác định bằng diff ở Phase 1, không theo từ khoá `Add.` / `Mod.` trong changelog.
  - Ví dụ: `artLibSetVarDate` chỉ có ở After → `Add`. `ArtLibGetRecipeData` có ở cả hai, nội dung khác → `Mod`.
- **Bản cắt**: file chứa riêng một đơn vị, cắt từ file gốc theo đúng phạm vi, dòng đầu là dòng 1. Đặt tên `<tên đơn vị>.<bản>.c`.
  - Ví dụ: `ArtLibGetRecipeData.latest.c` là hàm `ArtLibGetRecipeData` cắt từ Latest.

### Diff

- **Diff**: kết quả `get-diff(<mới>, <cũ>)`.
- **Hunk**: một khối thay đổi trong diff, bắt đầu bằng dòng `@@ -a,b +c,d @@`. Nghĩa là `b` dòng bắt đầu từ dòng `a` của bản cũ được thay bằng `d` dòng bắt đầu từ dòng `c` của bản mới.
  - Ví dụ: `@@ -50,3 +50,5 @@` là dòng 50–52 của bản cũ thành dòng 50–54 của bản mới.
- **Dòng `+` / `-` / context**: dòng chỉ có ở bản mới / chỉ có ở bản cũ / có ở cả hai (đứng quanh để định vị). **Luôn phải nói rõ là của diff nào.**
  - Ví dụ: trong diff RT (After so với Before), dòng `+` là code RT viết.
- **Diff (new)**: kết quả Phase 2. Là diff của feature đã cập nhật theo Latest, viết so với code Before. Đầu vào của Phase 3.
  - Ví dụ: `WORK/phase2/diff/src/artlib.c.diff`.

## Tool được dùng

- `get-diff(<file mới>, <file cũ>)`:
  - Dòng `+` là code của file mới.
  - Dòng `-` là code của file cũ.
  - Ví dụ kết quả:

```diff
@@ -3812,16 +3793,16 @@
     /** Get All Variable Data **/
-    retCode = RcpIfGetAllVariForce(subSystemId,
+    retCode = RcpIfGetAllVari(subSystemId,
```

- Được đọc file và tìm kiếm (grep) trong các thư mục đầu vào.
- Được copy một đoạn code (ví dụ thân một hàm) ra file riêng trong `WORK/` để gọi `get-diff` cho riêng đoạn đó.

### Tạo thêm tool khi cần

- Trong lúc chạy, được tạo thêm tool (script Python, shell...) cho các việc lặp lại hoặc dễ sai khi làm tay.
- **Trước khi tạo tool mới:** đọc `tools/README.md` trong thư mục skill này. Đã có tool làm được việc đó thì dùng lại, không tạo trùng.
- **Khi tạo tool mới:**
  - Lưu vào thư mục `tools/` của skill này (cùng chỗ với `SKILL.md`) để lần sau dùng lại.
  - Đặt tên file rõ việc nó làm, ví dụ `extract_function.py`.
  - Đầu file ghi: tool dùng để làm gì, cách gọi, đầu vào, đầu ra.
  - Thêm một dòng vào bảng trong `tools/README.md`.
- **Khi sửa tool có sẵn:** giữ cách gọi cũ vẫn chạy được, cập nhật lại mô tả trong `tools/README.md`.
- Tool chỉ được đọc các thư mục đầu vào và ghi vào `WORK/`. Không sửa `request/`, `source/`, `target/`.
- Ghi vào report của Phase: đã dùng hoặc tạo tool nào, cho việc gì.

## Quy tắc chung

- **Làm việc theo đơn vị, và theo từng hunk bên trong đơn vị:**
  - Tìm đơn vị theo **tên định nghĩa**. Không tìm đổi tên: không thấy đúng tên thì coi như không có.
  - **Không lấy nguyên hàm ở Latest**, vì hàm ở Latest có thể chứa code của feature khác. Chỉ lấy đúng code của RT.
  - Cắt đơn vị ra bản cắt trong `WORK/` để so sánh. Số dòng tính bên trong đơn vị (dòng đầu là dòng 1), không tính theo file gốc.
- **Không bỏ sót:** Code mới nhất của RT gọi thêm hàm nào, dùng thêm biến/macro/kiểu nào thì phải khám phá hết (đệ quy) để mang sang FOMULAR.
- **Dùng đúng từ khóa:** chỉ dùng các từ đã có trong bảng từ khóa (`SKILL.md` và đầu file Phase), đúng nghĩa đã ghi. Nói "dòng `+`" thì phải rõ là của diff nào.
- **Không sửa:** các thư mục đầu vào (`request/`, `source/`, `target/`). Kết quả merge ghi vào bản copy `WORK/target_out/`.
- **Không dừng giữa Phase để hỏi:**
  - Gặp chỗ không chắc: ghi vào mục "Cần xác nhận" của report, rồi làm tiếp phần còn lại.
  - Cuối Phase: gửi report và các câu hỏi cho người dùng.
- **Dừng sau mỗi Phase:** Người dùng xem report, trả lời câu hỏi, xác nhận xong mới sang Phase sau.
- **Đọc hướng dẫn đúng lúc:** Bắt đầu Phase nào thì đọc file hướng dẫn của Phase đó. Không đọc trước Phase sau.
- **Ghi rõ vị trí:** Mỗi hàm/symbol nhắc tới trong report phải kèm file và khoảng dòng, để người duyệt mở ra kiểm tra được.

## Quy trình 3 Phase

| Phase | File hướng dẫn | Việc chính | Cuối Phase báo cáo |
|---|---|---|---|
| 1. Lấy diff và khoanh vùng | `phases/phase-1-diff.md` | `get-diff(After, Before)` từng file, lập danh sách hàm/biến của RT | Đường dẫn các file diff + danh sách đơn vị của RT |
| 2. Đưa feature lên Latest | `phases/phase-2-latest.md` | Tìm từng đơn vị ở Latest theo tên, cập nhật code RT của từng hunk theo Latest, rồi khám phá đệ quy phụ thuộc | Diff feature mới nhất (diff (new)), phụ thuộc thêm vào, câu hỏi cần xác nhận |
| 3. Merge vào FOMULAR | `phases/phase-3-merge.md` | Tìm từng đơn vị ở FOMULAR theo tên, áp từng hunk của diff (new) vào đúng vị trí trong `target_out/`, thêm định nghĩa còn thiếu | Đã merge gì, bỏ qua gì, câu hỏi cần xác nhận |

## Cấu trúc thư mục kết quả

```text
WORK/
  phase1/
    diff/<đường dẫn file>.diff        # get-diff(After, Before)
    units.md                          # danh sách đơn vị của RT
    REPORT.md
  phase2/
    fn/<đường dẫn file>/<tên>.before.c   # đơn vị cắt ra từ Before
    fn/<đường dẫn file>/<tên>.after.c    # ... từ After
    fn/<đường dẫn file>/<tên>.latest.c   # ... từ Latest
    fn/<đường dẫn file>/<tên>.rt.diff    # diff RT: get-diff(after, before) của đơn vị
    fn/<đường dẫn file>/<tên>.ctx.diff   # diff sau RT: get-diff(latest, after) của đơn vị, chỉ để định vị
    fn/<đường dẫn file>/<tên>.feature.c  # bản Before + code RT đã cập nhật theo Latest
    diff/<đường dẫn file>.diff        # diff (new): diff feature mới nhất (đầu vào Phase 3)
    paused.md                         # danh sách tạm dừng (đồ cũ), Phase 3 kiểm tra với FOMULAR
    REPORT.md
  phase3/
    fn/<đường dẫn file>/<tên>.target.c   # đơn vị cắt ra từ Target
    fn/<đường dẫn file>/<tên>.ctx.diff   # diff định vị: get-diff(target, before) của đơn vị
    fn/<đường dẫn file>/<tên>.merged.c   # đơn vị sau khi áp các hunk
    diff/<đường dẫn file>.diff        # get-diff(target_out, target) để người duyệt xem
    REPORT.md
  target_out/                         # bản copy Target đã merge
```

## Các nhãn dùng chung

Nhãn của từng vùng RT ở Phase 2 (vùng RT: xem từ khóa của Phase 2):

| Nhãn | Ý nghĩa |
|---|---|
| `KEEP` | Code RT ở Latest không bị RT sau sửa. Giữ hunk như cũ |
| `UPDATED` | Code RT ở Latest đã bị RT sau sửa hoặc chèn thêm vào giữa. Lấy bản Latest |
| `DROPPED` | Không còn ở Latest. Loại khỏi feature (dùng cho cả vùng RT và đơn vị) |

Nhãn của đơn vị và phụ thuộc ở Phase 2:

| Nhãn | Ý nghĩa |
|---|---|
| `NOT_PORTED` | Đơn vị do RT thêm nhưng Latest không còn ai dùng |
| `DEP_NEW` | Tên được dùng trong code mới nhất, Before chưa có. Mang nguyên định nghĩa Latest |
| `DEP_CHANGED` | Có từ Before, Latest đã đổi, và code mới nhất dùng tới chỗ đã đổi. Mang phần đã đổi |
| `DEP_PAUSED` | Giống hệt Before (đồ cũ). Phase 2 tạm dừng, không đi sâu. Phase 3 kiểm tra với FOMULAR, thiếu thì mang sang và trace tiếp |
| `UNEXPLAINED` | Diff có thay đổi nhưng changelog của RT không nhắc tới |
| `UNRESOLVED` | Tên được dùng nhưng không tìm thấy định nghĩa |
| `NEED_CONFIRM` | Không tự quyết được, chờ người dùng trả lời |

Kết quả merge ở Phase 3:

| Nhãn | Ý nghĩa |
|---|---|
| `MERGED` | Đã áp một hunk vào đơn vị ở Target (sửa / thêm / xoá). Kèm kiểu khớp |
| `MERGED_NEW` | Target chưa có. Đã thêm đơn vị mới của feature |
| `MERGED_DEP` | Phụ thuộc cũ (trong `paused.md`) mà Target thiếu. Đã mang sang |
| `DELETED` | Đã xoá hẳn đơn vị khỏi Target (RT đã xoá đơn vị này) |
| `SKIP_EXISTS` | Target đã có sẵn, không cần làm gì |
| `SKIP_NOT_IN_TARGET` | Target không có đơn vị cần sửa. Bỏ toàn bộ diff của đơn vị đó |
| `SKIP_NO_FILE` | Target không có file tương ứng |

Kiểu khớp khi tìm vị trí của hunk ở Target (Phase 3):

| Kiểu khớp | Ý nghĩa |
|---|---|
| `EXACT` | Đoạn ở Target giống nguyên văn các dòng `-` của hunk, nằm trong vùng dự kiến |
| `NEAR` | Đoạn ở Target gần giống (khác tên biến, tham số, hằng số...), nằm trong vùng dự kiến |
| `MOVED` | Tìm thấy đúng một đoạn khớp nhưng nằm ngoài vùng dự kiến |

## Mẫu report

```markdown
# Report Phase <1|2|3> — <RT>

## Tổng kết
- Số file: <n> | Đã xử lý: <n> | Bỏ qua: <n> | Cần xác nhận: <n>

## Đã xử lý
| File | Hàm/Symbol | Nhãn / Kết quả | Ghi chú (RT nào sửa, khoảng dòng...) |
|---|---|---|---|

## Bỏ qua
| File | Hàm/Symbol | Lý do |
|---|---|---|

## Cần xác nhận
### <số>. <file> — <hàm/symbol>
- Vì sao chưa chắc: ...
- Code liên quan: trích ngắn, kèm file và số dòng
- Đề xuất: ...
- Trả lời của người dùng: (điền sau khi hỏi)

## Cảnh báo
- UNEXPLAINED / UNRESOLVED / chưa compile ...
```

## Khi nào hỏi người dùng

- Trường hợp nào cần hỏi, trường hợp nào tự quyết: xem trong file hướng dẫn của từng Phase.
- Nguyên tắc chung:
  - Tự quyết được theo hướng dẫn thì không hỏi.
  - Không chắc chắn thì không đoán. Gắn `NEED_CONFIRM` và ghi vào mục "Cần xác nhận".
  - Không xoá hoặc ghi đè logic riêng của FOMULAR khi chưa được xác nhận.
- Mỗi câu hỏi nêu rõ: file, hàm/symbol, đoạn code liên quan và đề xuất.
- Chờ trả lời một mục không phải lý do để dừng các mục còn lại.
