# port-changelog — Tổng quan dự án & cách xử lý (chế độ KHÔNG có snapshot)

> Trạng thái: **thiết kế** (chưa triển khai). Tài liệu này là nguồn tham chiếu để viết `SKILL.md` và các script.
> Phạm vi tài liệu: chỉ chế độ **không có snapshot trung gian**. Chế độ có snapshot sẽ viết ở tài liệu riêng.
>
> **Ghi chú cho v2:** quy trình chạy thực tế là 3 Phase trong `SKILL.md` (dùng tool `get-diff` có sẵn,
> không tạo script; mỗi Phase đều báo cáo cho người dùng). Khi tài liệu này khác `SKILL.md`, làm theo `SKILL.md`.
> Ánh xạ: Bước 0 + lấy diff → Phase 1; Bước 1 → Phase 2; Bước 2 + Bước 3 → Phase 3.

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
| `Before/`, `After/` | Hai source tree TELINDY; mỗi bên có thể chứa nhiều file và thư mục con |
| `feature-diffs/` | Tập diff riêng cho từng file thay đổi giữa Before và After, kèm manifest theo dõi toàn bộ danh sách |
| `latest/` | Source TELINDY mới nhất (đã chứa RT + mọi RT sau đó) |
| `target/` | Source FOMULAR mới nhất (nơi cần merge vào) |
| `RT` | Mã request cần port, ví dụ `RT2486` |

Tool so sánh Before và After đệ quy theo đường dẫn tương đối, bỏ qua file giống hệt và tạo một diff
riêng cho mỗi file được thêm, xóa hoặc sửa. Nếu khách đưa một patch nhiều file, tool tách thành cùng
dạng tập diff để có thể liệt kê và xử lý từng file. Không được chỉ lấy file có changelog RT: **mọi
file diff đầu vào đều thuộc danh sách cần xử lý**. File nhị phân/không giải mã được vẫn phải có trong
manifest với trạng thái rõ ràng, không được âm thầm bỏ qua.

---

## 2. Vấn đề cốt lõi

```
Before ──(RT2486)──> After ──(V8.07 … V8.14: RT2343, RT2611, RT2707, …)──> Latest
                              ↑ KHÔNG có code trung gian
```

- **Latest đã chứa sẵn chức năng**, nhưng ở dạng đã bị các RT về sau sửa tiếp.
- Phạm vi được xác định từ toàn bộ code diff Before→After: các hàm/symbol thay đổi trong diff là các
  đơn vị cần port. Với mỗi hàm thuộc phạm vi, lấy toàn bộ phiên bản Latest; các lần sửa về sau trong
  cùng hàm được mang theo theo chủ đích. Thay đổi ở hàm ngoài phạm vi chỉ được lấy nếu cần cho closure.
- Không có snapshot ⇒ không thể "rebase từng bước" A→B→C→D. Phải **nhảy một bước After → Latest**.
  Changelog giúp giải thích lịch sử, nhưng không dùng để lọc bỏ thay đổi trong hàm đã chọn.

Hai cách đã cân nhắc và **loại bỏ**:

| Cách | Lý do loại |
|---|---|
| 3-way merge thẳng (base=Before, ours=After, theirs=Latest) | Kết quả ≈ toàn bộ file Latest, kéo theo mọi feature không liên quan; chỉ dùng được để *phát hiện* chỗ thay đổi. Không dùng macOS `diff3 -m`. |
| Rebase từng bước theo changelog | Cần code của từng version trung gian — không có. |

---

## 3. Nguyên tắc thiết kế

1. **Quản lý một tập diff theo file.** Giữ bản gốc từng diff trong `WORK/feature-diffs.orig/`;
   cập nhật từng file diff lên trạng thái Latest ở Bước 1, rồi dùng toàn bộ tập đó ở Bước 2.
   Manifest trong `.port_changelog/` ghi danh sách file, trạng thái và tiến độ; không cần tạo report
   diễn giải riêng.
2. **Không bỏ sót file.** Hiển thị cho người dùng danh sách đầy đủ các diff với đường dẫn mở được.
   Có thể xem/xử lý lần lượt từng file, nhưng chỉ hoàn tất khi mọi file trong manifest đã có kết quả.
