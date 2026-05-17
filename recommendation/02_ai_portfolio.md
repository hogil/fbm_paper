## 1. AI 프로젝트 수행 전체이력

| 기간 | 내용(과제명, 리딩 규모, 담당업무, 본인 업무 내 과제관리/설계/개발비중) |
|---|---|
| 2024년 10월 ~ 현재 | **Failbit Map 이미지 데이터 생성 및 Known 불량 및 Unknown 불량 분류 시스템**. 3인 협업 과제로 본인 60% / 현업 엔지니어 20% / 관리자 20% 기여입니다. 담당 범위는 fail-map 데이터 파이프라인, 운영 뷰어 연동/기여, Known CNN -> ROI-YOLO 2-stage, Unknown contrastive learning, 후속 chip-CNN obj-id map 개발 구조였습니다. raw log 변환, 이미지/좌표 생성, 모델 분기, 현업 검증을 연결해 일 약 2만 장 wafer 이미지를 1시간 주기로 처리 가능한 운영형 AI 시스템으로 설계했습니다. |
| 2025년 3월 ~ 현재 | **Chip Multi-label Classification 및 FCM-PM 기반 결함 조합 학습**. 2인 협업 과제로 본인 80% / 관리자 20% 기여입니다. **[현업 defect chip 원천 + 도메인 확률분포 기반 생성/검증]** 구조로, 2-combo 결함 부족 문제를 보완했습니다. Full-Cover Mixup과 Pair Mask loss를 결합한 FCM-PM, BCE 기반 multi-label 학습, val-margin best-model selection, max-prob gate, bit_F1 / FAR 동시 평가와 운영성 검토를 수행했습니다. 본인 업무는 모델 구조, 학습/평가 로직, 조합 데이터 설계 중심으로 수행했습니다. |
| 2026년 1월 ~ 현재 | **Trend Chart 기반 Anomaly Detection 합성 데이터 및 검증 PoC**. 3인 협업 과제로 본인 70% / 관리자 20% / 공동 연구자 10% 기여입니다. 합성 trend chart에서는 trend episode generator, Region 5종, Noise 3종, anomaly 5종, 정상 산포 기준 최소 이상 강도 보정, 1차 binary gate 검증 PoC를 담당했습니다. 본인 업무는 생성 규칙 설계와 검증 구조 개발 중심으로 수행했고, 과제관리는 실험 기준 정리와 결과 리뷰 중심으로 담당했습니다. |

## 2. 대표 과제 상세 기술서

**P1. Failbit Map 이미지 데이터 생성 및 Known 불량 및 Unknown 불량 분류 시스템**

ㅁ **과제 기본정보**

| 항목 | 내용 |
|---|---|
| 과제명 | Failbit Map 이미지 데이터 생성 및 Known 불량 및 Unknown 불량 분류 시스템 |
| 수행기간 | 2024년 10월 ~ 현재 |
| 참여인원 | 3인 (본인, 현업 엔지니어, 관리자) |

ㅁ **과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|---:|---|---|---|---|---:|
| 1 | 최호길 | 개인정보 비공개 | 메모리제조센터 QIE그룹 | fail-map 데이터 파이프라인, 운영 뷰어 연동/기여, Known CNN -> ROI-YOLO 2-stage, Unknown contrastive learning, 후속 chip-CNN obj-id map 개발 구조 설계/구현 | 60% |
| 2 | 현업 엔지니어 | 개인정보 비공개 | 관련 현업부서(공식 기록 대조) | 아이디어 발의, Failbit Map 의미 및 불량 분석 교육, Unknown 후보 현업 검증 협업 | 20% |
| 3 | 관리자 | 개인정보 비공개 | 관리조직(공식 기록 대조) | 방향성, 일정, 리뷰 매니징 | 20% |

ㅁ **개인별 기여 서술**

[본인이 독자적으로 수행한 핵심 모듈]

