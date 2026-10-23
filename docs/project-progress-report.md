# Báo cáo tiến trình dự án CaroAI

**Ngày chốt số liệu:** 23/10/2026  
**Mục đích:** Báo cáo tiến độ với giảng viên; phân biệt rõ phần đã triển khai, phần đã kiểm thử và phần chưa được xác nhận ở môi trường production.

## 1. Tóm tắt điều hành

CaroAI là ứng dụng chơi Caro trên bàn cờ 15×15, gồm giao diện web, backend FastAPI, AI chơi cờ và lưu trữ dữ liệu. Qua các giai đoạn Sprint 1–3, nhóm đã xây dựng nền tảng luật chơi/API, tích hợp AI, triển khai lớp lưu trữ SQLAlchemy, bổ sung migration và kiểm thử PostgreSQL trong CI, đồng thời phát triển kiểm thử trình duyệt và giao diện lịch sử ván đấu.

**Kết luận tại thời điểm báo cáo:** phần nền tảng kỹ thuật và các job kiểm thử chính đã tiến bộ rõ rệt, nhưng chưa nên báo cáo dự án là đã hoàn thành phát hành. PR giao diện/E2E và PR chốt tài liệu QA vẫn đang mở; benchmark AI trên Linux/Docker còn chờ; các mục công bố image, triển khai production, kiểm tra HTTPS công khai và xác minh persistence sau deploy chưa có bằng chứng hoàn tất.

## 2. Mục tiêu và phạm vi sản phẩm

Mục tiêu là xây dựng ứng dụng Caro có hai chế độ:
- **PvP:** hai người chơi lần lượt đánh trên cùng bàn cờ.
- **PvAI:** người chơi đánh với AI ở các mức độ khó được backend hỗ trợ.

Backend là nguồn xác thực duy nhất cho trạng thái bàn cờ, lượt chơi, tính hợp lệ của nước đi và kết quả thắng/hòa. AI chỉ đề xuất tọa độ; backend kiểm tra và áp dụng nước đi. Các ván đấu và nước đi cần được lưu để có thể đọc lại sau khi tạo session mới hoặc khởi động lại dịch vụ.

Phạm vi kiểm thử/phát hành gồm kiểm thử luật chơi và API, lưu trữ PostgreSQL, migrations, Docker Compose, CI GitHub Actions, kiểm thử trình duyệt, build image và các bước phát hành có kiểm soát. Hint/Analysis/Replay nâng cao không được tính là hoàn thành nếu chưa có endpoint và kiểm thử thực tế tương ứng.

## 3. Kiến trúc hiện tại

Luồng chính của ứng dụng:

`Trình duyệt → Frontend tĩnh → FastAPI → GameService/GameRules → AI Engine (khi là lượt AI)`

`FastAPI/GameService → SQLAlchemy repository → PostgreSQL`

Các thành phần chính:
- **Frontend:** giao diện web tĩnh, hiển thị bàn cờ, chế độ chơi, trạng thái yêu cầu và lỗi từ API.
- **Backend:** FastAPI cung cấp API; GameService điều phối ca sử dụng; GameRules giữ quyền quyết định trạng thái game và tính hợp lệ của nước đi.
- **AI Engine:** nhận bản sao bàn cờ qua adapter, trả về nước đi dự kiến; backend xác thực kết quả trước khi áp dụng.
- **Persistence:** repository/unit-of-work dùng SQLAlchemy để lưu game và danh sách nước đi theo thứ tự. ID công khai dạng UUID được tách khỏi khóa nội bộ BIGINT.
- **Database/operations:** PostgreSQL, migrations có phiên bản, health/readiness endpoint, Docker Compose và GitHub Actions.

`/health` dùng để kiểm tra liveness của ứng dụng; `/ready` kiểm tra khả năng truy cập database. Hai endpoint có mục đích khác nhau và không nên dùng lẫn lộn.

