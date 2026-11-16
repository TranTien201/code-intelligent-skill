# port-changelog — Tổng quan dự án & cách xử lý (chế độ KHÔNG có snapshot)

> Trạng thái: **thiết kế** (chưa triển khai). Tài liệu này là nguồn tham chiếu để viết `SKILL.md` và các script.
> Phạm vi tài liệu: chỉ chế độ **không có snapshot trung gian**. Chế độ có snapshot sẽ viết ở tài liệu riêng.

---

## 1. Bối cảnh

### 1.1 Khách hàng không dùng git
Khách hàng không quản lý source bằng git. Mỗi lần sửa lỗi / thêm chức năng, họ ghi lịch sử thay đổi
**bằng tay** vào khối comment `Modification:` ở đầu file, ví dụ:

```c
/*#     Modification:                                                       #*/
/*#         2021/08/02  S.Kinoshita V8.14R000 RT2707                        #*/
/*#                     Add. artLibLinkOnVarSet()                           #*/
/*#                     Mod. ArtLibCopyRecipeName()                         #*/
/*# ------------------------------------------ From here TELINDY V8.14R000  #*/
/*#         2020/04/01  K.Ohtake (TTS)       RT2611                         #*/
/*#                     Add. WAVMACH_VER0800_0000                           #*/
/*#                     Mod. ArtLibEntryRecipeName()                        #*/
/*# -------------------------------------------- From here TELINDY V8.10R0  #*/
/*#         2019/11/07  H.Nakazawa V8.08R000 RT2343                         #*/
/*#                     Mod. ArtLibGetRecipeData()                          #*/
/*# -------------------------------------------- From here TELINDY V8.08R0  #*/
/*#         ...                                                             #*/
/*#         2018/08/31  Y.Kaneko (TTS-X)     RT2486                         #*/
/*#                     Add. artLibSetVarDate()                             #*/
/*#                          artLibSetCsTempToVar()                         #*/
/*#                     Mod. ArtLibGetRecipeData()                          #*/
/*#                          ArtLibPutOsfData()                             #*/
/*#                          ArtLibRecoverOsfHistoryData()                  #*/
/*#                          artLibMakeArtInfo()                            #*/
/*#                          ArtLibEntryRecipeName()                        #*/
/*#                          ArtLibCopyRecipeName()                         #*/
/*# -------------------------------------------- From here TELINDY V8.03R1  #*/
```

Đặc điểm của changelog này:
- **Mới nhất ở trên**, cũ nhất ở dưới. Các dòng `From here TELINDY Vx.yy` chia mốc version.
- Mỗi entry: ngày, người làm, mã RT (request), danh sách `Add.` / `Mod.` ở **mức hàm / macro / biến**.
- **Không có code** — chỉ là metadata, và do người viết tay nên **có thể thiếu hoặc sai**.

### 1.2 Yêu cầu
Khách muốn **copy một chức năng (một RT)** của máy **TELINDY** sang máy **FOMULAR**.
Ví dụ: copy RT2486 (2018/08/31).

### 1.3 Dữ liệu đầu vào (chế độ không snapshot)

| Đầu vào | Mô tả |
|---|---|
| `feature.diff` | **Một file diff duy nhất** mô tả chức năng: Before (trước RT) → After (sau RT) của TELINDY |
| `latest/` | Source TELINDY mới nhất (đã chứa RT + mọi RT sau đó) |
| `target/` | Source FOMULAR mới nhất (nơi cần merge vào) |
| `RT` | Mã request cần port, ví dụ `RT2486` |

Nếu khách đưa 2 folder Before/After thay vì diff, tool tự sinh `feature.diff` bằng
`diff -u -p -r before/ after/` (`-p` để header `@@` có tên hàm C).

---

## 2. Vấn đề cốt lõi

```
Before ──(RT2486)──> After ──(V8.07 … V8.14: RT2343, RT2611, RT2707, …)──> Latest
                              ↑ KHÔNG có code trung gian
```

