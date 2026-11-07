# CaroAI Competitive Engine — audit và nghiệm thu candidate

**Ngày:** 07/11/2026 (Asia/Bangkok). **Trạng thái release: DRAFT; chưa merge/deploy.**

**Source chạy thử:** `14abd856492f0ff2a5daf61968f8463aa3a39aae`. **Baseline production:** `b848a0e6a527b7ef3f1efa421971c356543fbc17`.

## 1. Audit và phạm vi đã triển khai

- Production được xác minh chỉ đọc: đúng image SHA baseline đang live; `/health`, `/ready` = 200; QA = 404. Không đổi Render, không tạo dữ liệu production.
- `develop` chưa có các sửa QA/security mới của main. Công việc bắt đầu từ main để giữ baseline đã nghiệm thu.
- Baseline có Alpha-Beta, move ordering và cached/incremental line evaluation; HARD/IMPOSSIBLE vẫn tìm depth cố định, mặc định không deadline. Khi timeout, baseline bỏ tiến độ và trả ô gần trung tâm.
- PR #66 có lỗi TT: tactical extension depth 0 được lưu thành depth 1, khóa không có ngân sách extension. Tái hiện cùng thế cờ: tìm mới −500; dùng cache từ tầng trước 9.579.500. Counters generated/leaves cũng thiếu.
- Phase A/B/C là bằng chứng lịch sử về latency và correctness; chưa có tournament đủ mẫu hoặc tiến triển difficulty. Artifact Phase C đã tải và đối chiếu SHA-256, 1.452 dòng đúng source lịch sử. Không dùng số giữa hai máy để tuyên bố speedup.

Chi tiết bảy mục audit, điểm yếu, benchmark thiếu, kiến trúc và acceptance từng milestone: [AUDIT_AND_ROADMAP.md](../../docs/competitive/AUDIT_AND_ROADMAP.md).

## 2. Kiến trúc và chất lượng quyết định

Engine mới dùng bitboard có padding, kiểm tra thắng/chặn toàn bàn, fork với hai ô thắng khác nhau, tìm chứng chỉ continuous-four và iterative deepening. TT theo cả hai bitboard, người đi, **nominal depth và extension còn lại**; chọn tập ứng viên trước khi ưu tiên TT. Các nước tạo four và phản ứng fork trong tập sinh được giữ trước quiet cap. Horizon chỉ mở rộng đòn ép hoặc nước chặn bắt buộc.

| Chế độ | Chính sách candidate | Ngân sách mặc định |
|---|---|---:|
| EASY | Giữ baseline depth 1 / cap 6 | Không đổi |
| MEDIUM | Giữ baseline depth 2 / cap 10 | Không đổi |
| HARD | Radius 1, quiet cap 8, depth tối đa 4, 1 extension, proof tối đa 3 đòn ép | 250 ms / 16.000 nodes |
| IMPOSSIBLE | Radius 2, quiet cap 12, depth tối đa 6, 3 extensions, proof tối đa 5 đòn ép | 700 ms / 40.000 nodes |

Clock bắt đầu ở entry của core, bao gồm quét chiến thuật gốc. Quét thắng/chặn bắt buộc vẫn hoàn tất khi budget bằng 0. Khi bị ngắt, engine giữ tầng đã hoàn tất; fallback khởi tạo được ghi riêng. Đây là deadline hợp tác, không phải cam kết hard real-time khi scheduler/GIL bị tranh chấp.

Corpus có **15 thế cơ sở, mở rộng thành 240 biến thể × 2 mức mạnh**, với expected move set/outcome, đổi màu và D4. Oracle riêng dùng luật game domain; hai chuỗi thắng 2/3 lượt tấn công được kiểm chứng vét cạn trong mô hình continuous-four. Thế chain 3 có đáp án `(7,7)`: baseline HARD và IMPOSSIBLE chọn `(8,8)` ngoài tập chứng chỉ thắng này; candidate chọn `(7,7)` ở cả hai mức. Không suy diễn rằng mọi nước khác đều thua trong game đầy đủ.

Tổng local: **829 passed, 14 skipped**, lint pass. PostgreSQL bị skip local được chạy riêng trong CI. Có regression TT on/off, lower/upper/exact windows, alias từ PR #66, input immutability, ngắt search, nhiều request đồng thời và zero budget. Probe bổ sung xác minh ngắt proof cũng khôi phục board, bitboards, occupied mask và raw scores.