- raw log를 wafer 이미지와 chip positions JSON으로 바꾸는 fail-map 파이프라인을 만들고, 운영 뷰어와 AI 분석 입력이 같은 wafer/chip 기준을 보도록 연결했습니다.
- 현업 엔지니어가 설명한 Failbit Map 불량 의미를 모델 입력, label, routing 조건, 후보 group 검증 흐름으로 구체화했습니다.
- Known 분류에서는 1-stage CNN 결과를 그대로 확정하지 않았습니다. center/edge처럼 비슷한 분포를 보이는 혼동 sample만 ROI-YOLO가 국소 영역을 다시 보게 하여, 모든 sample에 detector를 적용하지 않고도 성능을 올리는 구조로 설계했습니다.
- Unknown은 운영 데이터에서 정답 label이 없는 문제라서, 점수 하나로 불량을 단정하기보다 현업이 확인 가능한 후보 group으로 줄이는 방식으로 설계했습니다.
- P1은 raw log 변환부터 현업 후보 검증까지 이어지는 운영형 AI 흐름을 만든 과제입니다.

ㅁ **문제정의**

| 항목 | 내용 |
|---|---|
| 현장 난제 및 해결 목표 | Failbit Map은 wafer당 대량 cell의 Grade 정보를 담고 있어 사람이 일일이 비교하기 어렵습니다. Known 결함은 빠르게 분류하고, Unknown은 신규 의심 패턴을 현업이 확인 가능한 수준으로 줄이는 것이 목표였습니다. |
| 기존 방식의 한계 및 AI 도입 배경 | 조회 중심 방식만으로는 대량 누적 비교와 신규 불량 후보 선별이 어렵습니다. 또 wafer 전체 분포가 비슷한 class는 1-stage CNN만으로 center/edge 혼동이 남았습니다. |
| 기술적 / 환경적 제약 조건 | 16-class labeled sample은 1,500장 수준으로 제한적이었고, 운영에서는 이미지 생성, 조회 응답성, 모델 입력 정합성을 동시에 맞춰야 했습니다. ROI trigger는 confidence만이 아니라 class별 precision/recall로 식별한 difficult class와 low-confidence sample 기준을 함께 사용해야 했습니다. Unknown은 실전 운영 데이터에서 별도 정답 label이 없었습니다. |

ㅁ **기술적 해결 방안**

[본인이 직접 수행한 핵심 로직]

- 데이터: 압축 raw log를 Grade tensor, palette PNG, chip positions JSON으로 변환했습니다. hex 값을 Grade 0-7로 푸는 변환 루프는 Cython으로 재구성해 약 100배 가속을 확인했고, palette PNG 저장으로 용량을 약 75% 줄였습니다. fail-map은 이미지 생성 파이프라인이고, mapviewer는 생성된 이미지를 조회/검색하는 운영 뷰어로 역할을 분리했습니다.
- 알고리즘: wafer 전체 분포는 CNN이 먼저 보고, confidence가 낮거나 class별 precision/recall이 낮은 difficult class, center/edge 혼동 class는 ROI-YOLO로 넘겼습니다. confidence만으로 gate를 만들면 고신뢰 오판이 Stage 2를 건너뛸 수 있어, difficult class 기준을 같이 둔 구조입니다. difficult class에 들어간 sample은 confidence가 높아도 ROI 재확인 대상으로 남기고, 분석 sample 저장 기준으로 잔여 오판을 추적했습니다. Unknown은 label 없는 운영 이미지를 contrastive embedding으로 바꾼 뒤 HDBSCAN으로 묶어, 개별 이미지 확인을 후보 group 검토로 바꾸는 데 초점을 뒀습니다.
- 최적화: MaxViT와 ConvNeXtV2는 1-stage backbone 비교 단계에서 모두 weighted F1 0.87 수준이었지만, ConvNeXtV2가 parameter 약 26%, FLOPs 약 39% 낮아 운영량을 고려해 1-stage backbone으로 선정했습니다. 이후 tuning으로 0.92까지 올리고, ROI-YOLO 보정으로 최종 0.95를 확인했습니다.
- Unknown 추가 개발: 실전 운영 결과와 분리하여, 추가 생성 데이터에서는 Global InfoNCE, MoCo Queue, negative filtering, NeCo 조합을 비교하며 embedding noise와 cluster 안정성을 관리하고 있습니다.
- 추가 개발: ROI-YOLO를 계속 확장할 때 생길 수 있는 class 증가와 처리 부담을 줄이기 위해, **[추가 생성 chip 데이터, 개발 중]** CNN -> chip-CNN obj-id map 구조를 별도 검토하고 있습니다. 이 수치는 P1 2-stage 성과와 섞지 않고 관리합니다.