- **Latest đã chứa sẵn chức năng**, nhưng ở dạng đã bị các RT về sau sửa tiếp.
- Trong Latest, một hàm có thể là: *code của chức năng (đã tiến hoá)* **trộn lẫn** với *code của RT khác tình cờ cùng hàm*.
- Không có snapshot ⇒ không thể "rebase từng bước" A→B→C→D. Phải **nhảy một bước After → Latest**
  và dùng **vị trí trong code + changelog + con người** để phân định.

Hai cách đã cân nhắc và **loại bỏ**:

| Cách | Lý do loại |
|---|---|
| 3-way merge thẳng (base=Before, ours=After, theirs=Latest) | Kết quả ≈ toàn bộ file Latest, kéo theo mọi feature không liên quan; chỉ dùng được để *phát hiện* chỗ thay đổi. Không dùng macOS `diff3 -m`. |
| Rebase từng bước theo changelog | Cần code của từng version trung gian — không có. |

---

## 3. Nguyên tắc thiết kế

1. **Một file diff từ đầu đến cuối.** Không sinh file report riêng. `feature.diff` được **cập nhật tại chỗ**
   ở Bước 1 (thành diff của chức năng ở dạng Latest), rồi được dùng để merge ở Bước 2.
   Bản gốc tự lưu thành `feature.orig.diff` để có thể chạy lại.
2. **Quyết định ghi ngay trong diff** — bằng các dòng `#` ở phần đầu mỗi file (trước `---`),
   `patch` / `git apply` bỏ qua các dòng này.
3. **Làm việc theo hàm**, không bắt người dùng nhìn từng hunk. Hunk chỉ là cấu trúc nội bộ.
4. **Chỉ hỏi người dùng khi thật sự cần** (xem §6). Thay đổi logic đơn thuần thì tự xử lý.
5. **Rẻ & chắc trước, đắt & mờ sau** khi tìm code (xem §5). LLM chỉ dùng ở vùng xám.
6. **Changelog là giả thuyết, code là sự thật.** Changelog dùng để định hướng và giải thích, không dùng để quyết định thay code.

---

## 4. Pipeline

```
feature.diff + latest/ + target/ + RT
  │
  ├─ Bước 0  Chuẩn hoá & đọc changelog
  ├─ Bước 1  Cập nhật feature.diff lên Latest           ── [HỎI #1] symbol mới / không tìm thấy
  ├─ Bước 2  Map & merge sang FOMULAR                    ── [HỎI #2] không khớp / khớp nhiều chỗ
  └─ Bước 3  Kiểm tra cuối
```

Chỉ có **2 điểm dừng chờ người dùng**, mỗi điểm gom tất cả câu hỏi lại hỏi một lần.

### Bước 0 — Chuẩn hoá, khoanh vùng file & đọc changelog

1. Chuẩn hoá encoding (Shift-JIS → UTF-8) và xuống dòng (CRLF → LF) cho bản làm việc;
   khi ghi ra target thì **trả về đúng encoding/xuống dòng gốc của target**.
2. **Lấy "dấu vân tay" của RT từ chính `feature.diff`.** Khi làm RT, người viết đã thêm entry changelog
   vào khối `Modification:` — nên các dòng `+` trong khối đó của diff chính là entry của RT:
   ```
   +/*#         2018/08/31  Y.Kaneko (TTS-X)     RT2486                         #*/
   +/*#                     Add. artLibSetVarDate()                             #*/
   +/*#                     ...                                                 #*/
   ```
   Từ đó rút ra: mã RT (`RT2486`), ngày, người làm, danh sách `Add./Mod.`.
