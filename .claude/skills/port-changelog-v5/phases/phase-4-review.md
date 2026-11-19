# Phase 4 — Duyệt trên UI và chốt kết quả

## Mục tiêu

- Cho người dùng xem kết quả Phase 3 trên UI hai cột và quyết định từng chỗ thay đổi.
- Áp quyết định vào `WORK/target_out/`, ra bản Target cuối cùng.
- Đầu vào: `WORK/phase3/merge_view.json` (đã qua `merge_ui.py check`), `WORK/phase3/REPORT.md`, `target/`, `WORK/target_out/`.

## Hiểu đúng trước khi làm

- **`merge_view.json` là nguồn duy nhất.** UI, file kết quả và report đều dựng từ nó. Muốn đổi kết quả thì sửa JSON rồi chạy lại tool, không sửa tay `target_out/` rồi để JSON lệch.
- **`apply` dựng lại file từ `target/` gốc.** Mỗi lần chạy cho ra cùng kết quả với cùng JSON và cùng `decisions.json`.
- **Mục `NEED_CONFIRM` chỉ được áp khi người dùng chọn "Lấy feature" cho đúng mục đó** (quy tắc `NEED_CONFIRM` trong `SKILL.md`).

## Từ khóa của Phase này

Các từ dùng chung (RT, đơn vị, hunk, dòng `+` / `-`, diff (new)...) xem trong `SKILL.md`.

- **UI review**: file `merge_view.html` sinh từ `merge_view.json`. Cột trái là diff (new), cột phải là FOMULAR.
  - Vùng đã detect: nền đỏ nhạt ở cả hai cột (dòng `-` bên trái, block FOMULAR bên phải).
  - Code feature: nền xanh. Hunk đang được lấy thì phía `+` hiện ở cả hai cột. Hunk chưa lấy thì cột phải để trống, cao bằng phần `+`.
- **Quyết định**: lựa chọn của người dùng cho một hunk: `accept` (lấy feature) hoặc `reject` (giữ FOMULAR). Mục `NEED_CONFIRM` ban đầu là `pending` (chưa quyết định).
- **`decisions.json`**: file người dùng tải từ UI. Gồm quyết định và câu trả lời (ô ghi chú) của từng hunk.

```json
{
  "rt": "RT2707",
  "signature": "1a2b3c4d5e6f",
  "files": {
    "<path>": {
      "decisions": { "A5": "accept", "A4": "reject" },
      "answers":   { "A4": "Giữ FOMULAR, không dùng force-get" }
    }
  }
}
```

- **Mục sửa tay**: hunk `NEED_CONFIRM` có `target: null` (không xác định được vị trí). UI không bật/tắt được, chỉ ghi câu trả lời.

## Tóm tắt luồng

```text
Bước 1. Kiểm tra đầu vào: merge_ui.py check phải KHỚP
Bước 2. Render UI: merge_view.json → WORK/phase4/merge_view.html → báo người dùng → DỪNG chờ decisions.json
Bước 3. Nhận decisions.json
   ├─ Còn hunk pending           → hỏi lại đúng các hunk đó
   ├─ Mục sửa tay có câu trả lời → thêm vị trí vào JSON (Bước 4)
   └─ Mục đã accept               → kiểm tra phụ thuộc của nó (Bước 5)
Bước 4. Mục sửa tay → thành hunk có vị trí
Bước 5. Cập nhật changelog cho các mục mới được lấy
Bước 6. Áp quyết định: merge_ui.py apply → WORK/target_out/
Bước 7. Kiểm tra cuối
Bước 8. Report cuối → DỪNG
```

---

## Bước 1 — Kiểm tra đầu vào

```bash
TOOLS=<thư mục skill>/tools
python3 $TOOLS/merge_ui.py check WORK/phase3/merge_view.json --target-out-root WORK/target_out
```

- Phải `KHỚP` mọi file. Không khớp: dừng, báo người dùng. Không render UI từ một JSON không khớp với `target_out/`.

## Bước 2 — Render UI và dừng

```bash
python3 $TOOLS/merge_ui.py render WORK/phase3/merge_view.json -o WORK/phase4/merge_view.html
```

- `render` báo `LỖI` thì dừng, sửa JSON. Báo `CẢNH BÁO` thì ghi vào report.
- Báo cho người dùng:
  - Đường dẫn `WORK/phase4/merge_view.html`.
  - Số hunk đã lấy sẵn, số mục cần xác nhận, số mục sửa tay.
  - Cách dùng: chọn "Lấy feature" / "Giữ FOMULAR" (hoặc bấm `→` / `✓` ở giữa hai cột) cho từng mục, ghi câu trả lời vào ô dưới câu hỏi, bấm "Tải decisions.json", gửi lại file. Nút "Mục cần xác nhận tiếp" nhảy tới mục chưa quyết định.