ㅁ 실제 코드를 제외한 아키텍쳐 설계도, 플로우차트 등으로 기술

```text
[EDS Test raw log]
        |
        v
[fail-map 변환]
  - Grade tensor
  - palette PNG
  - chip positions JSON
        |
        v
[운영 뷰어 조회] + [AI 모델 입력]
        |
        +--> Known path
        |     [wafer-level CNN]
        |          |
        |          |  일반 sample: CNN 결과 사용
        |          |  저신뢰 / difficult class / center-edge 혼동: ROI 강제 재확인
        |          |  difficult class 고신뢰 결과: ROI 재확인
        |          v
        |     [ROI-YOLO]
        |          |
        |          v
        |     [16-class Known defect 판정]
        |
        +--> Unknown path
              [contrastive embedding]
                   |
                   v
              [HDBSCAN 후보 group]
                   |
                   v
              [현업 엔지니어 검증]

설계 기준
  - wafer 전체 분포와 국소 ROI를 분리해 보게 함
  - Known 성능 개선은 1-stage backbone, tuning, ROI 보정 단계를 분리해 확인
  - Stage 2 trigger는 confidence만 보지 않고 difficult class 기준을 함께 봄
  - difficult class는 ROI 재확인과 분석 sample 저장 기준으로 추적
  - 남는 잔여 오판은 Unknown 후보 검토와 obj-id map 후속 구조로 관리
  - Unknown은 후보 압축과 현업 검증 결과로 관리
  - 후속 chip-CNN obj-id map은 생성 데이터 개발값으로 분리
```

ㅁ **구현 성과**

[정량적/정성적 성과]

- 기술 지표: **[실전 현업 데이터]** Known CNN -> ROI-YOLO 2-stage는 16-class / 1,500 labeled samples / 4:1 stratified split 기준 weighted F1 0.95입니다. baseline 0.78, backbone 교체 0.87, tuning 0.92, ROI-YOLO 보정 0.95를 분리해 관리했습니다.
- Unknown 운영 결과: **[실전 운영 데이터]** 5일 10,000장 학습 후, 학습에 쓰지 않은 별도 1일치 2,000장에 적용해 13개 후보 group을 만들었고, 현업 확인 결과 7개가 실제 불량으로 판단되었습니다. 이 결과는 정답 label 기반 F1이나 recall 대신, 현업 검토 후보를 줄인 운영 결과로 관리합니다.
- 현업 임팩트: raw log를 이미지와 chip 좌표로 맞춘 뒤 Known 분류와 Unknown 후보 압축까지 같은 기준으로 연결했습니다. Cython 변환 재구성과 palette PNG 저장으로 처리 속도와 저장 부담을 같이 낮춰, 기존 1회 약 48매 조회 중심의 비교 한계를 일 약 2만 장 wafer 이미지 누적 비교와 1시간 주기 처리 흐름으로 확장했습니다. 현업 엔지니어가 전수 확인하기보다, AI가 먼저 분류하거나 후보 group으로 줄인 대상을 우선 검토하는 흐름을 만들었습니다.

**P2. Chip Multi-label Classification 및 FCM-PM 기반 결함 조합 학습**

ㅁ **과제 기본정보**

| 항목 | 내용 |
|---|---|
| 과제명 | Chip Multi-label Classification 및 FCM-PM 기반 결함 조합 학습 |
| 수행기간 | 2025년 3월 ~ 현재 |
| 참여인원 | 2인 (본인, 관리자) |

ㅁ **과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|---:|---|---|---|---|---:|
| 1 | 최호길 | 개인정보 비공개 | 메모리제조센터 QIE그룹 | 현업 single defect 원천 정의, 도메인 확률분포 기반 2-combo 생성, FCM-PM, Pair Mask loss, BCE multi-label 학습 구조, val-margin selection, max-prob gate, 운영성 검토, bit_F1 / FAR 평가 | 80% |
| 2 | 관리자 | 개인정보 비공개 | 관리조직(공식 기록 대조) | 방향성, 일정, 리뷰 매니징 | 20% |