## 4. Tiến độ theo hạng mục

| Hạng mục | Kết quả hiện có | Trạng thái tại ngày báo cáo |
|---|---|---|
| Nền tảng game/API | Domain game 15×15, validation nước đi, phát hiện kết thúc, endpoint tạo/đọc game và ghi nước đi | Đã triển khai trong các PR nền tảng đã merge |
| Tích hợp AI | Adapter chuyển đổi biểu diễn bàn cờ; backend xác thực nước đi AI; có xử lý mode, lượt, độ khó và đầu ra không hợp lệ | Đã tích hợp; tiếp tục củng cố regression/benchmark |
| Lưu trữ game | SQLAlchemy repository/unit-of-work; lưu game và ordered moves; dựng lại trạng thái từ lịch sử nước đi; transaction ghi nước đi và trạng thái kết thúc | PR #32 đã merge |
| Migrations và PostgreSQL CI | Migration có phiên bản, kiểm tra PostgreSQL trong CI, kiểm tra readiness; Compose smoke tạo game/nước đi, restart API rồi đọc lại dữ liệu | PR #37 đã merge; acceptance trong CI đã chạy thành công |
| AI regression/benchmark | PR #33 bổ sung benchmark harness và fixtures; có đo median/p95 và lưu dữ liệu thô theo SHA | Khung benchmark đã merge; benchmark Linux/Docker và xác nhận SLO vẫn chờ |
| Frontend browser E2E / History | Playwright test luồng PvP/PvAI, lỗi/retry/end-game; giao diện lịch sử sử dụng API | PR #34 đang mở; CI thông thường trên head mới nhất đã xanh, nhưng browser E2E còn đang chạy khi kiểm tra |
| Bổ sung/khôi phục history API | Có PR riêng liên quan tới contract `GET /api/history` | PR #35 đang mở và nhắm vào `main`, cần review/reconcile với nhánh tích hợp chuẩn trước khi coi là hoàn tất |
| Tài liệu QA và bàn giao | Ma trận test, test plan, persistence evidence và ranh giới release | PR #38 đang mở; CI trên head của PR xanh, nhưng tài liệu vẫn có một số tham chiếu SHA/run cũ cần đối chiếu và sửa trước khi chốt |
| Production release | Pipeline phát hành có điều kiện đã được thiết kế trong M4 | Chưa có bằng chứng hoàn tất publish/deploy production hoặc smoke test HTTPS công khai |

## 5. Pull request và bằng chứng kiểm thử

Các trạng thái dưới đây được đối chiếu từ repository và GitHub Actions vào ngày 23/10/2026.

