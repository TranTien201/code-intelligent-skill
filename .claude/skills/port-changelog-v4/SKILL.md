---
name: port-changelog-v4
description: Quy trình chuyển một chức năng (mã RT) từ máy này sang máy khác (TELINDY sang FOMULAR).
---

# Port RT từ TELINDY sang FOMULAR (v4)

## Bài toán

- Khách hàng không dùng git. Mỗi lần sửa code, họ ghi lại vào khối `Modification:` ở đầu file, ví dụ:

```text
/*#         2018/08/31  Y.Kaneko (TTS-X)     RT2486                         #*/
/*#                     Add. artLibSetVarDate()                             #*/
/*#                     Mod. ArtLibGetRecipeData()                          #*/
/*#                          ArtLibPutOsfData()                             #*/
```

- Khách đưa source của RT ở thời điểm làm RT (Before / After). Sau đó nhiều RT khác đã sửa tiếp các hàm này.
- Việc cần làm: lấy chức năng của RT **ở trạng thái mới nhất (Latest)** rồi merge vào máy FOMULAR.

## Đầu vào

- `request/Before/`: source TELINDY **trước** khi làm RT (nhiều file).
- `request/After/`: source TELINDY **sau** khi làm RT (nhiều file).
- `source/`: source TELINDY mới nhất (Latest). Đã có RT này và mọi RT về sau.
- `target/`: source FOMULAR mới nhất (Target). Nơi cần merge RT vào.
- `WORK/`: thư mục ghi kết quả.

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

- **Làm việc theo đơn vị, và theo từng block thay đổi (hunk) bên trong đơn vị:**
  - Đơn vị: hàm, macro (`#define`), biến global/static, kiểu (`struct`, `typedef`, `enum`), prototype, bảng dữ liệu.
  - Tìm đơn vị theo **tên định nghĩa**. Không tìm đổi tên: không thấy đúng tên thì coi như không có.
  - **Không lấy nguyên hàm ở Latest**, vì hàm ở Latest có thể chứa logic của feature khác. Chỉ lấy đúng các block logic của RT.
  - Cắt đơn vị ra file riêng trong `WORK/` để so sánh. Số dòng tính bên trong đơn vị (dòng đầu là dòng 1), không tính theo file gốc.
- **Trong block thì lấy, ngoài block thì không:** code nằm bên trong block logic của RT ở Latest là của feature (kể cả dòng do RT sau sửa hoặc chèn vào giữa). Code nằm ngoài là logic khác, không mang sang.
- **Không bỏ sót:** Code mới nhất của RT (các dòng `+`) gọi thêm hàm nào, dùng thêm biến/macro/kiểu nào thì phải khám phá hết (đệ quy) để mang sang FOMULAR.
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
| 2. Đưa feature lên Latest | `phases/phase-2-latest.md` | Tìm từng đơn vị ở Latest theo tên, cập nhật phía `+` của từng block thay đổi (hunk) theo Latest, rồi khám phá đệ quy phụ thuộc | Diff feature mới nhất (diff (new)), phụ thuộc thêm vào, câu hỏi cần xác nhận |
| 3. Merge vào FOMULAR | `phases/phase-3-merge.md` | Tìm từng đơn vị ở FOMULAR theo tên, áp từng block thay đổi (hunk) của diff feature vào đúng vị trí trong `target_out/`, thêm định nghĩa còn thiếu | Đã merge gì, bỏ qua gì, câu hỏi cần xác nhận |

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
    fn/<đường dẫn file>/<tên>.rt.diff    # get-diff(after, before) của đơn vị: các hunk của RT
    fn/<đường dẫn file>/<tên>.ctx.diff   # get-diff(latest, after) của đơn vị, chỉ làm context định vị
    fn/<đường dẫn file>/<tên>.feature.c  # bản Before + các hunk của RT đã cập nhật theo Latest
    diff/<đường dẫn file>.diff        # diff (new): diff feature mới nhất (đầu vào Phase 3)
    paused.md                         # danh sách tạm dừng (đồ cũ), Phase 3 kiểm tra với FOMULAR
    REPORT.md
  phase3/
    fn/<đường dẫn file>/<tên>.target.c   # đơn vị cắt ra từ Target
    fn/<đường dẫn file>/<tên>.ctx.diff   # get-diff(target, before) của đơn vị, chỉ làm context định vị
    fn/<đường dẫn file>/<tên>.merged.c   # đơn vị sau khi áp các hunk
    diff/<đường dẫn file>.diff        # get-diff(target_out, target) để người duyệt xem
    REPORT.md
  target_out/                         # bản copy Target đã merge
```

## Các nhãn dùng chung

Nhãn của từng hunk ở Phase 2:

| Nhãn | Ý nghĩa |
|---|---|
| `KEEP` | Block `+` của hunk ở Latest giống nguyên văn. Giữ hunk như cũ |
| `UPDATED` | Block `+` của hunk ở Latest đã bị RT sau sửa. Phía `+` lấy theo Latest |
| `DROPPED` | Không còn ở Latest. Loại khỏi feature (dùng cho cả hunk và đơn vị) |

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
| `EXACT` | Block ở Target giống nguyên văn block `-`, nằm trong vùng dự kiến |
| `NEAR` | Block ở Target gần giống (khác tên biến, tham số, hằng số...), nằm trong vùng dự kiến |
| `MOVED` | Tìm thấy đúng một block khớp nhưng nằm ngoài vùng dự kiến |

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
