---
name: port-feature
description: Port (copy 1-1) một chức năng từ source của máy/model A sang source của máy/model B (C/C++ firmware). Tự lần ra toàn bộ code liên quan (phụ thuộc ẩn ngoài diff, bảng đăng ký, #ifdef, drift), đánh giá ảnh hưởng, merge sang B và build kiểm chứng - chỉ đọc phần code liên quan thay vì cả repo. Dùng khi người dùng muốn "lấy/copy/port/bê chức năng X của máy A sang máy B" và có src_A_latest, src_B_latest, thư mục file trước/sau khi làm feature.
---

# Port feature A → B

Input gồm 4 thư mục: `A_latest`, `B_latest`, `feature_before` (các file của A trước khi làm feature),
`feature_after` (các file đó sau khi làm). Output là bản sao của B đã có feature, kèm báo cáo.

## Nguyên tắc vàng (để nhanh và rẻ)

1. **Không đọc cả repo.** Không `Read`/`cat` toàn bộ file trong A hay B, không grep tràn lan.
   Việc lần theo phụ thuộc là của script (0 token). Bạn chỉ đọc:
   `report.md`, `llm_review.md`, và output của `query.py` khi cần hỏi thêm.
2. Cần xem một hàm/struct cụ thể → `query.py <work> show <symbol>` (chỉ in đúng đoạn code đó).
3. **Không bao giờ sửa `B_latest`.** Luôn ghi ra thư mục output (mặc định `<B_latest>_ported`).
4. Code của feature được copy **y nguyên 1-1**. Không tự ý viết lại, refactor hay "cải tiến".
5. Mọi quyết định không chắc chắn → ghi vào báo cáo cuối để người duyệt. Không đoán.

`SK` = thư mục của skill này (`.claude/skills/port-feature`). Các script nằm trong `SK/scripts/`.

## Quy trình

### Bước 1 - Xác nhận input
Cần có: 4 thư mục trên, thư mục cấu hình model (mặc định `config`), file cấu hình của B
(vd `config/model_b.h`), lệnh build B (vd `make MODEL=B`), và macro model nếu dùng Doxygen.
Thiếu thì hỏi người dùng. Nếu chạy không tương tác và đủ 4 thư mục thì dùng mặc định, ghi rõ giả định vào báo cáo.

### Bước 2 - Phân tích bằng công cụ (0 token LLM)
```bash
bash SK/scripts/port_analyze.sh --a <A_latest> --b <B_latest> \
     --before <feature_before> --after <feature_after> --out <work_dir> [--config-dir config]
```
Mặc định `--builder ts` (tree-sitter). Chỉ dùng `doxygen` khi cần so sánh.
Sau đó **đọc `<work_dir>/report.md`** (và chỉ file đó).

### Bước 3 - Phán đoán (đọc `<work_dir>/llm_review.md`)
Áp dụng luật dưới đây cho từng mục trong báo cáo:

| Mục | Hành động |
|---|---|
| **Symbol cần thêm** (`feature` / `dependency`) | Chấp nhận. Kiểm tra chuỗi `path` có hợp lý không |
| **Merge** | Chấp nhận. Script sẽ merge 3 chiều, chỉ đưa hunk của feature sang |
| **Xung đột `SAFE_REPLACE`** (B không có chỗ nào dùng) | Chấp nhận thay bằng bản A |
| **Xung đột `NEEDS_REVIEW`** (B đang dùng) | **DỪNG.** So 2 snippet trong `llm_review.md`, đề xuất phương án (giữ bản B và chỉnh lời gọi của feature / đổi bản B và sửa caller ở B / thêm hàm mới). **Hỏi người dùng** trước khi làm, vì làm cách nào cũng phá vỡ "copy 1-1" hoặc đổi hành vi của B |
| **Guard `#ifdef`** B chưa define | Sẽ thêm `#define` vào file cấu hình B. Ghi vào báo cáo để người xác nhận B có muốn bật feature không |
| **Drift** | Dùng bản A_latest (đã có bug-fix). Nêu trong báo cáo |
| **Chỉ báo cáo** (feature khác của A dùng feature này) | **KHÔNG copy.** Liệt kê cho người dùng biết |
| **Điểm nối nghi vấn** (`glue_review`) | Xem snippet. Nếu đó là chỗ đăng ký hoặc khởi tạo mà feature cần để chạy (menu, bảng lệnh, init, NVRAM default...) → báo người dùng, vì nó nằm ngoài diff. Nếu chỉ là code khác dùng chung → bỏ qua |
| **Rủi ro HIGH do struct/enum** | Cảnh báo trong báo cáo (layout NVRAM, giá trị enum bị dịch) |

Đối chiếu thêm checklist nghiệp vụ trong `SK/references/printer_rules.md`. Chỉ đọc khi feature có thêm
setting, lệnh, chuỗi hay trạng thái máy.

Cần thêm thông tin thì hỏi graph, đừng mở file:
```bash
python SK/scripts/query.py <work_dir> show <symbol>        # code + trạng thái ở B
python SK/scripts/query.py <work_dir> showb <symbol>       # bản ở B
python SK/scripts/query.py <work_dir> callees|callers|callers-b <symbol>
python SK/scripts/query.py <work_dir> find <chuỗi>
```
Symbol static viết dạng `ten@duong/dan/file.c`.

### Bước 4 - Apply + build
```bash
python SK/scripts/apply.py --work <work_dir> --a <A_latest> --b <B_latest> \
     --before <feature_before> --after <feature_after> --out <B_ported> \
     --b-config <config/model_b.h> --build "<lệnh build B>" [--run "<lệnh chạy thử>"] \
     [--skip-conflict <symbol đã xử lý tay>]
```
(Dùng cùng python với bước 2, vd `.venv/bin/python` nếu có.)

### Bước 5 - Vòng lặp sửa lỗi build (tối đa 3 vòng)
Nếu build lỗi:
1. Lưu lỗi ra file, chạy `query.py <work_dir> undefined <file_lỗi>` để map symbol thiếu → vị trí ở A.
2. Symbol `MISSING_IN_B` mà thuộc chuỗi phụ thuộc của feature → copy nguyên định nghĩa từ A
   (dùng `show` để lấy code), ghi lại lý do. Symbol `DIFFERENT` → xử lý như xung đột `NEEDS_REVIEW`.
3. Conflict marker từ merge (`<<<<<<<`) → chỉ xem đúng đoạn marker đó, giữ phần của B và chèn hunk của feature.
4. Build lại. Sau 3 vòng vẫn lỗi → dừng, báo cáo.

### Bước 6 - Báo cáo cho người dùng
Trả lời theo mẫu `SK/references/report_template.md`, ngắn gọn, bằng tiếng Việt. Phải có:
kết quả build, danh sách file copy/merge, các quyết định đã đưa ra và lý do, việc người cần làm tiếp,
và chi phí context (số liệu ở cuối `report.md`).
