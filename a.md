### 1. Bối cảnh:
- Khách hàng khônhg sử dụng github mà khi có update thay đổi hoặc là thêm feature mới họ sẽ update vào file code đó dạng như git log như sau. Họ không hề có snapshot qua từng commit.

- Bài toán là họ có một máy TELINDY có chức năng A (trong quá khứ/hiện tại) tuỳ vào thời gian commit ở log như bên dưới. Họ có một máy khác là FOMULAR. Khách hàng họ cung cấp một source code trong qúa khứ và giờ mình phải làm sao từ source code feature đó mình có thể lấy được source code của feature đó ở hiện tại (latest) vì sao làm vậy code khách hàng cung cấp là thời điểm đầu tiên xây dựng tính năng. Qua thời gian tính năng sẽ được update và tạo ra các commit khác và giờ latest nó đã có sự khác biệt. Ví dụ như 2018/08/31  Y.Kaneko (TTS-X)     RT2486 bạn có thể thấy hàm ArtLibGetRecipeData này được chỉnh sửa ở 2019/11/07 đó nghĩa là có chỉnh sửa. Vì thế mình phải lấy code mới nhất của function để merge qua mấy mới. Tuy nhiên cũng có trường hợp function của feature đó không modify



/*#*************************************************************************#*/
/*#     Modification:                                                       #*/
/*#         2021/08/02  S.Kinoshita V8.14R000 RT2707                        #*/
/*#                     Add. artLibLinkOnVarSet()                           #*/
/*#                     Mod. ArtLibCopyRecipeName()                         #*/
/*# ------------------------------------------ From here TELINDY V8.14R000  #*/
/*#         2020/04/01  K.Ohtake (TTS)       RT2611                         #*/
/*#                     Add. WAVMACH_VER0800_0000                           #*/
/*#                          WAVMACH_ONLY_VER                               #*/
/*#                          WAVMACH_ONLY_REV                               #*/
/*#                          WAVMACH_REV_0001                               #*/
/*#                          WAVMACH_DEF_REV0001                            #*/
/*#                          artLibConvVariApc()                            #*/
/*#                          ArtLibConvVariable()                           #*/
/*#                          ArtLibConvJudgeVariable()                      #*/
/*#                     Mod. ArtLibEntryRecipeName()                        #*/
/*# -------------------------------------------- From here TELINDY V8.10R0  #*/
/*#         2019/11/07  H.Nakazawa V8.08R000 RT2343                         #*/
/*#                     Mod. ArtLibGetRecipeData()                          #*/
/*#         2019/11/01  K.Ohtake (TTS)       RT2343                         #*/
/*#                     Add. WAVMACH_VER0700_0000                           #*/
/*#                     Mod. ArtLibJudgeRecipeConvV700()                    #*/
/*# -------------------------------------------- From here TELINDY V8.08R0  #*/
/*#         2019/07/12  Y.Kaneko (TTS-X)     RT2586                         #*/
/*#                     Mod. artLibAdjustOsfData()                          #*/
/*# -------------------------------------------- From here TELINDY V8.07R0  #*/
/*#         2019/06/11  Y.Kaneko (TTS-X)     RT2586                         #*/
/*#                     Mod. artLibAdjustOsfData()                          #*/
/*#         2019/05/22  Y.Kaneko (TTS-X)     RT2586                         #*/
/*#                     Mod. artLibAdjustOsfData()                          #*/
/*# -------------------------------------------- From here TELINDY V8.06R0  #*/
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
/*#         2018/04/19  Y.Kaneko (TTS-X)     RT2283:V803-0001               #*/
/*#                     Mod. ArtLibTempProcessGdId[][]                      #*/
/*#         2018/04/06  Y.Kaneko (TTS-X)     RT2283                         #*/
/*#                     Mod. ArtLibGetRecipeData()                          #*/
/*#                          ArtLibCopyOsfData()                            #*/
/*#                          ArtLibEntryRecipeName()                        #*/
/*# -------------------------------------------- From here TELINDY V8.03R0  #*/

