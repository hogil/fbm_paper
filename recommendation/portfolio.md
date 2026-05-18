## 1. AI 프로젝트 수행 전체이력

| 기간 | 과제명 | 리딩 규모 | 담당업무 | 과제관리 | 설계 | 개발비중 |
|------|--------|-----------|----------|----------|------|----------|
| 2024년 10월 ~ 현재 | P1. Failbit Map Known & Unknown 불량 분석 아키텍처 | 3인 협업, 본인 60% 리딩. DRAM 전제품 라인 양산 운영, 일 약 2만 장 wafer 처리 | 본인이 FBM raw log 적재 / Cython 파싱 / palette PNG / chip 좌표 JSON 생성 모듈을 구성하고, 운영 뷰어와 연결한 뒤 Known 불량 및 Unknown 불량 AI 모델을 설계 / 학습 / 검증까지 했습니다. | 20% | 35% | 45% |
| 2025년 3월 ~ 현재 | P2. Chip Multi-label Classification (FCM-PM, val_margin) | 2인 PoC, 본인 80% 리딩. 16+ class × 약 3,850 chip controlled synthetic benchmark | chip single / 2-combo 합성, Pair Mask loss masking, FCM-PM 설계, val_margin 기반 best-model 선택, 대표 모델 검증까지 직접 진행했습니다. | 20% | 40% | 40% |
| 2026년 1월 ~ 현재 | P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC | 3인 PoC, 본인 70% 리딩. normal 3,500 + abnormal 3,500 = 총 7,000개 trend sample 구성 | BBD / Overlay / CD 담당 **9년** trend 판정 경험을 바탕으로 계측 밀도와 noise 분포로 normal baseline 을 합성하고, mean shift / standard deviation / spike / drift / context 5종 anomaly 를 더해 abnormal sample 을 생성하는 episode generator 를 코드화했습니다. | 20% | 45% | 35% |

## 2. 대표 과제 상세 기술서

**ㅁ P1. Failbit Map Known & Unknown 불량 분석 아키텍처**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Failbit Map Known & Unknown 불량 분석 아키텍처 |
| 수행기간 | 2024년 10월 ~ 현재 |
| 참여인원 | 본인 / 현업 엔지니어 / 관리자 |

**P1 핵심 수치 요약**

- Cython hex-to-grade 변환 재구성으로 데이터 처리 속도를 약 **100배** 향상시켰습니다.
- 32색 palette indexed PNG 저장으로 이미지 저장 용량을 약 **75%** 줄였습니다.
- 운영 뷰어 조회 한도를 1회 약 **48매** → **수천 wafer 초고속 조회**로 확장해 대량 wafer 동시 비교가 가능해졌습니다.
- 적재 흐름은 일 약 **2만 장 wafer / 1시간 주기** 누적으로 운영 중입니다.
- Known 2-stage 는 weighted F1 **0.95**, Unknown 검출은 실제 운영 환경에 다수의 noise group 이 존재해 정량 metric 의 정합성이 낮다고 판단해, 학습한 model 을 실전 데이터 2,000 장에 직접 돌려 추출한 13개 후보 group 을 현업이 확인한 결과 **7개가 실제 불량으로 입증**되어 운영 검출력이 확인되었습니다.
- chip-CNN object-id map 과 Unknown synthetic benchmark metric 은 생성 데이터 기반으로 개발 중인 트랙이라 대표 성과 (실전 현업 데이터 기반) 와 분리해 두었습니다.

**ㅁ 과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|----|------|---------|------|------|--------|
| 1 | 최호길 | 개인정보 비공개 | 메모리제조센터 QIE그룹 | FBM 데이터 파이프라인, 운영 뷰어 연동, Known CNN → ROI-YOLO 2-stage, Unknown contrastive 학습, 후속 chip-CNN obj-id map 보정 구조의 설계 / 구현 주도 | 60% |
| 2 | 현업 엔지니어 | 개인정보 비공개 | 관련 현업부서 (공식 기록 대조) | 아이디어 발의, Failbit Map 의미 및 불량 분석 교육 | 20% |
| 3 | 관리자 | 개인정보 비공개 | 관리조직 (공식 기록 대조) | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

**[본인이 독자적으로 수행한 핵심 모듈]**

- **과제 내에서 타 구성원과 차별화되는 본인만의 구체적 담당 영역**: 본인은 wafer 단위 분석 경험을 바탕으로 현업 엔지니어 교육을 거쳐 Failbit Map 의미와 분석 흐름을 확보한 뒤 AI 설계에 착수했습니다. raw log → wafer 이미지 변환 / 저장 / 조회 파이프라인 (fail-map) 과 사내 운영 뷰어 web app 을 직접 설계 / 구현했고, 그 위에 ConvNeXtV2 wafer-level classifier + ROI YOLO cascade 보정 + self-supervised contrastive embedding + HDBSCAN grouping 을 묶어 양산 운영 시스템을 구성했습니다. 후속 chip-CNN object-id map (Stage 2 ROI-YOLO 자리 대체 후보) 도 본인이 직접 설계 / 구현 중입니다.

- **본인의 기술적 해결책이 과제 성패에 미친 영향**: wafer 한 장 약 1,000만 cell 의 hex 값을 Grade 0-7 로 풀어내는 변환 루프를 Cython 으로 재구성해 약 **100배** 가속을 확보했고, 32색 palette indexed PNG 양자화로 저장 용량 약 **75%** 절감을 같이 묶어 **일 약 2만 장 / 1시간 주기** 양산 운영 적재 흐름을 가능하게 했습니다. **[실전 현업 데이터 — Known]** baseline **0.78** (ImageNet 사전학습 일반 CNN) → **0.87** (ConvNeXtV2 backbone 교체) → **0.92** (Optuna Bayesian hyperparameter sweep + LinearLR warmup / CosineAnnealing LR schedule) → **0.95** (wafer 신뢰도가 낮은 difficult sample 만 ROI YOLO 로 보내는 2-stage cascade 결합) 단계별 향상으로 weighted F1 **0.95** 까지 도달했습니다. **[실전 현업 데이터 — Unknown]** ConvNeXtV2 backbone 을 본 도메인 wafer 이미지로 Task-Adaptive Pretraining (TAPT) 한 뒤, Global InfoNCE + Queue (size 16384) + negative similarity filter (cos > 0.72) + Local InfoNCE (grid36_full, window=4) 를 결합해 wafer 전역과 sub-pattern 까지 같이 학습하도록 만들었습니다. 그 결과 운영 단계에서 13개 후보 group 중 **7개 불량 확인**으로 검출력이 검증되었습니다. **[추가 생성 chip 데이터, 개발 중]** chip-CNN object-id map 은 이미지 생성 시 chip 좌표를 같이 만들어 두어 crop 추출이 단순하고, 약 256x256 crop 안에서는 불량 비율이 wafer 전체보다 커서 chip-CNN 분류가 빠르게 수렴합니다 (val_f1 **0.9946**). 그 결과를 wafer 좌표계로 합쳐 전체 F1 도 함께 향상되는 구조입니다. **[Unknown 추가 생성 데이터, 개발 중]** 현업 데이터와 유사하게 구성한 synthetic benchmark 에서 Global InfoNCE + MoCo Queue (size 4096) + NV-Retriever (negative similarity 임계 0.72) + NeCo neighbor consistency 4-tool 결합 + noise 임계 τ=0.5 후처리 recipe 로 신규 class capture **1.000** (38/38) / noise **0.00%** / Completeness **0.9938** / Silhouette **0.781** 까지 측정했습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | (1) wafer Failbit Map 을 한 번에 약 48매까지만 느리게 조회할 수 있어 대량 wafer 분석이 어렵습니다. (2) wafer 당 약 1,000만 cell Grade map 을 분석 엔지니어가 수작업으로 판정해야 합니다. |
| 기존 방식의 한계 | hex → Grade 변환을 Python loop 로 돌아 wafer 한 장 처리에 시간이 오래 걸렸고, 메모리 제약으로 동시 조회가 약 48매로 묶여 제품 / 시간 단위 누적 분석이 어려웠습니다. |
| 기술적 / 환경적 제약 | Known 측은 학습 label 이 16 class / 1,500 장 으로 제한되어 supervised 학습 데이터가 부족하고, Unknown 측은 운영 환경에 다수의 noise group 이 존재해 supervised 정량 metric 의 정합성이 낮아 쓸 수 없습니다. 운영 측은 일 약 2만 장 wafer 와 1시간 주기 적재 throughput, 운영 뷰어 응답성, AI 센터 GPU 할당 한도가 동시에 묶여 모델 / 적재 / 조회 비용을 같이 줄여야 하는 조건이었습니다. |

**ㅁ 기술적 해결 방안**

본인이 직접 잡은 P1 end-to-end 파이프라인은 raw log → wafer 이미지 변환 → 좌표 JSON → 운영 뷰어 노출 → Known 분류 / Unknown 검출 → 현업 검증 까지입니다. 단계별 모듈은 아래와 같습니다.

