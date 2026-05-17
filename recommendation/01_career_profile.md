## 1. 기술 분야

| 기술 분야 | 세부 역량 |
|---|---|
| Computer Vision | Failbit Map wafer image classification, ROI object detection, chip-level defect classification |
| Self-Supervised Representation Learning | Contrastive learning, embedding learning, HDBSCAN 기반 Unknown 후보 group 압축 |
| Multi-label Image Classification | FCM-PM (Full-Cover Mixup + Pair Mask loss), val_margin checkpoint selection, sigmoid multi-label head (BCE) |
| Synthetic Data Engineering | 추가 생성 chip 데이터 기반 2-combo 조합 생성, trend episode generator, Normal / Invalid / OOD 평가셋 설계 |
| Model Optimization / Evaluation | hyperparameter tuning, threshold / max-prob gate, FAR 평가, Spearman 기반 checkpoint 기준 검증 |
| AI Data Pipeline | EDS raw log 변환, Cython 기반 hex-to-grade 가속, palette PNG, chip positions JSON, 운영 뷰어 연동 |

## 2. 업무경력

ㅁ **P1. Failbit Map 이미지 데이터 생성 및 Known 불량 및 Unknown 불량 분류 시스템**

(1) **과제 개요 및 규모 / 담당 역할 / 수행 업무 / 성과**

- 수행기간: 2024년 10월 ~ 현재
- 담당 역할: 본인 60% / 현업 엔지니어 20% / 관리자 20%
- 본인은 EDS Test raw log를 Failbit Map 이미지와 chip positions JSON으로 바꾸는 fail-map 파이프라인을 설계하고 구현했습니다. hex 값을 Grade 0-7로 푸는 변환 루프는 Cython으로 재구성해 약 100배 가속을 확인했고, 32색 palette PNG 저장으로 용량을 약 75% 줄였습니다.
- 이 구조를 운영 뷰어와 연결해 기존 1회 약 48매 조회 중심의 비교 한계를 일 약 2만 장 wafer 이미지 누적 비교와 1시간 주기 처리 흐름으로 확장했습니다. fail-map은 이미지 생성 파이프라인, mapviewer는 조회 / 검색 운영 뷰어로 역할을 나누어 관리했습니다.
- Known 불량 분류는 CNN 1-stage 결과를 그대로 확정하지 않고, center / edge처럼 혼동이 잦은 class와 low-confidence sample을 ROI-YOLO로 재확인하는 2-stage 구조로 설계했습니다. ROI 재확인 기준은 confidence만 보지 않고, class별 precision / recall로 식별한 difficult class 기준을 함께 두었습니다.
- **[실전 현업 데이터]** Known CNN -> ROI-YOLO 2-stage는 16-class / 1,500 labeled samples / 4:1 stratified split 기준 weighted F1 0.95입니다. 단계별로는 baseline 0.78, backbone 교체 0.87, tuning 0.92, ROI-YOLO 보정 0.95로 분리해 관리했습니다.
- Unknown 불량은 정답 label이 없는 운영 데이터 특성에 맞춰, contrastive embedding과 HDBSCAN으로 후보 group을 줄이고 현업 엔지니어가 검토 가능한 단위로 넘기는 구조로 잡았습니다. **[실전 운영 데이터]** 5일 10,000장 학습 후, 학습에 쓰지 않은 별도 1일치 2,000장에 적용해 13개 후보 group을 만들었고, 현업 확인 결과 7개가 실제 불량으로 판단되었습니다.
- 후속으로는 ROI-YOLO의 class 확장 비용을 줄이기 위해 **[추가 생성 chip 데이터, 개발 중]** CNN -> chip-CNN obj-id map 구조를 별도 검토하고 있습니다. 이 수치는 실전 2-stage 성과와 섞지 않고 분리해 관리합니다.

(2) **과제 관련 도메인 / AI 기술 / 모델 / 방법론**

- 도메인은 DRAM EDS Test Grade 0-7, Failbit Map zone pattern, wafer-level defect distribution, 대량 wafer 이미지 운영 파이프라인입니다.
- ConvNeXtV2는 운영 inference 비용과 국소 결함 민감도를 함께 보고 선정했습니다. MaxViT와 동일한 1-stage weighted F1 0.87을 보이면서 parameter 약 26%, FLOPs 약 39%가 낮아 일 단위 대량 inference 비용에서 유리했습니다. 결함이 특정 zone이나 국소 chip 영역에 몰리는 경우가 많아, sliding-window 기반 CNN 계열의 지역 특징 추출이 본 과제에 더 맞다고 판단했습니다.
- AI 설계는 wafer-level CNN, ROI-YOLO cascade, contrastive embedding, HDBSCAN clustering을 하나의 운영 흐름으로 묶은 구조입니다. 핵심은 모델 하나의 정확도보다 raw log 변환, 이미지 / 좌표 정합성, Known 불량 분류, Unknown 불량 후보 압축, 현업 검증까지 이어지는 현업 개선 흐름을 만든 점입니다.

ㅁ **P2. Chip Multi-label Classification 및 FCM-PM 기반 결함 조합 학습**

(1) **과제 개요 및 규모 / 담당 역할 / 수행 업무 / 성과**