- **PR #32 — Backend persistence:** đã merge. Bổ sung repository SQLAlchemy, transaction và kiểm thử persistence qua service/API. Thực hiện trên SQLite là bằng chứng regression hữu ích, nhưng tự nó không thay thế acceptance với PostgreSQL.
- **PR #33 — AI benchmark/regression:** đã merge. Bổ sung bộ fixtures, quy trình đo lặp lại, median/p95 và lưu raw CSV/JSON theo source SHA. Issue #28 vẫn mở vì benchmark/review còn các bước cần hoàn thiện.
- **PR #34 — Browser E2E và History UI:** đang mở. Head được kiểm tra là `4d540c65f4963d154229214dd34e6dec8f679534`. CI thông thường tương ứng đã thành công; workflow browser E2E được kiểm tra vẫn ở trạng thái `in_progress`. Do đó chưa thể kết luận browser E2E của head hiện tại đã pass.
- **PR #35 — History API:** đang mở, target branch là `main`. Cần xem xét đường tích hợp và bảo đảm history đọc dữ liệu persistence thật, không chỉ state trong bộ nhớ.
- **PR #36 — Sửa kiểm tra expected move và bổ sung kết quả benchmark:** đang mở. Nội dung PR ghi nhận một lần chạy benchmark Windows trên SHA `12b951cea3cdfe5bc6768a0197402bfdd28ba4d7`: 33 lượt warm-up, 165 lượt đo, 0 lượt đo thất bại. Đây là bằng chứng trên đúng snapshot đó, chưa phải benchmark Linux/Docker được nhóm chấp nhận cuối cùng.
- **PR #37 — PostgreSQL CI/migrations/readiness/release gate:** đã merge. CI có job PostgreSQL chặn trường hợp test bị skip, job Compose kiểm tra đọc lại dữ liệu sau khi restart API, và Docker build. PR này không có nghĩa là image đã được phát hành hay dịch vụ đã được deploy.
- **PR #38 — Persistence QA evidence và handover:** đang mở. Push run [#260](https://github.com/emt0147t/caroAI/actions/runs/39925356699) và pull-request run [#261](https://github.com/emt0147t/caroAI/actions/runs/39925364314) đều xanh trên head `b333273da91bc2e6bceb8be891ec91112681c9e2`, với năm job validation bắt buộc thành công. Tuy nhiên, một số file tài liệu trong PR vẫn gắn nhãn SHA `cc25a0f5eaf075ed1cee58944114b99e0d43971a` và run #250/#251 là bản “final”, không khớp head #38 mới nhất. Cần sửa tài liệu rồi review lại trước khi merge.

**Cách diễn giải test:** CI xanh chỉ chứng minh các job thuộc workflow đó thành công trên SHA tương ứng. Không được lấy số test của một SHA cũ và gán cho head mới. Test E2E chạy trên PR merge ref, test chạy trên branch, test trên Compose CI và test trên production là các loại bằng chứng khác nhau.

## 6. Những gì đã được kiểm chứng — và chưa được kiểm chứng

### Đã có bằng chứng
- CI cho head PR #38: lint/test, PostgreSQL service/API/migration acceptance, Compose persistence after API restart, frontend syntax/regression và Docker image build đều thành công trong push run #260 và pull-request run #261.
- M4 cung cấp đường kiểm thử PostgreSQL riêng, có guard để không tính test bị skip là pass.
- Compose smoke trong CI tạo game/nước đi, restart API rồi đọc lại trạng thái đã lưu.
- PR #37 đã merge phần migrations và readiness cần thiết để kiểm thử database có căn cứ hơn so với chỉ dùng SQLite.
- AI benchmark harness và các regression guard cơ bản đã được đưa vào repository qua PR #33.

### Chưa được tuyên bố hoàn tất
- **Production publish/deploy:** chưa có bằng chứng image đã được publish và release được triển khai thành công trên Render.
- **Public HTTPS/live smoke:** chưa có URL production cùng release SHA và kết quả kiểm thử công khai được xác nhận.
- **Persistence sau production redeploy:** Compose test kiểm tra restart API trong môi trường CI; điều này không tương đương với kiểm thử persistence sau deploy/redeploy production.
- **Browser E2E trên head mới nhất của PR #34:** lần kiểm tra gần nhất cho thấy workflow còn đang chạy. Kết quả 13/13 trên SHA cũ chỉ là bằng chứng lịch sử của SHA đó.
- **AI benchmark Linux/Docker và SLO:** còn chờ chạy cùng môi trường được thống nhất và xác nhận ngưỡng p95 với nhóm.
- **Hint/Analysis/Replay:** chưa có bằng chứng đủ để báo cáo là các chức năng đã hoàn chỉnh.
- **QA handover cuối:** PR #38 chưa merge và có tham chiếu bằng chứng cần làm mới.

## 7. Việc còn lại theo thứ tự ưu tiên

