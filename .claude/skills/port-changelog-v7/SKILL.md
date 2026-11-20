---
name: port-changelog-v7
description: Quy trình chuyển một chức năng (mã RT) từ máy TELINDY sang máy FOMULAR (v7: merge theo đồ thị phụ thuộc, UI duyệt conflict)
---

# Port RT từ TELINDY sang FOMULAR

## Bài toán

- **RT** là mã yêu cầu thay đổi của khách, ví dụ `RT1234`. Khách không dùng git. Mỗi RT ghi một **entry** vào khối `Modification:` ở đầu file C (entry mới nhất nằm trên cùng):

```text
/*#         2018/08/31  Y.Kaneko (TTS-X)     RT1200                         #*/
/*#                     Add. libSetVarData()                             #*/
/*#                     Mod. LibGetItemData()                          #*/
```

- **Port một RT**: lấy code của RT **ở trạng thái mới nhất (Latest)** rồi merge vào FOMULAR. Không có snapshot trung gian giữa After và Latest.

## Đầu vào

| Thư mục | Là gì |
|---|---|
| `request/Before/` | TELINDY ngay trước RT |
| `request/After/` | TELINDY ngay sau RT |
| `source/` | TELINDY mới nhất (Latest) |
| `target/` | FOMULAR mới nhất (Target). Không bao giờ sửa |
| `WORK/` | Thư mục cha chứa kết quả |

## Thư mục theo lần chạy

- Nhận `run-id` từ người dùng trước Phase 1. Chỉ gồm chữ ASCII, số, `_`, `-`; bắt đầu bằng chữ hoặc số; không dùng `CON`, `PRN`, `AUX`, `NUL`, `COM1`–`COM9`, `LPT1`–`LPT9`.
- `WORK/<run-id>/` đã tồn tại khi bắt đầu Phase 1: không ghi đè, không tự resume. Chỉ resume khi người dùng yêu cầu và fingerprint (SHA-256 ghi ở Phase 1) khớp.
- Mọi phase dùng cùng `run-id`. Mỗi phase chỉ ghi vào thư mục của mình.

```text
WORK/<run-id>/
  phase1/  diff/<file>.diff  units.md  REPORT.md
  phase2/  fn/<file>/<X>.{before,after,latest,feature,p1}.c  <X>.rt.diff  <X>.ctx.diff
           diff/<file>.diff  paused.md  ledger.md  REPORT.md
  phase3/  fn/<file>/<X>.target.c  <X>.ctx.diff  merge-plan.json  review.html
           decisions.empty.json  decisions.all_target.json  check_all_target/
           diff/<file>.diff  REPORT.md
  phase4/  decisions.json  diff/<file>.diff  REPORT.md
  target_out/                      # chỉ do render_review.py --apply tạo
  tool-gaps.md                     # chỉ khi tool lỗi
```

## Từ khóa

- **RT sau**: RT có entry nằm **phía trên** entry của RT đang port.
- **Đơn vị**: định nghĩa cấp file có tên: hàm, prototype, macro, biến global/static/extern, bảng dữ liệu, `struct`/`union`/`typedef`, `enum`. Field, hằng enum, phần tử bảng, câu lệnh trong hàm **không** là đơn vị riêng; thay đổi của chúng là hunk bên trong đơn vị chứa chúng. Biến cục bộ, tham số, comment, `#include`, khối `Modification:` không là đơn vị.
- **Phạm vi hàm**: từ **dòng đầu của comment đầu hàm** tới `}` đóng hàm. Comment đầu hàm = mọi dòng comment liền trên chữ ký (kể cả dòng kẻ `/*#----#*/`, cho phép 1 dòng trống xen giữa); dừng khi gặp dòng code, 2 dòng trống liên tiếp hoặc `}` của đơn vị trước.
- **`Add` / `Mod` / `Del`**: đơn vị RT thêm / sửa bên trong / xoá hẳn. Xác định bằng diff, không theo chữ `Add.`/`Mod.` trong changelog.
- **Bản cắt**: file chứa riêng một đơn vị, dòng 1 là dòng đầu đơn vị. Tên `<X>.<bản>.c`.
- **Diff, hunk, dòng `+`/`-`/context**: kết quả `get_diff(<mới>, <cũ>)`. Luôn nói rõ của diff nào.
- **Đoạn thay đổi**: các dòng `-`/`+` liền nhau trong một hunk, ngăn với đoạn khác bởi dòng context.
- **Diff (new)**: kết quả Phase 2, diff của Feature (code RT đã cập nhật theo Latest) so với Before. Đầu vào Phase 3.
- **Neo**: dòng có sẵn dùng để định vị chỗ chèn một đơn vị mới, ví dụ `trước "/** EOF **/"`.
- **Chunk, câu hỏi, `requires`, `skipped`, trạng thái**: định nghĩa trong `schema/README.md`. Đó là hợp đồng dữ liệu bắt buộc.