```
+------------------------------------------------------------------------------+
|  [SOURCE]  EDS Test raw log (Failbit hex per Memory Cell Block)              |
|            wafer ~10M cells, all DRAM product lines                          |
+------------------------------------------------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------------+
|  [PIPELINE]  fail-map conversion module (designed/implemented by author)     |
|  - Cython hex -> Grade(0..7) loop  -> ~100x speed-up                         |
|  - 32-color palette indexed PNG    -> ~75% storage reduction                 |
|  - output wafer image: 6400 x 6400 palette PNG (8-bit, 32 colors)            |
|  - chip grid 32 x 32 (1,024 chips / wafer, 200 x 200 px per chip)            |
|  - chip positions JSON -> coordinates fixed (reused by chip-CNN downstream)  |
+------------------------------------------------------------------------------+
                                    |
                                    v
+------------------------------------------------------------------------------+
|  [VIEWER]  internal viewer Web App (bulk wafer query + analysis utilities)   |
|  - SAML SSO + in-house authentication integration                            |
|  - ~20,000 wafers / day, 1-hour batch interval                               |
|  - replaces manual ~48-wafer-per-query workflow with bulk + analysis tools   |
+------------------------------------------------------------------------------+
                                    |
                +-------------------+-------------------+
                v                                       v
+--------------------------------------+   +--------------------------------------+
|  Known branch                        |   |  Unknown branch                      |
|  (16 registered classes)             |   |  (self-supervised contrastive)       |
+--------------------------------------+   +--------------------------------------+
|  Stage 1: ConvNeXtV2 wafer           |   |  - ConvNeXtV2 backbone with TAPT     |
|           classifier                 |   |  - Global InfoNCE + Queue (16384)    |
|       v   confidence < gate          |   |    + NEG sim filter (cos > 0.72)     |
|  Stage 2: ROI YOLO refinement        |   |    + Local InfoNCE (grid36, win=4)   |
|           (chip bbox + class vote)   |   |  - HDBSCAN clustering                |
|  ->       weighted F1 0.95           |   |  - 13 candidate groups -> 7 real     |
|                                      |   |    failures confirmed on-site        |
+--------------------------------------+   +--------------------------------------+
                |                                       |
                +-------------------+-------------------+
                                    v
+------------------------------------------------------------------------------+
|  [REVIEW]  viewer overlays results + on-site engineer verification loop      |
|  - new failure candidates added to catalog                                   |
|  - Known classifier training samples refreshed                               |
+------------------------------------------------------------------------------+
```

**[데이터]** 위 파이프라인의 [SOURCE] / [PIPELINE] 두 단계에 해당합니다. raw EDS Test log (wafer 당 약 1,000만 cell) 의 Failbit hex 표현을 Cython 변환 루프로 약 100배 가속해 Grade(0-7) 로 양자화합니다. **본 wafer image 는 자연 현상의 다양한 색채 이미지가 아닌 EDS Test 의 8단계 이산 측정값** 이라 32색 palette indexed PNG 로 **무손실** 양자화가 가능했고, 이 도메인 특성을 활용해 저장 용량을 약 **75%** 절감했습니다. 결과로 6400×6400 wafer 이미지 + 32×32 chip grid (1,024 chip / wafer, chip 당 200×200 pixel) + chip positions JSON 이 산출되고, chip positions JSON 은 Stage 2 ROI YOLO 와 후속 chip-CNN object-id map 입력 좌표로 그대로 재사용됩니다.

**[알고리즘]** 모델 선택과 결합 구조는 본 과제 데이터 특성에 맞춰 다음과 같이 결정했습니다.

**(1) Stage 1 Backbone — ConvNeXtV2 선택과 fine-tune 설계**

먼저 Transformer 와 CNN 을 같은 split 에서 비교했습니다.

- **도메인 판단**: ViT, Swin 같은 전역 attention 기반 backbone 은 wafer 전체 구조를 보는 데 강합니다. 다만 본 과제의 결함은 특정 zone 이나 국소 chip 영역에 몰리는 경우가 많아, CNN 계열의 local receptive field 와 계층적 feature extraction 이 더 어울린다고 판단했습니다 (자문: 연세대학교 인공지능학과 전해곤 교수).
- **비교 결과**: 동일 4:1 stratified split 에서 Optuna sweep 으로 hyperparameter 를 정렬한 뒤 측정했습니다. 결과는 ViT 0.81 / Swin 0.84 / EffNetV2 0.85 / MaxViT 0.87 / ConvNeXtV2 0.87 입니다.
- **최종 선택**: ConvNeXtV2 는 MaxViT 와 동일한 F1 0.87 을 유지하면서 파라미터 26% (119.5M → 88.6M), FLOPs 39% (74.2G → 45.1G) 감소가 따라와 양산 inference 비용 측면에서 최종 backbone 으로 채택했습니다.

**(2) Stage 2 ROI 보정 — cascade gate 와 보정 결정 로직**

Stage 1 만으로는 center 영역처럼 결함이 겹치는 영역의 class 들을 잘 분류하지 못하는 한계가 남아, wafer 신뢰도가 낮은 difficult sample 만 Stage 2 (ROI YOLO) 로 다시 보내도록 cascade gate 를 두었습니다. 신뢰도가 임계값 이상인 wafer 는 Stage 2 를 skip 하기 때문에 throughput 부담 없이, confidence 가 낮은 sample 만 다시 분류해 정확도를 향상시키는 구조입니다.

| Stage 1 (raw wafer) | Stage 2 ROI 영역 | Stage 2 chip 단위 box + class |
|:-------------------:|:----------------:|:-----------------------------:|
| <img src="./figures/wafer_center_scratch.png" height="240" /> | <img src="./figures/p1_roi_crop_real.png" height="240" /> | <img src="./figures/p1_chip_yolo_box_real.png" height="240" /> |

좌측 raw wafer 는 Stage 1 wafer-level CNN 만 보면 비슷한 형상의 class 로 오인되는 사례입니다. Stage 2 ROI YOLO 가 chip 단위 box 와 class 라벨을 다수 출력하고, 그 분포 majority 로 다시 정확한 class 로 잡아주는 구조입니다.

**(3) 후속 보정 — chip-CNN object-id map 재구성 (개발 중)**

ROI-YOLO 는 chip 위치를 모르는 상태에서 다수의 후보 bounding box 를 생성한 뒤 선별하는 방식이라 메모리 / 추론 속도 / 정확도 모두에 부담이 누적됩니다. chip-CNN 은 이미지 생성 시 같이 만들어 둔 chip 좌표 자리에서 crop 해서 만들어낸 chip 이미지를 classification 만 하면 되고, 작은 chip 이미지 대비 failure 영역이 커서 **정확도가 더 높고 추론도 더 빠르며** (chip 단위 정확도 0.9872 / 0.9838), 새 결함 class 가 추가될 때도 chip crop 분류 라벨만 추가하면 되어 class 확장 부담이 가볍습니다. 이 점을 살려 Stage 2 ROI-YOLO 자리를 chip-CNN object-id map 으로 대체하는 후속 모듈을 개발 중입니다 (val_f1 **0.9946** / test_f1 0.9872 / 5-seed 평균 0.9838 ± 0.0092).

<table>
  <thead>
    <tr>
      <th colspan="2" align="center">raw wafer map</th>
      <th colspan="2" align="center">chip-CNN obj-id map</th>
    </tr>
    <tr>
      <th align="center">center 결함 (class A)</th>
      <th align="center">center 결함 (class B)</th>
      <th align="center">center 결함 (class A)</th>
      <th align="center">center 결함 (class B)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td width="25%" align="center"><img src="./figures/AAN585_00P_18_20260501_010000_97.6_2_EE_NORMAL_raw.png" style="width:100%; height:auto; aspect-ratio:1/1; object-fit:contain" /></td>
      <td width="25%" align="center"><img src="./figures/ACZ452_00P_14_20260501_010000_97.6_2_PT_NORMAL_raw.png" style="width:100%; height:auto; aspect-ratio:1/1; object-fit:contain" /></td>
      <td width="25%" align="center"><img src="./figures/AAN585_00P_18_20260501_010000_97.6_2_EE_NORMAL_objid.png" style="width:100%; height:auto; aspect-ratio:1/1; object-fit:contain" /></td>
      <td width="25%" align="center"><img src="./figures/ACZ452_00P_14_20260501_010000_97.6_2_PT_NORMAL_objid.png" style="width:100%; height:auto; aspect-ratio:1/1; object-fit:contain" /></td>
    </tr>
  </tbody>
</table>

chip-CNN object-id map 의 내부 흐름은 아래 식으로 정리했습니다.

```
c_{u,v} = crop(x, pos_{u,v})
q_{u,v} = softmax(h_phi(c_{u,v}))
M_obj(u,v) = argmax_k q_{u,v,k}
```