## 3. Tournament — cùng cặp đổi màu, khai cuộc có seed

Mỗi nhóm đầu có 200 ván hoàn tất; IMPOSSIBLE–HARD ở 25 ms tăng lên 400 vì 200 ván chưa phân biệt được. 100/200 opening pairs dùng 91/174 khai cuộc riêng biệt; khai cuộc 2/4/6/8 ply, năm kiểu và D4. Không adjudicate ván chưa xong thành hòa. Baseline source và các file evaluator/minimax/generator được hash-check trước chạy.

| Nhóm | Budget | W / D / L | Tỷ lệ thắng | Wilson 95% (tỷ lệ thắng) | Bootstrap 95% (score theo opening) |
|---|---|---:|---:|---:|---:|
| MEDIUM–EASY | Mặc định | 138 / 1 / 61 | 69.0% | 62.3–75.0% | 63.7–75.3% |
| HARD–MEDIUM | Mặc định | 166 / 0 / 34 | 83.0% | 77.2–87.6% | 76.9–87.4% |
| IMPOSSIBLE–HARD | Mặc định | 121 / 1 / 78 | 60.5% | 53.6–67.0% | 53.8–65.4% |
| HARD–baseline HARD | Mặc định | 132 / 0 / 68 | 66.0% | 59.2–72.2% | 61.5–72.5% |
| IMPOSSIBLE–baseline IMPOSSIBLE | Mặc định | ĐANG CHẠY | — | — | — |
| IMPOSSIBLE–reference greedy | Mặc định | 189 / 0 / 11 | 94.5% | 90.4–96.9% | 90.7–97.3% |
| MEDIUM–EASY | 25 ms | 104 / 0 / 96 | 52.0% | 45.1–58.8% | 44.5–57.4% |
| HARD–MEDIUM | 25 ms | 165 / 0 / 35 | 82.5% | 76.6–87.1% | 76.9–87.4% |
| IMPOSSIBLE–HARD | 25 ms | 211 / 0 / 189 | 52.8% | 47.9–57.6% | 46.0–55.7% |

Wilson tính trên chỉ báo thắng của từng ván; các ván đổi màu có tương quan. Bootstrap resample **các khai cuộc riêng biệt**, với score trung bình của từng opening cluster (thắng=1, hòa=0,5, thua=0); đây là estimand cân bằng theo opening, có thể khác tỷ lệ game gộp. CI là mô tả cho tập phân phối khai cuộc này, không phải xác suất thắng mọi người chơi.

Tỷ lệ thắng còn lệch theo màu: HARD–baseline HARD thắng 86/100 khi là X, 46/100 khi là O; IMPOSSIBLE–HARD lần lượt 81/100 và 40/100. Vì vậy phải giữ paired colors và cần đánh thử vai AI đi sau như production.

Đối thủ greedy có chính sách độc lập: oracle luật game cho win/block và đánh giá một ply; không dùng tactical bitboard/TT của candidate. Đây chưa phải một engine Gomoku công bố mạnh. Bằng chứng không chỉ dựa trên self-play: có baseline executable và reference riêng.

**25 ms không phải cấu hình production.** IMPOSSIBLE–HARD ở 400 ván vẫn có CI cắt 50%; không kết luận mức cao nhất mạnh hơn trong stress budget này. Các counter missed immediate win/unique forced block của những nhóm đã hoàn tất đều bằng 0; điều đó không chứng minh không bỏ lỡ mọi chuỗi thắng sâu.

Replay độc lập hiện xác minh **1,800 ván / 44,660 nước AI đã ghi**, 0 sai lệch luật, terminal state, winner hay score. Chạy lại bằng [replay_artifacts.py](replay_artifacts.py) với các ZIP ID trong manifest.

## 4. Performance và stability

Engine baseline và candidate chạy luân phiên trong cùng process/host, 12 fixtures × 4 levels × 10 lần đo, có warm-up bỏ khỏi summary. Fixtures gồm opening, early/mid/dense board, tactical, near-win và edge. Có 960 measured calls mặc định; stress engine c=1/2/4/8 ở 25 ms có 14.400 measured calls. Runtime Python 3.11.18, CPU AMD EPYC 9V74; package freeze được lưu trong summary.