## Tool

- **`get_diff(<file mới>, <file cũ>)`**: tool có sẵn. Dòng `+` từ file mới, `-` từ file cũ. Được cắt đoạn code ra file riêng trong `WORK/<run-id>/` để diff riêng đoạn đó.
- **`tools/render_review.py`** (xem `tools/README.md`):
  - Tạo trang duyệt: `python3 tools/render_review.py --plan WORK/<run-id>/phase3/merge-plan.json --target-root <target> -o WORK/<run-id>/phase3/review.html`
  - Ghép output: `python3 tools/render_review.py --plan WORK/<run-id>/phase3/merge-plan.json --target-root <target> --decisions <decisions.json> --apply -o WORK/<run-id>/target_out`. Thêm `--allow-pending` khi còn câu hỏi chưa trả lời (giữ Target). Lệnh in dòng `Trạng thái:` và các chunk bị giữ: nguồn cho bảng trạng thái trong report.
  - Tool tự kiểm plan (`schema/README.md` §6); có lỗi thì không ghi output.
- Được đọc, grep, cắt dòng bằng lệnh có sẵn. **Không tạo tool mới. Không sửa tay `target_out/`.**
- **Tool lỗi** (crash, không phải lỗi dữ liệu): không sửa tool, không tự dựng output thay tool. Ghi `WORK/<run-id>/tool-gaps.md` (lệnh, lỗi, đầu vào), dừng phần đó, báo người dùng.
- **Lỗi dữ liệu** do tool/trang báo (lệch `target.text`, chồng range...): sửa `merge-plan.json` rồi chạy lại.

## Nhãn

| Nhãn | Phase | Nghĩa |
|---|---|---|
| `KEEP` / `UPDATED` / `DROPPED` | 2 | Vùng RT: không bị RT sau sửa / bị sửa, lấy bản Latest / không còn ở Latest |
| `NOT_PORTED` | 2 | Đơn vị RT thêm nhưng Latest không còn ai dùng |
| `DEP_NEW` / `DEP_CHANGED` / `DEP_PAUSED` | 2 | Phụ thuộc: Before chưa có / đã đổi và code RT dùng chỗ đổi / giống Before hoặc không có Before để so |
| `UNEXPLAINED` / `UNRESOLVED` | 1, 2 | Diff có mà changelog không nhắc / không tìm thấy định nghĩa |
| `NEED_CONFIRM` | 1–3 | Không tự quyết được, phải hỏi |
| `DROPPED_IN_LATEST`, `REPLACED_BY_LATEST`, `NOT_RT`, `CHANGELOG_ONLY`, `USER_DECISION` | 2 | Mã lý do trong `ledger.md` (Phase 2, Bước 8) |
| `CLEAN` / `ALREADY_IN_TARGET` / `CONFLICT` | 3 | Phân loại đoạn thay đổi so với Target (Phase 3, Bước 3) |
| `NOT_IN_TARGET` / `NO_FILE` | 3 | Target không có đơn vị `Mod` / không có file. Chỉ ghi ở report, mục "Bỏ qua" |
| `APPLIED` / `KEPT` / `NEED_CONFIRM` / `BLOCKED` / `FOLLOW` | 3, 4 | Trạng thái chunk, do tool **tính**, không ghi tay (`schema/README.md` §4) |

Lý do trong `skipped` của plan: `ALREADY_IN_TARGET`, `TARGET_EQUIVALENT`, `QUESTION` (`schema/README.md` §5).

## Luồng file

| File | Tạo ở | Đọc ở | Nguồn đúng cho |
|---|---|---|---|
| `phase1/diff/<file>.diff` | P1 B2 | P1 B4; P2 B8 (đơn vị `Add`); P3 B6 (tìm định nghĩa trong code RT) | Thay đổi gốc của RT |
| `phase1/units.md` | P1 B4 | P2 B1, B7 | Danh sách đơn vị, `Add`/`Mod`/`Del`, neo của đơn vị `Add` |
| `phase2/fn/<file>/<X>.*.c`, `.rt.diff`, `.ctx.diff` | P2 B1–B5 | P2; P3 B2, B4 (`before.c`) | Bản cắt và diff từng đơn vị |
| `phase2/diff/<file>.diff` | P2 B7 | P3 B1, B3, B5, B10 | Diff (new): code cần port + dòng tiêu đề (có `Anchor:`) |
| `phase2/paused.md` | P2 B6 | P3 B6 | Phụ thuộc cũ chưa kiểm với Target |
| `phase2/ledger.md` | P2 B8 | P3 B1 | Dòng RT cố ý không đưa vào Feature, kèm mã lý do |
| `phase2/REPORT.md` | P2 B9 | P3 B1 | Câu trả lời của người dùng ở Phase 2 |
| `phase3/fn/<file>/<X>.target.c`, `.ctx.diff` | P3 B2 | P3 B3–B5 | Bản cắt Target và chỗ Target lệch Before |
| `phase3/merge-plan.json` | P3 B8 | `render_review.py`; P4 | Chunk, `requires`, câu hỏi, `skipped`, `name_map` |
| `phase3/review.html` | P3 B9 | Người duyệt (P4) | Giao diện duyệt |
| `phase3/decisions.empty.json`, `decisions.all_target.json`, `check_all_target/` | P3 B9, B10 | P3 B9, B10 | Quyết định rỗng / giữ toàn Target để kiểm |
| `phase3/diff/`, `phase4/diff/` | P3 B10, P4 B4 | Người duyệt | `get_diff(target_out, target)` |
| `target_out/` | P3 B9, P4 B3 | P3 B10, P4 B4 | Output. Chỉ tool ghi |
| `phase4/decisions.json` | Người duyệt (xuất từ trang) | P4 B3 | Quyết định của người duyệt |

