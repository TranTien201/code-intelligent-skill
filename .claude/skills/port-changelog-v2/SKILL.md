---
name: port-changelog-v2
description: Port một chức năng (một mã RT ghi trong khối changelog "Modification:" ở đầu file C) từ máy TELINDY sang máy FOMULAR khi KHÔNG có git và KHÔNG có snapshot trung gian, chạy theo 3 Phase chỉ dùng tool get-diff có sẵn (không tạo script). Phase 1 lấy diff Before→After và After→Latest, Phase 2 gộp thành diff mới nhất cho các hàm của RT, Phase 3 merge diff đó vào FOMULAR; mỗi Phase báo cáo đã merge gì và còn gì cần người xác nhận. Use when the user asks to port/copy an RT/feature from TELINDY to FOMULAR with Before/After/Latest/Target folders and wants the 3-phase get-diff workflow (port-changelog v2).
---

# port-changelog-v2

Copy một chức năng (một mã RT, ví dụ `RT2486`) từ máy **TELINDY** sang máy **FOMULAR**.
Bối cảnh và lý do thiết kế: xem `OVERVIEW.md` (chỉ đọc khi cần tra cứu).

## Đầu vào

- `Before/`, `After/`: hai cây source TELINDY trước và sau khi làm RT.
- `latest/`: source TELINDY mới nhất (đã chứa RT và mọi RT về sau).
- `target/`: source FOMULAR mới nhất (nơi cần merge vào).
- `RT`: mã request cần port, ví dụ `RT2486`.
- `WORK/`: thư mục làm việc để ghi kết quả.
- Thiếu đầu vào nào thì hỏi người dùng. Không tự đoán đường dẫn.

## Tool duy nhất: `get-diff`

- Cú pháp: `get-diff(<file mới>, <file cũ>)`.
  - Dòng `+` = code của file mới.
  - Dòng `-` = code của file cũ.
- Tool nằm ở repo khác, đã có sẵn. **Không viết lại, không tạo thêm script/tool nào khác.**
- Nếu không gọi được `get-diff` → dừng và hỏi người dùng cách gọi. Không thay bằng `diff`/`diff3` tự chế.
- Việc còn lại (đọc file, tìm hàm, grep tên symbol) làm bằng công cụ đọc/tìm kiếm thông thường.

## Nguyên tắc chung

- Không bao giờ sửa trực tiếp `Before/`, `After/`, `latest/`, `target/`.
  - Kết quả merge chỉ ghi vào bản copy `WORK/target_out/`.
- Không bỏ sót file: mọi file có trong diff Before→After đều phải có trạng thái cuối trong report
  (`done`, `skipped` có lý do, hoặc `blocked` có lý do).
- Làm việc theo **hàm / symbol**, không bắt người dùng xử lý từng hunk.
- Code diff xác định phạm vi. Changelog `Modification:` chỉ dùng để đối chiếu và giải thích.
- Chỉ hỏi người dùng khi thật sự không chắc (danh sách ở mục "Khi nào hỏi người dùng").
  - Gom câu hỏi theo Phase, hỏi bằng AskUserQuestion (tối đa 4 câu mỗi lần).
  - Không tự trả lời thay người dùng.
- Khi ghi file vào `target_out/`: giữ đúng encoding (ví dụ Shift-JIS) và kiểu xuống dòng của file Target gốc.
- Chỉ tạo các file ghi trong mục "Kết quả" bên dưới. Không tạo file khác.

## Quy trình 3 Phase

Làm lần lượt. Mỗi Phase đọc file hướng dẫn tương ứng trước khi làm.
Kết thúc mỗi Phase phải **báo cho người dùng** rồi mới sang Phase sau.

### Phase 1 — Lấy diff (`phases/phase-1-diff.md`)

- Lấy diff Before→After cho từng file: `get-diff(After, Before)`.
- Lấy diff After→Latest cho từng file đó: `get-diff(Latest, After)`.
- Đọc changelog `Modification:` để lấy thông tin RT.
- **Báo người dùng:** danh sách đường dẫn tất cả file diff để người dùng mở xem.

### Phase 2 — Gộp thành diff mới nhất (`phases/phase-2-update.md`)

- So sánh diff Before→After với diff After→Latest theo từng hàm/symbol.
- Tạo diff mới nhất: hàm của RT lấy theo trạng thái Latest, kèm phụ thuộc (closure).
- **Báo người dùng:** report các đoạn đã gộp và các đoạn cần người xác nhận.

### Phase 3 — Merge vào FOMULAR (`phases/phase-3-merge.md`)

- Áp diff mới nhất vào bản copy Target theo luật:
  - Block chỉ có `+` → merge qua.
  - Block có `-` rồi `+` (sửa code) → kiểm tra Target có hàm/code đó không.
    - Có → merge.
    - Không có → **không merge**, ghi lý do.
- **Báo người dùng:** report các đoạn đã merge và các đoạn cần người xác nhận.

## Khi nào hỏi người dùng

| Tình huống | Xử lý |
|---|---|
| Latest thêm lời gọi hàm / macro / biến mới bên trong hàm của RT | **Không hỏi.** Lấy bản Latest, tự thêm định nghĩa vào closure |
| Hàm của RT không còn trong Latest | Ghi `DELETE`. Ở Phase 3, hỏi nếu Target có code/caller riêng |
| Symbol được dùng nhưng không tìm thấy định nghĩa ở Latest lẫn Target | Ghi `UNRESOLVED`, hỏi |
| Không biết chắc hunk thuộc hàm/file nào | Hỏi, đưa các ứng viên |
| Target có code riêng không hòa trộn an toàn được | Hỏi, không ghi đè cả hàm |
| Symbol có trong Target nhưng khác chữ ký/kiểu | Coi là conflict, hỏi |
| Changelog không khớp code diff | Chỉ ghi cảnh báo `UNEXPLAINED`, không hỏi |

- Mỗi câu hỏi phải nêu: file, hàm/symbol, đoạn code Before/After/Latest/Target liên quan, RT gợi ý (nếu có).

## Kết quả

```text
WORK/
  phase1/before-after/<đường dẫn file>.diff   # diff Before→After
  phase1/after-latest/<đường dẫn file>.diff   # diff After→Latest
  phase2/<đường dẫn file>.diff                # diff mới nhất (đã gộp)
  phase2/REPORT.md
  target_out/                                 # bản copy Target đã merge
  phase3/REPORT.md
```

## Kết thúc

- Báo ngắn gọn cho người dùng:
  - Đường dẫn `phase2/REPORT.md`, `phase3/REPORT.md` và `target_out/`.
  - Số đoạn đã merge / bỏ qua / chờ xác nhận.
  - Các cảnh báo `UNEXPLAINED`, `UNRESOLVED`, `DELETE`.
- Không báo "hoàn tất" khi còn file hoặc đoạn ở trạng thái chờ.
