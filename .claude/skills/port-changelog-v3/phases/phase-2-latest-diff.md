# Phase 2 — Tạo diff mới nhất

Mục tiêu: từ hai bộ diff của Phase 1, tạo ra một diff cho mỗi file, thể hiện chức năng của RT **theo trạng thái Latest**.

## 2.1 Lập danh sách hàm/symbol của RT

- Đọc `before-after/<file>.diff`, xác định mỗi dòng `+` / `-` thuộc hàm hoặc symbol nào.
- Bỏ qua thay đổi trong khối `Modification:` (không phải code).
- Phân loại từng đơn vị:
  - `Add`: không có ở Before, có ở After.
  - `Mod`: có ở cả hai, nội dung khác.
  - `Del`: có ở Before, không có ở After.
- Đối chiếu với changelog:
  - Diff có đổi nhưng changelog không nhắc ⇒ ghi cảnh báo `UNEXPLAINED`, vẫn xử lý.
  - Changelog nhắc nhưng diff không đổi ⇒ ghi cảnh báo, không mở rộng phạm vi.

## 2.2 So sánh từng hàm với Latest

Với mỗi đơn vị ở 2.1, xem `latest-after/<file>.diff` có đụng tới nó không.

- Cách biết "có đụng tới": mở file After, lấy khoảng dòng của hàm (từ dòng tên hàm tới dấu `}` đóng hàm),
  rồi xem các block `-` trong `latest-after/<file>.diff` có rơi vào khoảng dòng đó không.
- So sánh theo **hàm**, không so từng dòng. Hàm nào Latest có sửa thì lấy **toàn bộ hàm Latest**:
  mọi dòng thêm, sửa, bỏ về sau đều đi theo Latest, không lọc theo RT.

Quyết định theo bảng sau:

| Before-After (RT) | Latest-After (về sau) | Xử lý | Nhãn |
|---|---|---|---|
| Hàm bị sửa/thêm | Không đụng tới | Tự làm: giữ block Before-After | `GIỮ NGUYÊN` |
| Hàm bị sửa/thêm | Có sửa, code của RT vẫn còn (có thể đã sửa tiếp) | Tự làm: lấy toàn bộ hàm Latest | `CẬP NHẬT THEO LATEST` |
| Hàm bị sửa/thêm | Có sửa, **code của RT không còn** và không có dòng thay thế | **Hỏi** (có thể RT đã bị gỡ hoặc chuyển chỗ) | `CẦN XÁC NHẬN` |
| Hàm bị sửa/thêm | Hàm bị xóa | Tự làm (chưa xử lý đổi tên hàm) | `DELETE` |
| Hàm bị xóa | Latest không có lại | Tự làm | `DELETE` |
| Hàm bị xóa | **Latest có lại hàm** | **Hỏi** | `CẦN XÁC NHẬN` |
| Macro / struct / global / prototype bị sửa | Latest sửa tiếp | Tự làm: lấy định nghĩa Latest | `CẬP NHẬT THEO LATEST` |
| Macro / struct / global / prototype bị sửa | Phần RT thêm (field, macro, giá trị) không còn ở Latest | **Hỏi** | `CẦN XÁC NHẬN` |
| Không thuộc hàm/symbol nào của RT | Có thay đổi | Bỏ qua, không đưa vào diff | — |
| Không xác định được thuộc hàm/symbol nào | — | **Hỏi**, đưa các ứng viên | `CẦN XÁC NHẬN` |

## 2.3 Tìm và cập nhật phụ thuộc

Mục đích: hàm Latest vừa lấy ở 2.2 có thể dùng biến, macro, kiểu dữ liệu hoặc gọi hàm khác nằm **ngoài thân hàm**.
Phải mang theo đủ các thứ đó, nếu không FOMULAR sẽ lỗi compile hoặc chạy sai.

Ví dụ:

```text
ArtLibGetRecipeData()            ← hàm của RT (lấy bản Latest)
 ├─ artLibLinkOnVarSet()         ← hàm mới ở Latest          → PHỤ THUỘC
 │    └─ g_varLinkTbl[]          ← biến global hàm mới dùng   → PHỤ THUỘC (dò tiếp)
 ├─ WAVMACH_VER0800_0000         ← macro mới ở Latest         → PHỤ THUỘC
 └─ g_recipeBuf[]                ← biến có từ Before, Latest đổi kích thước → PHỤ THUỘC
```

### Bước 1 — Liệt kê tên được dùng