1. **Chốt tài liệu QA M5:** sửa các tham chiếu SHA/run cũ trong PR #38; chỉ giữ số liệu chi tiết gắn với đúng SHA đã chạy; sau đó review lại và mới xem xét merge.
2. **Chốt browser E2E/history:** chờ kết quả workflow E2E trên head PR #34; kiểm tra PR #35 để hợp nhất đúng contract history với backend persistence và xác nhận history lấy dữ liệu đã lưu.
3. **Chốt benchmark AI:** xử lý review/CI cho PR #36, chạy benchmark Linux/Docker với cấu hình được ghi lại, đối chiếu các kết quả và xác nhận ngưỡng p95 với nhóm.
4. **Chốt release gate:** xác nhận cấu hình GitHub Environment/secrets ngoài repository, chạy release workflow có phê duyệt, ghi lại image tag theo SHA và release ID; không đưa secrets vào Git.
5. **Thực hiện public smoke:** sau khi deployment thành công, xác minh HTTPS `/health`, `/ready`, luồng PvP/PvAI, history và persistence sau restart/redeploy. Lưu URL, source SHA, image SHA, môi trường, thời điểm và kết quả.
6. **Đóng issue theo evidence:** cập nhật ma trận QA và chỉ đóng các issue #23, #28, #29, #30, #31 khi acceptance criteria tương ứng có bằng chứng. Issue #24 vẫn là đầu mối điều phối Sprint 3.

## 8. Tóm tắt để trình bày với giảng viên

> CaroAI đã có nền tảng chơi Caro 15×15 với backend FastAPI, luật chơi do backend kiểm soát và AI được tích hợp qua một adapter riêng. Trong Sprint 3, nhóm đã đưa phần lưu game/nước đi qua SQLAlchemy vào nhánh tích hợp, bổ sung migration và CI kiểm thử PostgreSQL, đồng thời kiểm tra khả năng đọc lại dữ liệu sau khi restart API trong Docker Compose. Nhóm cũng đang hoàn thiện bộ kiểm thử trình duyệt và giao diện lịch sử ván đấu, cùng bộ benchmark AI có thể tái lập theo commit SHA.
>
> Kết quả CI gần nhất của PR tài liệu M5 đều xanh, nhưng nhóm chưa xem CI đó là bằng chứng release production. Những việc còn lại là chốt tài liệu QA theo đúng SHA, xác nhận browser E2E trên head mới nhất, hoàn tất benchmark Linux/Docker và thực hiện publish/deploy cùng smoke test HTTPS công khai. Vì vậy, trạng thái phù hợp hiện nay là **các thành phần nền tảng và CI đã tiến triển tốt; kiểm thử tích hợp/release cuối cùng vẫn đang được hoàn thiện**, chưa tuyên bố production release hoàn tất.

## 9. Liên kết theo dõi

- [PR #32 — Backend persistence](https://github.com/emt0147t/caroAI/pull/32)
- [PR #33 — AI benchmark/regression](https://github.com/emt0147t/caroAI/pull/33)
- [PR #34 — Browser E2E/History UI](https://github.com/emt0147t/caroAI/pull/34)
- [PR #35 — History API](https://github.com/emt0147t/caroAI/pull/35)
- [PR #36 — AI benchmark fix/results](https://github.com/emt0147t/caroAI/pull/36)
- [PR #37 — PostgreSQL CI/migrations/readiness](https://github.com/emt0147t/caroAI/pull/37)
- [PR #38 — Persistence QA handover](https://github.com/emt0147t/caroAI/pull/38)
- [Issue #23 — Persistence acceptance](https://github.com/emt0147t/caroAI/issues/23)
- [Issue #28 — AI benchmark](https://github.com/emt0147t/caroAI/issues/28)
- [Issue #29 — Frontend E2E/History](https://github.com/emt0147t/caroAI/issues/29)
- [Issue #30 — Release/deployment](https://github.com/emt0147t/caroAI/issues/30)
- [Issue #31 — QA evidence/docs](https://github.com/emt0147t/caroAI/issues/31)
- [Issue #24 — Sprint 3 coordination](https://github.com/emt0147t/caroAI/issues/24)