ㅁ **개인별 기여 서술**

[본인이 독자적으로 수행한 핵심 모듈]

- 실제 현장에서는 한 chip에 결함이 두 개 이상 겹칠 수 있지만, 2-combo label을 충분히 확보하고 평가하기 어렵습니다. 본 과제는 그 병목을 풀기 위한 **[현업 defect chip 원천 + 도메인 확률분포 기반 생성/검증]** 구조로 진행했습니다.
- 결함 조합 학습을 위해 실제 현업 single defect chip을 기준 defect set으로 정의했습니다. 이후 bank_boundary, fork, scratch, scratch_rot 4개 single defect를 원천으로 두고, 결함 위치와 강도, Grade 0-7 분포가 현업 defect 양상과 맞도록 2-combo 학습 구조를 만들었습니다. Normal / Invalid / OOD는 false alarm 확인용 negative 평가축으로 분리했습니다.
- Grade 0-7 pixel 값은 결함 강도 의미를 갖기 때문에 값을 평균 내는 Mixup류보다 원래 pixel patch를 보존하는 CutMix 계열이 맞다고 판단했습니다.
- 단순 CutMix만으로는 defect가 잘리거나 background를 defect로 외우는 문제가 남아 Full-Cover Mixup + Pair Mask 구조를 직접 설계했습니다.
- BCE는 multi-label 기본 loss로 사용했습니다. 차별점은 BCE 자체가 아니라, 그 앞단에서 FCM-PM으로 2-combo 학습 신호를 만들고, Pair Mask로 background 오학습을 줄인 뒤, val-margin과 max-prob gate로 false alarm 가능성을 같이 낮춘 구조입니다.
- 4-bag ensemble은 seed/checkpoint 안정성을 확인하기 위한 보조 실험으로 두었습니다. single model 압축 가능성은 후속 검증 항목으로 분리했습니다.
- 검증 누수를 막기 위해 원천 chip 단위 split을 먼저 수행한 뒤, train 원천에서만 FCM-PM 조합을 생성하고 test 원천 chip은 조합 생성 과정에서 배제하는 기준으로 관리했습니다.

ㅁ **문제정의**

| 항목 | 내용 |
|---|---|
| 현장 난제 및 해결 목표 | single defect 형태는 실제 현업 chip에서 상대적으로 정의할 수 있지만, 두 결함이 함께 있는 2-combo chip label은 충분히 모으고 평가하기 어렵습니다. 현업 single defect를 원천으로 2-combo 학습 신호를 만들고, Normal / Invalid / OOD를 결함으로 오인하는 false alarm을 억제하는 구조가 필요했습니다. |
| 기존 방식의 한계 및 AI 도입 배경 | BCE-only는 multi-label 기본 구조이지만 2-combo 검출 안정성과 false alarm을 동시에 만족시키기 어려웠습니다. Focal / ASL처럼 loss만 바꾸는 접근도 반도체 Grade image의 의미 보존 문제를 직접 풀지는 못했습니다. 일반 Mixup은 Grade 0-7의 범주형 의미를 훼손할 수 있었고, random CutMix는 결함 일부가 잘리거나 background를 defect로 외우는 문제가 있었습니다. |
| 기술적 / 환경적 제약 조건 | 실제 2-combo 평가 데이터가 부족한 상태에서, 반도체 defect chip의 모양과 Grade 의미를 보존하면서 조합 데이터를 만들어야 했습니다. controlled benchmark는 16+ class × 약 3,850 chip 규모로 구성했고, 작은 validation set, 2-combo 검출 안정성, Normal / Invalid / OOD false alarm, ensemble 추론 비용, 후속 압축 가능성을 함께 봐야 했습니다. |

ㅁ **기술적 해결 방안**

[본인이 직접 수행한 핵심 로직]

