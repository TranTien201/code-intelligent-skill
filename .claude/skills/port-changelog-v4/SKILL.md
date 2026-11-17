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

- **Làm việc theo hàm, không theo từng dòng:**
  - Đơn vị làm việc: hàm, macro (`#define`), biến global/static, kiểu (`struct`, `typedef`, `enum`), prototype.
  - Hàm nào cần cập nhật thì lấy **nguyên hàm** ở Latest.
- **Không bỏ sót:** Code mới nhất của RT gọi thêm hàm nào, dùng thêm biến/macro nào thì phải khám phá hết (đệ quy) để mang sang FOMULAR.
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
| 2. Đưa feature lên Latest | `phases/phase-2-latest.md` | Dựa vào changelog: giữ nguyên / lấy Latest / tìm đổi tên / xoá, rồi khám phá đệ quy phụ thuộc | Đã cập nhật gì cho feature, phụ thuộc thêm vào, câu hỏi cần xác nhận |
| 3. Merge vào FOMULAR | `phases/phase-3-merge.md` | So 3 phiên bản Before / Latest / Target cho từng hàm, merge vào `target_out/` | Đã merge gì, bỏ qua gì, câu hỏi cần xác nhận |

## Cấu trúc thư mục kết quả

```text
WORK/
  phase1/
    diff/<đường dẫn file>.diff        # get-diff(After, Before)
    units.md                          # danh sách đơn vị của RT
    REPORT.md
  phase2/
    fn/<đường dẫn file>/<tên>.before.c   # thân hàm/symbol cắt ra từ Before
    fn/<đường dẫn file>/<tên>.after.c    # ... từ After
    fn/<đường dẫn file>/<tên>.latest.c   # ... từ Latest
    fn/<đường dẫn file>/<tên>.diff       # diff riêng của hàm
    diff/<đường dẫn file>.diff        # diff feature mới nhất (đầu vào Phase 3)
    paused.md                         # danh sách tạm dừng (đồ cũ), Phase 3 kiểm tra với FOMULAR
    REPORT.md
  phase3/
    fn/<đường dẫn file>/<tên>.target.c   # thân hàm/symbol cắt ra từ Target
    diff/<đường dẫn file>.diff        # get-diff(target_out, target) để người duyệt xem
    REPORT.md
  target_out/                         # bản copy Target đã merge
```

## Các nhãn dùng chung

| Nhãn | Ý nghĩa |
|---|---|
| `KEEP` | Changelog không có RT nào sửa hàm này về sau. Dùng đúng block Before-After |
| `UPDATE_LATEST` | Có RT sau sửa hàm này. Lấy nguyên hàm ở Latest |
| `RENAMED` | Không còn tên cũ ở Latest, tìm được hàm mới chứa logic của RT |
| `DELETE` | Không còn ở Latest, không tìm được hàm thay thế. Loại khỏi feature |
| `NOT_PORTED` | Hàm do RT thêm nhưng Latest không còn ai gọi |
| `DEP_NEW` | Tên được dùng trong code mới nhất, Before chưa có. Phải mang sang |
| `DEP_CHANGED` | Có từ Before nhưng Latest đã đổi định nghĩa. Mang bản Latest sang |
| `DEP_PAUSED` | Giống hệt Before (đồ cũ). Phase 2 tạm dừng, không đi sâu. Phase 3 kiểm tra với FOMULAR, thiếu thì mang sang và trace tiếp |
| `UNEXPLAINED` | Diff có thay đổi nhưng changelog của RT không nhắc tới |
| `UNRESOLVED` | Tên được dùng nhưng không tìm thấy định nghĩa |
| `NEED_CONFIRM` | Không tự quyết được, chờ người dùng trả lời |

Kết quả merge ở Phase 3:

| Nhãn | Ý nghĩa |
|---|---|
| `MERGED` | Target giống Before. Đã thay nguyên đơn vị bằng bản Latest |
| `MERGED_NEW` | Target chưa có. Đã thêm đơn vị mới |
| `MERGED_DEP` | Đã thêm hoặc cập nhật phụ thuộc mà code đã merge cần |
| `MERGED_KEEP_TARGET` | Target có code riêng. Đã áp thay đổi của feature và giữ code riêng của FOMULAR |
| `DELETED` | Đã xoá đơn vị khỏi Target |
| `SKIP_EXISTS` | Target đã giống Latest, không cần làm gì |
| `SKIP_NOT_IN_TARGET` | Target không có hàm cần sửa, không merge |
| `SKIP_NO_FILE` | Target không có file tương ứng |

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
  - Không ghi đè code riêng của FOMULAR khi chưa được xác nhận.
- Mỗi câu hỏi nêu rõ: file, hàm/symbol, đoạn code liên quan và đề xuất.
- Chờ trả lời một mục không phải lý do để dừng các mục còn lại.
