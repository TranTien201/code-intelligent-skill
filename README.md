# Thử nghiệm: port feature A → B bằng code graph (tree-sitter vs Doxygen)

## Chạy

```bash
# cài 1 lần
uv venv .venv && uv pip install --python .venv/bin/python tree-sitter tree-sitter-c
brew install doxygen

./run_all.sh     # sinh dữ liệu -> dựng graph (2 builder) -> phân tích -> chấm điểm -> apply + build B
```

## Cấu trúc

```
dataset/make_dataset.py     Sinh dữ liệu giả lập firmware máy in + đáp án (expected.json)
data/
  A_latest/ B_latest/       source mới nhất của 2 máy
  feature_before/ after/    các file của feature "Toner Save" trước/sau khi làm
  expected.json             đáp án để chấm điểm
  B_ported/                 kết quả sau khi apply (sinh ra)
tools/
  common.py                 schema graph chung, chuẩn hoá + hash code
  build_graph_ts.py         dựng graph bằng tree-sitter
  build_graph_doxygen.py    dựng graph bằng Doxygen XML (cùng schema)
  seed.py                   B1: diff before/after ở cấp symbol
  analyze.py                B2-5: drift, closure ra/vào, guard, rủi ro -> manifest.json, report.md, llm_review.md
  evaluate.py               chấm manifest so với đáp án -> out/evaluation.md
  apply.py                  B6-7: copy/merge 3 chiều sang B, define guard, build + chạy
out/ts/, out/doxygen/       graph, manifest, report của từng builder
```

## Quy trình

| Bước | Làm gì | Ai làm |
|---|---|---|
| 0. Dựng graph | node = hàm/struct/macro/biến/hằng enum (+ hash code); edge = CALLS, REFERENCES, USES_*, GUARDED_BY | công cụ |
| 1. Seed | so graph `feature_before` và `feature_after` → symbol thêm/sửa | công cụ |
| 2. Drift | symbol của feature ở A_latest khác bản `after` → lấy bản A_latest | công cụ |
| 3. Closure đi ra | BFS từ seed; **dừng khi B đã có y hệt**; B thiếu → kéo theo; B khác → xung đột | công cụ |
| 4. Closure đi vào | ai ở A_latest dùng symbol của feature mà nằm ngoài diff → report_only / glue_review | công cụ + LLM |
| 5. Rủi ro | struct/enum dùng chung bị sửa, xung đột, guard thiếu | công cụ |
| 6. Apply | file mới: copy; file chung: `git merge-file` (base=before, ours=B, theirs=after) | công cụ |
| 7. Verify | build + chạy B; lỗi build quay lại bước 3 | công cụ |

LLM hoặc người chỉ cần đọc `out/*/llm_review.md`, gồm các snippet của xung đột, drift và phụ thuộc chiều vào. Không phải đọc cả repo.

## Các bẫy trong bộ dữ liệu

1. Phụ thuộc ẩn ngoài diff (`density.c`, B chưa có)
2. Chuỗi nhiều tầng (`TonerSave → Density_Scale → DENSITY_MAX`)
3. Xung đột chữ ký (`Clamp` ở B có 2 tham số)
4. Drift: bug-fix sau commit feature
5. `#ifdef SUPPORT_TONER_SAVE`, B chưa define
6. Bảng đăng ký bằng function pointer (menu, PJL)
7. Hàm `static is_valid` trùng tên ở 2 file
8. Eco Report (chỉ A có) dùng Toner Save: chỉ báo cáo, không copy
9. File chung đã bị B sửa riêng (FAX): phải merge, không ghi đè
10. Nhiễu: `Menu_Quality` khác nhau giữa A/B nhưng không liên quan
11. Struct NVRAM thêm field / enum chèn giữa danh sách

## Kết quả (xem `out/evaluation.md`)

| | tree-sitter | Doxygen |
|---|---|---|
| Recall các hạng mục | 100% | 100% |
| Báo động giả `glue_review` | 0 | **2** (nhầm 2 hàm `static is_valid`) |
| Phát hiện `#ifdef` (GUARDED_BY) | Có, kể cả `#ifdef` trong bảng khởi tạo | **Không**. Lần này vẫn bắt được guard chỉ vì diff có sửa `model_a.h`; nếu macro đã có từ trước thì sẽ sót |
| Code phải tự viết | ~250 dòng (tự nối tên) | ~150 dòng (đọc XML) |
| Tốc độ | nhanh, parse lại từng file | chạy lại toàn bộ dự án |

## Bài học từ lần chạy đầu (đã sửa)

Lần chạy đầu, công cụ kéo nhầm EcoReport và Menu_Quality vì nó duyệt **toàn bộ** `g_menu_table` ở A_latest.
**Quy tắc đúng:** với symbol dùng chung bị feature sửa, chỉ đi theo các tên mà feature **thêm vào**
(`new_tokens` trong seed). Ta chỉ merge hunk của feature sang B, nên chỉ phụ thuộc của hunk đó mới tính.

## Giới hạn và bước tiếp theo

- Dữ liệu còn nhỏ (~1.800 token). Cần thử trên một feature thật đã từng port tay để đo recall.
- Chưa xử lý: macro sinh code (`#define DECLARE_HANDLER(x) ...`), gọi qua con trỏ hàm gán lúc chạy, `#if` phức tạp.
  Nếu gặp thì bổ sung bằng clangd hoặc rule riêng.
- Bước LLM (đọc `llm_review.md`, quyết xung đột NEEDS_REVIEW) chưa tự động hoá. Có thể bọc thành Claude Code Skill.
- Để thử thêm bẫy: sửa `FILES`/`EXPECTED` trong `dataset/make_dataset.py` rồi chạy lại `./run_all.sh`.

## Skill cho Claude Code: `.claude/skills/port-feature/`

```
SKILL.md                      quy trình + luật phán đoán + nguyên tắc "không đọc cả repo"
scripts/port_analyze.sh       bước 0-5 (dựng graph, seed, phân tích): 0 token LLM
scripts/query.py              Claude hỏi graph: show / showb / callees / callers / find / undefined
scripts/apply.py              merge sang bản sao của B, define guard, build, chạy thử
references/printer_rules.md   checklist "chỗ đăng ký ngầm" (dev firmware cần bổ sung)
references/report_template.md mẫu báo cáo cuối
```
(`tools/` là symlink tới `scripts/` của skill.)

Dùng: mở Claude Code trong thư mục có skill rồi nhờ, ví dụ: *"Port chức năng Toner Save từ A sang B, input ở ..., dùng skill port-feature"*.

### Lần chạy thử 1 (`trials/run1/`)
Chạy bằng `claude -p` trong một thư mục sạch, chỉ có 4 input và skill, không có đáp án.
- Kết quả **giống hệt** bản port tham chiếu, build OK, B_latest không bị sửa, không kéo nhầm EcoReport.
- Claude chỉ đọc `report.md`, `llm_review.md`, 2 file reference của skill, cộng vài lần gọi `query.py`/grep. **Không mở file nguồn nào.**
- 14 lượt, khoảng 51 giây, khoảng $0,39. Phần lớn token là phần cố định (system prompt và skill, được cache), không tăng theo kích thước repo.
- Claude còn tự phát hiện thêm: chèn field vào giữa struct NVRAM làm lệch offset các field cũ, cần khách hàng quyết.
