# CaroAI — vòng thử nghiệm học offline 1

Ngày 07/11/2026 UTC. **Trạng thái: CHỜ CÁC NHÓM MẶC ĐỊNH; chưa đủ điều kiện promotion.** PR nghiên cứu [#71](https://github.com/emt0147t/caroAI/pull/71), chưa merge/deploy.
Production tiếp tục dùng `c10ee2739b6577ea0004f86e91126dd176132319`.

Source thử nghiệm: `0204bc5b12f6ec27058e220d5a14ca023ea598ee`.
Model semantic SHA-256: `4370e36660dd41a7ebd81c96a0e552bd44d165ca5f7d40d9d873307ec79182aa`.
[Workflow bằng chứng](https://github.com/emt0147t/caroAI/actions/runs/42395577075).
[Protocol và gate chốt trước khi xem holdout](../../docs/learning/OFFLINE_PROTOCOL.md).

## Việc đã triển khai

- Bộ đọc/replay lịch sử đầy đủ và bộ chẩn đoán đòn ép có chứng chỉ độc lập. Không suy diễn thứ tự từ bàn cuối; UNKNOWN khác NO_PROOF.
- Corpus thực và các thế phát sinh được giữ riêng tại local của chủ dự án. Không công khai game ID, timestamp, nước đi hoặc bàn cờ thực; CI công khai chỉ có fixture tổng hợp và self-play.
- Policy 8 đặc trưng và value 7 đặc trưng, Monte Carlo actor/critic với reward thắng/thua/hòa +1/−1/0. Cập nhật chỉ giữa các batch hoàn tất. Đây là RL tuyến tính trên CPU, chưa phải AlphaZero/MCTS/neural network.
- Candidate dùng policy/value ở gốc để chọn/ưu tiên nước và mở rộng tập nước khi cây selective báo thua. Search sâu/TT/proof giữ core production. Application không import model mới.

## Huấn luyện và tách dữ liệu

Đã huấn luyện **4.000 ván hoàn tất**, replay độc lập **44.474 nước sinh sau khai cuộc**, 0 sai lệch luật/kết quả.
Có **3.997 canonical training roots**; **80 canonical evaluation roots** được đặt riêng trước huấn luyện, không trùng các thế đầu ván đã dùng để cập nhật.
Seed 731, batch 20, learning rate 0,1, temperature 0,7. Khai cuộc train có 6/8 ply; evaluation dùng tập seed riêng, paired colors và D4.

Cả hai head đã đổi trọng số. Training value MSE từ 1,0 về khoảng 0.72; đây không phải bằng chứng mạnh hơn đối thủ.
Self-play có 2.346 X thắng, 1.654 O thắng, median 17 ply/ván; chỉ 210 ván >=30 ply và 2 ván >=50 ply. Phân phối này chưa bao phủ tốt các cuộc đấu dài.

## Đấu đối chứng — 200 ván hoàn tất mỗi nhóm

| Nhóm | W / D / L candidate | Wilson 95% tỷ lệ thắng | Bootstrap 95% score/canonical opening |
|---|---:|---:|---:|
| IMPOSSIBLE — production, 700 ms | ĐANG CHỜ | — | — |
| IMPOSSIBLE — initial model, 700 ms | ĐANG CHỜ | — | — |
| HARD — production, 250 ms | 112 / 0 / 88 | 49.1–62.7% | 50.3–60.9% |
| IMPOSSIBLE — production, 25 ms | 107 / 0 / 93 | 46.6–60.3% | 47.5–59.4% |

Wilson là mô tả theo ván có tương quan. Bootstrap resample các bàn khai cuộc tương đương D4; estimand là score cân bằng theo cluster, khác tỷ lệ thắng gộp theo ván.
Bốn đối chứng dùng lại tập khai cuộc nên không được gộp thành các mẫu khai cuộc độc lập mới.
So sánh với initial model giữ cùng thuật toán để tách lợi ích của thay đổi search khỏi lợi ích của việc học.

## Tactical và dữ liệu riêng

Candidate đạt **480/480 tactical variants** ở HARD/IMPOSSIBLE. Public CI ghi rõ human regression = **NOT_RUN_PUBLIC_CI**, không tự coi tập rỗng là PASS.
Kiểm tra corpus riêng được chạy local bằng đúng fingerprint model; dữ liệu gốc và báo cáo theo từng ván không được upload. Bộ này đánh giá việc phá kế hoạch đã quan sát, không chứng minh nước cứu thắng toàn game.
Các bước cập nhật metadata difficulty/engine version cho lịch sử production chưa được thêm trong PR này; dữ liệu cũ không được gán nhãn giả.

## Latency và stability

Cùng host/process/fixtures, xen kẽ thứ tự contender, có warm-up loại khỏi thống kê. Budget engine 700 ms cho cả hai.
Mỗi group có 12 fixture ×5 lần đo ×concurrency. Median rất thấp do nhiều root shortcut, không đại diện cho mọi nước chơi.

| Concurrency | Số call/engine | p95 production / candidate | Max production / candidate | Fallback production / candidate |
|---|---:|---:|---:|---:|
| 1 | 60 | 700.8 / 700.8 ms | 700.8 / 701.0 ms | 0 / 0 |
| 2 | 120 | 701.1 / 700.9 ms | 702.1 / 705.9 ms | 0 / 0 |
| 4 | 240 | 715.6 / 720.9 ms | 731.6 / 776.1 ms | 0 / 0 |
| 8 | 480 | 827.7 / 836.0 ms | 1406.9 / 1178.5 ms | 0 / 1 |

Đây là engine-thread stress, không phải HTTP hay production latency. Deadline hợp tác có thể vượt dưới scheduling/GIL contention.
Ở tournament 25 ms, candidate có 24 fallback so với production 4; không dùng preset stress này để kết luận cải thiện preset mặc định.

## Kiểm tra và phát hành

Local: **852 passed, 14 PostgreSQL skipped**; dedicated PostgreSQL CI bao phủ phần này. Lint pass.
[CI source cố định](https://github.com/emt0147t/caroAI/actions/runs/42395579359),
[Browser E2E](https://github.com/emt0147t/caroAI/actions/runs/42395579361): PASS, gồm PostgreSQL, persistence, secret scan, Docker và visual regression.
Không có thay đổi app/AI/domain so với production; comparator kiểm tra hash từng file.

Gate gồm tactical, private human validation, ưu thế trước production và initial-model, HARD noninferiority, serial latency/fallback.
Không có tự động publish/promote/deploy model. Nếu các gate chưa đạt, giữ NOT_PROMOTED và giữ production hiện tại.
Nếu tiếp tục vòng sau, cần opponent pool mạnh hơn/curriculum cho mid/late game và một protocol/holdout mới, không tune tiếp trên holdout vòng này.

Các summary/model được lưu kèm báo cáo. Raw self-play/evaluation, seeds, nước đi, environment và manifests ở GitHub Actions artifacts (retention30 ngày).
Dữ liệu ván chơi thực không có trong các artifact công khai này.
