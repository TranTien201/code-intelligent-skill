# Phase 3 — Merge diff mới nhất vào FOMULAR

## 3.1 Chuẩn bị

- Copy các file Target liên quan vào `WORK/target_out/` (giữ cấu trúc thư mục). Chỉ sửa trên bản copy.
- Tìm file tương ứng trong Target theo đường dẫn tương đối. Không thấy thì tìm theo tên file; có nhiều ứng viên thì hỏi.

## 3.2 Luật merge cho từng block

Xử lý lần lượt từng block trong `WORK/phase2/<file>.diff`:

- **Block chỉ có `+`** (hàm/symbol mới, kể cả `PHỤ THUỘC - MỚI`)
  - Target chưa có ⇒ thêm vào. Ghi `MERGED`.
  - Target đã có và giống nhau ⇒ không làm gì. Ghi `SKIP - đã có`.
  - Target đã có nhưng khác nội dung, chữ ký hoặc kiểu ⇒ đưa vào "Cần xác nhận".
- **Block có nhãn `PHỤ THUỘC - ĐÃ ĐỔI`** (biến/macro/kiểu mà hàm của RT cần)
  - Target có và phần `-` khớp ⇒ thay bằng phần `+`. Ghi `MERGED`.
  - Target **không có** ⇒ vẫn phải thêm bản Latest (phần `+`), vì hàm đã merge cần nó. Ghi `MERGED - thêm phụ thuộc`.
  - Target có nhưng khác phần `-` ⇒ đưa vào "Cần xác nhận".
- **Phụ thuộc giống nhau ở Before và Latest** (chỉ có trong report Phase 2, không có block)
  - Target có ⇒ không làm gì.
  - Target không có ⇒ thêm định nghĩa Latest. Ghi `MERGED - thêm phụ thuộc`.
- **Block có `-` rồi `+`** (sửa code đã có)
  - Kiểm tra Target có hàm/đoạn code đó không (tìm theo tên hàm trước, sau đó mới so nội dung).
  - **Target không có** ⇒ **không merge**. Ghi `SKIP - Target không có` kèm tên hàm.
  - Target có và phần `-` khớp ⇒ thay bằng phần `+`. Ghi `MERGED`.
  - Target có nhưng code khác phần `-` (FOMULAR có code riêng):
    - Giữ được code riêng và vẫn áp được thay đổi một cách chắc chắn ⇒ merge, ghi chú rõ đã giữ gì.
    - Không chắc ⇒ không ghi đè cả hàm, đưa vào "Cần xác nhận".
- **Block chỉ có `-`** hoặc nhãn `DELETE`
  - Target không có ⇒ ghi `SKIP - Target không có`.
  - Target có, giống bản cũ và không còn nơi nào gọi ⇒ xóa. Ghi `DELETED`.
  - Target có code riêng hoặc còn nơi khác gọi ⇒ đưa vào "Cần xác nhận".

## 3.3 Changelog của Target

- Thêm entry RT vào khối `Modification:` của các file Target đã sửa, theo đúng cách viết sẵn có của file đó.
- Chỉ liệt kê `Add.` / `Mod.` cho những hàm thật sự đã merge.

## 3.4 Kiểm tra cuối

- Mọi file ở Phase 1 đều có kết quả cuối.
- Mọi symbol được dùng trong code đã merge đều có định nghĩa trong Target.
- Prototype khớp với định nghĩa hàm.
- Không còn nơi nào gọi tới hàm đã xóa.
- Encoding và kiểu xuống dòng của file trong `target_out/` giống file Target gốc.
- Có môi trường build thì compile thử. Không có thì ghi rõ "chưa compile".

## 3.5 Report, thông báo và dừng

- Ghi `WORK/phase3/REPORT.md` theo mẫu ở mục "Mẫu report" trong `SKILL.md`.
- Báo cho người dùng đường dẫn report, đường dẫn `target_out/` và số đoạn `MERGED` / `SKIP` / `DELETED` / cần xác nhận.
- Hỏi người dùng từng mục "Cần xác nhận". Áp dụng câu trả lời vào `target_out/` và cập nhật report.
- Không báo "hoàn tất" khi còn mục chưa được trả lời.
