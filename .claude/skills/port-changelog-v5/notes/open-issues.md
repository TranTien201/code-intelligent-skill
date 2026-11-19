# Vấn đề còn mở của port-changelog-v5

File này ghi lại các vấn đề chưa có cách xử lý tự động, để xem lại sau.
Các file hướng dẫn Phase không tham chiếu tới file này. Agent chạy skill không cần đọc nó.

---

## 1. Phụ thuộc có từ trước, bị RT sau sửa thân, nhưng cách dùng không đổi

### Vấn đề

- Khi trace từ các dòng `+` của feature, gặp một phụ thuộc T (thường là hàm dùng chung) thoả cả ba điều:
  - T có từ Before (có trước RT đang port).
  - Ở Latest, thân của T đã bị RT sau sửa.
  - Dòng `+` của feature vẫn dùng T **đúng như cách cũ** (cùng chữ ký, cùng kiểu, cùng giá trị).
- Không biết phần sửa trong thân T thuộc feature đang port hay thuộc feature khác.
  - Mang sang: có thể kéo logic không liên quan vào FOMULAR.
  - Không mang: có thể thiếu một phần của feature.
- Không có snapshot trung gian nên không tách được phần sửa của từng RT.

### Ví dụ

- RT2486 thêm dòng gọi `LogPrint("GetAllVari NG")`. `LogPrint` có từ trước RT2486.
- Ở Latest, RT2800 thêm `LogWriteFile(fmt, ap);` vào thân `LogPrint`.
- Dòng của RT2486 vẫn gọi `LogPrint` như cũ.
- Câu hỏi: có mang `LogPrint` bản Latest (và `LogWriteFile`) sang FOMULAR không?

### Cách xử lý hiện tại

- Luôn ghi `NEED_CONFIRM`. Người duyệt quyết định.

### Ý tưởng thu hẹp bằng changelog (chưa áp dụng)

- **Tập S:** các RT sau đã sửa vào block của feature. Lấy từ changelog của file chứa hàm X: những RT ghi `Mod. X()` mà block `+` của X đã đổi ở Latest.
- **RT đã sửa T:** đọc từ changelog của file chứa T.
- So hai thứ:

| T bị sửa thân bởi | Ý nghĩa | Xử lý đề xuất |
|---|---|---|
| Chỉ các RT **không** nằm trong S | Những RT đó chưa từng đụng vào logic của feature | Không mang, coi T là đồ cũ (ghi vào `paused.md`). Không hỏi |
| Có RT **nằm trong** S | Cùng một RT vừa sửa block của feature vừa sửa T, nhiều khả năng liên quan | `NEED_CONFIRM`, đề xuất mang theo |
| Changelog không ghi ai sửa | Không có căn cứ | `NEED_CONFIRM` |

### Giới hạn của ý tưởng

- Changelog ghi ở mức hàm, không ở mức dòng. Hàm X có nhiều RT sau cùng sửa thì tất cả vào tập S, dù có thể chỉ một RT đụng vào block của feature. Tập S bị rộng: hỏi thừa, không bỏ sót.
- T bị cả RT trong S lẫn RT ngoài S sửa: không tách được phần của ai, vẫn phải `NEED_CONFIRM`.
- Phụ thuộc vào việc khách ghi changelog đầy đủ.

### Khi nào xem lại

- Sau vài lần chạy thật, nếu số câu hỏi `NEED_CONFIRM` loại này nhiều và phần lớn câu trả lời là "không mang".