- 데이터: 4개 현업 single defect chip을 원천으로 2-combo multi-hot target을 만들었습니다. 이미지 단순 혼합 대신, chip defect가 갖는 위치, 강도, Grade 0-7 분포가 유지되도록 조합 조건을 잡았습니다. 원천 chip 단위 split을 먼저 수행해 train/test 원천이 섞이지 않게 했고, train 원천에서만 FCM-PM 조합을 생성했습니다. 평가는 16+ class × 약 3,850 chip controlled benchmark에서 single, 2-combo, Normal, Invalid, OOD를 함께 두어 결함을 잘 잡는지와 정상/외부 패턴을 결함으로 오인하는지를 같이 봤습니다.
- 알고리즘: ConvNeXtV2 backbone + sigmoid multi-label head를 사용하고, BCE를 multi-label 기본 loss로 두었습니다. 다만 성능 차이는 BCE 자체보다 FCM-PM sample 구성, Pair Mask loss 제어, val-margin 모델 선택에서 더 크게 갈렸습니다.
- FCM-PM: Full-Cover Mixup은 한 defect가 합성 중 특정 crop에서 사라지지 않게 coverage를 보장합니다. Pair Mask는 유효 결함 영역과 background를 나누어, background가 defect label과 함께 잘못 학습되는 것을 막습니다. 학습 loss는 binary mask M을 두고 `L = Σ M_ij · BCE(y_ij, ŷ_ij)`로 계산해, mask가 1인 유효 영역만 loss에 반영했습니다.
- 모델 선택: 작은 validation set에서는 val_f1이 여러 epoch에서 비슷하게 붙었습니다. 그래서 `val_margin = mean(P positive bits) - max(P negative bits)` 기준을 넣어, positive는 충분히 높고 negative는 낮은 checkpoint를 골랐습니다. epoch-vs-test_f1 Spearman ρ는 val_margin +0.56, val_f1 -0.10으로 갈려, val_margin이 실제 test 흐름과 더 같은 방향으로 움직였습니다. F1만 높고 negative bit가 자주 튀는 모델은 현업 후보로 보기 어렵기 때문입니다.
- 추론 gate: 모든 결함 bit 확률이 애매하게 낮은 입력은 Normal로 강제하는 max-prob gate를 두었습니다. 정상/측정불능/OOD chip이 특정 결함 bit로 잘못 fire 되는 상황을 줄이기 위한 장치이며, 최종 평가는 bit_F1과 FAR를 같이 보도록 잡았습니다.
- Ensemble / KD: 4-bag ensemble은 seed/checkpoint 안정성을 확인하기 위한 보조 실험으로 두었습니다. 다만 4-bag 구조는 추론 비용이 커질 수 있습니다. KD student는 single model 수준의 latency / throughput / parameter 비용까지 보는 압축 후보로 검토 중이며, OOD 포함 Total FAR 기준 때문에 최종 운영 기준으로 확정하지 않았습니다.
- Ablation 관리: Baseline BCE, Focal loss, ASL, CutMix only, CutMix + Pair, FCM-PM best val_f1, FCM-PM best val_margin 순서로 비교했습니다. Ensemble은 보조 안정성 실험, KD는 후속 압축 후보로 분리했습니다. 기존 loss 변경만으로는 부족했고, 반도체 Grade image에서는 defect coverage 보장과 background loss 분리가 함께 필요했습니다.

ㅁ 실제 코드를 제외한 아키텍쳐 설계도, 플로우차트 등으로 기술