3. **Khoanh vùng file trong Latest bằng dấu vân tay** — chỉ đọc các file có chứa entry này,
   **không đọc các file không liên quan**:
   - `grep` mã RT (`RT2486`) **trong khối `Modification:`** của mọi file ở `latest/` (chỉ đọc phần header, rẻ).
   - Khớp cả các entry con cùng RT có hậu tố, ví dụ `RT2486:V806-0001` — đây là **bản sửa tiếp của chính
     chức năng**, mặc định coi là thuộc chức năng (ghi chú vào diff).
   - Xác nhận thêm bằng ngày + người làm để tránh trùng mã RT ngẫu nhiên.
   - Tập file cần làm việc = **(file có entry RT trong Latest) ∪ (file xuất hiện trong `feature.diff`)**.
     File có trong diff nhưng **không** thấy entry trong Latest ⇒ cảnh báo (file `.h` thường không có
     khối `Modification:`, hoặc file đã đổi tên/gộp) — vẫn xử lý, tìm theo tên file rồi theo nội dung.
   - Mở rộng ra ngoài tập này **chỉ** khi closure (Bước 1.4) cần tìm định nghĩa symbol — lúc đó dùng
     grep tên symbol, không đọc toàn bộ source.
4. **Đếm & liệt kê các thay đổi về sau trong Latest.** Với mỗi file trong tập làm việc, đọc khối
   `Modification:` của **Latest**: mọi entry nằm **phía trên** entry của RT là thay đổi xảy ra **sau** RT.
   Đây là danh sách "đã có bao nhiêu thay đổi sau chức năng" và **tất cả đều phải được xét**:
   - Entry đụng tới hàm của RT ⇒ vào bảng nghi vấn (bước 6).
   - Entry `Add.` symbol mới (ví dụ `WAVMACH_VER0800_0000`, `artLibLinkOnVarSet()`) ⇒ ghi lại làm
     **nguồn giải thích** cho closure: khi Latest gọi symbol này trong code chức năng, biết ngay RT nào thêm nó.
   - Entry không đụng tới gì của RT ⇒ ghi nhận "không liên quan", không đọc thêm.
5. Bỏ khối `Modification:` khỏi phần so sánh code (tránh nhiễu), nhưng giữ lại để đọc.
6. Đọc changelog thành dữ liệu có cấu trúc:
   ```json
   [{"version":"V8.14R000","date":"2021/08/02","rt":"RT2707",
     "add":["artLibLinkOnVarSet"],"mod":["ArtLibCopyRecipeName"]}, ...]
   ```
7. Lập **bảng nghi vấn**: các hàm của RT cần port, và entry **mới hơn** nào có nhắc tới cùng hàm.

   Ví dụ RT2486 — trong Latest có **6 entry sau RT2486** (RT2586 ×3, RT2343 ×2, RT2611, RT2707):

   | Entry sau RT2486 | Đụng tới hàm của RT2486? | Vai trò |
   |---|---|---|
   | RT2586 (V8.06 ×2, V8.07) `artLibAdjustOsfData()` | Không | không liên quan |
   | RT2343 (2019/11/01) `WAVMACH_VER0700_0000`, `ArtLibJudgeRecipeConvV700()` | Không trực tiếp | nguồn giải thích symbol |
   | RT2343 (2019/11/07) `ArtLibGetRecipeData()` | **Có** | nghi vấn |
   | RT2611 `ArtLibEntryRecipeName()` + 5 macro `WAVMACH_*` + 3 hàm Conv | **Có** | nghi vấn + nguồn giải thích symbol |
   | RT2707 `ArtLibCopyRecipeName()` + `artLibLinkOnVarSet()` | **Có** | nghi vấn + nguồn giải thích symbol |

   Bảng theo hàm:

   | Hàm của RT2486 | Entry về sau đụng tới | Kỳ vọng trong Latest |
   |---|---|---|
   | `artLibSetVarDate()` (Add) | — | giữ nguyên |
   | `artLibSetCsTempToVar()` (Add) | — | giữ nguyên |
   | `ArtLibGetRecipeData()` | RT2343 (V8.08) | đã bị sửa |
   | `ArtLibPutOsfData()` | — | giữ nguyên |
   | `ArtLibRecoverOsfHistoryData()` | — | giữ nguyên |
   | `artLibMakeArtInfo()` | — | giữ nguyên |
   | `ArtLibEntryRecipeName()` | RT2611 (V8.10) | đã bị sửa |
   | `ArtLibCopyRecipeName()` | RT2707 (V8.14) | đã bị sửa |

   > Lưu ý thứ tự: RT2283 (V8.03) nằm **dưới** RT2486 nên là **cũ hơn**, không thuộc danh sách "về sau".

