# CaroAI — Test Plan (Sprint 1)

> **Trạng thái:** Kế hoạch kiểm thử, không phải test code. Danh sách endpoint trong tài liệu này lấy từ Team Guide được cung cấp cho Sprint 1. Request/response schema, status code và một số quy tắc vẫn cần M1 xác nhận; tài liệu không tự định nghĩa các contract đó.

## 1. Mục tiêu kiểm thử

Kế hoạch này xác định cách kiểm tra các quy tắc Caro, API, lưu trữ PostgreSQL và tích hợp triển khai trong Sprint 1. Mục tiêu là giúp nhóm phát hiện sớm lỗi ở các ranh giới giữa game rules, API và database, đồng thời ghi rõ những trường hợp chỉ có thể kiểm thử sau khi contract liên quan được chốt.

Đây là test plan, không triển khai test tự động. Các test phụ thuộc vào API, game-state transition, database migration hoặc môi trường Docker chưa được xác nhận sẽ được giữ ở trạng thái chờ.

## 2. Phạm vi

Phạm vi kiểm thử dự kiến:

- Game rules và trạng thái bàn cờ 15×15.
- Move validation, kiểm tra thắng và hòa.
- Các API endpoint được liệt kê trong Team Guide.
- Persistence và constraints PostgreSQL theo [`database-design.md`](database-design.md).
- Tích hợp luồng game với database.
- Health check.
- Docker smoke test.

Phạm vi này không bổ sung endpoint, request/response schema, authentication, user feature, AI behavior hoặc game logic ngoài specification/contract đã được nhóm xác nhận.

## 3. Unit Test Plan

Các tên `Board`, `MoveValidator`, `WinChecker` và `GameState` dưới đây là component được Team Guide/specification nêu hoặc cần M1 xác nhận. Chúng không phải khẳng định rằng repository hiện đã có các implementation này.

| Component | Test case | Kết quả cần kiểm tra |
|---|---|---|
| Board | Khởi tạo bàn cờ | Kích thước là 15×15 theo specification; trạng thái ban đầu theo contract M1 |
| Board | Truy cập ô biên `(0, 0)` và `(14, 14)` | Hai tọa độ biên hợp lệ; cách biểu diễn nội bộ chờ M1 nếu chưa có contract |
| MoveValidator | Move hợp lệ vào ô trống với tọa độ trong `0..14` | Move được chấp nhận theo contract đã xác nhận |
| MoveValidator | Move có row hoặc col ngoài `0..14` | Move bị từ chối theo contract; exception/error format chờ M1 |
| MoveValidator | Move vào ô đã có quân | Move bị từ chối; error format chờ M1 |
| MoveValidator | Player có giá trị X hoặc O | Chỉ X/O được chấp nhận theo specification |
| WinChecker | X thắng theo hàng ngang | Nhận diện X thắng |
| WinChecker | O thắng theo hàng dọc | Nhận diện O thắng |
| WinChecker | X hoặc O thắng theo đường chéo | Nhận diện đúng player thắng |
| WinChecker | Có từ 5 quân liên tiếp | Kiểm tra quy tắc thắng “5 hoặc nhiều hơn” theo specification; hướng kiểm tra gồm ngang, dọc và hai đường chéo |
| WinChecker | Chuỗi dưới 5 quân liên tiếp | Không báo thắng nếu contract xác nhận điều kiện thắng là tối thiểu 5 quân |
| GameState / transitions | Chuyển trạng thái sau một move hợp lệ | Chờ M1 xác nhận trạng thái, player turn và transition được hỗ trợ |
| GameState / transitions | Không cho move sau khi game kết thúc | Chờ M1 xác nhận transition/response ở tầng logic; không suy diễn API error |
| Draw | Bàn đầy nhưng không có người thắng | Xác định DRAW theo specification; quy tắc ưu tiên nếu nước cuối cũng tạo thắng cần M1 xác nhận |
| AI legal move | AI chọn ô còn trống trong bàn cờ | Chỉ kiểm tra khi M2 xác nhận AI behavior/criteria; M1 xác nhận API contract liên quan và M4 cung cấp runtime environment nếu cần. M5 không tự định nghĩa AI behavior |

**Lưu ý:** GameState/transitions chỉ được biến thành test thực thi sau khi M1 xác nhận component và domain contract. AI legal move chỉ được kiểm thử sau khi M2 xác nhận AI behavior/criteria; M1 xác nhận API contract liên quan và M4 xác nhận runtime environment nếu cần. M5 không tự định nghĩa AI behavior hoặc expected output.

## 4. API Test Plan