```text
[현업 single defect chip A]        [현업 single defect chip B]
label: [1,0,0,0]                   label: [0,1,0,0]
        |                                  |
        v                                  v
 [source chip split]                [source chip split]
 train/test 원천 분리               test 원천은 조합 생성 제외
        |                                  |
        +--------------+-------------------+
                       v
              [FCM-PM sample builder]
              - CutMix 계열: Grade 0-7 원값 보존
              - 도메인 분포: defect 위치/강도/조합 조건 반영
              - Full-Cover: 결함 영역이 합성 중 사라지지 않게 보장
              - Pair Mask: 결함 영역과 background loss 분리
                       |
                       v
        x_mix, y_multi_hot=[1,1,0,0], mask M
                       |
                       v
          [ConvNeXtV2 backbone + sigmoid head]
                       |
                       v
              [BCE multi-label loss + Pair Mask]
              - 결함 영역: positive bit 학습
              - background: defect negative로 과도하게 밀지 않음
                       |
                       v
          [val-margin checkpoint selection]
              positive bit 평균은 높게
              negative bit 최대값은 낮게
                       |
                       v
          [max-prob gate]
              모든 bit가 애매하면 Normal로 강제
                       |
                       v
          [Normal / Invalid / OOD false alarm 확인]
                       |
                       v
          [bit_F1 + FAR 동시 평가]
                       |
                       v
          [4-bag ensemble 보조 안정성 검토]
              seed / gamma / checkpoint 조합으로 흔들림 확인
              latency 비용은 single 대비 4x로 관리
                       |
                       v
          [KD student follow-up check]
              ensemble 판단의 single model 압축 가능성 검토
              latency / throughput / params 운영성 확인
              OOD 포함 Total FAR는 별도 관리

적용 이유
  - 반도체 chip Grade 값의 의미를 유지해야 함
  - 현업 single defect 원천에서 2-combo label 부족을 보완해야 함
  - source chip 단위 split으로 train/test 원천 누수를 막아야 함
  - BCE 자체보다 FCM-PM / Pair Mask / val-margin 조합이 성능을 좌우함
  - 현업 defect 양상과 맞는 확률분포로 조합 평가셋을 만들어야 함
  - 실제 적용 전부터 false alarm 가능성을 같이 봐야 함
  - bit_F1만 높고 FAR가 남는 모델은 운영 후보로 보기 어려움
  - ensemble은 보조 안정성 검토용이고, KD는 OOD FAR까지 확인해야 함
```

ㅁ **구현 성과**

[정량적/정성적 성과]

- 기술 지표: **[현업 defect chip 원천 + 도메인 확률분포 기반 생성/검증]** 기준으로 bit_F1 0.9943 / Total FAR 0.00%를 확인했습니다. 이 지표는 현업 single defect 원천과 반도체 분포 설계가 결합된 FCM-PM 구조에서 2-combo 학습 신호와 false alarm 억제가 함께 작동했음을 보여주는 검증 결과입니다. 원천 chip 단위 split 이후 train 원천에서만 조합을 생성해, 같은 원천 chip이 학습과 평가 조합에 동시에 섞이지 않도록 관리했습니다.

**성능 / 운영성 관리표**

| # | Recipe | bit_F1 | FAR | NI-FAR | OOD-FAR | Latency | Throughput | Params | Note |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | FCM-PM best val_f1 | 0.9652 | 0.15 | 0.00 | 0.62 | 1x | 1x | 1x | F1 기준 checkpoint |
| 2 | FCM-PM best val_margin | 0.9943 | 0.00 | 0.00 | 0.00 | 1x | 1x | 1x | 제출 대표 checkpoint. 전체 bit_F1과 FAR 기준입니다. |
| 3 | Ensemble 4-bag | 0.9615 | 0.00 | 0.00 | 0.00 | 4x | 1/4x | 4x | seed/checkpoint 안정성 확인용 보조 실험. 제출 대표 성과와 분리합니다. |

- 성능 개선 과정은 BCE-only, Focal loss, ASL, CutMix only, CutMix + Pair, FCM-PM, val-margin 순서로 비교했습니다. Ensemble은 seed/checkpoint 안정성 확인용 보조 실험으로 분리했습니다.
- 제출본 표에는 완료 근거가 있는 FCM-PM과 ensemble 결과만 남겼고, loss 변경 및 단순 CutMix 비교값은 내부 ablation 관리 항목으로 분리했습니다.
- 내부 ablation에서는 Pair Mask를 제거했을 때 Normal / Invalid / OOD negative 평가축의 Total FAR이 100%까지 올라가는 운영 부적합 사례를 확인했습니다. 이 결과를 기준으로 FCM-PM의 핵심을 coverage 보장과 background loss 분리의 결합으로 정리했습니다.
- 대표 checkpoint는 전체 bit_F1과 Normal / Invalid / OOD FAR 기준으로 선정했으며, 2-combo 분해 성능은 별도 평가표에서 관리했습니다.
- 제출 본문에서는 val_f1 checkpoint의 2combo 0.9517 확인값과 val_margin checkpoint의 전체 bit_F1 / FAR 균형을 분리해 해석합니다.
- 성능 개선의 핵심은 반도체 defect의 Grade 의미를 보존한 조합 생성, Pair Mask를 통한 background 오학습 차단, val-margin 기반 checkpoint 선택, max-prob gate 기반 FAR 억제였습니다.
- Ensemble은 seed/checkpoint 안정성 확인용 보조 실험으로 두고, KD student는 1x 추론 가능성과 OOD 포함 FAR를 함께 보는 후속 검증 항목으로 분리했습니다.
- 현업 의미: 이 과제는 실제 현업 single defect chip을 출발점으로 삼아, 현업에서 충분히 모으기 어려운 2-combo 결함을 도메인 확률분포 기반 조합으로 학습 가능한 문제로 바꾼 multi-label learning 방법론입니다. wafer 단위 분류를 chip 좌표계의 결함 조합 판단으로 좁히고, P1 후속 chip-CNN obj-id map 개발의 기반으로 연결할 수 있습니다.