3. **Quyết định gắn với từng file và symbol** — lưu trong diff tương ứng hoặc manifest.
4. **Làm việc theo hàm và symbol**, không bắt người dùng xử lý từng hunk. Một file diff có thể chứa
   nhiều hàm, nhiều hunk và thay đổi ngoài thân hàm.
5. **Chỉ hỏi người dùng khi thật sự cần** (xem §6). Thay đổi bên trong hàm đã thuộc phạm vi sẽ lấy
   phiên bản Latest; dependency trong source được xử lý qua closure.
6. **Rẻ & chắc trước, đắt & mờ sau** khi tìm code (xem §5). LLM chỉ dùng ở vùng xám.
7. **Diff xác định phạm vi, changelog đối chiếu.** Code diff là sự thật về thay đổi; `Modification:`
   cung cấp RT/Add/Mod để giải thích và cảnh báo thiếu/thừa, không thay thế diff.

---

## 4. Pipeline

```
Before/ + After/ + latest/ + target/ + RT
  │
  ├─ Bước 0  Tạo toàn bộ per-file diff, manifest, liệt kê link và đọc changelog
  ├─ Bước 1  Cập nhật từng diff theo các hàm/symbol trong phạm vi lên Latest
  ├─ Bước 2  Merge toàn bộ diff đã cập nhật sang FOMULAR ── [HỎI] conflict/không xác định được
  └─ Bước 3  Kiểm tra cuối
```

Xử lý lần lượt từng file diff và duy trì trạng thái trong manifest. Gom các câu hỏi chưa giải quyết
theo từng bước; không báo hoàn tất khi còn file diff hoặc symbol ở trạng thái pending.

### Bước 0 — Chuẩn hoá, khoanh vùng file & đọc changelog

1. Chuẩn hoá encoding và xuống dòng cho bản làm việc; khi ghi ra target thì **trả về đúng encoding/
   xuống dòng gốc của từng file Target**.
2. So sánh đệ quy hai cây Before/After theo đường dẫn tương đối. Tạo một diff cho từng file thêm,
   xóa hoặc sửa; ghi cả file status (added/deleted/modified) vào manifest. Bỏ qua file byte-identical.
3. **Báo người dùng danh sách đầy đủ**: số file diff, trạng thái và link tới từng diff. Người dùng có
   thể chọn xem lần lượt; hệ thống vẫn phải tiếp tục cho tới khi toàn bộ danh sách được xử lý.
   Mọi đường dẫn trong manifest phải kết thúc ở trạng thái done, skipped theo quyết định rõ ràng,
   hoặc blocked có lý do — không âm thầm bỏ qua.
4. **Lấy dấu vân tay RT từ tất cả file diff**, không chỉ một file. Đọc khối `Modification:` ở cả hai
   phía Before và After; entry của RT có thể nằm ở dòng `+` hoặc `-`:
   ```
   +/*#         2018/08/31  Y.Kaneko (TTS-X)     RT2486                         #*/
   +/*#                     Add. artLibSetVarDate()                             #*/
   +/*#                     ...                                                 #*/
   ```
   Từ đó rút ra mã RT, ngày, người làm và danh sách `Add./Mod.` cho từng file.
5. Với mỗi file diff, lấy các hàm/symbol có thay đổi code làm phạm vi xử lý. Dùng `Modification:`
   để đối chiếu:
   - Changelog nhắc symbol nhưng diff không có thay đổi tương ứng ⇒ cảnh báo; không tự mở rộng phạm vi.
   - Diff thay đổi symbol nhưng changelog không nhắc ⇒ cảnh báo `UNEXPLAINED`; vẫn xử lý diff.
   - File không có changelog (thường là `.h`) vẫn được giữ và xử lý nếu có trong diff.
6. Tìm các file tương ứng trong Latest bằng đường dẫn tương đối trước; xác nhận các hàm/symbol trong
   phạm vi có còn tồn tại hay không. Bản này chưa xử lý đổi tên hàm: nếu không tìm thấy hàm theo tên
   trong Latest, ghi nhận là đã bị xóa để tạo thao tác xóa tường minh ở Bước 2.