- Dừng, chờ `decisions.json`. Lưu file nhận được vào `WORK/phase4/decisions.json`.

## Bước 3 — Đọc `decisions.json`

- `signature` khác với `merge_view.json` hiện tại: UI được tạo từ một bản JSON cũ. Báo người dùng, hỏi có dùng tiếp không.
- Còn hunk `pending`: không áp. Hỏi lại người dùng đúng các hunk đó.
- Ghi mọi quyết định và câu trả lời vào report. Không tự điền thay người dùng.
- Mục `accept` mà câu trả lời có yêu cầu sửa phía `+` (ví dụ "lấy nhưng đổi tên tham số"): sửa `plus` của hunk trong JSON theo đúng yêu cầu, ghi rõ vào report. Không tự sửa khi người dùng không yêu cầu.

## Bước 4 — Mục sửa tay

- Với mỗi hunk `target: null`:
  - Câu trả lời là "không lấy" / "giữ FOMULAR": giữ nguyên, ghi vào report.
  - Câu trả lời chỉ ra chỗ sửa: tìm đúng chỗ đó ở `target/` gốc, ghi `target` (`start`/`end` hoặc `after`) vào hunk trong JSON, đổi `result` thành `MERGED`, ghi trong `note` là "vị trí do người dùng chỉ".
  - Câu trả lời chưa đủ để xác định vị trí: hỏi lại, không đoán.

## Bước 5 — Phụ thuộc và changelog của các mục mới được lấy

- **Phụ thuộc:** mục `NEED_CONFIRM` được `accept` có thể cần đơn vị khác cũng đang chờ (note "chờ mục <id>").
  - Mục cha được `accept` mà mục con (thứ nó cần) bị `reject` hoặc `pending`: báo người dùng, hỏi lại. Không tự đổi quyết định.
  - Mục cha bị `reject` mà mục con được `accept`: báo người dùng là mục con sẽ thành code thừa.
- **Changelog:** sửa `plus` của hunk `CHANGELOG` trong JSON để entry RT liệt kê thêm các đơn vị vừa được lấy (`Add.` / `Mod.`). Bỏ các đơn vị bị `reject`. Giữ đúng định dạng cột của khối `Modification:`.
- Sau khi sửa JSON, `signature` thay đổi. `apply` sẽ báo cảnh báo khác signature: đây là điều mong đợi, ghi vào report.

## Bước 6 — Áp quyết định

```bash
python3 $TOOLS/merge_ui.py apply WORK/phase3/merge_view.json \
        --decisions WORK/phase4/decisions.json -o WORK/target_out
```

- `apply` dựng lại từng file từ `target/` gốc + các hunk `accept`, giữ encoding và kiểu xuống dòng gốc.
- Còn hunk `pending` thì `apply` dừng và báo tên hunk. Quay lại Bước 3.

## Bước 7 — Kiểm tra cuối

- Chạy lại toàn bộ danh sách "Kiểm tra cuối" của Phase 3 (Bước 8) trên `target_out/` mới.
- Thêm:
  - Mọi hunk `reject`: vị trí của nó trong `target_out/` giống `target/` gốc.
  - Mọi hunk `accept`: phía `+` có trong `target_out/` đúng vị trí.
  - Mọi tên mà các hunk vừa được lấy dùng tới đều có định nghĩa trong `target_out/`.
- Gọi `get-diff(target_out/<file>, target/<file>)` cho mỗi file, lưu vào `WORK/phase4/diff/<đường dẫn file>.diff`.

## Bước 8 — Report cuối, thông báo và dừng

- Ghi `WORK/phase4/REPORT.md` theo mẫu trong `SKILL.md`, thêm:
  - **Bảng quyết định**: file, id hunk, đơn vị, kết quả Phase 3, quyết định (`accept` / `reject`), câu trả lời của người dùng.
  - **Mục sửa tay**: vị trí đã ghi vào JSON, theo câu trả lời nào.
  - **Thay đổi JSON trong Phase 4**: changelog, `plus` sửa theo yêu cầu, vị trí mục sửa tay.
  - **Kiểm tra cuối** và "chưa compile" nếu không build.
- Báo cho người dùng: đường dẫn report, `target_out/`, các diff ở `WORK/phase4/diff/`.
- Không báo "hoàn tất" khi còn mục chưa được trả lời.
