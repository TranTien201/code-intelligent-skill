# Danh sách tool của port-changelog-v5

- Đọc bảng dưới trước khi tạo tool mới. Đã có tool làm được việc cần làm thì dùng lại.
- Tạo tool mới thì lưu vào thư mục này và thêm một dòng vào bảng.

| Tool | Dùng để làm gì | Cách gọi | Đầu vào | Đầu ra | Dùng ở Phase |
|---|---|---|---|---|---|
| `merge_ui.py` (+ `merge_ui_template.html`) | Kiểm tra `merge_view.json` khớp `target_out/`; dựng UI review 2 cột; áp quyết định của người dùng | `merge_ui.py check <json> --target-out-root DIR` · `merge_ui.py render <json> [-o html]` · `merge_ui.py apply <json> --decisions D -o DIR` | `WORK/phase3/merge_view.json`, `target/`, `decisions.json` | `merge_view.html`, file đã merge (giữ encoding / EOL gốc) | 3 (Bước 9: `check`), 4 (`render`, `apply`) |

## Test

```bash
cd tools && python3 -m unittest test_merge_ui.py -v
```

## Mock Phase 4: `fixtures/phase4_mock/`

Giả lập trạng thái ngay sau Phase 3 của một RT (RT9001, 3 file: `artrcp.c`, `rifback2.c`, `rcpif.h`):

```text
phase4_mock/
  target/                        # Target gốc (FOMULAR)
  WORK/phase3/merge_view.json    # đầu ra Phase 3: mọi hunk + vị trí
  WORK/target_out/               # đầu ra Phase 3: đã áp MERGED*, chưa áp NEED_CONFIRM
  decisions.mock.json            # giả lập file người dùng tải từ UI
  expected/target_out_final/     # kết quả mong đợi sau khi áp decisions.mock.json
  run_mock.sh                    # chạy check → render → apply → so với expected
```

- Chạy: `bash tools/fixtures/phase4_mock/run_mock.sh [thư mục chạy]`. Mock gốc không bị sửa. Cuối cùng in ra đường dẫn `merge_view.html` để mở xem UI.
- Phủ các trường hợp: `MERGED` (EXACT / NEAR), `MERGED_NEW`, `MERGED_DEP`, `DELETED`, `SKIP_EXISTS`, changelog, `NEED_CONFIRM` có vị trí (guard riêng FOMULAR, tên tham số khác, neo mơ hồ, macro khác giá trị, đơn vị chờ mục khác), `NEED_CONFIRM` không có vị trí (sửa tay).
- `decisions.mock.json` lấy nhóm A5 (+ A2, A3, A6, C4), B5 (+ B6); giữ FOMULAR ở A4, C2, C5; B8 trả lời "giữ FOMULAR".
- Mock chỉ chạy phần tool của Phase 4 (Bước 1, 2, 6). Bước 5 (cập nhật changelog cho mục mới lấy) là việc agent sửa JSON, nên changelog trong `expected/` chưa liệt kê các mục `NEED_CONFIRM` được lấy.
- Mở thẳng file / tab trong UI: thêm `#f=1` hoặc `#f=2&v=result` vào URL.