세 줄을 일상 표현으로 풀면 다음과 같습니다 (결함 class 개수를 `K` 로 두고, 예를 들어 K=4 면 결함 class 4 종이라는 뜻).

- 첫째 줄 `c_{u,v} = crop(x, pos_{u,v})` — wafer 이미지 `x` 에서 (u,v) 위치의 chip 영역만 잘라 약 256x256 작은 이미지로 만듭니다 (`crop` = 잘라내기).
- 둘째 줄 `q_{u,v} = softmax(h_phi(c_{u,v}))` — 잘라낸 chip 이미지를 chip-CNN (`h_phi`) 에 넣으면 결함 class K 종 각각에 대한 점수가 K 개 나옵니다. 이 점수를 `softmax` 로 합 1.0 의 확률값으로 바꿉니다. 예를 들어 K=4 일 때 결과는 `(0.85, 0.10, 0.03, 0.02)` 처럼 "class 1 일 확률 0.85, class 2 일 확률 0.10, class 3 일 확률 0.03, class 4 일 확률 0.02" 분포가 됩니다.
- 셋째 줄 `M_obj(u,v) = argmax_k q_{u,v,k}` — 위에서 만든 K 개 확률값 중 가장 큰 값을 갖는 class 번호 `k` 를 하나 고르고 (`argmax` = 가장 큰 값의 위치를 골라준다는 뜻), 그 번호를 (u,v) 위치 chip 의 최종 결함 class 로 둡니다. wafer 전체 32×32 chip 위치마다 이 class 번호 하나씩 채우면 `M_obj` 라는 **32×32 결함 지도**가 만들어집니다. 각 chip 을 하나의 "object" 로 보고 그 object 의 ID (class 번호) 를 격자에 박아 둔 형태라 **object-id map** 이라고 부릅니다.

이 결함 지도가 그대로 Stage 2 의 출력입니다 (수식 `p_chip_obj(y | crop(x))` 도 같은 뜻 — "chip crop 이미지를 입력했을 때 결함 class `y` 일 확률" 을 chip 마다 확정해 둔 것이고, 통계 용어로 posterior 라고 부릅니다). 이 출력값이 기존 Stage 2 ROI-YOLO 자리를 그대로 대체할 수 있도록 모듈을 구성했습니다.

**[최적화]** Known 2-stage 의 성능은 실전 현업 데이터 (16 class / 1,500 labeled / 4:1 stratified split) 위에서 baseline 부터 단계별로 다음과 같이 향상시켰습니다.

- **baseline**: 일반 ImageNet 사전학습 CNN 으로 시작한 1차 학습이 weighted F1 **0.78** 정도였습니다. 16 class 중 center 영역처럼 결함이 겹치는 영역의 class 들이 서로 헷갈리는 사례가 가장 컸습니다.
- **backbone 교체**: ViT / Swin / EffNetV2 / MaxViT / ConvNeXtV2 를 동일 split 에서 비교한 뒤, 본 과제 결함이 국소 영역에 몰리는 특성에 맞는 ConvNeXtV2 로 교체해 **0.87** 까지 향상시켰습니다.
- **Optuna hyperparameter 정렬 + LR schedule**: learning rate, weight decay, augmentation 강도, class weight, batch size 를 Bayesian sweep 으로 정렬하고, 학습률은 LinearLR warmup (시작 LR 을 base 의 0.05 부터 5 epoch 에 걸쳐 base 까지 올림) 뒤 CosineAnnealing (base → 1e-6) 으로 감쇠시키는 schedule 을 적용해 **0.92** 에 도달했습니다.
- **2-stage cascade**: wafer 신뢰도가 낮은 difficult sample 만 ROI YOLO 로 보내 confidence 가 낮은 케이스를 다시 분류하게 만든 결합으로 최종 weighted F1 **0.95** 까지 완성했습니다.

Unknown 검출은 정답 label 이 없는 운영 환경이라 정량 ladder 대신 production 학습 구성요소와 단일 anchor (13 → 7) 로 보고합니다. production 학습은 TAPT 한 ConvNeXtV2 backbone 위에 다음을 결합했습니다.

- **Global InfoNCE**: 같은 wafer 의 두 augmentation view 는 positive, 다른 wafer 는 negative.
- **Queue (size 16384)**: 직전 batch 들의 representation 을 negative pool 로 누적 (한 batch 안의 좁은 negative 다양성 보강).
- **Negative similarity filter (cos > 0.72 제외)**: queue 안에서 anchor 와 너무 유사한 wafer 는 사실 같은 class 일 가능성이 있어 negative 에서 제외 → false negative 차단.
- **Local InfoNCE (grid36_full, window=4)**: wafer 안 36 개 anchor 위치마다 patch-level positive 까지 같이 학습해 sub-pattern (edge ring 각도 등) 분리력 보강.
- **HDBSCAN**: 학습된 embedding 위에서 자동 grouping → 13개 후보 group 산출 → 현업 확인으로 7개 실제 불량 검증.

위 production 구성과 분리해, MoCo Queue / NV-Retriever / NeCo 같은 SOTA recipe ablation 은 synthetic benchmark (per class 500, normal 2000) 별도 트랙에서 진행 중입니다 (§구현 성과 표 참고).

```
+--------------------------------------------------------------------------+
|  Stage 1: ConvNeXtV2 wafer classifier (16 classes)                       |
|  - backbone scan ViT 0.81 / Swin 0.84 / EffV2 0.85 / MaxViT 0.87         |
|                  / ConvNeXtV2 0.87                                       |
|  - vs MaxViT: params -26%, FLOPs -39%                                    |
|  - ladder 0.78 -> 0.87 (backbone) -> 0.92 (Optuna) -> 0.95 (cascade)     |
+----------------------------------+---------------------------------------+
                                   |
                                   v
       +-----------------------------------------------------+
       |  cascade gate: confidence < gate (difficult sample) |
       +-----------------------------------------------------+
                  conf >= gate                  conf < gate
                       |                            |
                       v                            v
+--------------------------+   +--------------------------------------------+
|  Stage 1 only            |   |  Stage 2 (operational module selection)    |
|  (skip Stage 2,          |   |  (A) ROI-YOLO [in production]              |
|   ~zero throughput cost) |   |      - bbox + coord regression + class+NMS |
|                          |   |  (B) chip-CNN obj-id map [in development]  |
|                          |   |      - ~256x256 crop classification only   |
|                          |   |      - val_f1 0.9946 / test_f1 0.9872      |
+--------------------------+   +---------------------+----------------------+
                |                                    |
                +-----------------+------------------+
                                  v
+--------------------------------------------------------------------------+
|  OUTPUT: Known weighted F1 0.95 (16 class / 1,500 labeled / 4:1 split)   |
|  - ladder 0.92 -> 0.95 (+0.03, cascade gain)                             |
|  - operational guard: skip-wafer daily sampling re-check                 |
|                       + Stage 1 distribution drift monitoring            |
|                       -> gate periodic re-tuning (blocks FN accumulation)|
+--------------------------------------------------------------------------+
```

합성 wafer 이미지 예시 (2행 3열, 본인 생성 평가셋):

| Edge-Top Scratch | Edge-Ring Scratch_rot | Center Bank-Boundary (신규) |
|:----------------:|:---------------------:|:---------------------------:|
| <img src="./figures/wafer_edge_top_scratch.png" width="180" /> | <img src="./figures/wafer_edge_ring_scratch_rot.png" width="180" /> | <img src="./figures/wafer_center_bank_boundary.png" width="180" /> |
| **BrokenRing** | **RingDots** | **CrescentArc (신규)** |
| <img src="./figures/wafer_brokenring.png" width="180" /> | <img src="./figures/wafer_ringdots.png" width="180" /> | <img src="./figures/wafer_crescentarc.png" width="180" /> |

후속 chip-CNN object-id map 재구성 흐름은 다음과 같이 두었습니다.

```
+--------------------------------------------------------------------------+
|  INPUT: wafer 6400 x 6400 PNG + chip positions JSON (32 x 32 grid)       |
|  chip coordinates created at image-generation time -> no detection step  |
+----------------------------------+---------------------------------------+
                                   v
+--------------------------------------------------------------------------+
|  chip-CNN object-id map reconstruction                                   |
|  c_{u,v}   = crop(x, pos_{u,v}), ~256x256 input                          |
|  q_{u,v}   = softmax(h(c_{u,v}))           <- chip classification only   |
|  M_obj     = argmax_k q_{u,v,k}            <- 32x32x5 one-hot map        |
|  metrics   val_f1 0.9946 / test_f1 0.9872 / 5-seed 0.9838 +/- 0.0092     |
+----------------------------------+---------------------------------------+
                                   v
+--------------------------------------------------------------------------+
|  M_obj feeds Stage 2 posterior p_chip_obj(y | crop(x))                   |
|  Deploy decision: ROI-YOLO (in production) OR chip-CNN (in development)  |
|  picked at Stage 2 slot after validation passes operational checks       |
+--------------------------------------------------------------------------+

+--------------------------------------------------------------------------+
|  Why replace ROI-YOLO with chip-CNN                                      |
|  ROI-YOLO learns bbox + coord + class + NMS jointly with unknown chip    |
|  locations. chip-CNN slots into the fixed-grid chip positions and only   |
|  has to classify a ~256x256 crop, so accuracy goes up and latency drops. |
+--------------------------------------------------------------------------+
```

