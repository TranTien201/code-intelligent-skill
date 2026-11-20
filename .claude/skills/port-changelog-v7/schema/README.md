# Hợp đồng dữ liệu Phase 3 → Phase 4

File `WORK/<run-id>/phase3/merge-plan.json` là đầu ra của Phase 3 và là đầu vào của UI (`tools/render_review.py`).
Schema: `merge-plan.schema.json`. Quyết định của người duyệt: `decisions.schema.json`.

Nguyên tắc:

- **Tọa độ chỉ tính theo file Target gốc.** Target gốc không bao giờ bị sửa nên tọa độ luôn đúng. Số dòng trong output được tính lại mỗi lần ghép, không lưu.
- **Lưu nội dung code**, không chỉ số dòng.
- **Trạng thái không lưu.** NEED_CONFIRM, BLOCKED, FOLLOW… được tính từ `questions`, `requires` và quyết định (xem mục 4).

## 1. Cấp cao nhất

| Trường | Ý nghĩa |
|---|---|
| `rt` | Mã RT |
| `version` | Luôn là `1` |
| `files` | Khóa là đường dẫn file Target (tương đối từ `target/`). Giá trị: `encoding`, `name_map` |
| `chunks` | Các đoạn thay đổi (mục 2) |
| `questions` | Các câu hỏi NEED_CONFIRM (mục 3) |
| `skipped` | Các đoạn RT đã xét nhưng không tạo chunk, kèm lý do (mục 5) |

`name_map[]`: `{from, to, proof}`. Tên Before → tên Target, kèm chứng cứ. UI tô đậm các token `to` trong `apply`.

## 2. Chunk

Một chunk là **một vùng liên tục trong Target gốc** sẽ được thay bằng code khác khi áp.

| Trường | Bắt buộc | Ý nghĩa | UI dùng để |
|---|---|---|---|
| `id` | ✔ | `K1`, `K2`… | Tham chiếu |
| `file` | ✔ | Một khóa trong `files` | Gom theo file |
| `unit` | ✔ | Tên hàm / prototype / global / `Modification` | Gom theo hàm |
| `src` | ✔ | Hunk nguồn ở diff(new) Phase 2 | Hiện nguồn để đối chiếu |
| `summary` | ✔ | Một câu mô tả | Tiêu đề khung |
| `target.start`, `target.end` | ✔ | Dòng đầu và dòng cuối (tính từ 1, tính cả hai đầu) trong Target gốc | Vị trí thay và vị trí hiển thị |
| `target.text` | ✔ | Nguyên văn các dòng đó | Phía **Current**; kiểm tra tọa độ |
| `apply` | ✔ | Code thay vào khi áp, đã đổi tên theo `name_map` | Phía **Đề xuất** |
| `base` | | Code Before tương ứng. Chỉ ghi cho chunk có câu hỏi hoặc Target khác Before | Phía **Base** |
| `rt` | | Code RT nguyên văn (đã đổi tên). Chỉ ghi khi khác `apply` | Phía **Incoming** + nút "RT" |
| `requires` | | `[{chunk, why}]`: các chunk phải được áp thì chunk này mới áp được | Kéo theo khi bấm →; tính BLOCKED/FOLLOW |
| `note` | | Giải thích thêm | Tooltip |

### Quy ước text

- Mỗi dòng kết thúc bằng `\n`, kể cả dòng cuối. Luôn dùng `\n` trong JSON, dù file thật dùng CRLF. Khi ghi file, tool dùng lại kiểu xuống dòng của file gốc.
- `apply` có thể rỗng (`""`), nghĩa là xóa vùng đó.
- Dòng cuối file Target không có `\n`: `target.text` vẫn ghi `\n`. Tool tự xử lý khi ghép.

### Chèn mới (đơn vị NEW)

Không có range rỗng. Muốn chèn thì **thay một dòng neo** bằng "code mới + dòng neo":

```json
"target": { "start": 270, "end": 270, "text": "/** EOF **/\n" },
"apply":  "/*#---…#*/\nstatic uint32 libLinkVarSet(…)\n{\n…\n}\n\n/** EOF **/\n"
```

Hai thứ cần chèn cùng một neo thì gộp thành một chunk.

### `requires`

- `X requires Y`: X dùng thứ Y tạo ra (biến, hàm, giá trị), hoặc X phục vụ cùng ý đồ với Y (`why` phải nói rõ).
- Chiều luôn là **chỗ dùng → chỗ định nghĩa**. Không phân biệt cùng hunk hay khác hunk, cùng file hay khác file.
- Không tạo cạnh chỉ vì hai chunk nằm gần nhau.

## 3. Câu hỏi

| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| `id` | ✔ | `Q1`, `Q2`… |
| `text` | ✔ | Câu hỏi |
| `evidence` | | Bằng chứng (vị trí, kết quả tìm kiếm) |
| `chunks` | ✔ | Các chunk mà câu hỏi quyết định |
| `options[]` | ✔ | `{id, label, apply}`. `apply` = các chunk trong `chunks` được áp khi chọn phương án này; chunk còn lại trong `chunks` giữ Target |
| `recommended` | | Mã phương án đề xuất |

Một chunk chỉ thuộc tối đa một câu hỏi.

## 4. Tính trạng thái và ghép output

Đầu vào: plan + `decisions` (`answers`: Q → phương án, `choices`: K → `target` / `rt` / `apply`).

**Bước 1. Ý muốn của từng chunk**

| Điều kiện (xét theo thứ tự) | Ý muốn | Trạng thái tạm |
|---|---|---|
| Có trong `choices` | Giá trị đó | `target` → KEPT; `apply`/`rt` → APPLIED |
| Thuộc câu hỏi đã trả lời | `apply` nếu nằm trong `option.apply`, ngược lại `target` | APPLIED / KEPT |
| Thuộc câu hỏi chưa trả lời | `target` | NEED_CONFIRM |
| Còn lại | `apply` | APPLIED |

**Bước 2. Hạ cấp, lặp tới khi không còn thay đổi**

- **BLOCKED:** chunk đang APPLIED nhưng có `requires` tới chunk không APPLIED → hạ thành `target`, trạng thái BLOCKED (ghi chunk chặn). Riêng chunk người duyệt chọn tay trong `choices` cũng bị hạ; UI phải kéo theo trước (xem 4b).
- **FOLLOW:** chunk đang APPLIED, **không** nằm trong `choices`, không thuộc câu hỏi, có ít nhất một chunk khác `requires` tới nó, và **mọi** chunk `requires` tới nó đều không APPLIED → hạ thành `target`, trạng thái FOLLOW.
- Chỉ hạ cấp, không bao giờ nâng cấp, nên vòng lặp luôn dừng. Chu trình không bị hạ nếu không có gì từ ngoài chặn.

**Bước 3. Ghép output**

- Sắp chunk theo `target.start` giảm dần. Với mỗi chunk, thay dòng `start..end` bằng text theo lựa chọn cuối: `target` → `target.text`, `apply` → `apply`, `rt` → `rt`.
- Ghi lại với encoding và kiểu xuống dòng của file gốc.

**Bảng trạng thái cuối**

| Trạng thái | Nghĩa | Màu UI |
|---|---|---|
| APPLIED | Đã áp (`apply` hoặc `rt`) | Xanh |
| KEPT | Người duyệt / câu trả lời chọn giữ Target | Xám |
| NEED_CONFIRM | Chờ câu hỏi | Đỏ |
| BLOCKED | Chờ chunk khác (ghi chunk chặn) | Vàng |
| FOLLOW | Chỉ phục vụ chunk đang bị giữ, sẽ đi theo | Vàng nhạt |

### 4b. Thao tác trên UI

- **→ (áp):** đặt `choices[K] = apply` và mọi chunk trong bao đóng `requires` của K cũng `apply`. Nếu bao đóng có chunk thuộc câu hỏi **chưa trả lời**, hoặc thuộc câu hỏi **đã trả lời giữ Target** cho chunk đó, thì không áp; UI chỉ tới câu hỏi để người duyệt trả lời / đổi câu trả lời trước. Bấm → ngay trên chunk thuộc câu hỏi vẫn được (người duyệt chủ động chọn tay).
- **RT:** như → nhưng `choices[K] = rt`. Chỉ hiện khi chunk có `rt`.
- **← (giữ Target):** đặt `choices[K] = target`. Bước 2 tự hạ các chunk phụ thuộc.
- Trước khi đổi, UI hiện danh sách chunk sẽ bị kéo theo / lùi theo.

## 5. `skipped`

Mỗi đoạn RT trong diff(new) mà không thành chunk phải có một dòng ở đây:

| `reason` | Khi nào |
|---|---|
| `ALREADY_IN_TARGET` | Target đã có nguyên văn (sau đổi tên) |
| `TARGET_EQUIVALENT` | Target đã có logic tương đương nhưng viết khác. `detail` ghi vị trí |
| `QUESTION` | Không xác định được vị trí để tạo chunk; câu hỏi nằm ở `detail` |

## 6. Kiểm tra bắt buộc (UI tự chạy khi mở trang)

1. Mọi `chunk.file` có trong `files`.
2. `1 <= start <= end <= số dòng của file`.
3. Các chunk cùng file không chồng range.
4. `target.text` khớp đúng các dòng `start..end` của Target.
5. Mọi `requires[].chunk`, `questions[].chunks`, `options[].apply` trỏ tới chunk có thật; `options[].apply` là tập con của `chunks` của câu hỏi.
6. Một chunk không thuộc hai câu hỏi.
7. `rt` chỉ có khi khác `apply`.

Lỗi bất kỳ → banner đỏ, khóa nút xuất.