- Đây là log quá trình xây dựng các feature/fix bug của một máy tên là TELINDY. Và yêu cầu của khách hàng khi họ muốn copy một tính năng tức là một log nằm trong cái git log file trên qua máy Fomula cho khách như trên ví dụ:
/*#         2018/08/31  Y.Kaneko (TTS-X)     RT2486                         #*/
/*#                     Add. artLibSetVarDate()                             #*/
/*#                          artLibSetCsTempToVar()                         #*/
/*#                     Mod. ArtLibGetRecipeData()                          #*/
/*#                          ArtLibPutOsfData()                             #*/
/*#                          ArtLibRecoverOsfHistoryData()                  #*/
/*#                          artLibMakeArtInfo()                            #*/
/*#                          ArtLibEntryRecipeName()                        #*/
/*#                          ArtLibCopyRecipeName()                         #*/ 

 ### 2. Dữ liệu được cung cấp:
- Source code (Source) mới nhất của TELINDY.
- Source code (Target) mới nhất của FOMULAR.
- Source code chức năng cần được thêm vòa FOMULAR gồm hai phần là Before (src trước khi có chức năng) và After (src sau khi có chức năng).

- `request/Before/...(nhiều file)`, `request/After/...(nhiều file)`: source TELINDY trước và sau khi làm RT.
- `source/`: source TELINDY mới nhất (đã chứa RT và mọi RT về sau).
- `target/`: source FOMULAR mới nhất (nơi cần merge RT vào).

 

### 3. Insight xây dựng
Mình sẽ chia ra 3 pharse để thực hiện việc xử lý vấn đề:

Pharse 1: Lấy diff và khoanh vùng các function và các biến của chức năng.
- Gọi tool `get_diff()` mình đã xây dựng trước đó để thực hiện lấy ra sự khác nhau trước và sau khi implement feature từ After so với Before. Ví dụ kết quả:

```diff
@@ -3812,16 +3793,16 @@
     /** Get All Variable Data **/
-    retCode = RcpIfGetAllVariForce(subSystemId,
-                                   className_org,
-                                   recipeName_org,
-                                   &varCount,
-                                   &variable);
-    if (retCode != NORMAL_END)
+    retCode = RcpIfGetAllVari(subSystemId,
+                              className_org,
+                              recipeName_org,
+                              &varCount,
+                              &variable);
+    if (retCode != NORMAL_END && retCode != RCP_NOTLINKEDERROR)
```

- Vì nó có nhiều file nên tương đương có nhiều file diff nhé.
- Từ file diff mình sẽ xác định được các hàm nào trong file được modify. Lưu ý cái đoạn function này bạn nhé. Ngoài function ra thì sẽ cần biết các biến cục bộ global được định nghĩa bên ngoài không trong hàm.
- Mục đích thay vì mình sẽ cần check từng dòng code thay đổi ở feature so với latest mình sẽ thực hiện check hàm thôi và lấy nguyên hàm ở latest và thực hiện khám phá thêm sâu bên trong.
- Trường hợp không tìm thấy được hàm thì có thể bị xoá hoặc đổi tên thì mới dùng các thành phần code diff bên trong nội hàm để tìm (phân này nói sâu hơn ở pharse sau).

- Ở port-changelog-v2 và port-changelog-v3 có sử dụng thêm phần check diff giữa phần After <-> Latest và để thực hiện các bước trace, so sánh cho pharse 2. Nhưng mình đang đánh giá là có thực sự cần thiết hay là không bởi vì từ hàm mình có thể search ra file đó và gần như copy nguyên function và các thông tin liên quan nhờ vào sự khám phá. Hoặc cũng có thể diff cũng được dùng để biết thông tin trong hàm A (feature) và hàm A (latest) đã có thêm gì rồi. 


Pharse 2: Lấy feature mới nhất.

- Đầu tiên, tôi thấy một trích có thể dùng được. Đầu tiên ở diff của A-B ngay đầu trang mình nhận được cái này.

```diff
@@ -8,11 +8,6 @@
/*#*************************************************************************#*/
/*#*************************************************************************#*/
/*#     Modification:                                                       #*/
+/*#         2018/08/31  Y.Kaneko (TTS-X)     RT2486                         #*/
+/*#                     Add. artLibSetVarDate()                             #*/
+/*#                          artLibSetCsTempToVar()                         #*/
+/*#                     Mod. ArtLibGetRecipeData()                          #*/
+/*#                          ArtLibPutOsfData()                             #*/
+/*#                          ArtLibRecoverOsfHistoryData()                  #*/
+/*#                          artLibMakeArtInfo()                            #*/
+/*#                          ArtLibEntryRecipeName()                        #*/
+/*#                          ArtLibCopyRecipeName()                         #*/ 
/*#         2020/04/01  K.Ohtake      V8.10R000 RT2611                      #*/
/*#                     Mod. mmiWavRestoreVarData()                         #*/
/*# -------------------------------------------- From here TELINDY V8.10R0  #*/
@@ -279,12 +274,7 @@
```