## Bốn Phase

| Phase | Hướng dẫn | Việc chính | Đầu ra | Cổng (cuối phase) |
|---|---|---|---|---|
| 1 | `phases/phase-1-diff.md` | Diff Before→After, lập danh sách đơn vị + neo | `diff/`, `units.md` | Mọi dòng thay đổi đã gán đơn vị; mọi đơn vị `Add` có neo |
| 2 | `phases/phase-2-latest.md` | Đưa code RT lên Latest, trace phụ thuộc, rà độ phủ | Diff (new), bản cắt, `paused.md`, `ledger.md` | `CHƯA XÉT = 0`; mọi đơn vị NEW có `Anchor:`; câu hỏi đã trả lời |
| 3 | `phases/phase-3-merge.md` | Chia chunk, `requires`, câu hỏi; ghép bằng tool | `merge-plan.json`, `review.html`, `target_out/` | Trang không báo lỗi; diff output ↔ chunk APPLIED khớp 1-1; mọi hunk diff (new) có nơi nhận |
| 4 | `phases/phase-4-review.md` | Người duyệt quyết định trên trang; ghép lại | `decisions.json`, `target_out/` cuối | Như Phase 3 với quyết định thật |

- Báo cáo mọi phase theo `templates/report.md`.
- **Cổng**: mỗi dòng checklist phải có con số (ví dụ `42/42`). Ghi "đã kiểm tra" không có số là không đạt. Không đạt thì sửa, không sang phase sau.
- Bắt đầu phase nào thì đọc file hướng dẫn của phase đó. Dừng sau mỗi phase, chờ người dùng xác nhận.

## Mô hình phụ thuộc (tóm tắt, chi tiết ở `schema/README.md` §2, §4)

- Chỉ chặn qua `requires`. `X requires Y` khi X dùng thứ Y tạo ra (biến, hàm, giá trị, cấp phát), hoặc cùng ý đồ với Y (`why` phải nói rõ). Chiều luôn là **chỗ dùng → chỗ định nghĩa**, xuyên hunk, xuyên file.
- Chunk phụ thuộc vào chunk bị giữ → `BLOCKED`. Chunk chỉ phục vụ các chunk bị giữ → `FOLLOW`. Chunk độc lập → áp.
- **Không bao giờ chặn vì nằm gần**, cùng hunk, cùng hàm hay nằm dưới chunk có câu hỏi.
- Hàm thiếu ở Target → câu hỏi đặt trên chunk **gọi** hàm đó; chunk khác chỉ bị ảnh hưởng qua `requires`.

## Quy tắc chung

- **Chỉ lấy code của RT.** Không lấy nguyên hàm Latest (có code của RT khác), không lấy nguyên hàm Target.
- **Tìm đơn vị theo tên định nghĩa.** Không tự đi tìm tên khác có code giống.
- **Không mất code âm thầm.** Mỗi dòng RT phải đi tới Feature, `ledger.md`, chunk, `skipped` hoặc câu hỏi.
- **Không xoá logic riêng của FOMULAR** khi chưa được xác nhận.
- **Không dừng giữa phase để hỏi.** Ghi vào "Cần xác nhận", làm tiếp phần còn lại, hỏi cuối phase.
- **Ghi rõ vị trí**: mỗi đơn vị/symbol trong report kèm file và khoảng dòng của bản code nào.
- Không sửa `request/`, `source/`, `target/` và các file của skill.

## Khi nào hỏi người dùng

- Tự quyết được theo hướng dẫn phase thì không hỏi. Không chắc thì không đoán: gắn `NEED_CONFIRM`.
- Mỗi câu hỏi nêu: file, đơn vị, code liên quan, bằng chứng, các phương án và hệ quả.
- Một quyết định hỏi một lần. Không hỏi lặp lại cho từng phần phụ thuộc.
- Chờ trả lời một mục không làm dừng các mục khác.
