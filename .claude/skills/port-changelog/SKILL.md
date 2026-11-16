---
name: port-changelog
description: Port một chức năng (một mã RT trong khối changelog "Modification:" ở đầu file C) từ máy TELINDY sang máy FOMULAR khi KHÔNG có git và KHÔNG có snapshot trung gian. Đầu vào là 1 file diff (Before→After) + source Latest + source Target. Dùng một file diff duy nhất từ đầu đến cuối - cập nhật nó lên Latest rồi merge sang Target, chỉ hỏi người dùng ở chỗ cần. Use when the user asks to port/copy an RT/feature between machines/models using a changelog-style history block and a feature diff.
---

# port-changelog

Port một chức năng (một RT) từ TELINDY sang FOMULAR.
Thiết kế chi tiết: `OVERVIEW.md`. Giao diện giữa các script: `references/CONTRACT.md`.

## Khi nào dùng
- Người dùng muốn copy một chức năng/bản sửa lỗi (một mã RT, ví dụ `RT2486`) từ máy này sang máy khác.
- Lịch sử thay đổi nằm trong khối comment `Modification:` ở đầu file C, không có git.
- Không có code của các version ở giữa (chỉ có Before/After của chức năng và bản Latest).

## Cần chuẩn bị
- `feature.diff`: một file diff Before → After của chức năng.
  - Hoặc 2 folder `before/` và `after/` → script tự tạo diff.
- `latest/`: source TELINDY mới nhất.
- `target/`: source FOMULAR mới nhất.
- Mã RT (không bắt buộc nếu diff chỉ có 1 RT).
- Hỏi người dùng nếu thiếu một trong các thứ trên. Không tự đoán đường dẫn.

## Nguyên tắc
- Chỉ có một file kết quả là `feature.diff`. Không viết thêm file report.
- Không bao giờ sửa trực tiếp `latest/` hay `target/`. Kết quả merge nằm ở `WORK/target_out/`.
- Bản gốc của diff luôn được giữ ở `WORK/feature.orig.diff`.
- Không tự trả lời thay người dùng các câu hỏi `HỎI NGƯỜI DÙNG`.
- Gom các câu hỏi lại, hỏi một lần cho mỗi bước (dùng AskUserQuestion, tối đa 4 câu mỗi lần).

## Cách chạy
Đặt `S=<thư mục skill>/scripts`, `W=<thư mục làm việc>`. Luôn chạy bằng `python3 -I`.

- Khởi tạo:
  ```
  python3 -I $S/run.py init --work $W --latest LATEST --target TARGET --diff feature.diff [--rt RT2486]
  # hoặc: --before BEFORE --after AFTER thay cho --diff
  ```
- Chạy toàn bộ (tự dừng khi có câu hỏi):
  ```
  python3 -I $S/run.py all --work $W
  ```
- Kết quả trả về:
  - `0` → xong bước/xong hết.
  - `2` → có câu hỏi. Xem phần "Xử lý câu hỏi" rồi chạy lại `run.py all`.
  - `1` → lỗi. Đọc thông báo, báo cho người dùng.

## Các bước (script tự làm)
- **Bước 0 — Đọc changelog, khoanh vùng file**
  - Lấy entry của RT từ dòng `+` trong khối `Modification:` của diff.
  - Chỉ làm việc trên file có entry RT trong Latest + file có trong diff.
  - Đếm các thay đổi xảy ra sau RT, lập danh sách hàm "nghi vấn".
  - Báo cho người dùng: số file, số thay đổi về sau, các hàm nghi vấn, các cảnh báo.
- **Bước 1 — Cập nhật diff lên Latest**
  - Tìm từng đoạn chức năng trong Latest (tên hàm → khớp chuẩn hoá → mỏ neo → điểm %).
  - Thay đổi đơn giản về sau (điều kiện if, tham số) → tự lấy bản Latest.
  - Thay đổi đưa vào hàm/macro/biến mới mà FOMULAR chưa có → hỏi.
  - Thay đổi nằm xa chức năng → bỏ qua (của RT khác).
  - Ghi lại `feature.diff` (stage=latest).
- **Bước 2 — Merge sang FOMULAR**
  - Tìm vị trí từng đoạn trong Target.
  - Khớp chắc chắn → áp dụng. Đã có sẵn → bỏ qua. Không khớp/khớp nhiều chỗ → hỏi.
  - Thêm entry changelog của RT vào khối `Modification:` của file FOMULAR.
  - Ghi kết quả vào `target_out/` và ghi chú vào `feature.diff` (stage=merged).
- **Bước 3 — Kiểm tra**
  - Đủ các hàm của RT, đủ định nghĩa symbol, không còn câu hỏi, encoding/xuống dòng giữ nguyên.
  - Nếu người dùng cho lệnh build: thêm `--build-cmd "make ..."`.

## Xử lý câu hỏi
- Xem câu hỏi: `python3 -I $S/run.py questions --work $W` (chi tiết trong `$W/.port_changelog/questions.json`).
- Câu `LLM tự đánh giá` (`who: llm`, loại `llm_judge`):
  - Tự đọc đoạn gốc và các ứng viên trong `context`.
  - Chắc chắn cùng logic → trả lời `Y` (hoặc số ứng viên) với `--by llm` và ghi lý do ngắn trong `--note`.
  - Không chắc → hỏi người dùng (đưa đoạn gốc + ứng viên tốt nhất).
- Câu `HỎI NGƯỜI DÙNG` (`who: user`):
  - Hỏi bằng AskUserQuestion. Mỗi câu nêu rõ: tên hàm, symbol mới, gợi ý RT từ changelog (`rt_hint`).
  - Ghi đúng câu trả lời của người dùng.
- Ghi câu trả lời:
  ```
  python3 -I $S/run.py answer --work $W --id "<id>" --answer Y|N|1|2|3 [--by user|llm] [--note "..."]
  ```
- Ý nghĩa câu trả lời:
  - `new_symbol`: `Y` = merge kèm định nghĩa symbol, `N` = giữ dạng cũ (After).
  - `missing_unit`: `Y` = giữ dạng After, `N` = bỏ đoạn đó.
  - `target_mismatch` / `target_ambiguous`: `Y` = áp vào ứng viên tốt nhất, số = chọn ứng viên, `N` = bỏ qua.
  - `target_file_missing`: `Y` = tạo file mới từ Latest, `N` = bỏ qua.
- Sau khi trả lời hết → chạy lại `run.py all`.

## Kết thúc
- Báo cho người dùng ngắn gọn:
  - Đường dẫn `feature.diff` và `target_out/`.
  - Số đoạn tự áp dụng / bỏ qua / theo quyết định của người dùng (đọc các dòng `# step2` trong diff).
  - Các ghi chú `UNEXPLAINED` (thay đổi không có trong changelog) → khuyên người dùng xem lại.
  - Kết quả Bước 3.
- Muốn xem thay đổi trên Target: `diff -ru TARGET $W/target_out`.

## Giới hạn
- Không tách được tự động khi một dòng vừa là cải tiến của chức năng vừa là logic của RT khác → luôn hỏi.
- File không ghi entry RT (thường là `.h`) chỉ được tìm qua danh sách file trong diff.
- Ngưỡng (0.9 / 0.6, k = 3) nằm trong `.port_changelog/config.json`, có thể chỉnh.