**ㅁ 구현 성과**

**[정량적/정성적 성과]**

- **기술 지표**
  - **[실전 현업 데이터]** Known 2-stage weighted F1 **0.95** (16 class / 1,500 labeled samples / 4:1 stratified split). 단계별 ladder 는 0.78 (baseline) → 0.87 (ConvNeXtV2 backbone 교체) → 0.92 (+Optuna hyperparameter optimization) → **0.95** (+ROI YOLO 2-stage 보정) 로 누적되었습니다. label 부족 조건에서 backbone 교체와 cascade 결합이 결정적이었습니다.
  - **[실전 현업 데이터]** Unknown 검출은 특정 제품 실전 데이터 1만 장 학습 후, 학습에 쓰지 않은 별도 2,000장에 적용해 13개 후보 group 중 **7개 불량을 확인**해 운영 검출력이 검증되었습니다. 정답 label 이 없는 환경이라 정량 metric 대신 현업 확인 결과로 보고합니다.
  - **[Unknown 추가 생성 데이터, 개발 중]** 현업 데이터와 최대한 유사하게 구성한 별도 평가셋에서 신규 class **capture 1.000 (38/38 발견)** / **noise 0.00%** / **Completeness 0.9938** / **Silhouette 0.781** 까지 측정했습니다. 실전 Unknown 운영 검출력 (13개 후보 group 중 7개 불량 확인) 과는 분리해, 심화 질의 대비용 보조 지표로 둡니다.
  - **[Known 추가 생성 chip 데이터, 개발 중]** chip-CNN object-id map 보정 구조는 Stage 2 ROI-YOLO 자리를 대체할 후속 모듈로 개발 중이며 (test_f1 **0.9872**), 양산 deploy 는 validation 검증 후 운영 절차에 따라 결정합니다. 본 수치는 P1 대표 성과가 아닌 후속 개발 보조 지표입니다.

  **Unknown contrastive 구성요소 성능표 (per class 500, normal 2000) [심화 질의 대비용 / 추가 생성 데이터, 개발 중]**

  | # | Recipe (per class 500, normal 2000) | M1 (capture) | M2 (noise %) | M3 (Completeness) | M4 (Homogeneity) | ARI | AMI | Sil |
  |---|--------|--------------|--------------|-------------------|------------------|-----|-----|-----|
  | 1 | Global InfoNCE only (baseline) | 1.000 | 6.20% | 0.9602 | 0.9290 | 0.823 | 0.929 | 0.582 |
  | 2 | + Local DenseCL (LW=0.5) | 1.000 | 3.93% | 0.9665 | 0.9351 | 0.851 | 0.939 | 0.514 |
  | 3 | + MoCo Queue 4096 | 1.000 | 1.31% | 0.9828 | 0.9365 | 0.846 | 0.950 | 0.573 |
  | 4 | + NV-Retriever NEG 0.72 | 1.000 | 0.52% | 0.9852 | 0.9439 | 0.861 | 0.956 | 0.611 |
  | 5 | + NeCo 0.2 (5-tool full) | 1.000 | 0.96% | 0.9801 | 0.9403 | 0.8564 | 0.9503 | 0.6104 |
  | 6 | 최종 recipe (Local DenseCL 제외 4-tool) | 1.000 | 1.48% | 0.9938 | 0.9424 | 0.859 | 0.960 | 0.781 |
  | 7 | 최종 recipe + 후처리 (noise 임계 τ=0.5) | 1.000 | 0.00% | 0.9938 | 0.9424 | 0.868 | 0.960 | 0.781 |

  본 표는 P1 Unknown 의 실전 운영 검출력 (13개 후보 group 중 7개 불량 확인) 과는 분리된 후속 개발 / metric 관리용 synthetic benchmark 결과입니다.

- **현업 임팩트**
  - **[양산 적용 단계]** 2025년 5월부터 DRAM 전제품 라인 Failbit Map 을 120일치씩 누적 처리 중이며, 일 약 2만 wafer 규모입니다.
  - **[전수 자동 적용 단계 확장 계획]** 전수 자동 추론으로 확장하려면 추가 GPU 자원이 필요하며, AI 센터 GPU 할당 기준 **2026년 9월** 제공이 예정되어 있습니다. GPU 할당 후 현재 검증된 Known / Unknown 모델을 전수 자동 추론 흐름으로 단계 확장할 계획입니다.

**ㅁ P2. Chip Multi-label Classification (FCM-PM, val_margin)**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Chip Multi-label Classification (FCM-PM, val_margin) |
| 수행기간 | 2025년 3월 ~ 현재 |
| 참여인원 | 본인 / 관리자 |

**ㅁ 과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|----|------|---------|------|------|--------|
| 1 | 최호길 | 개인정보 비공개 | 메모리제조센터 QIE그룹 | chip single / 2-combo 합성, CutMix 계열 선정, Pair Mask loss masking 설계, FCM-PM 본 과제 신규 적용, val_margin 기반 best-model selection, Temperature Scaling, pos/neg target asymmetry sweep, max-prob threshold gate, bit-level majority voting ensemble, Knowledge Distillation 압축 후보 검토 | 80% |
| 2 | 관리자 | 개인정보 비공개 | 관리조직 (공식 기록 대조) | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

**[본인이 독자적으로 수행한 핵심 모듈]**

- **과제 내에서 타 구성원과 차별화되는 본인만의 구체적 담당 영역**: chip 하나의 multi-label failure 검출 과제에서, 현업 single failure chip 4 class 를 학습 원천으로 확보하고, 부족한 2-combo 6 종을 도메인 분포에 맞춰 합성하는 FCM-PM (Full-Cover Mixup + Pair Mask) 설계, Pair Mask 로 합성 background 를 loss 에서 분리하는 손실 제어, val_margin 기반 best-model selection, Temperature Scaling, max-prob threshold gate, bit-level majority voting ensemble, Knowledge Distillation 압축 후보 검토까지 본인 80% 리딩으로 직접 수행했습니다. Normal / Invalid / OOD negative 평가셋도 현업 분포에 가깝게 본인이 직접 설계했습니다.

- **본인의 기술적 해결책이 과제 성패에 미친 영향**: BCE / Focal / ASL 단순 loss 변형만으로는 2-combo recall 과 false alarm 억제를 동시에 만족시키기 어려웠던 한계를, FCM-PM + val_margin selection 결합 설계로 풀었습니다. Pair Mask 제거 ablation 에서 Total FAR 이 **100%** 까지 치솟아 background loss masking 이 false-positive 억제의 결정적 요인임을 정량으로 확인했고, 최종적으로 FCM-PM val_margin 단일 모델 **bit_F1 0.9943 / Total FAR 0.00%** 를 controlled benchmark 위에서 달성했습니다. bit-level majority voting ensemble (champion `vote_majority_bits`) **bit_F1 0.9941 / Total FAR 0.00%** 와 Knowledge Distillation single student (sweep best bit_F1 **0.9470**) 도 후속 안정성 / 압축 보조로 확보했습니다.

**[평가 지표]** single F1 은 single failure class 별 F1 의 평균입니다. bit_F1 은 한 chip 의 label 을 `[0, 1, 1, 0]` 같은 4-bit vector 로 보고 각 bit 를 독립적으로 따로 측정한 뒤 모든 bit (chip × class) 를 micro-averaged 로 합쳐낸 값입니다. 제출 대표 수치 0.9943 도 bit_F1 기준입니다.

**P2 대표 성과 / 후속 개발 / 한계 및 관리**

- **대표 성과**: FCM-PM val_margin 단일 모델 bit_F1 **0.9943** / Total FAR **0.00%** 입니다.
- **후속 개발**: bit-level majority voting ensemble (champion `vote_majority_bits`, bit_F1 0.9941 / Total FAR 0.00%) 은 실전 운영의 모델 안정성 확보, Knowledge Distillation single student 는 양산 추론 생산성 (single-model latency) 확보를 위한 압축 후보로 검토 중이며, 운영 threshold calibration 과 함께 대표 성과와 분리해 관리합니다.
- **한계 및 관리**: P2 결과는 실제 현업 발생 failure 를 최대한 동일하게 구현하고 Normal / Invalid / OOD 같은 negative 환경까지 동일하게 구성한 controlled benchmark 기준입니다. single failure 4 class 의 가능한 2-combo 6종을 모두 포함해 조합 누락 없이 평가했으며, 실제 운영에서 추가될 수 있는 신규 failure class 와 장기 운영 분포 변화는 후속 확장 및 검증 대상으로 분리합니다.