7. Đọc `Modification:` trong Latest cho mọi file liên quan, không chỉ file có entry RT:
   - `grep` mã RT (`RT2486`) **trong khối `Modification:`** của mọi file ở `latest/` (chỉ đọc phần header, rẻ).
   - Khớp cả các entry con cùng RT có hậu tố, ví dụ `RT2486:V806-0001` — đây là **bản sửa tiếp của chính
     chức năng**, mặc định coi là thuộc chức năng (ghi chú vào diff).
   - Xác nhận thêm bằng ngày + người làm để tránh trùng mã RT ngẫu nhiên.
8. Với từng hàm trong phạm vi, liệt kê các entry mới hơn có nhắc tới hàm đó. Bảng này giải thích
   lịch sử; không dùng để loại các thay đổi khỏi phiên bản Latest của hàm:
   - Entry đụng tới hàm của RT ⇒ ghi vào bảng lịch sử theo hàm.
   - Entry `Add.` symbol mới (ví dụ `WAVMACH_VER0800_0000`, `artLibLinkOnVarSet()`) ⇒ ghi lại làm
     **nguồn giải thích** cho closure.
   - Entry không nhắc tới hàm/symbol trong phạm vi ⇒ ghi nhận để tra cứu, không mở rộng phạm vi.
9. Bỏ khối `Modification:` khỏi phần so sánh code (tránh nhiễu), nhưng giữ lại để đọc. Đọc changelog
   thành dữ liệu có cấu trúc:
   ```json
   [{"version":"V8.14R000","date":"2021/08/02","rt":"RT2707",
     "add":["artLibLinkOnVarSet"],"mod":["ArtLibCopyRecipeName"]}, ...]
   ```
10. Lập bảng theo file và symbol: trạng thái diff, hàm/symbol thay đổi, `Add./Mod.` trong changelog,
    entry mới hơn có nhắc tới, và trạng thái hiện diện trong Latest (present/deleted).

   Ví dụ RT2486 — trong Latest có các entry sau RT2486; phải đối chiếu trên tất cả file trong manifest:

   | Entry sau RT2486 | Đụng tới hàm của RT2486? | Ghi chú lịch sử |
   |---|---|---|
   | RT2586 (V8.06 ×2, V8.07) `artLibAdjustOsfData()` | Không | không liên quan |
   | RT2343 (2019/11/01) `WAVMACH_VER0700_0000`, `ArtLibJudgeRecipeConvV700()` | Không trực tiếp | nguồn giải thích symbol |
   | RT2343 (2019/11/07) `ArtLibGetRecipeData()` | **Có** | lịch sử sửa hàm |
   | RT2611 `ArtLibEntryRecipeName()` + 5 macro `WAVMACH_*` + 3 hàm Conv | **Có** | lịch sử sửa hàm + nguồn giải thích symbol |
   | RT2707 `ArtLibCopyRecipeName()` + `artLibLinkOnVarSet()` | **Có** | lịch sử sửa hàm + nguồn giải thích symbol |

   > Lưu ý thứ tự: RT2283 (V8.03) nằm **dưới** RT2486 nên là **cũ hơn**, không thuộc danh sách "về sau".

11. Đối chiếu danh sách `Add./Mod.` với các hàm/symbol thực sự thay đổi trong **toàn bộ** diff set.
    Thiếu/thừa ⇒ cảnh báo trong manifest và diff tương ứng; diff xác định phạm vi, changelog là
    thông tin đối chiếu.

### Bước 1 — Cập nhật toàn bộ diff set theo trạng thái Latest

Lặp qua **mọi file trong manifest**; trong mỗi file xử lý mọi hàm, khai báo và thay đổi file-scope
được xác định từ diff. Một file có thể có nhiều hàm và mỗi hàm có thể có nhiều hunk. Không lấy tên
hàm từ header `@@` làm điều kiện duy nhất; phải ánh xạ các dòng thay đổi vào định nghĩa hàm/symbol.