Đây chính là phần log khi thực hiện xong 1 feature. Nghĩa là so sánh A->B thì thấy có thấy diff liên quan đến thông tin này. Và thông tin này có thể có thể search vào được ngay trong phần file latest và từ đây mình có thể tận dụng như sau. Mình có thể biết được ở feature mình có hàm nào vừa được add và vừa được mod. Từ từ log của feature hiện tại lên đến latest mà các hàm của mình không có Mod thì nghĩa là không có chỉnh sửa nào cả thì mình sẽ không cần dùng đoạn diff của hàm đó so sánh hoặc tìm kiếm mà chủ động bỏ qua luôn. Còn nếu nó có thì mình sẽ thực hiện search vào và lấy code latest mà thôi. Ngoài ra ở trong thông tin Modification có thể giúp ta xác định được thực chất là có bao nhiêu function hoặc có nhiêu biến ví dụ như WAVMACH_ONLY_VER được có trong feature để làm cơ sở so sánh vào trong latest để lấy ra hàm đó trong latest.


Giờ cùng phân tích về lấy update mới nhé với nhưng hàm hay biến được modify:

TH1: Nếu trường hợp có 1 hàm hay 1 biến ví dụ: WAVMACH_ONLY_VER (không biét mô tả nó là loại dữ liệu gì trong C) thì mình sẽ search vào latest và thấy nó có mình sẽ lấy đoạn function đó update vào diff và ngoài ra thực hiện thêm. Khám phá trong hàm đó có thể dùng diff của A-L và A-B để thấy được có những hàm những biến nào mới được gọi được sử dụng bên trong function trên latest này và mình cần lấy được thông tin cái đó và cập nhập luôn cho phần feature cũ nhé. Ví dụ: Ở feature A-B diff ta có hàm login bên trong gọi 3 hàm nhưng giờ ở latest gọi 4 hàm trong đó 3 hàm trước đó giờ còn 2 hàm (2 hàm mới và 2 hàm cũ) ngoài ra có các biến sử dụng bên trong được định nghĩa ngoài block của function cũng nên được khám phá và cập nhập vào trong cái diff feature A-B đó.

TH2: Nếu tìm không ra thì sao, trường hợp có thể bị xoá hoặc đổi tên. Nhưng mình đang nghiên về hướng bị xoá.

- Thực hiện hai bước lấy cái diff logic bên trong function đó ở A-B Diff tìm kiếm vào trong file latest được check đó xem thử có nội dung đó hay không nếu có nội dung gần giống thì có thể lấy function chưa logic đó để tạo đề xuất/câu hỏi rằng có phải function này đã được chỉnh sửa tên hay không. Trường hợp không có cái nào oke hết thì mặt định xoá và xoá phần function đó ra khỏi diff A-B (feature) ra khỏi đó và sẽ không được dùng để merge vào máy FOMULAR.

Còn trường hợp nào về dữ liệu đề xuất nhé.


TH3: Merge vào máy FOMULAR

- Đây là bước mà mình thực sự chưa nghĩ ra cách xử lý như thế nào để ổn thoả và cũng chưa hình dung ra được rõ ràng như 2 Pharse đầu.
- Pharse này theo hướng thì sẽ check diff của code Before với Latest của máy FOMULAR. Mình sẽ dựa vào tên file ở Before để tìm vào trong source của phần latest FOMULAR để lấy diff. Sau đó sẽ lấy thông tin diff feature đã latest để update nhưng mình không biết nên xử lý chổ này như thế nào mình cần bạn phân tích và hỗ trợ thêm nhé.

Lưu ý thêm:

Ở tất cả các pharse sau khi xong lượnt phải cần có báo cáo:
- Pharse 1 báo cáo về đương dẫn thông tin về các file diff.
- Pharse 2 thì báo cáo về việc update thêm cho feature như thế nào. Cần các câu hỏi confirm hay xác nhận gì không
- Pharse 3 gần như pharse 2
- Khôgn có human in the loop. Mỗi pharse xong báo cáo và con người xác nhận mới thực hiện tiếp.