8. Đối chiếu danh sách `Add./Mod.` của RT với các hàm xuất hiện trong `feature.diff`
   (lấy từ header `@@ ... <tên hàm>`). Thiếu/thừa ⇒ cảnh báo (ghi vào diff).

### Bước 1 — Cập nhật `feature.diff` lên Latest

Với **từng hàm** (hoặc từng khai báo ngoài hàm: macro, mảng global, field struct) trong `feature.diff`:

**1.1 Tìm vị trí trong Latest** — dùng bậc thang §5.

**1.2 Phân loại thay đổi After → Latest**

Gọi:
- **D1** = các dòng chức năng thêm/sửa (phía `+` của `feature.diff`)
- **D2** = khác biệt giữa bản After của hàm và bản Latest của hàm

Mỗi thay đổi trong D2 được xếp loại theo **vị trí so với D1**:

| Loại | Điều kiện | Xử lý mặc định |
|---|---|---|
| **OVERLAP** | Sửa/xoá đúng dòng của D1 | Chức năng đã tiến hoá → **lấy bản Latest** |
| **ADJACENT** | Cách dòng D1 trong khoảng *k* dòng (mặc định *k* = 3) | Xét luật §6 |
| **DISJOINT** | Nằm xa D1 | Code của RT khác → **không port**, ghi chú RT có thể liên quan |

Trường hợp đặc biệt:
- **Hàm do chức năng `Add.`**: toàn bộ hàm là của chức năng ⇒ lấy nguyên bản Latest (không cần phân loại).
- **DISJOINT nhưng code chức năng phụ thuộc vào nó** (ví dụ khai báo biến mà dòng OVERLAP dùng) ⇒ nâng lên ADJACENT.
- **Dòng của D1 bị xoá trong Latest** ⇒ chức năng đã bị gỡ một phần; theo trạng thái Latest (không đưa dòng đó sang), ghi chú rõ.
- **Không tìm thấy hàm trong Latest** (kể cả sau bậc thang §5) ⇒ HỎI #1.

**1.3 Đối chiếu với changelog**

| Code thực tế | Changelog | Ghi chú vào diff |
|---|---|---|
| Không đổi | Không nhắc | khớp |
| Đổi | Nhắc 1 RT | gắn RT đó |
| Đổi | Nhắc nhiều RT | liệt kê các RT có thể liên quan |
| Đổi | **Không nhắc** | `UNEXPLAINED` — log thiếu, cần review |
| Không đổi | Có nhắc | RT sau có thể sửa file khác / đã revert |

**1.4 Closure (đủ phụ thuộc)**

Quét identifier trong code đã lấy (OVERLAP + các ADJACENT được chấp nhận). Symbol nào
**định nghĩa trong Latest** nhưng **chưa có trong target** (hàm, macro, global, field, typedef) ⇒
thêm thành hunk mới trong `feature.diff` (sau khi qua luật §6).

**1.5 Ghi lại `feature.diff`**

- Phía `-` và dòng ngữ cảnh lấy từ **Latest**; phía `+` là dạng mới nhất của chức năng.
- Hunk mới cho các symbol closure.
- Dòng `#` ghi quyết định ở đầu mỗi file (xem §7).

### Bước 2 — Map & merge sang FOMULAR

Với từng hunk của `feature.diff` (đã cập nhật), tìm vị trí trong target bằng bậc thang §5, rồi:

| Phía `-` có trong target | Phía `+` có trong target | Xử lý |
|---|---|---|
| Có, khớp duy nhất | Không | **AUTO** — áp dụng |
| Không | Có | **SKIP** — đã port rồi |
| Không | Không | **HỎI #2** — FOMULAR đã khác đi (không được tự bỏ qua) |
| Một phần / khớp nhiều chỗ | — | **HỎI #2** |