- 수행기간: 2025년 3월 ~ 현재
- 담당 역할: 본인 80% / 관리자 20%
- 본 과제는 **[현업 defect chip 원천 + 도메인 확률분포 기반 생성/검증]** 구조로, 현업에서 충분히 모으기 어려운 2-combo 결함 조합을 학습 가능한 문제로 바꾸는 과제입니다. controlled benchmark는 16+ class × 약 3,850 chip 규모로 구성했습니다.
- 본인은 bank_boundary, fork, scratch, scratch_rot 4개 single defect를 원천으로 정의하고, train / test 원천 chip을 먼저 split했습니다. 2-combo와 Pair Mask 조합은 train 원천에서만 생성하고, test 원천 chip은 조합 생성 과정에서 배제해 원천 chip 단위 누수를 막았습니다.
- 일반 Mixup은 Grade 0-7 pixel 값의 의미를 흐릴 수 있어 배제했습니다. CutMix 계열로 원값을 보존하되, random CutMix에서 defect가 잘리는 문제와 background를 defect로 외우는 문제를 풀기 위해 Full-Cover Mixup과 Pair Mask를 결합한 FCM-PM 구조를 적용했습니다.
- Pair Mask loss는 유효 결함 영역만 학습에 반영하도록 `L = sum(M_ij * BCE(y_ij, yhat_ij))` 형태로 두었습니다. 차별점은 BCE 자체가 아니라, FCM-PM으로 2-combo 학습 신호를 만들고 Pair Mask로 background 오학습을 줄인 뒤, val_margin과 max-prob gate로 false alarm 가능성을 같이 낮춘 구조입니다.
- **[현업 defect chip 원천 + 도메인 확률분포 기반 생성/검증]** 기준 대표 모델은 bit_F1 0.9943 / Total FAR 0.00%입니다. Pair Mask 제거 시 Normal / Invalid / OOD negative 평가축의 Total FAR이 100%까지 올라가는 사례를 확인해, background loss 분리가 필요한 이유를 ablation으로 확인했습니다.
- 4-bag ensemble은 seed / checkpoint 안정성 확인용 보조 실험으로 두었습니다. KD student는 1x 추론 가능성과 OOD 포함 FAR를 보는 후속 압축 후보로 분리했습니다.

(2) **과제 관련 도메인 / AI 기술 / 모델 / 방법론**

- 도메인은 반도체 chip Grade 0-7 양자화 이미지, multi-label defect co-occurrence, 2-combo label 부족, Normal / Invalid / OOD false alarm 억제입니다.
- 모델은 ConvNeXtV2 backbone + sigmoid multi-label head를 사용했습니다. 학습은 BCE를 기본 loss로 두되, FCM-PM sample builder, Pair Mask loss, val_margin checkpoint selection, max-prob gate, bit_F1 / FAR 동시 평가를 함께 구성했습니다.
- 작은 validation set에서는 val_f1이 여러 epoch에서 비슷하게 붙어 best epoch가 흔들렸습니다. 그래서 `val_margin = mean(P positive bits) - max(P negative bits)`를 사용했습니다. epoch-vs-test_f1 Spearman rho는 val_margin +0.56, val_f1 -0.10으로 갈려, val_margin이 실제 test 흐름과 더 같은 방향으로 움직였습니다.
- 성능 개선의 핵심은 추가 생성 chip 데이터에서 2-combo 부족 문제를 보완하고, Grade 의미 보존, defect coverage 보장, background loss 분리, false alarm 기준의 checkpoint 선택을 하나로 묶은 데 있습니다.

ㅁ **P3. Trend Chart 기반 Anomaly Detection 합성 데이터 및 검증 PoC**

(1) **과제 개요 및 규모 / 담당 역할 / 수행 업무 / 성과**

- 수행기간: 2026년 1월 ~ 현재
- 담당 역할: 본인 70% / 관리자 20% / 동료 엔지니어 (공동 연구자) 10%
- 본 과제는 실제 abnormal trend label이 부족한 상황에서, 현업 trend 판정 경험을 generator parameter로 코드화해 학습 가능한 trend episode 데이터를 만드는 과제입니다. 데이터 생성과 1차 학습 가능성 확인을 목표로 두었습니다.
- 본인은 BBD담당 / Overlay담당 / CD담당으로 쌓은 trend 분석 경험을 바탕으로 Region 5종, Noise 3종, anomaly 5종을 설계했습니다. Region은 계측 밀도 차이와 missing / thin region을, anomaly는 산포 확대 / spike / drift / context mismatch를 episode parameter로 옮겼고, 약한 이상이 정상 산포에 묻히지 않도록 최소 이상 강도 보정 기준을 넣었습니다.
- 데이터는 normal 5,000건과 anomaly 5종 각 1,000건으로 총 10,000 scenarios를 구성하고, train / validation / test = 70 / 15 / 15로 나눴습니다. 1차 binary gate 검증에서는 synthetic test 기준 Binary F1 0.9967, Abnormal Recall 0.9987을 확인했습니다.
- 이 수치는 실제 현업 trend log 일반화 성능과 분리해 해석합니다. 본인이 만든 generator rule이 정상 / 이상 구분 신호를 학습 가능한 형태로 담고 있는지 확인한 PoC 결과입니다.

(2) **과제 관련 도메인 / AI 기술 / 모델 / 방법론**

- 도메인은 BBD / Overlay / CD trend chart, spec-in drift, 산포 확대, 설비 hunting, spike, context mismatch입니다.
- AI 방법론은 synthetic time-series episode generation, chart image rendering, binary anomaly gate, type classifier 보조 진단입니다.
- P3의 핵심은 본인이 현업에서 trend chart를 판정하며 쌓은 기준을 parameter와 label rule로 옮겨, 실제 abnormal data가 부족한 조건에서도 AI 검증을 시작할 수 있는 데이터 기반을 만든 점입니다.