**P3. Trend Chart 기반 Anomaly Detection 합성 데이터 및 검증 PoC**

ㅁ **과제 기본정보**

| 항목 | 내용 |
|---|---|
| 과제명 | Trend Chart 기반 Anomaly Detection 합성 데이터 및 검증 PoC |
| 수행기간 | 2026년 1월 ~ 현재 |
| 참여인원 | 3인 (본인, 관리자, 공동 연구자) |

ㅁ **과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|---:|---|---|---|---|---:|
| 1 | 최호길 | 개인정보 비공개 | 메모리제조센터 QIE그룹 | trend episode generator, Region 5종, Noise 3종, anomaly 5종, 정상 산포 기준 최소 이상 강도 보정, 1차 binary gate 검증 PoC 설계/구현 | 70% |
| 2 | 관리자 | 개인정보 비공개 | 관리조직(공식 기록 대조) | 방향성, 일정, 리뷰 매니징 | 20% |
| 3 | 동료 엔지니어 (공동 연구자) | 개인정보 비공개 | 관련 엔지니어 조직(공식 기록 대조) | AI 모델 실행, 데이터 정리, 실험 결과 취합 | 10% |

ㅁ **개인별 기여 서술**

[본인이 독자적으로 수행한 핵심 모듈]

- 본인이 BBD담당 / Overlay담당 / CD담당으로 보던 계측 누락, 희소 구간, 설비 hunting, 산포 확대, drift 양상을 합성 episode 생성 조건과 규칙으로 옮겼습니다.
- 공동 연구자는 AI 모델 실행과 결과 취합을 함께 맡았고, generator rule, anomaly 강도 floor, normal/abnormal gate 기준은 본인이 설계했습니다.
- 이 과제의 초점은 실제 abnormal label이 부족한 상황에서 학습 가능한 trend 데이터를 먼저 만드는 데 있습니다.

ㅁ **문제정의**

| 항목 | 내용 |
|---|---|
| 현장 난제 및 해결 목표 | L1 trend는 단순 threshold만으로 판단하기 어렵습니다. spec-in 범위 안의 미세 drift, 산포 확대, context mismatch는 사람이 chart를 보며 판단하는 경우가 많습니다. 본 과제의 목표는 현업 판단 기준을 generator rule로 옮겨 AI gate 검증을 시작할 수 있는 데이터 기반을 만드는 것입니다. |
| 기존 방식의 한계 및 AI 도입 배경 | 실제 abnormal label을 충분히 모으기 어렵고, label이 부족한 상태에서 모델만 키우면 데이터 편향을 먼저 학습할 수 있습니다. 먼저 현업 판단 기준이 반영된 생성 데이터가 필요했습니다. |
| 기술적 / 환경적 제약 조건 | 계측 밀도 차이, missing/thin region, 설비 산포, hunting, 정상 outlier와 약한 이상 사이의 경계를 함께 맞춰야 했습니다. 본인이 만든 rule로 생성한 데이터의 성능이 과대해 보일 수 있으므로, 합성 test 성능은 실제 현업 trend log 성능과 분리해 해석해야 했습니다. |

ㅁ **기술적 해결 방안**

[본인이 직접 수행한 핵심 로직]