- Đọc thân từng hàm Latest có nhãn `CẬP NHẬT THEO LATEST` hoặc `GIỮ NGUYÊN`.
- Ghi ra mọi tên được dùng:
  - Tên hàm được gọi.
  - Biến không khai báo bên trong hàm (biến global, biến `static` đầu file, `extern`).
  - Macro, hằng số, giá trị `enum`.
  - Kiểu dữ liệu (`struct`, `typedef`) và các field được dùng (`rec.xxx`, `p->xxx`).
- Bỏ qua: biến cục bộ, tham số của hàm, từ khóa C, hàm thư viện chuẩn (`memcpy`, `strcpy`, `printf`...).

### Bước 2 — Tìm định nghĩa trong Latest

Tìm theo thứ tự, thấy ở đâu thì dừng ở đó:

- Cùng file `.c` (phần đầu file, ngoài các hàm).
- Các file `.h` mà file đó `#include`.
- Toàn bộ `latest/` (grep tên chính xác). Thấy ở nhiều nơi thì đưa vào "Cần xác nhận".

Ghi lại: tên, loại (hàm / biến / macro / kiểu / field), file và dòng định nghĩa.

### Bước 3 — So với Before để quyết định

| Định nghĩa ở Latest so với Before | Xử lý |
|---|---|
| Không có ở Before (mới thêm về sau) | Thêm định nghĩa Latest vào diff. Ghi `PHỤ THUỘC - MỚI` |
| Có ở Before nhưng Latest đã đổi (kiểu, kích thước mảng, giá trị khởi tạo, giá trị macro, field của struct) | Thêm bản Latest vào diff dưới dạng `-` cũ / `+` mới. Ghi `PHỤ THUỘC - ĐÃ ĐỔI` |
| Có ở Before và giống hệt Latest | Không đưa vào diff, chỉ ghi vào report để Phase 3 kiểm tra Target có hay không |
| Không tìm thấy định nghĩa trong `latest/` | Ghi `UNRESOLVED`, đưa vào "Cần xác nhận" |

- Phụ thuộc nằm ở file khác (không có trong danh sách file của Phase 1) ⇒ vẫn tạo diff cho file đó
  trong `WORK/phase2/`, ghi rõ trong report là file được thêm vì phụ thuộc.
- Hàm mới có prototype trong `.h` ⇒ lấy cả prototype.

### Bước 4 — Dò tiếp

- Với mỗi hàm mới vừa thêm ở Bước 3, đọc thân hàm và làm lại Bước 1 → 3.
- Với mỗi biến / kiểu mới, xem định nghĩa của nó có dùng macro hoặc kiểu khác không (ví dụ kích thước mảng là một macro) và làm lại Bước 2 → 3.
- Dừng khi không còn tên mới.
- Không hỏi người dùng chỉ vì Latest gọi thêm hàm hoặc dùng thêm biến mới.

## 2.4 Ghi diff mới nhất

- Gọi `get-diff(latest/<file>, Before/<file>)`.
- Chỉ giữ lại các block thuộc đơn vị ở 2.2 và 2.3. Bỏ block của hàm ngoài phạm vi.
- Lưu vào `WORK/phase2/<file>.diff`. Phía trên mỗi block ghi một dòng chú thích:
  tên hàm/symbol + nhãn (`GIỮ NGUYÊN`, `CẬP NHẬT THEO LATEST`, `DELETE`, `PHỤ THUỘC - MỚI`,
  `PHỤ THUỘC - ĐÃ ĐỔI`, `UNEXPLAINED`, `CẦN XÁC NHẬN`).
- File `added`: toàn bộ nội dung file ở Latest là block `+`.
- File `deleted`, hoặc file không còn trong Latest: ghi `DELETE` cho cả file.

## 2.5 Report, thông báo và dừng

- Ghi `WORK/phase2/REPORT.md` theo mẫu ở mục "Mẫu report" trong `SKILL.md`.
  - "Đã xử lý": từng hàm/symbol, nhãn, và ghi chú ngắn (ví dụ: "Latest bỏ lời gọi `xxx()`", entry RT mới hơn có nhắc tới hàm).
  - "Phụ thuộc": danh sách cây phụ thuộc như ví dụ ở 2.3 (hàm của RT → tên được dùng → file định nghĩa → nhãn).
  - "Cần xác nhận": các dòng **Hỏi** trong bảng 2.2, `UNRESOLVED`, tên có nhiều định nghĩa, file `blocked`.
- Báo cho người dùng đường dẫn report, đường dẫn các diff mới nhất và số lượng từng loại.
- Hỏi người dùng từng mục "Cần xác nhận". Ghi câu trả lời vào report.
- Dừng, chờ người dùng xác nhận rồi mới sang Phase 3.