BCE + Label Smoothing 으로 시작했으나 2-combo 신호가 거의 학습되지 않았고, Focal / ASL 로 loss 만 바꿔도 false-positive 가 크게 줄지 않았습니다. 다음으로 시도한 random CutMix 는 결함 위치가 잘려 학습 신호가 사라지거나 background 영역이 failure 로 학습되며 Normal / Invalid / OOD negative 에서 false-positive 가 늘어났습니다.

본인은 이를 Full-Cover Mixup 과 Pair Mask 로 나누어 풀었습니다.

- **Full-Cover Mixup**: chip 을 **GRID × GRID 격자로 분할**한 뒤 일부 cell 을 B 의 같은 위치 cell 로 덮어써, A 와 B 의 cell 이 chip 전체를 빈 영역 없이 덮도록 만든 합성입니다. 일반 CutMix 가 직사각형 한 덩어리만 잘라 붙여 결함 위치가 잘릴 수 있는 것과 달리, grid 분할로 두 chip 의 결함이 chip 전체에 골고루 노출됩니다. 합성 sanity 는 `failure_pixel_ratio(blended) ≥ max(d_i) - 0.01` 로 두어, 합성 후 결함 픽셀 비율이 입력 chip 중 결함 많던 쪽보다 떨어지면 그 sample 을 폐기해 failure signal 이 손실되지 않도록 제약했습니다.
- **Pair Mask**: B 가 붙은 영역을 mask 처리한 **추가 augmentation chip** 을 만들어 mixed chip 과 함께 학습합니다. masked chip 은 A label 만으로 학습되어 모델이 single class 의 단독 패턴을 다시 한 번 보게 되고, background fill 자리에서 false-positive 도 같이 차단됩니다.
- **Pair Mask 제거 ablation**: Total FAR 이 **100%** 까지 치솟아, background loss 가 false-positive 의 핵심 원인임이 정량으로 확인됐습니다.

마지막 쟁점은 best epoch 선택이었습니다. val_f1 변동이 test bit_F1 / FAR 변동과 상관성이 낮아 test 단계에서 성능이 일관되게 따라오지 않았습니다. 그래서 `val_margin = mean(score over positive bits) - max(score over negative bits)` 를 기준으로 잡았습니다 — positive 평균과 가장 위험한 negative 최대값의 차이를 직접 반영하기 때문에 test bit_F1 과의 일관성이 훨씬 높습니다 (Spearman ρ val_margin **+0.56** vs val_f1 **−0.10**).

이후 운영 환경 약 80% Normal 분포에 대응하는 추론 단계를 같이 검토했습니다.

- **Maximum probability threshold gate**: 운영 환경 약 80% Normal 분포 사전 정보를 반영해 기본 임계 0.5 를 **0.55** 로 올려 max-prob 가 0.55 미만이면 Normal 로 강제, 운영 false-positive 를 한 단계 더 줄였습니다.
- **pos / neg target 설계**: 최종 채택은 positive target 0.85 / negative target 0.15 입니다. 비대칭 positive target 0.95 / negative target 0.30 조합도 별도 trial 로 검토했지만 Normal / Invalid / OOD negative 평가에서 FAR 가 collapse 해 채택하지 않았고, 본 과제에서는 symmetric 0.85 / 0.15 가 bit_F1 과 FAR 안정성을 같이 만족한다는 결론이었습니다.
- **Majority Voting Ensemble**: 본 학습이 합성 데이터 위에서 진행된 만큼 현업 데이터에서 단일 모델 성능이 흔들릴 가능성을 대비해 만든 robustness 검증 구조입니다. champion `vote_majority_bits` 가 bit_F1 **0.9941** / Total FAR **0.00%** 로 단일 대표 모델 (0.9943) 과 동급 수준에 zero FAR 까지 확인되어, 현업 분포 shift 가 들어와도 어느 한 모델이 흔들리면 다른 두 모델 합의로 보정되는 안전 마진을 확보했습니다.
- **Knowledge Distillation (single student)**: ensemble 은 robustness 는 좋지만 모델 3 개를 동시에 돌려야 해 추론 비용이 3 배 듭니다. KD 는 ensemble 의 판단을 single student 로 압축해 **추론 비용은 단일 모델 수준 (1× latency / throughput / params) 으로 유지하면서 성능은 ensemble 수준으로 살리는** 양산 배포 후보로, 학생 모델 collapse 회피 설정 + α / T sweep 으로 bit_F1 **0.9265 → 0.9470** 까지 검증 완료한 상태입니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | chip 내부 failure 위치를 사전에 알 수 없고, single failure chip 만 가지고 multi-label 평가로 확장해야 합니다. |
| 기존 방식의 한계 | 일반 CutMix 는 일부 영역만 잘라 붙이다 보니 failure signal 이 잘려 버리거나 background 가 failure 로 학습되어 버려서, Normal / Invalid / OOD negative 평가에서 false-positive 가 운영에 쓰기 어려운 수준까지 올라갑니다. |
| 기술적 / 환경적 제약 | 2-combo label 부족, 작은 validation set 의 best epoch plateau, OOD / negative false-positive 억제, 압축 후보의 1× inference cost 제약이 한꺼번에 묶여 있습니다. |

**ㅁ 기술적 해결 방안**

**[데이터]** 실제 현업 chip 의 single failure 4 class 위에 두 결함씩 조합한 2-combo 6 종을 합성해, 현업 multi-label failure 양상과 매우 유사한 학습 / 평가 데이터를 구성했습니다. negative 측은 Normal (정상 chip 분포 모사) + Invalid + OOD wafer-pattern + OOD synthetic 까지 같이 두어 single 4 + 2-combo 6 + negative 6 = 16+ class × 약 3,850 chip 규모의 controlled benchmark 로 구성했습니다.

data leakage 방지를 위해 single failure chip 원천을 chip 단위로 먼저 train / test 로 split 한 뒤, 2-combo 와 Pair Mask 합성은 train 원천 chip 만 사용했습니다. test 원천 chip 은 합성 과정에서 완전히 배제해, train / test 사이 chip 단위 누수가 없도록 정리했습니다.

**[P2 수식 요약]**

```
p_k = sigmoid(z_k),  k = 1..K

L_BCE = -Σ_k [y_k log p_k + (1-y_k) log(1-p_k)]

x_mixed   = paste B grid cells onto A   (Full-Cover Mixup)
y_mixed   = y_A ∨ y_B                    (label union)
x_masked  = mask B-pasted cells of A     (paired aug.)
y_masked  = y_A                          (A-only label)

L_total   = L_BCE(x_mixed, y_mixed)
          + w · L_BCE(x_masked, y_masked)

val_margin = mean_{k in P+}(p_k) - max_{j in P-}(p_j)

FAR = FP_negative / N_negative
```

학습 원천 single 4 class 예시 chip (1행 4열, 본인 생성 평가셋):

| bank_boundary | fork | scratch | scratch_rot |
|:-------------:|:----:|:-------:|:-----------:|
| <img src="./figures/chip_eval_bank_boundary_selected.png" width="160" /> | <img src="./figures/chip_eval_fork_selected.png" width="160" /> | <img src="./figures/chip_eval_scratch_selected.png" width="160" /> | <img src="./figures/chip_eval_scratch_rot_selected.png" width="160" /> |

single 4 class 의 모든 2-조합으로 만든 2-combo 평가 chip 6종 (1행 6열, 본인 생성 평가셋):

| bb + fork | bb + scratch | bb + scratch_rot | fork + scratch | fork + scratch_rot | scratch + scratch_rot |
|:---------:|:------------:|:----------------:|:--------------:|:------------------:|:---------------------:|
| <img src="./figures/chip_combo_bb_fork_selected.png" width="130" /> | <img src="./figures/chip_combo_bb_scratch_selected.png" width="130" /> | <img src="./figures/chip_combo_bb_scratch_rot_selected.png" width="130" /> | <img src="./figures/chip_combo_fork_scratch_selected.png" width="130" /> | <img src="./figures/chip_combo_fork_scratch_rot_selected.png" width="130" /> | <img src="./figures/chip_combo_scratch_scratch_rot_selected.png" width="130" /> |

Normal / Invalid / OOD negative 평가셋 예시 (1행 6열, 본인 생성 평가셋):

| Normal | Invalid | OOD Starburst | OOD CenterDonut | OOD CrossScratch | OOD DiagonalSmear |
|:------:|:-------:|:-------------:|:---------------:|:----------------:|:-----------------:|
| <img src="./figures/chip_eval_normal_selected.png" width="130" /> | <img src="./figures/chip_eval_invalid_selected.png" width="130" /> | <img src="./figures/chip_ood_starburst_selected.png" width="130" /> | <img src="./figures/chip_ood_centerdonut_selected.png" width="130" /> | <img src="./figures/chip_ood_crossscratch_selected.png" width="130" /> | <img src="./figures/chip_ood_diagonalsmear_selected.png" width="130" /> |