Các endpoint dưới đây là danh sách từ Team Guide. Với mọi endpoint, request/response schema, status code, error format và trường response cụ thể **chờ M1 xác nhận** nếu chưa được định nghĩa trong contract. Các happy path mô tả mục đích ở mức cao, không quy định payload.

| Endpoint | Mục đích | Happy path cần kiểm tra | Invalid input / not found / game kết thúc | Response cần kiểm tra |
|---|---|---|---|---|
| `GET /health` | Kiểm tra health của ứng dụng; phạm vi health của database chờ M1 xác nhận | Khi ứng dụng và database hoạt động, endpoint trả success theo contract | Database unavailable: kiểm tra failure chỉ khi health contract hỗ trợ; không giả định status code/body | Success/failure theo schema và status đã được M1 chốt; hiện chờ M1 xác nhận |
| `POST /api/games` | Tạo game | Tạo được game cho mode được specification hỗ trợ; giá trị difficulty và điều kiện áp dụng chờ M1 xác nhận | Invalid input theo schema đã chốt; không áp dụng not found; điều kiện tạo game sau khi kết thúc không liên quan nếu chưa có contract | Kiểm tra dữ liệu game được trả về theo schema đã chốt; fields/status code chờ M1 xác nhận |
| `GET /api/games/{game_id}` | Lấy thông tin game | Lấy game đã tồn tại | `game_id` không tồn tại cần not-found behavior theo contract; invalid ID format chờ M1 | Kiểm tra dữ liệu game theo response schema; không giả định thêm fields |
| `POST /api/games/{game_id}/moves` | Ghi một move cho game | Gửi move hợp lệ theo request schema đã chốt và xác nhận game/move được xử lý | Tọa độ ngoài bàn, ô đã có quân, game không tồn tại; game đã kết thúc phải bị xử lý theo contract. Status/error response chờ M1 | Kiểm tra move/game data theo response schema đã chốt; không suy diễn fields hoặc status code |
| `POST /api/games/{game_id}/ai-move` | Yêu cầu AI thực hiện move | Chỉ kiểm tra sau khi M2 chốt AI behavior/criteria và M1 chốt API contract; M4 cung cấp runtime environment nếu cần | Game không tồn tại/game đã kết thúc theo M1; AI-specific invalid/no-legal-move behavior chờ M2 contract | Response/status theo M1 API contract; expected AI move theo M2 contract. M5 không đặt tiêu chí chiến thuật |
| `POST /api/games/{game_id}/hint` | Yêu cầu hint | Chỉ kiểm tra sau khi M2 chốt behavior/ý nghĩa hint và M1 chốt API contract; M4 cung cấp runtime environment nếu cần | Game không tồn tại/game đã kết thúc theo M1; hint-specific behavior chờ M2 contract; invalid input nếu endpoint có request body theo M1 | Response/status theo M1 API contract; expected hint theo M2 contract. Không giả định hint tương đương AI move |
| `POST /api/games/{game_id}/analyze` | Yêu cầu phân tích game | Chỉ kiểm tra sau khi M2 chốt analysis behavior/criteria và M1 chốt API contract; M4 cung cấp runtime environment nếu cần | Game không tồn tại hoặc điều kiện game theo M1; analysis-specific behavior chờ M2 contract; invalid input nếu có theo M1 | Response/status theo M1 API contract; expected analysis theo M2 contract. Các trường/ý nghĩa analysis chờ M1/M2 xác nhận |
| `GET /api/games/{game_id}/moves` | Lấy danh sách moves của game | Trả các move đã lưu của game theo quy tắc ordering được chốt | Game không tồn tại theo not-found contract; invalid ID format chờ M1 | Kiểm tra danh sách và thứ tự theo schema/ordering contract; không giả định pagination |
| `GET /api/history` | Lấy history | Kiểm tra history theo phạm vi dữ liệu và tiêu chí truy vấn đã chốt | Invalid query parameters nếu contract có; không suy diễn authentication hoặc user scoping | Schema, thứ tự, giới hạn và nội dung history chờ M1 xác nhận |

Không endpoint nào trong test plan được gán request body, query parameter, field response, status code hoặc error schema chưa có trong contract.

## 5. Database Test Plan

Các test database bám theo [`database-design.md`](database-design.md). Chỉ thực thi khi schema/migration tương ứng được triển khai. Các lựa chọn còn chờ M1 được đánh dấu có điều kiện.