| Level | Baseline engine p95 | Candidate engine p95 | Candidate worst observed | Timeout / n | Fallback / n |
|---|---:|---:|---:|---:|---:|
| EASY | 9.27 ms | 9.27 ms | 9.71 ms | 0/120 | 0/120 |
| MEDIUM | 45.39 ms | 45.45 ms | 45.84 ms | 0/120 | 0/120 |
| HARD | 386.33 ms | 205.95 ms | 211.24 ms | 0/120 | 0/120 |
| IMPOSSIBLE | 1663.03 ms | 700.54 ms | 700.58 ms | 50/120 | 0/120 |

Các median rất thấp vì nhiều root shortcut. Dữ liệu search-only được tách trong JSON nhưng tập fixture còn phải search có thể khác giữa hai engine; không lấy hai tập khác nhau để tuyên bố speedup search. Bảng trên là engine end-to-end trên cùng fixture mix. Latency tốt hơn một mình chưa chứng minh strength tốt hơn.

Counters gồm nodes, effective branching, alpha-beta pruning, TT probes/hits, stop reason và fallback; raw JSONL giữ từng call. Candidate pre-search pruning bao gồm lọc phản ứng fork và quiet cap, không diễn giải toàn bộ thành pure quiet-cap pruning. Branching/nodes có cả proof-search; không so trực tiếp số node như cùng một đơn vị công việc với legacy minimax.

API benchmark dùng **HTTP thật, một API worker và PostgreSQL disposable**, 10 measured batches + 1 warm-up ở c=1/2/4/8. Có 1.243 request rows, 6.654 server metric rows, 70.319 PostgreSQL observations; **801/801 correctness checks hợp lệ**, 0 unexpected errors, 0 invalid successful responses. Same-game conflict được phân loại riêng, không coi là nước AI thành công.

| IMPOSSIBLE / different games | API p50 | API p95 | Worst observed | Engine p95 |
|---|---:|---:|---:|---:|
| c=1 | 710.1 ms | 710.9 ms | 710.9 ms | 700.5 ms |
| c=2 | 718.7 ms | 724.4 ms | 724.5 ms | 702.9 ms |
| c=4 | 787.7 ms | 880.1 ms | 907.6 ms | 735.1 ms |
| c=8 | 1038.8 ms | 1213.4 ms | 1556.5 ms | 815.1 ms |

API c=8 cho thấy engine có thể vượt clock 700 ms do tranh chấp scheduling; đây không phải hard real-time. Benchmark API chỉ dùng fixture opening của harness Phase B. Engine-thread stress không được gọi là API latency; CI HTTP không được gọi là production latency. Render có CPU/RAM samples nhưng HTTP latency trống, nên production latency = **BLOCKED / chưa có dữ liệu**. Không đổi production để lấp khoảng trống này.

## 5. Milestone, PR và acceptance