Hunk chỉ có `+` (thêm mới): không "merge thẳng" — phải tìm **vị trí chèn** dựa vào ngữ cảnh /
hàm-khai báo kề bên. Không xác định được vị trí ⇒ HỎI #2.

Áp dụng vào **bản copy** của target (không sửa trực tiếp `target/`), đồng thời thêm entry
changelog tương ứng vào khối `Modification:` của file FOMULAR.

### Bước 3 — Kiểm tra cuối

- Mọi hàm trong `Add./Mod.` của RT đều đã được xử lý (AUTO / SKIP / người dùng quyết định).
- Mọi symbol được dùng trong code đã merge đều có định nghĩa trong target.
- Compile nếu có môi trường build.
- Encoding / xuống dòng của file target không bị đổi.

---

## 5. Bậc thang tìm code (dùng cho cả Bước 1 và Bước 2)

Đi từ trên xuống, dừng ở bậc đầu tiên thành công.

| Bậc | Cách | Thành công khi |
|---|---|---|
| **1. Tên hàm** | Lấy tên hàm từ header `@@`, tìm định nghĩa hàm đó | Gần như luôn được với C; thu phạm vi từ cả file xuống 1 hàm |
| **2. Khớp sau chuẩn hoá** | Bỏ khoảng trắng, comment rồi so dòng | Code chỉ bị format lại |
| **3. Grep mỏ neo hiếm** | Lấy token đặc trưng của dòng chức năng (tên hàm được gọi, macro, chuỗi, field), grep trong phạm vi | Logic xung quanh đổi nhưng mỏ neo còn |
| **4. Điểm giống nhau** | So đoạn chức năng với từng cửa sổ trong phạm vi (difflib / token), ra % | Code bị sửa một phần |
| **5. LLM đánh giá** | Đưa đoạn gốc + 2–3 ứng viên tốt nhất từ bậc 3–4; hỏi "có phải cùng logic đã sửa không, vì sao" | Logic viết lại, chỉ còn giống về ý nghĩa |

Hàm không tìm thấy theo tên (đổi tên / chuyển file) ⇒ chạy bậc 3–5 trên **toàn bộ source**.

### Ngưỡng quyết định

| Điểm giống (bậc 4, do code tính) | Xử lý |
|---|---|
| ≥ 90% **và** 1 ứng viên | Tự lấy |
| 60–90%, hoặc nhiều ứng viên | LLM (bậc 5): "đúng" + lý do rõ ⇒ tự lấy, ghi chú; không chắc ⇒ **HỎI** |
| < 60% và không còn mỏ neo | **HỎI** (có thể chức năng đã bị gỡ / viết lại hoàn toàn) |

> **% dùng để đặt ngưỡng luôn do code tính**, không dùng % LLM tự báo (không ổn định giữa các lần chạy).
> LLM chỉ trả lời *có/không + lý do* ở vùng xám. Ngưỡng 60/90 và *k* = 3 cần hiệu chỉnh trên ca thật (RT2486).

Ví dụ: dòng chức năng `setVarDate(&rec);` trong Latest thành
`if (mode) { setVarDateEx(&rec, mode); }` — bậc 2 thất bại, bậc 3 bắt được nhờ `rec` / `setVarDate`,
bậc 4 ≈ 50%, bậc 5 xác nhận cùng logic đã mở rộng.

---

## 6. Khi nào hỏi người dùng (luật symbol mới)

Câu hỏi thực chất: **thay đổi có kéo theo phụ thuộc mới mà FOMULAR chưa có không?**

| Thay đổi trong Latest (OVERLAP / ADJACENT) | Ví dụ | Hỏi? |
|---|---|---|
| Đổi điều kiện / toán tử / hằng số | `if (a > 0)` → `if (a >= 0)` | Không — tự lấy |
| Đổi tham số, dùng biến sẵn có | `f(x)` → `f(x, y)` | Không — tự lấy (kiểm tra chữ ký `f` ở target) |
| **Gọi hàm mới** | thêm `artLibLinkOnVarSet()` | **Có** |
| **Dùng macro mới** | `if (ver >= WAVMACH_VER0800_0000)` | **Có** |
| **Dùng global / field mới** | `rec.csTemp` | **Có** |
| Symbol mới nhưng FOMULAR **đã có** | — | Không |
| DISJOINT (xa chức năng, không phụ thuộc) | — | Không — bỏ qua, ghi chú |