softmax 대신 sigmoid multi-label head 를 쓴 이유는 single failure 와 2-combo failure 가 mutually exclusive 가 아니기 때문입니다. FCM-PM 합성은 포함된 failure label 의 union 을 target 으로 두고, Pair Mask 는 B 영역이 mask 처리된 추가 augmentation chip 을 같이 학습시켜 single class 단독 패턴을 다시 한 번 보게 하면서 background false-positive 차단까지 같이 잡습니다. FAR 는 Normal / Invalid / OOD negative set 에서 별도로 계산해 운영 false-positive 위험을 직접 보게 했습니다.

```
+--------------------------------------------------------------------------+
|  SOURCE: real production single-failure chips, 4 classes (Grade 0..7)    |
|  - chip-wise train / test split first -> no synthesis leakage            |
+----------------------------------+---------------------------------------+
                                   v
+--------------------------------------------------------------------------+
|  Step 1-2: pick CutMix family + diagnose its limits                      |
|  - Mixup / Diffusion blend pixels -> Grade meaning lost -> not usable    |
|  - CutMix is region-based -> Grade preserved (advice: Prof. Eunbyung Park)|
|  - random CutMix issue: signal cut + background -> false positives rise  |
+----------------------------------+---------------------------------------+
                                   |
                +------------------+------------------+
                v                                     v
+----------------------------------+  +----------------------------------------+
|  Step 3a: Full-Cover Mixup       |  |  Step 3b: Pair Mask                    |
|  - GRID x GRID grid cut          |  |  - mask B-pasted cells (corner /       |
|  - some cells overwritten by B   |  |    white / noise fill) on a paired     |
|    at the same cell positions    |  |    augmentation chip                   |
|    -> full chip cover, no gap    |  |  - paired chip carries A label only    |
|  - sanity ratio >= max(d_i)-0.01 |  |    -> B class not activated on bg fill |
+----------------+-----------------+  +----------------+-----------------------+
                 +---------------+--------------------+
                                 v
+--------------------------------------------------------------------------+
|  Step 4-5: FCM-PM training + val_margin checkpoint selection             |
|  - val_margin = mean(pos bit score) - max(neg bit score)                 |
|  - Spearman(epoch, test_f1): val_margin +0.56 vs val_f1 -0.10            |
|  - target pos 0.85 / neg 0.15 (symmetric)                                |
+----------------------------------+---------------------------------------+
                                   v
+--------------------------------------------------------------------------+
|  Step 6: Inference-stage operational safeguards                          |
|  - max-prob gate: max-prob < 0.55 -> force Normal (ops mix is ~80% Normal)|
|  - bit-level majority voting (vote_majority_bits, 3 models):             |
|    bit_F1 0.9941 / Total FAR 0.00%, lifts cells where one model wobbles  |
|  - Knowledge Distillation: compresses the ensemble vote into a single    |
|    student at 1x latency / throughput / params, deploy candidate         |
+--------------------------------------------------------------------------+
```

**[알고리즘]** 합성 / 선택 / 추론 세 단계로 본 과제 데이터 특성에 맞춰 본인이 직접 설계했습니다. Pair Mask 는 합성의 보강 augmentation 으로 (1) 합성 단계 안에서 같이 다룹니다.

**(1) 합성 — CutMix 계열 채택과 Full-Cover Mixup 확장**

Grade 0-7 양자화 chip 이미지를 다루는 본 과제에서는 생성 방식 선택이 곧 label 의미 보존 문제였습니다.

- **Mixup 배제**: 입력과 label 을 함께 보간하면 Grade 0-7 사이에 실재하지 않는 중간 grade 가 만들어져 분류기가 그 값을 noise 로 학습할 위험이 있습니다.
- **Diffusion 보류**: Diffusion 으로 본 과제 수준의 chip 이미지를 생성하려면 충분한 실제 2-combo 분포가 학습 데이터로 먼저 쌓여 있어야 하는데, 본 과제는 그 데이터 자체가 부족한 상황이라 운영 적용 후보로 두지 않았습니다.
- **CutMix 계열 채택**: 영역 단위로 원값을 보존해 붙이는 CutMix 계열이 양자화 의미 보존 측면에서 적합하다고 본인이 판단해 채택했습니다 (자문: 연세대학교 인공지능학과 박은병 교수).
- **Full-Cover Mixup 확장**: 일반 CutMix 는 일부 직사각형 영역만 잘라 붙입니다. chip 내부 어디에 failure 가 올지 모르는 본 과제에서는 failure signal 이 잘릴 위험이 남아, chip 전체 grid 를 cover 하는 Full-Cover Mixup 으로 확장했습니다 (현업 Overlay dynamic sampling 경험에서 wafer 전 영역을 빠짐없이 cover 해야 sampling 누락이 없다는 아이디어를 가져옴).
- **Pair Mask 보강 augmentation**: FCM mixed chip 만 학습하면 A / B 가 항상 섞여 들어가 single class 단독 패턴을 보는 학습 신호가 약해질 수 있어, B 영역을 mask 처리한 추가 augmentation chip 을 같이 학습시키는 paired forward 를 두었습니다 (`loss = loss(mixed, A+B label) + w · loss(masked, A-only label)`). FCM 이 multi-label 학습의 메인 축이고, Pair Mask 는 그 부작용을 같은 학습 루프 안에서 잡아주는 보강 장치입니다. Pair Mask 제거 시 Total FAR 이 100% 로 치솟는 ablation 이 본 설계의 직접 근거입니다.

FCM-PM 학습 augmentation 을 실제 chip 이미지에 적용한 예시입니다 (`complement` 모드, `n_groups=2`, pair-fill white — per-class 50 group2 SOTA iter26F: bit_F1 0.9953 / Total FAR 0.00%). 실제 운영 학습은 GRID=8 (총 64 cell) 이고, 아래 예시는 셀 분포가 한눈에 보이도록 GRID 만 4 (16 cell, 그룹당 8 cell) 로 줄였습니다 (1행 6열).

| chip A: scratch | chip B: scratch_rot | FCM mixed (A label) | FCM mixed (B label) | Pair Mask (A-only) | Pair Mask (B-only) |
|:---------------:|:-------------------:|:-------------------:|:-------------------:|:------------------:|:------------------:|
| <img src="./figures/fcm_pm_step_a.png" width="130" /> | <img src="./figures/fcm_pm_step_b.png" width="130" /> | <img src="./figures/fcm_pm_step_mixed_a.png" width="130" /> | <img src="./figures/fcm_pm_step_mixed_b.png" width="130" /> | <img src="./figures/fcm_pm_step_masked_a.png" width="130" /> | <img src="./figures/fcm_pm_step_masked_b.png" width="130" /> |

FCM-PM 은 chip 을 격자로 나눈 뒤 두 그룹 cell 로 쪼개고, A label / B label 쪽에 각각 독립 분할을 한 번씩 뽑아 4 장의 학습 chip 을 만드는 방식입니다.

- **FCM mixed**: 한쪽 chip 위에 다른쪽 chip 의 절반 cell 을 덮어쓴 합성 chip, label = A∪B → multi-label 신호 학습.
- **Pair Mask**: 같은 합성 chip 에서 다른쪽 cell 자리를 흰색으로 가린 chip, label = 한쪽 결함만 → 단독 패턴 유지 + 흰 배경의 false-positive 억제.

A-only 와 B-only 의 가림 위치가 다른 것은 두 partition 을 따로 뽑기 때문이고, 네 장이 같은 paired forward 에 함께 들어갑니다.

**(2) checkpoint 선택 — val_margin 정의**

val_margin = mean(score over positive bits) − max(score over negative bits)

평균과 최대의 차이로 정의했기에 val_f1 plateau 구간에서도 미세 변동이 남아 best epoch 이 동률로 묶이지 않습니다. negative 측 최대를 쓴 정의 근거는 §개인별 기여 서술 에 상세히 기술했습니다. epoch-vs-test_f1 Spearman ρ 는 val_margin +0.56 / val_f1 −0.10 으로, val_margin 이 ground-truth test_f1 과 양의 일관성을 보였습니다.

```
       [chip image]
            ↓
    [classifier 출력 bit score]
            │
   ┌────────┴────────┐
   ▼                 ▼
positive bits     negative bits
(실제 결함)        (정상 bit)
   │                 │
 평균 score        최대 score  ← false-positive 위험점
   │                 │
   └────────┬────────┘
            ▼
   val_margin = mean(positive) − max(negative)
            ↓
   클수록 결함과 정상 분리가 안정적
```

**(3) 추론 단계 보강 — Threshold gate / Ensemble / Knowledge Distillation**