**1.1 Lập danh sách đơn vị thay đổi**

- Dùng nội dung code của diff để xác định hàm `Add`/`Mod`, hàm bị xóa, prototype và symbol ngoài hàm.
- Dùng `Modification:` để đối chiếu tên và trạng thái `Add./Mod.`; ghi cảnh báo khi changelog và code
  không khớp, nhưng không bỏ qua thay đổi code chỉ vì changelog thiếu.
- Giữ trạng thái theo từng file và từng đơn vị trong manifest để bảo đảm xử lý hết diff set.

**1.2 Lấy trạng thái mới nhất của từng đơn vị**

- Hàm trong phạm vi còn tồn tại trong Latest ⇒ lấy **toàn bộ thân hàm Latest**. Mọi lần sửa, bổ sung
  chức năng hoặc sửa lỗi về sau trong chính hàm đó đều được giữ; changelog RT sau chỉ dùng để giải
  thích lịch sử, không dùng để lọc bỏ code trong hàm.
- Hàm trong phạm vi không còn trong Latest ⇒ với phạm vi hiện tại (chưa xử lý đổi tên), ghi nhận
  thao tác `DELETE` tường minh để Bước 2 có thể xóa hàm tương ứng khỏi Target. Không chỉ bỏ hàm
  khỏi diff vì như vậy có thể làm mất chỉ thị xóa.
- Với macro, global, type, field và khai báo ngoài hàm thuộc diff: lấy định nghĩa hiện có trong
  Latest; nếu không còn được định nghĩa/dùng thì loại khỏi trạng thái mong muốn. Nếu code Latest
  vẫn tham chiếu symbol nhưng chưa tìm được định nghĩa, đánh dấu unresolved thay vì âm thầm bỏ.

**1.3 Closure (đủ phụ thuộc)**

Quét toàn bộ thân các hàm Latest đã chọn cùng các khai báo/file-scope cần thiết. Symbol được định
nghĩa trong Latest mà Target chưa có (hàm, macro, global, type, prototype, v.v.) ⇒ tự động thêm vào
closure, rồi tiếp tục kiểm tra phụ thuộc của symbol đó. Không hỏi chỉ vì một dependency mới được
thêm vào trong một hàm thuộc phạm vi. Dependency bên ngoài source hoặc không tìm được định nghĩa
phải được xác minh; nếu không thể xác minh an toàn thì hỏi người dùng.

**1.4 Đối chiếu changelog và ghi kết quả**

- Gắn RT/date/entry mới hơn vào các đơn vị tương ứng nếu có; thay đổi không được changelog giải thích
  ghi `UNEXPLAINED`. Đây là thông tin kiểm tra, không phải tiêu chí loại thay đổi trong hàm.
- Cập nhật diff tương ứng ở stage `latest`; lưu thao tác xóa, closure và trạng thái theo file trong
  manifest. Giữ nguyên bộ diff gốc để có thể chạy lại.

### Bước 2 — Map & merge sang FOMULAR

Lặp qua **toàn bộ file diff stage=latest** trong manifest; không dừng sau khi chọn/xử lý một file.
Map theo file và symbol, sau đó áp dụng lên **bản copy** của Target; không sửa trực tiếp `target/`.

- Hàm/symbol Latest còn tồn tại: hòa trộn các thay đổi từ Latest nhưng giữ code riêng của FOMULAR
  nếu không xung đột. Nếu không thể phân biệt hoặc hòa trộn an toàn, hỏi người dùng.
- Hàm bị xóa khỏi Latest: nếu hàm tương ứng còn trong Target và không có khác biệt/caller riêng cần
  giữ, áp dụng thao tác `DELETE`; nếu Target đã xóa rồi thì ghi `SKIP`. Nếu Target có code riêng hoặc
  việc xóa có thể ảnh hưởng caller ngoài phạm vi, hỏi người dùng.
- Symbol closure: thêm định nghĩa còn thiếu vào file tương ứng. Nếu symbol đã có nhưng chữ ký/type
  không tương thích, không coi đó là “đã có”; xử lý như conflict và hỏi khi không thể hòa trộn chắc chắn.
