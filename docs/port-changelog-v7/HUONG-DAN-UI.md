# Hướng dẫn sử dụng trang duyệt merge (`review.html`)

Trang này dùng ở **Phase 4**, để người duyệt xem kết quả merge của một RT theo kiểu merge-conflict trên GitHub. Trên trang, người duyệt trả lời các câu hỏi cần xác nhận, chọn giữ code Target hoặc áp code RT cho từng đoạn, rồi xuất quyết định.

Trang là **một file HTML duy nhất**, mở bằng double-click, không cần mạng hay server.

Ví dụ trong tài liệu này dùng một RT minh họa (RT1234).

---

## 1. Mở trang

Agent tạo trang sau khi xong Phase 3:

```
python3 tools/render_review.py --plan WORK/<run-id>/phase3/merge-plan.json --target-root <thư mục target> -o WORK/<run-id>/phase3/review.html
```

Mở file `review.html` bằng Chrome, Edge hoặc Firefox.

- Đầu trang có **banner đỏ** nghĩa là dữ liệu merge bị lỗi (sai vị trí dòng, liên kết hỏng…). Khi đó **không duyệt tiếp**: báo agent quay lại Phase 3 để sửa. Các nút xuất cũng bị khóa.
- Trang **tự nhớ** các quyết định trong trình duyệt. Mở lại sẽ thấy dòng "Đã khôi phục … quyết định". Muốn làm lại từ đầu thì bấm **Xóa quyết định**.

---

## 2. Bố cục trang

![Tổng quan](docs/ui-tong-quan.png)

| Vùng | Nội dung |
|---|---|
| **Đầu trang** | Mã RT, số đoạn theo từng trạng thái, các nút: Nạp decisions.json · Xóa quyết định · Tải decisions.json · Tải file output |
| **Thanh bên trái** | Danh sách câu hỏi (đỏ = chưa trả lời), rồi file → hàm → từng đoạn (chunk) với chấm màu trạng thái. Bấm vào mục nào thì trang nhảy tới mục đó |
| **Khung "Câu hỏi cần xác nhận"** | Mỗi câu hỏi có nội dung, bằng chứng và các phương án |
| **Khu code của mỗi file** | Cột trái là **code output hiện tại**. Cột phải là **thẻ chunk** nằm ngang hàng với đoạn code tương ứng |
| **Đã xét, không áp** | Những đoạn RT đã được xem xét nhưng không cần merge, kèm lý do (ví dụ Target đã có sẵn) |

### Chunk là gì?

Chunk là **một đoạn code liên tục trong file Target** có thể thay bằng code RT. Mỗi chunk có mã `K1`, `K2`…

### Cột trái

- Là file **sau khi ghép theo các quyết định hiện tại**. Nó được cập nhật ngay sau mỗi lần bấm.
- Những đoạn dài không thay đổi được gập lại (`⋯ 48 dòng không đổi`), bấm để mở ra.
- Vùng của mỗi chunk được tô màu theo trạng thái. Dòng nhỏ phía trên ghi `K4 · NEED_CONFIRM · Target`, nghĩa là chunk K4 đang chờ xác nhận và đang hiển thị code Target.

---

## 3. Ý nghĩa màu và trạng thái

| Màu | Trạng thái | Nghĩa | Cần làm gì |
|---|---|---|---|
| 🟩 Xanh lá | **APPLIED** | Đã áp code RT | Xem lại cho chắc. Không đồng ý thì bấm ← |
| ⬜ Xám | **KEPT** | Bạn (hoặc câu trả lời) đã chọn giữ Target | — |
| 🟥 Đỏ | **NEED_CONFIRM** | Đang chờ một câu hỏi | Trả lời câu hỏi ghi trên thẻ |
| 🟨 Vàng | **BLOCKED** | Muốn áp nhưng đang chờ chunk khác (thẻ ghi "chờ K4: lý do") | Xử lý chunk đang chặn nó |
| 🟨 Vàng nhạt | **FOLLOW** | Code chỉ phục vụ chunk đang bị giữ (khai báo, helper…). Sẽ tự áp khi chunk dùng nó được áp | Thường không cần làm gì |