운영 환경 약 80% Normal 분포에 대응해 max-prob < 0.55 입력을 Normal 로 강제하는 threshold gate (기본 0.5 → 0.55) 로 false-positive 를 추가 억제했고, 학습 단계는 positive target 0.85 / negative target 0.15 로 negative 측 보수성을 같이 잡았습니다. bit-level majority voting ensemble (`vote_majority_bits`) 은 합성 데이터 학습 모델이 현업 분포 shift 에서 흔들릴 가능성을 대비한 robustness 검증 구조로, bit_F1 **0.9941** / Total FAR **0.00%** 로 단일 대표 (0.9943) 와 동급 zero FAR 까지 확인됐습니다. Knowledge Distillation single student 는 ensemble 의 3× 추론 비용을 1× latency 로 압축하는 양산 배포 후보로, CutMix 활성 batch 의 distillation loss 를 제외해 collapse 를 회피했고 α / T sweep 최고점은 bit_F1 **0.9470** / Total FAR **0.00%** 였습니다. 대표 모델보다 bit_F1 이 낮아 후속 압축 후보로 분리합니다.

**[최적화]** 합성 단계에서는 CutMix → CutMix + Pair → FCM-PM 순서로 단계별 효과를 직접 측정했고, false-positive 와 bit_F1 의 trade-off 가 어디서 깨지는지를 아래 ablation 표로 추적했습니다.

- **cover grid sweep**: chip 분할 그룹 수 (partition count) 와 그룹 내 cell 세분화 배수 (grid multiplier) 를 범위로 sweep, **partition=3 / multiplier=1 조합이 bit_F1 0.9960** 으로 최적이었습니다.
- **분할 선택 근거**: partition 수를 늘리면 chip 이 더 잘게 분할되어 공간 다양성은 증가하지만, partition≥4 부터는 failure 영역 자체가 너무 잘게 쪼개져 학습 모델이 failure 형태를 인식하기 어려워지면서 **분류 정확도가 오히려 감소합니다**. partition=3 부근이 본 과제 데이터에 최적이었습니다.
- **pos / neg target 선택**: 본 데이터에서는 positive target 0.85 / negative target 0.15 (symmetric) 가 bit_F1 과 FAR 안정성을 동시에 만족했습니다. 비대칭 positive target 0.95 / negative target 0.30 trial 은 별도로 검토했지만 Normal / Invalid / OOD negative 평가에서 FAR collapse 가 확인되어 채택하지 않았습니다.

**ㅁ 구현 성과**

**[정량적/정성적 성과]** (P2 성과는 **[현업 failure chip 원천 + 도메인 확률분포 기반 생성/검증]** 위에서 측정한 값입니다. 아래 성과 항목별 데이터 출처는 inline 라벨로 분리 표기합니다.)

- **기술 지표** (단계별 적용 효과):
  - 학습 ladder: BCE+Label Smoothing → Focal / ASL loss 변형 → 단순 CutMix → **FCM-PM (Full-Cover Mixup + Pair Mask) + val_margin best-model selection** 순으로 단계별 적용해 bit_F1 0.1093 → **0.9943** / Total FAR 99.47% → **0.00%** 까지 향상시켰습니다.
  - 핵심 근거: Pair Mask 제거 시 Total FAR 이 **100%** 로 치솟아, **background loss 분리가 false-positive 억제 핵심 요인**임을 직접 확인했습니다.
  - val_margin 기반 best-model selection 이 val_f1 보다 실제 test bit_F1 을 훨씬 정확히 예측 (Spearman ρ **+0.56 vs −0.10**) — best epoch 안정성 확보.
  - 추론 단계 보강: max-prob threshold gate + bit-level majority voting ensemble (champion `vote_majority_bits` bit_F1 0.9941 / Total FAR 0.00%) + Knowledge Distillation single student 압축 후보.

  **Multi-label 학습 recipe 성능표 (per class 2000) [현업 failure chip 원천 + 도메인 확률분포 기반 생성/검증]**

  | # | Recipe (per class 2000) | bit_F1 | single | 2combo | FAR | NI-FAR | OOD-FAR | Latency | Throughput | Params | Note |
  |---|--------|--------|--------|--------|-----|--------|---------|---------|------------|--------|------|
  | 1 | BCE + Label Smoothing | 0.1093 | TBD | TBD | 99.47% | 99.65% | 98.91% | 1x | 1x | 1x | ladder baseline |
  | 2 | Sigmoid Focal Loss | 0.7980 | TBD | TBD | 45.72% | TBD | TBD | 1x | 1x | 1x | ladder baseline |
  | 3 | Asymmetric Loss (ASL) | 0.6435 | TBD | TBD | 100.0% | TBD | TBD | 1x | 1x | 1x | ladder baseline |
  | 4 | CutMix (random rectangle) | 0.9359 | TBD | TBD | 42.05% | 37.00% | 57.81% | 1x | 1x | 1x | ladder baseline |
  | 5 | CutMix + Pair Mask | 0.9256 | TBD | TBD | 100.0% | TBD | TBD | 1x | 1x | 1x | ladder baseline |
  | 6 | FCM-PM + val_f1 selection | **0.9652** | 1.0000 | 0.9517 | 0.15% | 0.00% | 0.62% | 1x | 1x | 1x | val_f1 기준 checkpoint |
  | 7 | **FCM-PM + val_margin selection** | **0.9943** | **0.9918** | **0.9894** | **0.00%** | 0.00% | 0.00% | 1x | 1x | 1x | **제출 대표 모델** |
  | 8 | vote_majority_bits Ensemble※ | **0.9941** | **1.0000** | **0.9893** | **0.00%** | 0.00% | 0.00% | 3x | 1/3x | 3x | champion ensemble |
  | 9 | Knowledge Distillation (single student, baseline) | 0.9265 | 0.9785 | TBD | 0.00% | 0.00% | 0.00% | 1x | 1x | 1x | 압축 후보 — collapse 회피 첫 안정 |
  | 10 | Knowledge Distillation (single student, sweep best) | **0.9470** | TBD | TBD | **0.00%** | 0.00% | 0.00% | 1x | 1x | 1x | 압축 후보 — α / T sweep 최고점 |

  본 표는 per class 2000 chip synthetic benchmark 기준의 잠정값이며, 추가 evaluation 이 완료되면 정식 값으로 갱신할 예정입니다. row 8 의 ensemble 은 보조 안정성 실험으로 01_career_profile.md / 02_ai_portfolio.md 의 ensemble 수치와는 동일 실험이 아닙니다. 표 row 1~7 흐름을 보면 CutMix 단독으로는 FAR 이 운영에 쓰기 어려운 구간에 남고, FCM-PM + val_margin 으로 와서야 bit_F1 0.9943 / Total FAR 0.00% 의 균형이 맞춰집니다. 제출 대표 성과는 row 7 (bit_F1 0.9943 / Total FAR 0.00%) 로 고정합니다.

- **현업 임팩트**
  - 실전 single failure chip 원천 위에 부족한 2-combo 결함을 도메인 분포로 합성해 multi-label 학습 / 평가가 가능해졌습니다. 현업에서는 2-combo label 수와 균형을 얻기 어려워 사실상 막혀 있던 분류 문제를, 반도체 도메인 (Grade 0-7 의미와 failure 위치 / 강도 / 조합 분포) 위에서 다시 푼 방법론입니다.
  - 현업 eval 환경을 얻기 어려운 상황에서 Normal / Invalid / OOD negative 평가셋을 현업 분포에 가깝게 직접 설계한 점도 본 과제 변별 포인트입니다.
  - 정량으로는 bit F1 0.9943, Normal / Invalid / OOD negative Total FAR 0.00% 로 양산 적용 전 false-positive 리스크 검증을 마쳤습니다.
  - val_margin 기반 best-model 선택은 작은 validation set 에서 val_f1 이 여러 epoch 에 동률로 묶여 best 가 변동하는 문제를 제어하는 추가 검증 기준으로 같이 들어 있습니다.
  - 이 구조는 P1 의 wafer-level 판단을 chip 좌표계로 정밀화하는 후속 기반으로도 이어집니다.


**ㅁ P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC |
| 수행기간 | 2026년 1월 ~ 현재 |
| 참여인원 | 본인 / 관리자 / 동료 엔지니어 (공동 연구자) |

**ㅁ 과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|----|------|---------|------|------|--------|
| 1 | 최호길 | 개인정보 비공개 | 메모리제조센터 QIE그룹 | trend episode 합성 generator 설계, Region 5종 / Noise 3종 / trend 불량 4종 + context 1종 parameter 코드화, 합성 normal 산포의 상한 / 하한을 같이 잡는 두 가지 수식 설계, 1차 Binary gate 검증 PoC 설계 / 구현 | 70% |
| 2 | 관리자 | 개인정보 비공개 | 관리조직 (공식 기록 대조) | 방향성, 일정, 리뷰 매니징 | 20% |
| 3 | 동료 엔지니어 (공동 연구자) | 개인정보 비공개 | 관련 엔지니어 조직 (공식 기록 대조) | AI 모델 실행, 데이터 정리, 실험 결과 취합 | 10% |