- File mới/xóa: áp dụng theo trạng thái trong manifest và kiểm tra các tham chiếu/cấu hình liên quan.

Ghi kết quả `AUTO` / `SKIP` / `DELETE` / quyết định của người dùng vào diff tương ứng và manifest.
Chỉ thêm entry changelog vào các file Target theo đúng quy ước của chúng.

### Bước 3 — Kiểm tra cuối

- Mọi file diff đầu vào đã được xử lý; không còn file/symbol pending trong manifest.
- Mọi hàm/symbol thuộc phạm vi đều có trạng thái rõ: cập nhật, đã có, xóa, hoặc quyết định của người dùng.
- Mọi symbol được dùng trong code đã merge đều có định nghĩa/nhà cung cấp tương thích trong Target.
- Kiểm tra không còn caller trong phạm vi tham chiếu đến hàm đã xóa; kiểm tra prototype và định nghĩa khớp nhau.
- Compile nếu có môi trường build.
- Encoding / xuống dòng của file target không bị đổi.

---

## 5. Bậc thang tìm code

Ở Bước 1, dùng tên hàm/symbol chính xác để tìm trạng thái Latest; nếu hàm không còn thì ghi `DELETE`
(đổi tên chưa được hỗ trợ). Bậc thang dưới đây chủ yếu dùng ở Bước 2 để map phần thay đổi vào Target,
giữ code riêng của FOMULAR và nhận diện conflict.

| Bậc | Cách | Thành công khi |
|---|---|---|
| **1. Tên hàm/symbol** | Lấy tên từ code diff và changelog đối chiếu; tìm định nghĩa trong file tương ứng | Tìm được đúng hàm/symbol; một file có thể chứa nhiều hàm và nhiều hunk |
| **2. Khớp sau chuẩn hoá** | Bỏ khoảng trắng, comment rồi so dòng | Code chỉ bị format lại |
| **3. Grep mỏ neo hiếm** | Lấy token đặc trưng của dòng chức năng (tên hàm được gọi, macro, chuỗi, field), grep trong phạm vi | Logic xung quanh đổi nhưng mỏ neo còn |
| **4. Điểm giống nhau** | So đoạn chức năng với từng cửa sổ trong phạm vi (difflib / token), ra % | Code bị sửa một phần |
| **5. LLM đánh giá** | Đưa đoạn gốc + 2–3 ứng viên tốt nhất từ bậc 3–4; hỏi "có phải cùng logic đã sửa không, vì sao" | Logic viết lại, chỉ còn giống về ý nghĩa |

Không dựa vào việc header `@@` luôn có tên hàm: một số công cụ diff chỉ ghi số dòng. Ánh xạ hunk vào
hàm bằng cách đọc source/manifest. Bản này **chưa xử lý đổi tên hàm**; nếu hàm trong phạm vi không còn
trong Latest thì ghi nhận `DELETE`, không chạy tìm kiếm rename trên toàn source. Khi map sang Target,
dùng các bậc trên để giữ code riêng và phát hiện xung đột.

### Ngưỡng quyết định

| Điểm giống khi map vào Target (bậc 4, do code tính) | Xử lý |
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

## 6. Khi nào hỏi người dùng

Không hỏi chỉ vì Latest thêm lời gọi hàm, macro, global hoặc field mới bên trong một hàm thuộc phạm vi.
Lấy bản Latest của hàm đó và tự động đưa các dependency được định nghĩa trong source vào closure.

| Tình huống | Xử lý |
|---|---|
| Thay đổi logic hoặc thêm dependency trong hàm thuộc phạm vi | Tự lấy phiên bản Latest; closure dependency trong source |
| Hàm không còn trong Latest | Ghi `DELETE`; khi merge hỏi nếu Target có code/caller riêng hoặc thao tác xóa không an toàn |
| Dependency được gọi nhưng không tìm thấy định nghĩa/nhà cung cấp trong source hay Target | Đánh dấu unresolved; hỏi, không âm thầm bỏ |
| Hunk/symbol không ánh xạ chắc chắn vào file/hàm | Hỏi người dùng với các ứng viên và diff liên quan |
| Target có thay đổi riêng không thể hòa trộn an toàn | Hỏi; không ghi đè nguyên hàm Target |
| Symbol đã có trong Target nhưng khác chữ ký/type | Xử lý như conflict, không coi là đã có |
| Changelog không khớp code diff | Ghi cảnh báo; code diff vẫn xác định phạm vi |