- 데이터: normal 5,000건과 anomaly 5종 각 1,000건으로 총 10,000 scenarios를 만들고 train / validation / test = 70 / 15 / 15로 나누었습니다.
- Generator rule: Region은 dense / sparse / very_sparse / thin / missing 5종, Noise는 Gaussian / Laplacian / Correlated 3종, anomaly는 mean_shift / standard_deviation / spike / drift / context 5종으로 나눴습니다.
- 도메인 반영: BBD담당 / Overlay담당 / CD담당으로 보던 정상 산포와 설비 변동을 기준으로, 약한 anomaly가 정상처럼 묻히지 않도록 minimum floor를 두었습니다. 반대로 normal outlier가 과하게 abnormal처럼 보이면 noise 조건을 다시 조정했습니다.
- 검증 모델: 1D trend를 224x224 chart image로 렌더링하고, ConvNeXtV2-Tiny 기반 normal/abnormal gate로 학습 가능성을 확인했습니다. p_normal이 0.9를 넘는 경우만 normal로 통과시키는 기준을 두어, 불량을 normal로 보내는 FN을 줄이는 쪽에 우선순위를 뒀습니다. type classifier는 anomaly rule이 헷갈리는 지점을 보는 보조 진단으로 두었습니다. 합성 test에서 나온 높은 F1은 generator rule과 label 정의가 구분 가능한 신호를 만들었는지 보는 1차 확인값으로 해석했습니다.

ㅁ 실제 코드를 제외한 아키텍쳐 설계도, 플로우차트 등으로 기술

```text
[본인 담당 업무에서 보던 trend 판단]
  - BBD담당: 계측 누락, 희소 region, baseline 흔들림
  - Overlay담당: 위치 기준 차이, context mismatch, drift
  - CD담당: 산포 확대, spike, 미세 mean shift
        |
        v
[Synthetic trend episode generator]
  Region : dense / sparse / very_sparse / thin / missing
  Noise  : Gaussian / Laplacian / Correlated
  Anomaly: mean_shift / standard_deviation / spike / drift / context
  Floor  : 정상 산포에 묻히는 약한 이상은 최소 강도 보정
        |
        v
[1D trend -> 224x224 chart image]
        |
        v
[Stage 1 normal/abnormal gate]
  model: ConvNeXtV2-Tiny baseline
  loss : FocalLoss 기반 binary classification
  rule : p_normal > 0.9일 때만 normal 통과
        |
        v
[Error feedback]
  FN: anomaly가 너무 약하거나 정상 산포에 묻혔는지 확인
  FP: normal outlier / hunting 조건이 과한지 확인
  Type confusion: drift, mean_shift, spike, standard_deviation rule 재점검

운영 적용 기준
  - 1차 gate는 불량을 normal로 통과시키지 않는 것이 우선
  - 2차 type은 원인 분석 보조로 분리
  - 오분류는 generator rule을 고치는 근거로 사용
```

ㅁ **구현 성과**

[정량적/정성적 성과]

- 기술 지표: **[합성 trend chart, PoC]** train 7,000 + validation 1,500 + test 1,500 = 총 10,000 scenarios입니다. test 1,500건 기준 1차 binary gate는 normal_threshold=0.9에서 TN/FN/FP/TP = 746/1/4/749, Binary F1 0.9967, Abnormal Recall 0.9987입니다. 이 값은 합성 rule 내부 검증값이며, 실제 현업 trend log 성능으로 제출하지 않습니다.
- 결과 해석: 이 수치는 현업 trend data 일반화 성능과 분리해, 생성 rule이 정상/이상 구분 신호를 담고 있는지 보기 위한 결과로 관리합니다. 1차 FN은 standard_deviation 1건, normal FP는 4건으로 확인되어, 산포 확대 rule과 normal outlier 조건을 어느 방향으로 보정해야 하는지 확인할 수 있었습니다.
- 후속 적용 방향: 실제 abnormal label이 부족한 상태에서도 AI gate를 검증할 수 있는 데이터 생성 기반을 만들었습니다. 본인이 담당 업무에서 보던 trend 판단을 생성 조건과 규칙으로 옮긴 것이 과제의 중심이며, 다음 단계는 실제 현업 trend log와 hard-normal log를 별도 hold-out으로 모아 FN/FP를 다시 보는 것입니다. 실전 적용 전 단계에서는 FN을 우선 줄이는 1차 선별 구조로 검증하고 있습니다.