Mẫu câu hỏi (HỎI #1):

```
ArtLibCopyRecipeName()  — Latest gọi thêm artLibLinkOnVarSet()
  Changelog: artLibLinkOnVarSet được Add. ở RT2707 (V8.14)
  Đây là phần mở rộng của RT2486 hay chức năng riêng của RT2707? Có merge sang FOMULAR không? [Y/N]
  (Y ⇒ kéo theo định nghĩa artLibLinkOnVarSet() vào closure)
```

---

## 7. Định dạng `feature.diff` sau khi cập nhật

```diff
# port-changelog RT=RT2486 base=TELINDY-latest stage=latest
# ArtLibGetRecipeData   : OVERLAP@L120 tự lấy (đổi điều kiện if) ← RT2343
# ArtLibCopyRecipeName  : +artLibLinkOnVarSet() ← RT2707, user=Y
# ArtLibCopyRecipeName  : DISJOINT@L180 bỏ qua (log lỗi) ← RT2707?
# artLibMakeArtInfo     : UNEXPLAINED thay đổi không có trong changelog — đã review, user=Y
--- a/src/artlib.c
+++ b/src/artlib.c
@@ -110,7 +110,9 @@ ArtLibCopyRecipeName
 ...
```

- Dòng `#` nằm **trước** `---` của mỗi file ⇒ `patch` / `git apply` bỏ qua.
- Trường `stage=` cho biết diff đang ở giai đoạn nào (`original` → `latest` → `merged`).
- Sau Bước 2, ghi thêm kết quả map (`AUTO` / `SKIP` / quyết định của người dùng) theo cùng cách.

---

## 8. Giới hạn (cần nói rõ với khách)

- Nếu **một hunk vừa cải tiến chức năng vừa thêm logic RT khác trên cùng dòng** ⇒ không tách tự động, luôn hỏi.
- Không có snapshot ⇒ chỉ biết "RT nào *có thể* liên quan" ở mức hàm, không biết chắc ở mức dòng.
- Changelog viết tay có thể thiếu ⇒ thay đổi `UNEXPLAINED` luôn được nêu ra.
- Thay đổi ở file khác (header `.h`, bảng đăng ký) mà diff không chứa ⇒ chỉ bắt được qua closure symbol.
- Khoanh vùng file dựa vào entry changelog: file **không ghi** entry RT (thường là `.h`) sẽ không được
  grep tìm ra ⇒ luôn hợp thêm các file có trong `feature.diff`, và cảnh báo khi chỉ một phía có.
- Ngưỡng (60/90, *k*) là giả định ban đầu, cần đo trên dữ liệu thật.

---

## 9. Cấu trúc dự kiến của skill

```
port-changelog/
  OVERVIEW.md           # tài liệu này
  SKILL.md              # (sẽ viết) hướng dẫn chạy 4 bước + 2 điểm hỏi
  scripts/
    normalize.py        # Bước 0: encoding, CRLF, tách & parse changelog, bảng nghi vấn
    locate.py           # Bậc thang §5 (dùng chung Bước 1 & 2)
    carry.py            # Bước 1: phân loại OVERLAP/ADJACENT/DISJOINT, closure, ghi lại diff
    merge_target.py     # Bước 2: map 4 trạng thái, áp vào bản copy target
    verify.py           # Bước 3
```

## 10. Việc tiếp theo

1. Chạy thử Bước 0 + Bước 1 (bậc 1–4) trên dữ liệu thật của một RT để đo tỷ lệ OVERLAP / ADJACENT / DISJOINT và hiệu chỉnh ngưỡng.
2. Viết `SKILL.md` + scripts theo cấu trúc §9.
3. Tài liệu riêng cho chế độ **có snapshot** (dùng lại `carry.py`, lặp qua chuỗi version).
