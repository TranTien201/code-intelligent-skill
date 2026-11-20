# tools/ — Phase 4: duyệt merge-plan.json

Dựng một trang HTML tự chứa (mở offline bằng double-click, Windows/macOS) để người duyệt xem `merge-plan.json` theo kiểu merge-conflict của GitHub, trả lời câu hỏi, chọn Target / RT / Đề xuất cho từng chunk, rồi xuất `decisions.json` và file output.
Hợp đồng dữ liệu: `../schema/README.md` (mục 4: trạng thái + ghép, 4b: thao tác, 6: kiểm tra).
| File | Vai trò |
|---|---|
| `review_core.js` | Logic thuần (không DOM): `validate`, `computeStatus`, `build`, `closure`, `dependents` (+ `buildFile`, `previewAction`, `previewAnswer`, `normalizeDecisions`). Dùng được trong trang và qua `require()` trong Node. |
| `review_template.html` | Giao diện (CSS + JS). `render_review.py` nhúng plan, nội dung Target và `review_core.js` vào đây. |
| `render_review.py` | CLI: render trang, hoặc `--apply` ghi file output. Có bản Python của `validate` / `computeStatus` / `build`, giữ giống hệt `review_core.js` (test so sánh). |

## Lệnh

Render trang duyệt:

```
python3 tools/render_review.py --plan WORK/<run>/phase3/merge-plan.json --target-root <thư mục target> -o WORK/<run>/phase4/review.html [--decisions decisions.json]
```

- Đọc từng file trong `plan.files` tại `<target-root>/<khóa>` bằng encoding khai báo; CRLF → LF trong bộ nhớ, ghi nhớ kiểu xuống dòng và BOM để ghi lại đúng.
- `--decisions`: nạp sẵn quyết định cũ vào trang. Không có thì trang tự khôi phục quyết định lưu trong trình duyệt (nếu có).
- In tóm tắt: số file, chunk, câu hỏi, skipped, số chunk theo trạng thái, lỗi kiểm tra.

Ghi file output từ quyết định (bắt buộc dùng cách này cho file không phải UTF-8/ASCII, ví dụ cp932):

```
python3 tools/render_review.py --plan merge-plan.json --target-root <target> --decisions decisions.json --apply -o <thư mục output> [--allow-pending]
```

- Ghi `<output>/<khóa>` với encoding + kiểu xuống dòng (+ BOM) của file gốc. Dòng cuối Target không có `\n` thì output cũng không có.
- Còn câu hỏi chưa trả lời thì dừng (exit 3); `--allow-pending` coi các chunk đó là giữ Target.

## Trên trang

- Đầu trang: mã RT, số chunk theo trạng thái (APPLIED xanh, KEPT xám, NEED_CONFIRM đỏ, BLOCKED vàng, FOLLOW vàng nhạt), banner đỏ nếu plan không qua 7 kiểm tra mục 6 — khi đó nút xuất bị khóa.
- Trái: danh sách câu hỏi, file → unit → chunk. Giữa: cột trái là output hiện tại (đã ghép theo quyết định, có số dòng, vùng chunk tô màu theo trạng thái); cột phải là khung chunk nằm ngang vùng của nó.
- Khung chunk: tab Thay đổi / Current / Base / Incoming / Đề xuất (token `name_map[].to` được tô, rê chuột xem from → to + chứng cứ); BLOCKED/FOLLOW ghi "chờ Kx: lý do".
- Nút `← Giữ Target`, `RT` (khi có `rt`), `Áp →`, `↺ mặc định`. Trước khi đổi, trang hiện danh sách chunk bị kéo theo / lùi theo. Nếu bao đóng `requires` có chunk thuộc câu hỏi chưa trả lời, trang không áp mà cuộn tới câu hỏi đó.
- Xuất: `Tải decisions.json`; tải file output (chỉ file UTF-8/ASCII — trình duyệt chỉ ghi được UTF-8; file khác hiện lệnh `--apply` ở trên).

## Exit code

| Code | Nghĩa |
|---|---|
| 0 | Ổn |
| 1 | Plan không qua kiểm tra mục 6 (render vẫn ghi HTML có banner đỏ; `--apply` không ghi gì) |
| 2 | Lỗi đầu vào: JSON hỏng, thiếu file Target, encoding sai / không decode hoặc encode được, `--apply` thiếu `--decisions` |
| 3 | `--apply` khi còn câu hỏi chưa trả lời mà không có `--allow-pending` |

## Test

Từ thư mục `tools/` (cần Python 3; Node ≥ 18 cho test JS và test so sánh Python ↔ JS):

```
node --test "tests/*.js"
python3 -m unittest discover -s tests -v
```

- `tests/test_review_core.js`, `tests/test_render_review.py`: fixture `tests/fixtures/synthetic/` (câu hỏi, chuỗi BLOCKED qua hai hunk, FOLLOW nhiều vòng, chèn trước neo EOF ở dòng cuối không có `\n`, file cp932 + CRLF). Gồm cả chạy script của trang trong DOM giả và so sánh Python ↔ JS trên ~900 ca ngẫu nhiên.