**Quy tắc liên kết:** một chunk chỉ bị chặn bởi những chunk **mà nó thật sự cần** (dùng biến, gọi hàm do chunk kia tạo ra), không bị chặn chỉ vì nằm gần đoạn đang chờ. Trên thẻ có hai dòng:
- `cần:` các chunk mà chunk này phụ thuộc.
- `được dùng bởi:` các chunk phụ thuộc vào chunk này.

---

## 4. Thẻ chunk

![Thẻ chunk](docs/ui-chunk.png)

Từ trên xuống, một thẻ gồm:

1. **Tiêu đề:** mã chunk, trạng thái, tên hàm, và code đang dùng (Target hay Đề xuất).
2. **Tóm tắt** thay đổi.
3. **`src`:** hunk gốc trong diff Phase 2, dùng để đối chiếu.
4. **Vị trí:** `Target dòng 188–193 → output dòng 190–195`.
5. **Ghi chú** của agent (nền xám), và lý do đang bị giữ (nền vàng hoặc đỏ).
6. **Các nút thao tác** (mục 5).
7. **Các tab xem code:**

| Tab | Hiển thị |
|---|---|
| **Thay đổi** | Diff giữa Target và Đề xuất: dòng `-` đỏ, dòng `+` xanh |
| **Current** | Code Target hiện có |
| **Base** | Code Before (TELINDY, trước RT). Chỉ có ở chỗ Target khác Before, giúp hiểu vì sao phải hỏi |
| **Incoming** | Code RT nguyên văn. Chỉ có khi khác Đề xuất |
| **Đề xuất** | Code sẽ được áp. Tên biến đã đổi theo Target được **tô đậm**, rê chuột vào để xem tên gốc và chứng cứ (ví dụ `name_new → nameNew`, tham số #4, kiểu `text*`) |

---

## 5. Các nút thao tác

| Nút | Tác dụng | Chunk khác bị ảnh hưởng |
|---|---|---|
| **Áp →** | Dùng code Đề xuất cho chunk này | Mọi chunk mà nó **cần** cũng được áp theo |
| **← Giữ Target** | Giữ code Target cho chunk này | Mọi chunk **đang cần nó** lùi về Target (thành BLOCKED) |
| **RT** | Dùng code RT nguyên văn (tab Incoming) | Giống Áp →. Chỉ hiện khi chunk có tab Incoming |
| **↺** | Bỏ lựa chọn tay, chunk quay về trạng thái tự tính | Tính lại tự động |

- Nếu thao tác làm thay đổi chunk khác, trang hiện **hộp xác nhận** liệt kê những chunk sẽ bị kéo theo hoặc lùi theo. Bấm **Đồng ý** thì mới thực hiện.
- Trang **không cho áp** trong hai trường hợp sau, mà sẽ cuộn tới câu hỏi liên quan kèm lời nhắc:
  - chunk cần tới một chunk đang chờ câu hỏi **chưa trả lời**;
  - chunk cần tới một chunk mà câu hỏi đã được trả lời **giữ Target**. Muốn áp thì đổi câu trả lời trước.

### Ví dụ với RT1234

| Thao tác | Kết quả |
|---|---|
| Áp K2 (`value_new = NULL`) | K2 được áp, K1 (khai báo `value_new`) được kéo theo |
| Áp K10 (helper `libLinkVarSet`) | Helper được chèn trước `/** EOF **/`, không kéo theo gì |
| Áp K5 (thông báo lỗi của getter) | Không áp được: K5 cần K4, mà K4 đang chờ Q1. Trang cuộn tới Q1 |
| Giữ K1 (khai báo) | K2 thành BLOCKED vì K2 dùng `value_new` do K1 khai báo |

---

## 6. Trả lời câu hỏi

Mỗi câu hỏi (khung viền đỏ) gồm:
- **Nội dung câu hỏi** và **bằng chứng** (vị trí, kết quả tìm kiếm).
- Dòng `quyết định: K4, K8`: các chunk mà câu hỏi này quyết định.
- **Các phương án.** Mỗi phương án ghi chọn nó thì chunk nào được áp, chunk nào giữ Target. Phương án agent đề xuất có nhãn **đề xuất**.

Bấm vào một phương án để chọn. Nếu lựa chọn làm thay đổi chunk khác, trang hiện hộp xác nhận. Muốn đổi câu trả lời thì bấm phương án khác.

### Ví dụ với RT1234

| Trả lời | Kết quả |
|---|---|
| Q1 = apply (sẽ có source hai hàm Force) | K4 được áp, K5 hết bị chặn. K8 chuyển sang BLOCKED vì còn cần K6, K9 của Q2 |
| Tiếp Q2 = apply | K6, K9 được áp, K7, K8 được mở khóa. Khai báo K1, K2 và helper K10 đi theo. **Cả 10 chunk được áp** |
| Q1 = keep | K4, K8 giữ Target. K5 vẫn BLOCKED. Helper K10 không được thêm |

---

## 7. Lưu và xuất kết quả

| Nút | Dùng khi |
|---|---|
| **Tải decisions.json** | Lưu toàn bộ câu trả lời và lựa chọn tay. **Gửi file này cho agent** (lưu vào `WORK/<run-id>/phase4/decisions.json`) |
| **Nạp decisions.json** | Mở lại các quyết định đã lưu, ví dụ để duyệt tiếp trên máy khác |
| **Tải file output** | Tải code đã ghép. **Chỉ có với file UTF-8/ASCII** |
| **Xóa quyết định** | Bỏ hết, quay về trạng thái ban đầu |

**File cp932 (tiếng Nhật):** trình duyệt chỉ ghi được UTF-8, nên trang không có nút tải mà hiện sẵn lệnh để agent ghép đúng encoding:

```
python3 tools/render_review.py --plan merge-plan.json --target-root <target> --decisions decisions.json --apply -o <thư mục output>
```

File ghi bằng lệnh này **giống hệt** cột trái của trang, giữ nguyên encoding và kiểu xuống dòng của file gốc.

---

## 8. Quy trình duyệt gợi ý

1. Xem đầu trang: không có banner đỏ, ghi lại số đoạn theo từng trạng thái.
2. **Trả lời các câu hỏi trước.** Đọc bằng chứng, xem tab **Base** và **Current** của các chunk liên quan để hiểu vì sao phải hỏi.
3. Xem lại từng chunk **xanh**: tab **Thay đổi** và tên được tô đậm. Thấy sai thì bấm ← và ghi chú lý do để báo agent.
4. Xem các chunk **vàng** còn lại: thẻ ghi đang chờ gì. Nếu chờ một câu hỏi bạn chủ ý để lại thì chấp nhận được.
5. Xem mục **Đã xét, không áp** để chắc không có đoạn nào bị bỏ sai.
6. **Tải decisions.json** rồi gửi cho agent. Nếu bạn muốn sửa code khác cả Target lẫn RT, hoặc có câu hỏi mới, hãy ghi bằng lời cho agent: phần đó phải quay lại Phase 3.

---

## 9. Câu hỏi thường gặp

**Bấm Áp → mà không có gì xảy ra?**
Trang đã cuộn tới một câu hỏi. Xem dòng nhắc phía trên: chunk đang cần một chunk chờ câu hỏi chưa trả lời, hoặc chờ câu hỏi đã trả lời giữ Target.

**Chunk FOLLOW có cần bấm Áp không?**
Thường là không. Nó tự áp khi chunk dùng nó được áp. Chỉ bấm khi bạn muốn áp riêng nó, ví dụ để thêm một helper sẵn.

**Mở lại trang thấy quyết định cũ?**
Trang nhớ trong trình duyệt. Bấm **Xóa quyết định** để làm lại, hoặc **Nạp decisions.json** để mở đúng bản đã gửi.

**Trang có sửa file Target không?**
Không. Trang chỉ đọc. File output chỉ được tạo khi bạn tải về hoặc khi agent chạy lệnh `--apply`.