**ㅁ 개인별 기여 서술**

**[본인이 독자적으로 수행한 핵심 모듈]**

- **과제 내에서 타 구성원과 차별화되는 본인만의 구체적 담당 영역**: 본인이 BBD담당 / Overlay담당 / CD담당으로 **9년간** trend chart 를 직접 판정해 온 경험을 generator parameter 로 옮겼습니다. 먼저 **Noise 3분포** (Gaussian / Laplacian / Correlated) 와 **계측 밀도 Region 5단계** (dense / sparse / very_sparse / thin / missing) 를 본인이 정의해 합성 normal baseline 을 실전 환경에 맞춰 구현하고, normal 산포 상한 / 하한 두 가지 수식까지 직접 설계했습니다. 그 위에 **mean shift / standard deviation / spike / drift / context** 5종 불량을 어느 강도에서 실제 불량으로 이어지는지 기준을 정해 generator parameter 로 코드화했습니다. 동료 엔지니어는 AI 모델 실행, 데이터 정리, 실험 결과 취합을 공동 수행했습니다.

- **본인의 기술적 해결책이 과제 성패에 미친 영향**: 실전 abnormal label 이 부족해 막혀 있던 anomaly 검증을, 본인 담당 경험을 반영한 trend 합성 데이터로 풀었습니다. **normal 3,500 + abnormal 3,500 = 총 7,000개** trend sample 을 만들어 AI 학습이 가능한 상태로 만들었고, 1차 Binary gate baseline 에서 **Binary F1 0.9967 / Abnormal Recall 0.9987** (test 1,500 / threshold=0.9) 로 생성 데이터만으로도 정상과 이상이 안정적으로 구분되는 것을 확인했습니다. **현업 데이터 적용 직전** 단계까지 진행했습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | trend 이상은 단순 threshold 만으로 판정하기 어렵고, 설비 산포 / hunting / 미세 drift / baseline 흔들림 / spec out 위험까지 같이 봐야 합니다. |
| 기존 방식의 한계 | 실전 abnormal data 는 양과 label 균형 확보가 어렵고 수작업 chart 판독에 의존하다 보니 초보자 누락과 모니터링 시간 부담이 누적됩니다. |
| 기술적 / 환경적 제약 | 실전 label 부족을 전제로 trend domain knowledge 를 합성 데이터 parameter 로 옮기는 단계가 먼저 풀려야 뒤 단계 검증이 가능합니다. |

**ㅁ 기술적 해결 방안**

작업 흐름은 크게 세 단계입니다. 먼저 trend 판정 경험을 generator parameter 에 반영하고, 합성 normal 산포는 상한 / 하한 두 수식으로 실전 baseline 안에 가둔 뒤 abnormal 은 정상 산포에 묻히지 않게 분리합니다. 마지막으로 1차 Binary gate baseline 으로 생성한 데이터의 학습 가능성을 검증하며, 이 모델은 운영 후보가 아니라 데이터 검증용으로만 사용합니다.

```
+--------------------------------------------------------------------------+
|  SOURCE: 9-year BBD / Overlay / CD trend-judgment experience             |
|  criteria (scatter / hunting / drift / spec-out risk) -> generator       |
|  parameters: this coding step is the core asset of the project           |
+----------------------------------+---------------------------------------+
                                   v
+--------------------------------------------------------------------------+
|  Step 1-3: encode the domain distribution                                |
|  - Region density 5 levels: dense 70-100% / sparse 40-70%                |
|                              / very_sparse 20-35% / thin 10-20% / 0%     |
|  - Noise 3 distributions (one-to-one to physical origin):                |
|      Gaussian 0.80 = chamber thermal / mechanical baseline scatter       |
|      Laplacian 0.15 = equipment hunting, heavy-tailed                    |
|      Correlated 0.05 = post-process align time-axis drift                |
|  - Anomaly 5 types: mean_shift / std / spike / drift / context           |
+----------------------------------+---------------------------------------+
                                   v
+--------------------------------------------------------------------------+
|  Step 4-5: upper / lower bounds for synthetic-normal scatter + render    |
|  - target_baseline_std = max(baseline_std, 0.01)   <- lower bound        |
|  - target_std <= fleet_within_std * 1.2            <- upper bound        |
|    synthetic normal stays inside real baseline statistics;               |
|    abnormal intensity stays above the noise floor                        |
|  - Render: 224 x 224 PNG, 3,500 normal + 3,500 abnormal = 7,000 samples  |
+----------------------------------+---------------------------------------+
                                   v
+--------------------------------------------------------------------------+
|  Binary gate baseline (normal / abnormal)                                |
|  - F1 0.9967 (TN/FN/FP/TP = 746/1/4/749), normal threshold 0.9           |
|  - 5-seed best F1 0.9987 (TN/FN/FP/TP = 748/0/2/750)                     |
|  - training stabilizers: val-F1 median smoothing + val-loss spike guard  |
+----------------------------------+---------------------------------------+
                                   v
+--------------------------------------------------------------------------+
|  OUTPUT: synthetic dataset is learnable (PoC confirmed)                  |
|  Next: feed real-line abnormal logs back as parameter-recalibration      |
|  triggers and verify unseen-domain generalization                        |
+--------------------------------------------------------------------------+
```

trend 합성 원리 (baseline + anomaly 산식 / 사내 도면 별도 첨부):

| Trend 생성 수식 / 도면 (사내 자료) |
|:----------------------------------:|
| <img src="./figures/p3_trend_generation_formula.png" alt="trend 합성 원리 (사내 첨부 예정)" width="640" /> |

> ※ 위 칸은 사내 보고서에 실릴 trend 생성 수식 / 도면 자리표시자입니다. 실제 제출 시 사내 자료로 교체합니다.

합성 trend chart 예시 (정상 + 일반 trend 불량 4종 + context 1종):

| Normal | Mean Shift | Standard Deviation Change |
|:------:|:----------:|:-------------------------:|
| <img src="./figures/trend_normal.png" width="200" /> | <img src="./figures/trend_mean_shift.png" width="200" /> | <img src="./figures/trend_standard_deviation.png" width="200" /> |
| **Spike** | **Drift** | **Context** |
| <img src="./figures/trend_spike.png" width="200" /> | <img src="./figures/trend_drift.png" width="200" /> | <img src="./figures/trend_context.png" width="200" /> |

검증 baseline 학습 측의 checkpoint 안정화에는 일시 spike 에 선택이 흔들리지 않도록 val-F1 median smoothing 과 val-loss spike guard 를 같이 두었습니다.

**ㅁ 구현 성과**

**[정량적/정성적 성과]** (P3 성과는 모두 **[합성 trend chart, PoC]** 기반이며, 주 성과는 데이터 생성 자체입니다.)

- **기술 지표** (단계별 적용 효과):
  - 데이터: **normal 3,500 + abnormal 3,500 = 총 7,000개** trend sample, test split 1,500 (normal 750 / abnormal 5종 각 150).
  - 도메인 코드화: Region 5단계 (계측 밀도) × Noise 3분포 (Gaussian / Laplacian / Correlated) × 불량 5종 (mean shift / standard deviation / spike / drift / context) 를 generator parameter 로 직접 구현.
  - 정상성 보정: `target_baseline_std = max(baseline_std, 0.01)` + `target_std ≤ fleet_within_std × 1.2` 두 식으로 합성 normal 통계는 실전 baseline 에 맞추고 abnormal 강도는 정상 산포에 묻히지 않게 분리.
  - Binary gate baseline: test 1,500건 / normal threshold=0.9 기준 **Binary F1 0.9967 / Abnormal Recall 0.9987** (TN/FN/FP/TP=746/1/4/749), 5-seed best **F1 0.9987**, threshold sweep 임계 둔감 확인.

- **현업 임팩트**
  - 본인이 BBD / Overlay / CD 담당 경험에서 직접 본 trend 분석 기준을 generator parameter 로 옮긴 결과, 실전 abnormal label 이 부족한 환경에서도 AI 학습이 가능한 데이터 자산을 확보했고 학습 + 성능 검증 단계까지 마쳤습니다. L1 trend 모니터링의 수작업 부담과 초보자 누락, spec out 위험을 줄이는 1차 스크리닝 기반으로 **현업 데이터 적용 직전** 단계입니다.
  - 다음 단계는 실전 현업 trend log 를 generator parameter 재보정 trigger 로 흘려 unseen 영역 일반화 검증으로 이어가는 흐름입니다.

**P3 결론**: 본인 trend 판정 경험을 Region / Noise / anomaly parameter 로 코드화한 **normal 3,500 + abnormal 3,500 = 총 7,000개** 합성 trend sample 데이터 자산 + Binary F1 **0.9967** 학습 / 검증 완료 (현업 데이터 적용 직전). 실전 abnormal log 기반 generator 재보정 trigger 와 type 세분화 분류기는 후속 단계.