| Milestone | PR | Trạng thái | Gate còn lại |
|---|---|---|---|
| M0 audit/evaluation | [#68](https://github.com/emt0147t/caroAI/pull/68) | PASS cho hạ tầng | Corpus ban đầu, không phải chứng minh mọi chiến thuật |
| M1 core | [#69](https://github.com/emt0147t/caroAI/pull/69) | PASS theo regression hiện có | Quiet long-range moves vẫn selective; proof không phải VCT/perfect play đầy đủ |
| M2 integration | [#70](https://github.com/emt0147t/caroAI/pull/70) | PASS correctness/compatibility CI | Chưa merge, chưa deploy |
| M3 strength/performance | #70 + artifacts | PARTIAL | Chờ IMPOSSIBLE–baseline; stress 25 ms progression chưa phân biệt được |
| M4 release | Chưa thực hiện | BLOCKED | Review người thật, đánh thử, xác nhận capacity/SLO, và cho phép rõ ràng trước merge/deploy |

- [CaroAI CI #42367773080](https://github.com/emt0147t/caroAI/actions/runs/42367773080) trên head `ed51afd8`: Python/lint, PostgreSQL acceptance, persistence, frontend regression, secret scan và Docker build PASS; release job skipped.
- [Browser E2E #42367773121](https://github.com/emt0147t/caroAI/actions/runs/42367773121) trên head `ed51afd8`: PASS, gồm visual regression.
- [Competitive evidence ban đầu #42363497808](https://github.com/emt0147t/caroAI/actions/runs/42363497808): 8 nhóm hoàn tất, nhóm cuối bị hủy ở 94 ván và không được tính; lượt thay thế [#42365889564](https://github.com/emt0147t/caroAI/actions/runs/42365889564) chạy cùng byte runtime. Không đồng nhất CI xanh với strength đã đạt.

Tiêu chí quyết định tiếp theo: chỉ kết luận candidate mạnh hơn baseline/level trước khi kết quả mặc định và CI ủng hộ; tăng tập khai cuộc khi chưa phân biệt được, hoặc giữ PARTIAL. Không sửa nhãn để che việc chưa đạt. Chưa triển khai Replay/Hint/Multiplayer; validator ở đây chỉ dùng nhật ký thật để kiểm chứng tournament.

## 6. Bằng chứng có thể kiểm tra

[artifact-manifest.json](artifact-manifest.json) lưu ID, source SHA, archive SHA-256 và link tải. Summary JSON được giữ cùng báo cáo; ZIP raw giữ đầy đủ nước đi, seeds, opening, runtime/package metadata và timing rows trong GitHub Actions (retention 30 ngày). Artifact digest đã đối chiếu sau tải. Không dùng benchmark Windows/Phase C cũ để tính speedup trên runner hiện tại.

HARD có bằng chứng cải thiện ở nhóm mặc định đã đo. IMPOSSIBLE đã có bằng chứng hơn HARD ở preset mặc định; còn chờ so sánh với baseline cũ; chưa đề xuất merge hoặc tuyên bố engine bất bại/optimal.


Workflow follow-up: cập nhật báo cáo đã hủy lượt IMPOSSIBLE–baseline ở source `14abd856` trước khi đủ 200 ván; artifact dở dang không được tính. Workflow được sửa bằng preflight so sánh runtime diff và concurrency theo từng job. Lượt đo chạy lại ở `2e9f869` có cùng byte của toàn bộ app/AI/harness với `14abd856`; chỉ report khác. Thay đổi tài liệu không hủy hoặc lặp lại benchmark. Workflow-only matrix/infrastructure edits có thể chạy chủ động bằng workflow_dispatch.


Browser harness follow-up: run 42366401700 failed only the first mobile start
capture (baseline 390×2928; candidate 390×2807), with different fallback/webfont
metrics despite byte-identical frontend files. The capture harness now pins the
external Plus Jakarta Sans font to Google Fonts commit
`8cd7d0de182c88592d6852c245fe48f66eef55ee`, verifies SHA-256 and routes that response
in test pages only. Product CSS/fonts and comparator thresholds stay unchanged.
Local repeated captures: 12/12 identical comparisons (0% diff); deliberate mutation,
dimension mismatch and missing-image checks still fail as expected (4/4 checks).
CI verification PASS: Browser E2E run [42367773121](https://github.com/emt0147t/caroAI/actions/runs/42367773121) on `ed51afd87e62442598105580a361b0676673c100`; regular CI [42367773080](https://github.com/emt0147t/caroAI/actions/runs/42367773080) also PASS. Cached font/test
artifacts are excluded from Git and Docker build context.

## 7. Lượt lặp lại và độ nhạy môi trường

Lượt chạy [42365889564](https://github.com/emt0147t/caroAI/actions/runs/42365889564)
ở source `2e9f869694953c2dcde75eb213cde79ab6da2574` dùng **cùng byte app,
benchmarks, scripts, frontend** với source thử ban đầu `14abd856`; chỉ report khác.
Git tree hashes và kết quả đối chiếu nằm trong [replication-summary.json](replication-summary.json).
Từng cặp vẫn đấu cùng host/runtime; runner giữa các nhóm/lượt có thể khác CPU.
Các package và baseline hashes được đối chiếu. Đây là lặp lại cùng seeds/openings,
không cộng gộp thành mẫu khai cuộc độc lập mới hoặc chọn lượt có kết quả đẹp hơn.

| Nhóm | Ván/lượt | W / D / L ban đầu | W / D / L lặp lại | Wilson 95% lặp lại | Bootstrap opening 95% lặp lại |
|---|---:|---:|---:|---:|---:|
| hard-baseline-default | 200 | 132 / 0 / 68 | 134 / 0 / 66 | 60.2–73.1% | 61.5–73.1% |
| hard-medium-default | 200 | 166 / 0 / 34 | 165 / 0 / 35 | 76.6–87.1% | 76.4–86.8% |
| hard-medium-screen25 | 200 | 165 / 0 / 35 | 164 / 0 / 36 | 76.1–86.7% | 75.8–86.8% |
| impossible-greedy-default | 200 | 189 / 0 / 11 | 181 / 0 / 19 | 85.6–93.8% | 86.8–95.1% |
| impossible-hard-default | 200 | 121 / 1 / 78 | 127 / 0 / 73 | 56.6–69.9% | 57.4–69.2% |
| impossible-hard-screen25 | 400 | 211 / 0 / 189 | 182 / 0 / 218 | 40.7–50.4% | 42.4–52.0% |
| medium-easy-default | 200 | 138 / 1 / 61 | 138 / 1 / 61 | 62.3–75.0% | 63.7–75.3% |
| medium-easy-screen25 | 200 | 104 / 0 / 96 | 11 / 0 / 189 | 3.1–9.6% | 2.7–9.3% |

Preset mặc định giữ được hướng kết quả trong các nhóm đã có hai lượt hoàn tất.
Ở **25 ms**, MEDIUM–EASY giảm từ 104/200 xuống **11/200 thắng**. MEDIUM giữ legacy
depth-2: deadline nhỏ trên runner chậm hơn có thể bỏ tiến độ rồi chọn fallback gần
trung tâm. Đây là stress regression của preset dùng override 25 ms, không được
che bằng tỷ lệ mặc định. IMPOSSIBLE–HARD có 400 ván mỗi lượt nhưng Wilson và
opening-bootstrap vẫn cắt 50%; hướng W/L thay đổi giữa hai lượt. Vì vậy progression
ở 25 ms = **PARTIAL / không đạt bằng chứng thứ bậc ổn định**; không tiếp tục tăng mẫu
chỉ để tìm ra một kết quả thuận lợi. EASY/MEDIUM cần nghiên cứu deadline và fallback
riêng nếu sản phẩm muốn hỗ trợ ngân sách rất ngắn.

Lượt performance lặp lại cũng đo baseline/candidate trong cùng process/host:
HARD p95 **454,06 → 250,13 ms**, IMPOSSIBLE **1966,77 → 700,38 ms**; fallback=0/120
cho mỗi mức mạnh. HARD dừng theo deadline 7/120, IMPOSSIBLE 50/120. Không dùng
chênh lệch giữa hai runner làm speedup. API lặp lại có **801/801** correctness checks,
không invalid success/unexpected error; IMPOSSIBLE p95 c1/2/4/8 lần lượt
**709,8 / 721,2 / 1089,5 / 1128,0 ms**, max c8 **1599,7 ms**. Deadline engine vẫn
không phải API SLO. Summary đầy đủ nằm trong [replica/](replica/), raw ZIP và digest
trong [replica-artifact-manifest.json](replica-artifact-manifest.json).

## 8. Chứng chỉ chiến thuật và giới hạn nghiệm thu

[forcing-certificate.json](forcing-certificate.json) ghi hai lịch sử khai cuộc hợp lệ,
14/15 ply cho hai màu, rồi chuỗi `(7,7) → ép chặn (7,8) → (8,8) → ép chặn (9,9)
→ (8,7)` tạo hai ô thắng `(8,6)` và `(8,11)`. Nhật ký được luật domain kiểm tra đến
terminal win. Cả baseline lẫn candidate tìm được nước đầu `(7,7)` ở thế cân bằng
này; không dùng nó để tuyên bố baseline bỏ lỡ hay cộng vào số ván tournament.
Thế composed chain-3 ở corpus mục 2 là một fixture khác. Probe phòng thủ nhiều lớp
ở [multilayer-defense-probe.json](multilayer-defense-probe.json) cũng là kiểm tra bổ
sung, không phải tournament.

Chưa có thử nghiệm với người chơi mới để kết luận EASY dễ hoặc MEDIUM cân bằng;
chưa có đối thủ Gomoku công bố mạnh, VCT đầy đủ hoặc bằng chứng perfect play.
Production candidate latency và capacity trên Render chưa đo; production vẫn chạy
baseline. Các giới hạn này giữ trạng thái PARTIAL/BLOCKED cho phát hành, dù regression
và pipeline xanh. Replay/Hint/Multiplayer chưa được triển khai.