Mỗi câu hỏi cần nêu file, hàm/symbol, nội dung Before/After/Latest/Target liên quan và RT gợi ý nếu có.
Gom các câu hỏi theo file/bước, nhưng không dùng việc hỏi một file làm lý do bỏ qua các file còn lại.

---

## 7. Định dạng diff set sau khi cập nhật

Mỗi đường dẫn source có một diff riêng, giữ cấu trúc đường dẫn tương đối để người dùng mở đúng file.
Ví dụ:

```text
feature-diffs/
  ec/source/artlib/artrcp.c.diff
  ec/source/mmi/rcpbk/filer/mrcplib.c.diff
  ec/source/rcp/mach2/rifback2.c.diff
.port_changelog/
  manifest.json
```

Manifest ghi tối thiểu: đường dẫn source, trạng thái Before→After, các hàm/symbol thay đổi, trạng thái
Latest, trạng thái Target và tiến độ xử lý. Mỗi diff mang metadata về RT/stage tương ứng
(`original` → `latest` → `merged`) và các ghi chú `UNEXPLAINED`, `DELETE`, `AUTO`, `SKIP` hoặc quyết
định của người dùng. Bước 1 cập nhật từng diff; Bước 2 chỉ hoàn tất khi mọi entry trong manifest đã
có kết quả cuối.

---

## 8. Giới hạn (cần nói rõ với khách)

- Phạm vi là các hàm/symbol thực sự thay đổi trong toàn bộ diff Before→After; changelog chỉ đối chiếu.
- Với hàm thuộc phạm vi, lấy trạng thái Latest đầy đủ theo chủ đích. Vì vậy thay đổi RT sau trong cùng
  hàm cũng được mang theo; đây là lựa chọn phạm vi, không phải kết luận rằng mọi thay đổi đó thuộc RT gốc.
- Bản hiện tại chưa xử lý đổi tên hàm. Không tìm thấy hàm trong Latest thì ghi `DELETE`; trước khi xóa
  trên Target vẫn kiểm tra khác biệt/caller riêng và hỏi nếu không an toàn.
- Không có snapshot ⇒ chỉ biết "RT nào *có thể* liên quan" ở mức hàm, không biết chắc ở mức dòng.
- Changelog viết tay có thể thiếu ⇒ thay đổi `UNEXPLAINED` luôn được nêu ra.
- Dependency ngoài hàm (header, macro, global, type, bảng đăng ký, v.v.) được kéo theo khi Latest cần;
  dependency ngoài source hoặc không tìm được định nghĩa cần được xác minh.
- Mọi file diff đầu vào phải được xử lý; file không đọc/giải mã được phải báo trạng thái rõ ràng, không bỏ qua.

---

## 9. Công cụ trong runtime

- Không tạo sẵn bộ script/tool trước khi chạy trên dữ liệu thật.
- Khi một bước runtime cần công cụ, tạo tối thiểu công cụ phục vụ bước đó dựa trên input và quy tắc
  trong tài liệu; chạy/kiểm chứng trên dữ liệu thật rồi lưu source công cụ vào `scripts/` để dùng lại.
- Không tạo tool thay thế workflow hoặc bỏ qua việc liệt kê/xử lý toàn bộ file diff.

## 10. Việc tiếp theo

1. Dùng dữ liệu thật để chạy Bước 0: tạo và hiển thị toàn bộ per-file diff cùng manifest.
2. Xử lý từng diff theo thứ tự, cập nhật Latest, closure và Target; bảo đảm manifest không còn pending.
3. Chỉ tạo/lưu công cụ runtime khi quy trình thực tế cần đến; không scaffold trước.
4. Tài liệu riêng cho chế độ **có snapshot** sẽ viết sau.
