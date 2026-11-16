---
name: port-changelog-v3
description: Port một chức năng (một mã RT ghi trong khối changelog "Modification:" ở đầu file C) từ máy TELINDY sang máy FOMULAR khi KHÔNG có git và KHÔNG có snapshot trung gian. Chỉ dùng tool get-diff có sẵn (không tạo script/tool). Chạy 3 Phase, dừng chờ người dùng xác nhận sau mỗi Phase - Phase 1 lấy diff Before-After và Latest-After, Phase 2 tạo diff mới nhất bằng cách so sánh theo hàm và lấy toàn bộ hàm Latest, Phase 3 merge diff đó vào FOMULAR. Use when the user asks to port/copy an RT/feature from TELINDY to FOMULAR with Before/After/Latest/Target folders (port-changelog v3).
---

# port-changelog-v3

Copy một chức năng (một mã RT, ví dụ `RT2486`) từ máy **TELINDY** sang máy **FOMULAR**.
Bối cảnh và lý do thiết kế nằm trong `OVERVIEW.md` (chỉ đọc khi cần tra cứu).

## Đầu vào

- `Before/`, `After/`: source TELINDY trước và sau khi làm RT.
- `latest/`: source TELINDY mới nhất (đã chứa RT và mọi RT về sau).
- `target/`: source FOMULAR mới nhất (nơi cần merge vào).
- `RT`: mã request cần port, ví dụ `RT2486`.
- `WORK/`: thư mục ghi kết quả.
- Thiếu đầu vào nào thì hỏi người dùng. Không tự đoán đường dẫn.

## Tool duy nhất: `get-diff`

- Cách gọi: `get-diff(<file mới>, <file cũ>)`.
  - Dòng `+` là code của file mới.
  - Dòng `-` là code của file cũ.
- Tool đã có sẵn ở repo khác. Không viết lại, không tạo thêm script hay tool nào.
- Nếu không tìm thấy cách gọi `get-diff` thì dừng và hỏi người dùng. Không thay bằng `diff` / `diff3`.
- Các việc khác (liệt kê file, đọc file, tìm tên hàm) làm bằng công cụ đọc và tìm kiếm thông thường.

## Quy tắc chung

- **So sánh theo hàm trước, không so từng dòng.**
  - Đơn vị làm việc là hàm, macro, biến global, type, prototype.
  - Hàm nào bị đổi trong diff Before-After thì lấy **toàn bộ hàm đó ở Latest**.
  - Ví dụ: ở After, `ArtLibGetRecipeData()` gọi thêm 3 hàm; ở Latest chỉ còn gọi 2 hàm
    ⇒ lấy đúng theo Latest (2 hàm), vì Latest là bản đã được sửa qua nhiều lần.
  - Không dùng tên hàm ở dòng `@@` làm căn cứ duy nhất. Mở source để biết dòng thay đổi thuộc hàm nào.
- **Diff quyết định phạm vi.** Changelog `Modification:` chỉ để đối chiếu và giải thích.
- **Không bỏ sót file.** Mọi file khác nhau giữa Before và After đều phải có kết quả cuối:
  `done`, `skipped` (có lý do) hoặc `blocked` (có lý do).
- **Không sửa** `Before/`, `After/`, `latest/`, `target/`. Kết quả merge ghi vào bản copy `WORK/target_out/`.
- **Giữ nguyên encoding** (ví dụ Shift-JIS) và kiểu xuống dòng của từng file Target khi ghi ra.
- **Không tự quyết khi không chắc.** Ghi đoạn đó vào mục "Cần xác nhận" của report và hỏi người dùng.
- **Dừng sau mỗi Phase.** Thông báo, chờ người dùng xem và trả lời xong mới sang Phase sau.
- **Chỉ tạo các file trong mục "Kết quả".** Không tạo manifest, script hay file ghi chú khác.

## Kết quả

```text
WORK/
  phase1/before-after/<đường dẫn file>.diff   # get-diff(After, Before)
  phase1/latest-after/<đường dẫn file>.diff   # get-diff(Latest, After)
  phase2/<đường dẫn file>.diff                # diff mới nhất
  phase2/REPORT.md
  target_out/                                 # bản copy Target đã merge
  phase3/REPORT.md
```

## Quy trình 3 Phase

- Làm lần lượt Phase 1 → 2 → 3.
- Trước khi làm Phase nào thì đọc file hướng dẫn của Phase đó. Không đọc trước file của Phase sau.
- Cuối mỗi Phase: thông báo cho người dùng rồi dừng chờ xác nhận.

| Phase | File hướng dẫn | Việc chính | Thông báo cuối Phase |
|---|---|---|---|
| 1. Lấy diff | `phases/phase-1-diff.md` | `get-diff(After, Before)` và `get-diff(Latest, After)` cho từng file | Đường dẫn các file diff để người dùng xem |
| 2. Tạo diff mới nhất | `phases/phase-2-latest-diff.md` | So sánh theo hàm, lấy toàn bộ hàm Latest, thêm phụ thuộc | Report: đoạn đã xử lý + đoạn cần xác nhận |
| 3. Merge vào FOMULAR | `phases/phase-3-merge.md` | Áp diff mới nhất vào bản copy Target theo luật `+` / `-` | Report: đoạn đã merge + đoạn cần xác nhận |

## Mẫu report (Phase 2 và Phase 3)

```markdown
# Report Phase <2|3> — <RT>

## Tổng kết
- Số file: <n> | Đã xử lý: <n> | Bỏ qua: <n> | Cần xác nhận: <n>

## Đã xử lý
| File | Hàm/Symbol | Kết quả | Ghi chú |
|---|---|---|---|

## Bỏ qua
| File | Hàm/Symbol | Lý do |
|---|---|---|

## Cần xác nhận
### <số>. <file> — <hàm/symbol>
- Vì sao chưa chắc: ...
- Code liên quan: Before / After / Latest / Target (trích ngắn, kèm số dòng)
- Đề xuất: ...
- Trả lời của người dùng: (điền sau khi hỏi)

## Cảnh báo
- UNEXPLAINED / UNRESOLVED / chưa compile ...
```

## Khi nào hỏi người dùng

| Tình huống | Xử lý |
|---|---|
| Latest sửa, thêm hoặc bỏ code trong hàm của RT | Không hỏi. Lấy theo Latest |
| Latest gọi thêm hàm/macro/biến mới, có định nghĩa trong `latest/` | Không hỏi. Thêm vào phụ thuộc (Phase 2, mục 2.3) |
| Latest bỏ hẳn code của RT trong hàm, hoặc có lại hàm mà RT đã xóa | Hỏi (bảng ở Phase 2, mục 2.2) |
| Changelog không khớp diff | Không hỏi. Ghi cảnh báo `UNEXPLAINED` |
| Block sửa code nhưng Target không có hàm đó | Không hỏi. Không merge, ghi vào "Bỏ qua" |
| Symbol được dùng nhưng không tìm thấy định nghĩa | Hỏi |
| Không xác định được dòng thay đổi thuộc hàm/file nào | Hỏi, đưa các ứng viên |
| Target có code riêng, không hòa trộn chắc chắn được | Hỏi, không ghi đè cả hàm |
| Symbol có trong Target nhưng khác chữ ký/kiểu | Hỏi |
| Xóa hàm mà Target có code riêng hoặc còn nơi gọi | Hỏi |

- Mỗi câu hỏi nêu rõ: file, hàm/symbol, đoạn code liên quan và đề xuất.
- Gom câu hỏi vào cuối Phase. Việc chờ trả lời một mục không phải là lý do bỏ qua các file còn lại.