| Test case | Điều kiện / kết quả cần kiểm tra |
|---|---|
| Tạo game | Lưu được bản ghi `games` với các giá trị hợp lệ theo schema đã chốt; default và nullability kiểm tra theo quyết định cuối cùng |
| Đọc game | Đọc lại game đã lưu và đối chiếu các cột đã ghi |
| Tạo move | Lưu move có `game_id`, `player`, tọa độ trong `0..14`, `move_number` hợp lệ |
| Move liên kết đúng game | `moves.game_id` trỏ tới game tương ứng; FK từ chối game ID không tồn tại |
| Game có nhiều moves | Một game liên kết được nhiều move; unique thứ tự vẫn được giữ |
| Analysis liên kết đúng game | `game_analysis.game_id` trỏ tới game tương ứng. Nếu chọn composite FK, kiểm tra `move_id` chỉ tham chiếu move trong cùng game |
| Foreign key | Thử tham chiếu game không tồn tại; nếu bật composite FK, thử cặp game/move không khớp. Kết quả lỗi cụ thể phụ thuộc tầng xử lý đã chốt |
| `UNIQUE (game_id, move_number)` | Không chấp nhận move number trùng trong cùng game; cùng move number ở game khác được phép |
| `UNIQUE (game_id, row, col)` | **Chỉ khi M1 chấp thuận constraint này:** không chấp nhận hai move chiếm cùng ô trong cùng game |
| Tọa độ bàn cờ | Chấp nhận row/col `0` và `14`; từ chối giá trị ngoài `0..14` theo CHECK constraint đã chốt |
| Player | Chấp nhận `X` và `O`; từ chối giá trị khác theo constraint đã chốt |
| Analysis nullable/multiple | `move_id` có thể null; không giả định uniqueness theo move; lưu nhiều analysis cho một move nếu schema cuối cho phép |
| Rollback transaction | Khi transaction rollback, thay đổi trong transaction đó không được commit; chi tiết atomicity/error propagation phụ thuộc persistence implementation |
| Persistence sau transaction hợp lệ | Sau commit hợp lệ, dữ liệu vẫn đọc được trong transaction/session mới theo test database strategy đã chọn |
| Timestamp | Kiểm tra cột timestamp có timezone và giá trị được diễn giải nhất quán theo UTC; cách assert chính xác phụ thuộc driver/SQLAlchemy configuration |

Không test `users`, vì schema users chưa được chốt. Không kiểm tra miền `score` hoặc `classification`, vì database design chưa đặt miền giá trị. Hành vi `ON DELETE CASCADE` chỉ kiểm tra sau khi chính sách xóa được xác nhận.

## 6. Integration Test Plan

### Human move và persistence

Luồng kiểm thử dự kiến:

1. Tạo game qua contract đã chốt.
2. Gửi một move hợp lệ qua API.
3. Xác nhận move được lưu vào PostgreSQL và liên kết đúng `game_id`.
4. Đọc lại game.
5. Đọc danh sách moves của game.
6. Thực hiện các move cần thiết để kết thúc game theo luật đã xác nhận.
7. Đọc lại game/moves và xác nhận persistence cùng trạng thái kết thúc theo contract M1.

Payload, thứ tự cụ thể của request, response fields và cách kết thúc game phụ thuộc API/game contract của M1.

### Human versus AI và persistence

Luồng kiểm thử dự kiến:

1. Tạo game `HUMAN_VS_AI` nếu mode và request contract được xác nhận.
2. Gửi human move hợp lệ.
3. Yêu cầu AI move theo AI contract của M2 và API contract của M1.
4. Kiểm tra tính hợp lệ/expected AI move theo criteria M2 xác định, rồi xác nhận move được lưu đúng game; M4 cung cấp runtime environment nếu cần.
5. Đọc lại game/moves và kiểm tra consistency giữa state được trả về và dữ liệu PostgreSQL theo contract đã chốt.

M5 không tự định nghĩa hoặc kiểm thử chiến thuật, độ khó hay chất lượng AI nếu M2 chưa cung cấp behavior/criteria; API request/response thuộc M1 và runtime environment thuộc M4.

## 7. Health Check Test

- Khi application và PostgreSQL hoạt động, gọi `GET /health`; endpoint phải trả success theo contract.
- Nếu PostgreSQL unavailable, kiểm tra failure chỉ khi health contract quy định kiểm tra database dependency.
- Không tự đặt status code, body, response fields, timeout hoặc retry behavior. Các chi tiết này chờ M1 xác nhận.

## 8. Docker Smoke Test

Khi project có Docker Compose configuration, thực hiện smoke test theo thứ tự:

1. Build image bằng `docker compose build`.
2. Khởi động application container và PostgreSQL container theo cấu hình team.
3. Xác nhận application kết nối được PostgreSQL.
4. Gọi `GET /health` và kiểm tra kết quả theo contract.
5. Tạo game thành công qua API đã chốt.
6. Ghi một move hợp lệ.
7. Đọc lại game và moves để xác nhận dữ liệu được lưu.

Repository hiện chưa có Docker Compose configuration; test này phụ thuộc việc team cung cấp môi trường/configuration. Không giả định tên service, port, biến môi trường bổ sung hoặc migration command.

## 9. Test Environment

- **Test runner:** `pytest` (đã có trong `requirements.txt`).
- **API client:** FastAPI `TestClient` hoặc `httpx` (chọn theo implementation/fixture của M1; `httpx` đã có trong `requirements.txt`).
- **Database:** PostgreSQL tương thích với cấu hình SQLAlchemy của ứng dụng.
- **Container smoke test:** Docker Compose nếu team cung cấp cấu hình.
- **Test database/isolation:** Chưa có quyết định trong repository. Team cần chốt database riêng cho test, cách tạo/reset dữ liệu và cách cô lập test song song trước khi thực thi DB/integration tests.
- **Schema setup:** Migration strategy chưa được chốt; không giả định test tự tạo schema bằng cách nào.

## 10. Test Data

Mô tả dữ liệu cần chuẩn bị, không quy định API payload:

- Một game `HUMAN_VS_HUMAN` với các trường còn lại theo contract M1.
- Một game `HUMAN_VS_AI` với difficulty được chọn trong `EASY`, `MEDIUM`, `HARD` theo quy tắc mode/difficulty đã xác nhận.
- Bàn cờ kích thước 15×15, tọa độ hợp lệ `0..14`.
- Các move dùng player `X` và `O`.
- Tình huống X thắng ngang, O thắng dọc, và thắng chéo cho từng hướng liên quan.
- Tình huống có từ 5 quân liên tiếp.
- Bàn đầy không có người thắng để kiểm tra DRAW.
- Tọa độ ngoài biên: row hoặc col nhỏ hơn `0` hoặc lớn hơn `14`.
- Tình huống ghi move vào ô đã có quân.
- `game_id` không tồn tại.
- Move number trùng trong cùng game; duplicate cell chỉ áp dụng nếu constraint được M1 chấp thuận.

Thứ tự move/player turn để tạo các fixture thắng/hòa phải tuân thủ game contract khi M1 chốt; tài liệu này không quy định thêm luật lượt.

## 11. Exit Criteria

Test plan Sprint 1 được coi là hoàn tất khi:

- Các nhóm test và case tối thiểu trong phạm vi đã được định nghĩa.
- Những dependency lên API/game/database/Docker contract được đánh dấu rõ.
- Không có test case dựa vào API schema chưa chốt mà tự suy diễn request/response.
- Các lựa chọn database có điều kiện, gồm unique cell constraint và composite FK, được nhận diện là cần xác nhận.
- Tài liệu sẵn sàng làm cơ sở để Sprint 2 triển khai automated tests sau khi contract và test environment được chốt.

## 12. Open Questions / Dependencies

1. **M1 — API:** Request/response schema, status code, error format và validation behavior cho từng endpoint.
2. **M1 — Game state:** Quan hệ giữa `status`, `result`, `ended_at`; trạng thái sau move và behavior khi game đã kết thúc.
3. **M1 — Difficulty:** Quy tắc null/bắt buộc cho `difficulty` theo `mode`.
4. **M1 — Game ID:** Kiểu, format và validation của `game_id` trong API so với kiểu ID database.
5. **M2 — AI:** AI design, AI contract, behavior và criteria cho AI move/legal move/hint/analyze. **M1:** API request/response và game-state contract liên quan. **M4:** runtime/deployment environment nếu cần. M5 chỉ lập test plan/QA coverage theo các contract đã xác nhận, không tự định nghĩa AI behavior.
6. **Team — Test database:** Database riêng hay strategy khác, isolation/reset và hỗ trợ chạy test song song.
7. **Team — Migration:** Cách thiết lập schema cho integration tests và môi trường smoke test.
8. **M1/Team — Transaction:** Ranh giới transaction, rollback behavior và xử lý lỗi persistence cần được kiểm thử.
9. **M1 — Database constraints:** Chấp thuận `UNIQUE (game_id, row, col)`, composite FK cho analysis, chính sách cascade và rules khác.
10. **Team — Docker:** Dockerfile/Compose configuration, service readiness và cách cấu hình kết nối database.
11. **M1 — History:** Phạm vi dữ liệu, thứ tự, pagination/filtering (nếu có) của `GET /api/history`.

