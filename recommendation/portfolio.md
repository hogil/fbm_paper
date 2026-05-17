## 1. AI 프로젝트 수행 전체이력

| 기간 | 과제명 | 리딩 규모 | 담당업무 | 과제관리 | 설계 | 개발비중 |
|------|--------|-----------|----------|----------|------|----------|
| 2024년 10월 ~ 현재 | P1. Failbit Map Known & Unknown 불량 분석 아키텍처 | 3인 협업, 본인 60% 리딩. DRAM 전제품 라인 양산 운영, 일 약 2만 장 wafer 처리 | 본인이 FBM raw log 적재 / Cython 파싱 / palette PNG 와 chip 좌표 JSON 생성을 짜고, 운영 뷰어 쪽과 연결한 뒤 Known 불량 및 Unknown 불량 AI 모델을 설계 / 학습 / 검증까지 끌고 갔습니다. | 20% | 35% | 45% |
| 2025년 3월 ~ 현재 | P2. Chip Multi-label Classification | 2인 PoC, 본인 80% 리딩. 16+ class × 약 3,850 chip controlled synthetic benchmark | chip single / 2-combo 합성, Pair Mask loss masking, FCM-PM 설계, val_margin 기반 best-model 선택, 대표 모델 검증까지 본인이 직접 진행. | 20% | 40% | 40% |
| 2026년 1월 ~ 현재 | P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC | 3인 PoC, 본인 70% 리딩. normal 3,500 + abnormal 3,500 = 총 7,000개 trend sample 구성 | 현업에서 BBD / Overlay / CD 담당으로 **9년간** trend 이상 감지를 해 오며 확인한 전형적인 불량 패턴과 정상 chart 산포 / noise 환경을 episode generator parameter 로 코드화했습니다. | 20% | 45% | 35% |

**핵심 요약**

1. P1 은 Failbit Map raw log → wafer image 변환, **사내 운영 뷰어 web app 직접 구현**, Known 2-stage 분류, Unknown 후보 group 검토까지 양산 운영 흐름 전체를 한 줄로 연결한 AI 시스템입니다.
2. P2 는 현업 single failure chip 원천 기반 FCM-PM + Pair Mask loss 로 2-combo label 부족을 풀고, **bit_F1 과 false alarm 을 동시에 잡은** multi-label 방법론입니다.
3. P3 는 본인 BBD / Overlay / CD 담당 trend 판정 경험을 generator parameter 로 코드화해, **AI 학습이 가능한 trend 데이터 자산 자체를 만든** 것이 주 성과인 PoC 입니다 (1차 Binary gate 검증까지 확보).

## 2. 대표 과제 상세 기술서

**ㅁ P1. Failbit Map Known & Unknown 불량 분석 아키텍처**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Failbit Map Known & Unknown 불량 분석 아키텍처 |
| 수행기간 | 2024년 10월 ~ 현재 |
| 참여인원 | 본인 / 현업 엔지니어 / 관리자 |

**양산 파이프라인 핵심 수치 요약**

- Cython hex-to-grade 변환 재구성으로 데이터 처리 속도를 약 **100배** 끌어올렸습니다.
- 32색 palette indexed PNG 저장으로 이미지 저장 용량을 약 **75%** 줄였습니다.
- 기존 1회 약 48매 조회 중심의 흐름을 일 약 **2만 장 wafer / 1시간 주기** 누적 비교 흐름으로 확장했습니다.
- Known 2-stage 는 weighted F1 **0.95**, Unknown 검출은 특정 제품 실전 데이터 기반 13개 후보 group 중 7개 실제 불량 확인으로 분리해 보고합니다.

**P1 결론**: 일 약 2만 장 wafer / 1시간 주기 처리 Failbit Map 운영 파이프라인, Known 2-stage weighted F1 **0.95** + Unknown 13 후보 → **7 실제 불량 현업 확인**. chip-CNN object-id map 과 Unknown synthetic benchmark metric 은 심화 질의 대비 항목으로 분리, Unknown 운영 데이터는 정답 label 부재로 후보 group 압축 + 현업 확인 결과로만 보고합니다.

**ㅁ 과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|----|------|---------|------|------|--------|
| 1 | 최호길 | 개인정보 비공개 | 메모리제조센터 QIE그룹 | FBM 데이터 파이프라인, 운영 뷰어 연동, Known CNN → ROI-YOLO 2-stage, Unknown contrastive 학습, 후속 chip-CNN obj-id map 보정 구조의 설계 / 구현 주도 | 60% |
| 2 | 현업 엔지니어 | 개인정보 비공개 | 관련 현업부서 (공식 기록 대조) | 아이디어 발의, Failbit Map 의미 및 불량 분석 교육, Unknown 후보 13개 중 실제 불량 7개 현업 검증 협업 | 20% |
| 3 | 관리자 | 개인정보 비공개 | 관리조직 (공식 기록 대조) | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

본인은 wafer 단위 분석 경험을 바탕으로 현업 엔지니어 교육을 거쳐 Failbit Map 의미와 분석 흐름을 확보한 뒤 AI 설계에 착수했습니다. raw log → wafer 이미지 변환 / 저장 / 조회 파이프라인 (fail-map) 과 운영 뷰어를 직접 설계 / 구현하고, 그 위에 Known 2-stage 분류와 Unknown self-supervised 검출을 결합한 운영 시스템을 구축했습니다.

wafer 한 장에 약 1,000만 cell 규모의 hex 값을 Grade 0~7 로 풀어내는 변환 루프를 Cython 으로 다시 짜서 약 100배 가속을 잡았고, 32색 palette indexed PNG 양자화로 저장 용량을 약 75% 줄여 일 약 2만 장 / 1시간 주기 적재 흐름이 양산 운영으로 가능해졌습니다.

AI 모델 단에서는 ConvNeXtV2 wafer-level classifier 와 ROI YOLO 보정 stage 를 cascade 로 묶었습니다. **[실전 현업 데이터]** 16 class / 1,500 labeled samples / 4:1 stratified split 에서 weighted F1 **0.95** 에 도달했고, Unknown 검출은 13 후보 group 가운데 7개가 실제 불량으로 현업 확인되었습니다 (학습 / eval 세부는 §현업 임팩트 박스에 정리).

Unknown 측은 운영 단계에 정답 label 이 없어 별도 보조 metric 으로 분리해 추적하고 있습니다. **[추가 생성 데이터, 개발 중]** 본인이 직접 구성한 추가 생성 데이터셋 기반 cross-anchor 평가는 심화 질의 대비용으로 별도 관리하며, 실전 Unknown 운영 성과와 섞지 않습니다.

**[추가 생성 chip 데이터, 개발 중]** ROI-YOLO 는 6400×6400 wafer 에서 작은 chip 을 detection 하느라 small object detection 한계 + anchor / NMS 비용이 누적됩니다. chip-CNN object-id map 은 fail-map 이 chip 좌표를 확정해 둔 상태에서 chip crop 전체를 CNN 으로 분류하므로 detection 단계가 빠지면서 chip 단위 정확도도 더 높습니다. Stage 2 대체 후보이며 양산 deploy 는 validation 검증 후 결정합니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | (1) wafer Failbit Map 을 한 번에 약 48매까지만 느리게 조회할 수 있어 대량 wafer 분석이 어렵습니다. (2) wafer 당 약 1,000만 cell Grade map 을 분석 엔지니어가 수작업으로 판정해야 합니다. |
| 기존 방식의 한계 | hex → Grade 변환을 Python loop 로 돌아 wafer 한 장 처리에 시간이 오래 걸렸고, 메모리 제약으로 동시 조회가 약 48매로 묶여 제품 / 시간 단위 누적 분석이 어려웠습니다. |
| 기술적 / 환경적 제약 | 등록되지 않은 신규 결함 패턴은 known classifier 로 잡히지 않고, label 1,500장 / 16 class 의 작은 학습 set, 일 약 2만 장 wafer 처리, 1시간 주기 적재, 운영 뷰어 응답성이 한꺼번에 걸려 있었습니다. |

**ㅁ 기술적 해결 방안**

본인이 직접 잡은 P1 end-to-end 파이프라인은 raw log → wafer 이미지 변환 → 좌표 JSON → 운영 뷰어 노출 → Known 분류 / Unknown 검출 → 현업 검증 까지입니다. 단계별 모듈은 아래와 같습니다.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  [SOURCE]  EDS Test raw log (Memory Cell Block 단위 Failbit hex 표현)       │
│            • wafer 당 ~1,000만 cell, DRAM 전제품 라인                         │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  [PIPELINE]  fail-map 변환 모듈 (본인 직접 설계 / 구현)                       │
│  • Cython hex→Grade(0~7) 변환 루프 → 약 **100배** 가속                       │
│  • 32색 palette indexed PNG 양자화 → 저장 용량 약 **75%** 감소                │
│  • 출력 wafer image: **6400×6400** palette PNG (8-bit, 32색)                  │
│  • chip grid **32×32** (1,024 chip / wafer, chip 당 200×200 pixel)            │
│  • chip positions JSON 생성 → chip 좌표 확정 (후속 chip-CNN 입력 사용)        │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  [VIEWER]  운영 뷰어 Web App (대량 wafer 조회 / 다양한 분석 편의 기능)        │
│  • 사내 인증 시스템 (SSO) 연동                                                │
│  • 일 약 **2만** wafer / **1시간 주기** batch 처리                            │
│  • 기존 수작업 조회 1회 ~48매 한계 → 대량 wafer 조회 + 다양한 분석 편의 기능  │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┴───────────────────┐
                ▼                                       ▼
┌──────────────────────────────────┐   ┌──────────────────────────────────────┐
│  Known 분기                       │   │  Unknown 분기                         │
│  (등록 16-class)                  │   │  (self-supervised contrastive)        │
├──────────────────────────────────┤   ├──────────────────────────────────────┤
│  Stage 1: ConvNeXtV2             │   │  • InfoNCE + MoCo Queue (4096)        │
│   wafer-level classifier         │   │    + NV-Retriever NEG 임계 0.72       │
│           ↓ confidence < τ_gate  │   │  • HDBSCAN clustering                 │
│  Stage 2: ROI YOLO refinement    │   │  • 운영 13 후보 group → 7 실제 불량   │
│   (chip bbox + class 분포)       │   │    현업 확인 완료                     │
│  → weighted F1 **0.95**           │   │  • 후속 synthetic benchmark metric    │
│                                   │   │    은 대표 성과와 분리 관리           │
└──────────────────────────────────┘   └──────────────────────────────────────┘
                │                                       │
                └───────────────────┬───────────────────┘
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  [REVIEW]  운영 뷰어 결과 표시 + 현업 엔지니어 검증 cycle                     │
│  • 신규 결함 후보 카탈로그 등재                                                │
│  • Known classifier 학습 sample 보강                                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

**[데이터]** 위 파이프라인의 [SOURCE] / [PIPELINE] 두 단계에 해당합니다. raw EDS Test log (wafer 당 약 1,000만 cell) 의 Failbit hex 표현을 Cython 변환 루프로 약 100배 가속해 Grade(0~7) 양자화하고, 32색 palette indexed PNG 양자화로 저장 용량을 약 75% 줄여 6400×6400 wafer 이미지와 32×32 chip grid (1,024 chip / wafer, chip 당 200×200 pixel), chip positions JSON 을 산출합니다. chip positions JSON 은 Stage 2 ROI YOLO 와 후속 chip-CNN object-id map 입력 좌표로 그대로 재사용됩니다.

**[알고리즘]** 모델 선택과 결합 구조는 본 과제 데이터 특성에 맞춰 다음과 같이 결정했습니다.

**(1) Stage 1 Backbone — ConvNeXtV2 선택과 fine-tune 설계**

먼저 Transformer 와 CNN 을 같은 split 에서 비교했습니다.

- **도메인 판단**: ViT, Swin 같은 전역 attention 기반 backbone 은 wafer 전체 구조를 보는 데 강합니다. 다만 본 과제의 결함은 특정 zone 이나 국소 chip 영역에 몰리는 경우가 많아, CNN 계열의 local receptive field 와 계층적 feature extraction 이 더 어울린다고 판단했습니다 (자문: 연세대학교 인공지능학과 전해곤 교수).
- **비교 결과**: 동일 4:1 stratified split 에서 Optuna sweep 으로 hyperparameter 를 정렬한 뒤 측정했습니다. 결과는 ViT 0.81 / Swin 0.84 / EffNetV2 0.85 / MaxViT 0.87 / ConvNeXtV2 0.87 입니다.
- **최종 선택**: ConvNeXtV2 는 MaxViT 와 동일한 F1 0.87 을 유지하면서 파라미터 26% (119.5M → 88.6M), FLOPs 39% (74.2G → 45.1G) 감소가 따라와 양산 inference 비용 측면에서 최종 backbone 으로 채택했습니다.
- **과적합 제어**: 본 과제는 label 이 1,500장 / 16 class 로 작은 편입니다. backbone 전체를 풀 미세조정하면 좁은 class 분포에 빠르게 과적합될 수 있어, ConvNeXtV2 block 본체의 학습률은 낮게 두고 분류 head 와 마지막 stage 만 분리해 올렸습니다.
- **Layer-wise learning rate**: backbone block 본체에 가장 낮은 base learning rate 를 적용하고, 마지막 stage 는 그 약 3배, 분류 head 는 약 10배로 올려 학습했습니다. backbone 사전 학습 표현은 그대로 보존하고 분류 head 만 본 과제 분포에 맞춰 빠르게 적응시키는 구조입니다.

**(2) Stage 2 ROI 보정 — cascade gate 와 보정 결정 로직**

Stage 1 만으로는 center 영역의 비슷한 class 들이 헷갈리는 한계가 남아, wafer-level confidence 가 낮은 difficult sample 만 ROI YOLO 로 넘기는 cascade gate 를 잡았습니다. confidence ≥ gate 인 wafer 는 Stage 2 를 건너뛰어 throughput 손실 없이 헷갈리는 sample 의 분리력만 선택적으로 보강합니다. skip 된 wafer 일부는 일일 sampling 으로 Stage 2 재검증 + Stage 1 분포 drift monitoring 으로 gate 를 주기적으로 재조정합니다. 단계별 ladder 는 [구현 성과] 기술 지표에 모았습니다.

**(3) 후속 보정 — chip-CNN object-id map 재구성 (개발 중)**

Stage 1 wafer-level CNN 은 그대로 두고 Stage 2 ROI-YOLO 자리를 chip-CNN object-id map 으로 대체하는 후속 모듈을 개발 중이며 (val_f1 **0.9946** / test_f1 0.9872 / 5-seed 평균 0.9838 ± 0.0092), deploy 는 validation 검증 후 운영 절차에 따라 결정합니다.

chip-CNN object-id map 의 내부 흐름은 아래 식으로 정리했습니다.

```
c_{u,v} = crop(x, pos_{u,v})
q_{u,v} = softmax(h_phi(c_{u,v}))
M_obj(u,v) = argmax_k q_{u,v,k}
```

`c_{u,v}` 는 wafer 내 (u,v) 위치의 chip crop (256×256 입력), `h_phi` 는 chip-CNN, `M_obj` 는 chip 위치별 failure family map 입니다. 이 map 이 Stage 2 의 posterior p_chip_obj(y | crop(x)) 로 들어가, 기존 Stage 2 ROI-YOLO 자리를 대체할 수 있는 모듈 형태로 구성됩니다.

**[최적화]** Known 2-stage 에서 결정적이었던 두 step 은 backbone 교체 (0.78 → 0.87) 와 cascade 결합 (0.92 → 0.95) 입니다. Unknown 검출은 실전 현업 데이터에서 13 후보 group 중 7개 실제 불량 확인을 대표 anchor 로 두고, contrastive recipe ablation (DenseCL / MoCo Queue / NV-Retriever 등) 은 추가 생성 데이터셋 기반 별도 트랙으로 분리 관리합니다.

```
┌─ Stage 1: ConvNeXtV2 wafer classifier (16-class) ────────────────────────┐
│ backbone 비교 ViT 0.81 / Swin 0.84 / EffV2 0.85 / MaxViT 0.87 / Conv 0.87 │
│ MaxViT 대비 param −26% / FLOPs −39% / FT LR head 10× last stage 3×        │
│ ladder: 0.78 → 0.87 (backbone) → 0.92 (Optuna)                            │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   ▼
       ┌─ cascade gate: confidence < τ_gate (difficult sample) ─┐
       │                                                         │
   conf ≥ gate                                          conf < gate
       │                                                         │
       ▼                                                         ▼
 Stage 1 채택            ┌─ Stage 2 (운영 절차로 모듈 선택) ────────────────┐
 (skip Stage 2,          │ (A) ROI-YOLO [현재 양산] — bbox + 좌표회귀       │
  throughput≈0)          │     + class + NMS 동시 수행                       │
       │                  │ (B) chip-CNN obj-id map [개발 중] — crop 256×256 │
       │                  │     분류만 / val_f1 0.9946 / test_f1 0.9872      │
       │                  └────────────────────┬─────────────────────────────┘
       └───────────────────────────────────────┤
                                               ▼
┌─ OUTPUT: Known weighted F1 0.95 (16-class / 1,500 / 4:1) ────────────────┐
│ ladder 0.92 → 0.95 (+0.03, cascade 결합)                                  │
│ 운영 안전판: skip wafer 일일 sampling 재검증 + Stage 1 drift monitoring   │
│             → τ_gate 주기 재조정 (FN 누적 차단)                            │
└───────────────────────────────────────────────────────────────────────────┘
```

학습 / 평가에 사용된 실제 wafer 이미지 예시 (2행 3열):

| Edge-Top Scratch | Edge-Ring Scratch_rot | Center Bank-Boundary (신규) |
|:----------------:|:---------------------:|:---------------------------:|
| <img src="./figures/wafer_edge_top_scratch.png" width="180" /> | <img src="./figures/wafer_edge_ring_scratch_rot.png" width="180" /> | <img src="./figures/wafer_center_bank_boundary.png" width="180" /> |
| **BrokenRing** | **RingDots** | **CrescentArc (신규)** |
| <img src="./figures/wafer_brokenring.png" width="180" /> | <img src="./figures/wafer_ringdots.png" width="180" /> | <img src="./figures/wafer_crescentarc.png" width="180" /> |

Stage 1 만으로 헷갈리는 사례를 Stage 2 ROI YOLO 가 보정하는 흐름:

| Stage 1 (raw wafer) | Stage 2 ROI 영역 | Stage 2 chip 단위 box + class |
|:-------------------:|:----------------:|:-----------------------------:|
| <img src="./figures/wafer_center_scratch.png" height="280" /> | <img src="./figures/p1_roi_crop_real.png" height="280" /> | <img src="./figures/p1_chip_yolo_box_real.png" height="280" /> |

좌측 raw wafer 는 Stage 1 wafer-level CNN 만 보면 비슷한 형상의 class 로 오인되는 사례입니다. Stage 2 ROI YOLO 가 chip 단위 box 와 class 라벨을 다수 출력하고, 그 분포 majority 로 다시 정확한 class 로 잡아주는 구조입니다.

후속 chip-CNN object-id map 재구성 흐름은 다음과 같이 두었습니다.

```
┌─ INPUT: wafer 6400×6400 PNG + chip positions JSON (32×32 grid) ──────────┐
│ chip 좌표 pos_{u,v} 확정 — detection 단계 생략                            │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   ▼
┌─ Step 1-3: chip 단위 분류 + wafer 좌표계 재구성 ──────────────────────────┐
│ c_{u,v} = crop(x, pos_{u,v}), 입력 256×256                                │
│ q_{u,v} = softmax(h_φ(c_{u,v})) ∈ R^K   ← chip 분류만 수행                │
│ M_obj(u,v) = argmax_k q_{u,v,k}          ← 32×32×5 one-hot map 재구성      │
│ 성능: val_f1 0.9946 / test_f1 0.9872 / 5-seed 0.9838 ± 0.0092             │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   ▼
┌─ Step 4: Stage 2 ROI-YOLO 대체 모듈로 결합 ──────────────────────────────┐
│ M_obj → Stage 2 posterior p_chip_obj(y | crop(x))                          │
│ 양산 진입: Stage 2 자리에 ROI-YOLO 또는 chip-CNN 중 하나만                 │
│ deploy 결정: validation 검증 후 운영 절차에 따라                            │
└───────────────────────────────────────────────────────────────────────────┘

┌─ 두 모듈의 차이 ─────────────────────────────────────────────────────────┐
│ ROI-YOLO 는 chip 위치를 모르는 상태에서 box / 좌표 / class / NMS 를       │
│ 한꺼번에 학습해야 하지만, chip-CNN 은 chip 좌표가 이미 확정된 자리에      │
│ 들어가 chip crop 분류만 하면 됩니다. 학습이 분류 한 가지로 좁아지면서     │
│ 정확도가 올라가고 latency 가 줄었고, class 가 추가될 때 annotation 도     │
│ 가벼워졌습니다. 이 차이가 chip-CNN 으로 교체를 검토하게 된 이유입니다.    │
└───────────────────────────────────────────────────────────────────────────┘
```

raw wafer map (좌측 2칸) 과 동일 wafer 의 chip-CNN object-id map (우측 2칸) 비교:

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

**ㅁ 구현 성과**

**[정량적/정성적 성과]**

- **기술 지표**
  - **[실전 현업 데이터]** Known 2-stage weighted F1 **0.95** (16 class / 1,500 labeled samples / 4:1 stratified split). 단계별 ladder 는 0.78 (baseline) → 0.87 (ConvNeXtV2 backbone 교체) → 0.92 (+Optuna hyperparameter optimization) → **0.95** (+ROI YOLO 2-stage 보정) 로 누적되었습니다. label 부족 조건에서 backbone 교체와 cascade 결합이 결정적이었습니다.
  - **[실전 현업 데이터]** Unknown 검출은 특정 제품 실전 데이터 1만 장 학습 후, 학습에 쓰지 않은 별도 2,000장에 적용해 13 후보 group 중 7개가 실제 불량으로 현업 확인되었습니다. 정답 label 이 없는 환경이라 정량 metric 대신 현업 확인 결과로 보고합니다.
  - **[Unknown 추가 생성 데이터, 개발 중]** 현업 데이터와 최대한 유사하게 구성한 별도 평가셋에서 신규 class **capture 1.000 (38/38 발견)** / **noise 0.00%** / **Completeness 0.9938** / **Silhouette 0.781** 까지 측정했고, 실전 Unknown 운영 성과 (13 후보 → 7 실제 불량 confirm) 와는 분리한 심화 질의 대비 근거입니다.
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

  본 표는 per class 500 sample + Normal 2000 sample 평가셋 기준의 잠정값이며, 진행 중인 n500 전수 evaluation 이 완료되면 정식 값으로 갱신할 예정입니다. 또한 P1 Unknown 의 실전 현업 확인 성과 (13 후보 중 7 실제 불량 현업 확인) 와는 분리된 후속 개발 / metric 관리용 synthetic benchmark 결과입니다. 실전 Unknown 에는 정답 label 이 없어 F1 / ARI / recall 같은 정량 metric 이 성립하지 않고, 13/7 현업 확인은 후보 압축 결과이지 분류 metric 이 아닙니다.

- **현업 임팩트**
  - **[양산 적용 단계]** 2025년 5월부터 DRAM 전제품 라인 Failbit Map 을 120일치씩 누적 처리 중이며, 일 약 2만 wafer 규모입니다.
  - **[전수 자동 적용 단계 확장 계획]** 전수 자동 추론으로 확장하려면 추가 GPU 자원이 필요하며, AI 센터 GPU 할당 기준 **2026년 9월** 제공이 예정되어 있습니다. GPU 할당 후 현재 검증된 Known / Unknown 모델을 전수 자동 추론 흐름으로 단계 확장할 계획입니다.

**ㅁ P2. Chip Multi-label Classification**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Chip multi-label classification — CutMix → CutMix + Pair Mask → FCM-PM |
| 수행기간 | 2025년 3월 ~ 현재 |
| 참여인원 | 본인 / 관리자 |

**ㅁ 과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|----|------|---------|------|------|--------|
| 1 | 최호길 | 개인정보 비공개 | 메모리제조센터 QIE그룹 | chip single / 2-combo 합성, CutMix 계열 선정, Pair Mask loss masking 설계, FCM-PM 본 과제 신규 적용, val_margin 기반 best-model selection, Temperature Scaling, pos/neg target asymmetry sweep, max-prob threshold gate, bit-level majority voting ensemble, Knowledge Distillation 압축 후보 검토 | 80% |
| 2 | 관리자 | 개인정보 비공개 | 관리조직 (공식 기록 대조) | 방향성, 일정, 리뷰 매니징 | 20% |

**ㅁ 개인별 기여 서술**

P2 는 chip 하나에 multi-label failure 가 같이 발생하는 사례까지 검출하기 위한 과제입니다. 현업에서 single failure 원천은 충분히 쌓여 있지만 2-combo 이상 동시 발생 데이터는 부족해, single failure 원천을 확장해 multi-label 학습 / 평가 환경을 구성했습니다.

- single failure 원천 데이터는 Grade 의미와 결함 분포를 유지했습니다.
- 2-combo label 부족은 FCM-PM 으로 도메인 분포에 맞춰 보완했습니다.
- Normal / Invalid / OOD negative 평가셋은 현업 분포에 가깝게 직접 설계했습니다.
- 목표는 bit_F1 만 올리는 것이 아니라, false-positive 리스크를 사전에 확인하는 구조를 만드는 것이었습니다.

본 과제의 핵심은 chip 하나의 multi-label failure 를 안정적으로 분석하고 검출하기 위해, 본 과제 데이터 구조에 맞춰 합성 / 손실 / 모델 선택 / 추론 기법을 직접 설계해 결합한 것입니다.

**[평가 지표]** single F1 은 single failure class 별 F1 의 평균입니다. bit_F1 은 한 chip 의 label 을 `[0, 1, 1, 0]` 같은 4-bit vector 로 보고 각 bit 별로 정답 여부를 따집니다. 예를 들어 정답이 `[0, 1, 1, 0]` 일 때 예측이 `[1, 1, 1, 0]` 이면 첫 bit 가 틀린 것이고, `[0, 1, 1, 0]` 처럼 모든 bit 가 정확히 맞아야 정답입니다. multi-label 에서는 한 chip 안에 여러 failure 가 동시에 켜질 수 있어, 모든 bit (chip × class) 를 micro-averaged 로 합쳐 본 bit_F1 이 전체 검출 품질을 가장 잘 보여줍니다. 제출 대표 수치 0.9943 도 bit_F1 기준입니다.

- **데이터 합성**: FCM-PM 으로 2-combo 결함 학습 신호를 구성했습니다.
- **손실 통제**: Pair Mask 로 합성 background 의 오학습 경로를 분리했습니다.
- **모델 선택**: `val_margin` 기준으로 false-alarm 위험까지 checkpoint 선택에 반영했습니다.
- **추론 최적화**: max-prob threshold gate, bit-level majority voting ensemble (champion `vote_majority_bits`, bit_F1 0.9941 / Total False Alarm Rate (FAR) 0.00%), Knowledge Distillation single student (1× cost) 압축 후보 검토를 대표 성과와 분리해 관리했습니다.

기존 BCE, Focal, ASL 같은 loss 변경만으로는 2-combo recall 과 false alarm 억제를 동시에 만족시키기 어려웠습니다. 본인은 아래 세 조건이 같이 필요하다고 봤고, 이를 FCM-PM 과 val_margin checkpoint selection 으로 묶었습니다.

- Grade 0-7 결함 픽셀 의미 보존
- chip 내부 failure signal coverage 보장
- 합성 background 의 오학습 억제

**P2 대표 성과 / 후속 개발 / 한계 및 관리**

- **대표 성과**: FCM-PM val_margin 단일 모델 bit_F1 **0.9943** / Total FAR **0.00%** 입니다.
- **후속 개발**: bit-level majority voting ensemble (champion `vote_majority_bits`, bit_F1 0.9941 / Total FAR 0.00%) 은 실전 운영의 모델 안정성 확보, Knowledge Distillation single student 는 양산 추론 생산성 (single-model latency) 확보를 위한 압축 후보로 검토 중이며, 운영 threshold calibration 과 함께 대표 성과와 분리해 관리합니다.
- **한계 및 관리**: P2 결과는 실제 현업 발생 failure 를 최대한 동일하게 구현하고 Normal / Invalid / OOD 같은 negative 환경까지 동일하게 구성한 controlled benchmark 기준입니다. single failure 4 class 의 가능한 2-combo 6종을 모두 포함해 조합 누락 없이 평가했으며, 실제 운영에서 추가될 수 있는 신규 failure class 와 장기 운영 분포 변화는 후속 확장 및 검증 대상으로 분리합니다.

처음에는 BCE + Label Smoothing 으로 시작했지만 2-combo 신호 자체가 거의 학습되지 않았습니다. Focal 이나 ASL 로 loss 만 바꿔봐도 false-positive 는 크게 줄지 않았습니다. 다음으로 CutMix 를 시도했더니 두 가지 문제가 같이 나왔습니다. 직사각형 영역만 잘라 붙이다 보니 정작 결함 위치가 잘려 학습 신호가 사라지는 경우가 있었고, 잘라 붙이지 않은 background 영역이 failure 로 학습되면서 Normal / Invalid / OOD negative 에서 false-positive 가 크게 늘었습니다.

본인은 이를 Full-Cover Mixup 과 Pair Mask 로 나누어 풀었습니다.

- **Full-Cover Mixup**: pixel-level MIN-BLEND (`np.minimum(a, b)`) 로 Grade 원값을 보존하면서 chip 전체 grid 를 cover 합니다. 합성 sanity 는 `failure_pixel_ratio(blended) ≥ max(d_i) - 0.01` 로 두어 입력 chip 의 failure signal 이 잘리지 않도록 잡았습니다.
- **Pair Mask**: 합성 영역과 background 를 구분하는 binary mask M (M_ij ∈ {0, 1}) 으로 loss 를 `L = Σ_ij M_ij · BCE(y_ij, ŷ_ij)` 에 제한해 background 픽셀 / bit 를 학습에서 제외합니다.
- **Pair Mask 제거 ablation**: Total FAR 이 **100%** 까지 치솟아, background loss 가 false-positive 의 핵심 원인임이 정량으로 확인됐습니다.

마지막 쟁점은 best epoch 선택이었습니다. 작은 validation set 에서는 val_f1 이 여러 epoch 에서 같은 값으로 붙어 선택이 흔들렸습니다. 그래서 본인은 `val_margin = mean(score over positive bits) - max(score over negative bits)` 를 기준으로 잡았습니다. val_margin 으로 고른 epoch 이 val_f1 보다 실제 test bit_F1 을 훨씬 정확히 예측합니다 (Spearman ρ val_margin +0.56 vs val_f1 −0.10). 즉 val_margin 기준 best checkpoint 가 실제 test 성능을 더 안정적으로 끌어올립니다.

이후 운영 환경 약 80% Normal 분포에 대응하는 추론 단계를 같이 검토했습니다.

- **Maximum probability threshold gate**: 운영 80% Normal 분포 사전 정보를 반영해 max-prob < 0.55 일 때 Normal 로 강제, 운영 false-positive 를 한 단계 더 줄였습니다.
- **pos / neg target 설계**: 최종 채택은 positive target 0.85 / negative target 0.15 입니다. 비대칭 positive target 0.95 / negative target 0.30 조합도 별도 trial 로 검토했지만 Normal / Invalid / OOD negative 평가에서 FAR 가 collapse 해 채택하지 않았고, 본 과제에서는 symmetric 0.85 / 0.15 가 bit_F1 과 FAR 안정성을 같이 만족한다는 결론이었습니다.
- **Majority Voting Ensemble**: bit 단위 majority voting 으로 단일 모델이 흔들리는 cell 도 다른 두 모델의 합의로 잡아내는 보조 실험입니다. champion `vote_majority_bits` 가 bit_F1 0.9941 / Total FAR 0.00% 로 단일 대표 모델 (0.9943) 과 동급 수준에 zero FAR 까지 확인했습니다.
- **Knowledge Distillation (single student)**: 양산 추론 비용을 단일 모델 수준으로 줄이는 압축 후보로, 학생 모델 collapse 회피 설정까지 검증 완료한 상태입니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | chip 내부 failure 위치를 사전에 알 수 없고, single failure chip 만 가지고 multi-label 평가로 확장해야 합니다. |
| 기존 방식의 한계 | 일반 CutMix 는 일부 영역만 잘라 붙이다 보니 failure signal 이 잘려 버리거나 background 가 failure 로 학습되어 버려서, Normal / Invalid / OOD negative 평가에서 false-positive 가 운영에 쓰기 어려운 수준까지 올라갑니다. |
| 기술적 / 환경적 제약 | 2-combo label 부족, 작은 validation set 의 best epoch plateau, OOD / negative false-positive 억제, 압축 후보의 1× inference cost 제약이 한꺼번에 묶여 있습니다. |

**ㅁ 기술적 해결 방안**

**[데이터]** 실제 현업 chip 의 single failure 4 class 위에 두 결함씩 조합한 2-combo 6 종을 합성해, 현업 multi-label failure 양상과 매우 유사한 학습 / 평가 데이터를 구성했습니다. negative 측은 Normal (정상 chip 분포 모사) + Invalid + OOD wafer-pattern + OOD synthetic 까지 같이 두어 single 4 + 2-combo 6 + negative 6 = 16+ class × 약 3,850 chip 규모의 controlled benchmark 가 되도록 잡았습니다.

data leakage 방지를 위해 single failure chip 원천을 chip 단위로 먼저 train / test 로 split 한 뒤, 2-combo 와 Pair Mask 합성은 train 원천 chip 만 사용했습니다. test 원천 chip 은 합성 과정에서 완전히 배제되어 train / test 사이 chip 단위 누수가 없도록 잡았습니다.

**[P2 수식 요약]**

```
p_k = sigmoid(z_k),  k = 1..K

L_BCE = -Σ_k [y_k log p_k + (1-y_k) log(1-p_k)]

x_tilde = Σ_r M_r ⊙ T_r(x_r)
y_tilde = OR_r y_r

L_PM = Σ_{i,k} M_{i,k} · BCE(y_{i,k}, p_{i,k})
       / (Σ_{i,k} M_{i,k} + ε)

val_margin = mean_{k in P+}(p_k) - max_{j in P-}(p_j)

FAR = FP_negative / N_negative
```

softmax 대신 sigmoid multi-label head 를 쓴 이유는 single failure 와 2-combo failure 가 mutually exclusive 가 아니기 때문입니다. FCM-PM 합성은 포함된 failure label 의 union 을 target 으로 두고, Pair Mask loss 는 합성 background 가 failure negative 로 과도하게 학습되는 경로를 끊습니다. FAR 는 Normal / Invalid / OOD negative set 에서 별도로 계산해 운영 false-positive 위험을 직접 보게 했습니다.

```
┌─ SOURCE: 실전 현업 single failure chip 4 class (Grade 0~7) ──────────────┐
│ 실제 현업 EDS Failbit Map 에서 관찰되는 failure 형태 기준 4 class 구성     │
│ chip 단위 train / test split 먼저 → 합성 누수 차단                         │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   ▼
┌─ Step 1-2: CutMix 계열 채택 + 한계 진단 ─────────────────────────────────┐
│ Mixup/Diffusion 픽셀 보간 → Grade 의미 깨짐 → 부적합                       │
│ CutMix 영역 단위 → Grade 원값 보존 (자문: 박은병 교수)                     │
│ random CutMix 한계: signal 잘림 + background → failure 오학습 → FAR ↑     │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   │
                  ┌────────────────┴────────────────┐
                  ▼                                 ▼
┌─ Step 3a: Full-Cover Mixup ───┐  ┌─ Step 3b: Pair Mask ──────────────────┐
│ pixel-level MIN-BLEND          │  │ binary mask M_ij ∈ {0,1}              │
│ np.minimum(a, b) → Grade 보존  │  │ L = Σ M_ij · BCE(y_ij, ŷ_ij)         │
│ sanity: failure_pixel_ratio    │  │ 합성 영역만 loss 진입                  │
│         ≥ max(d_i) − 0.01      │  │ (background bit 제외)                  │
└────────────────┬───────────────┘  └────────────────┬──────────────────────┘
                 └───────────────┬───────────────────┘
                                 ▼
┌─ Step 4-5: FCM-PM 학습 + val_margin checkpoint selection ────────────────┐
│ val_margin = mean(pos bit score) − max(neg bit score)                     │
│ Spearman ρ(epoch, test_f1): val_margin +0.56 / val_f1 −0.10               │
│ positive target 0.85 / negative target 0.15 (symmetric)                   │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   ▼
┌─ Step 6: Inference 단 운영 안전판 ───────────────────────────────────────┐
│ max-prob threshold gate: max-prob<0.55 → Normal 강제 (운영 80% Normal)    │
│ bit-level majority voting ensemble: champion `vote_majority_bits`         │
│   bit_F1 0.9941 / Total FAR 0.00% — 3 모델 bit 단위 majority voting       │
│   (단일 모델 흔들리는 cell 도 다른 두 모델 합의로 보정)                    │
│ Knowledge Distillation single student: ensemble 판단을 단일 모델 추론     │
│   비용 (1x latency/throughput/params) 으로 압축하는 양산 배포 후보         │
└───────────────────────────────────────────────────────────────────────────┘
```

학습 원천 single 4 class 예시 chip:

<p align="left">
  <img src="./figures/chip_eval_bank_boundary_selected.png" width="160" />
  <img src="./figures/chip_eval_fork_selected.png" width="160" />
  <img src="./figures/chip_eval_scratch_selected.png" width="160" />
  <img src="./figures/chip_eval_scratch_rot_selected.png" width="160" />
</p>

single 4 class 의 모든 2-조합으로 만든 2-combo 평가 chip 6종:

<p align="left">
  <img src="./figures/chip_combo_bb_fork_selected.png" width="130" />
  <img src="./figures/chip_combo_bb_scratch_selected.png" width="130" />
  <img src="./figures/chip_combo_bb_scratch_rot_selected.png" width="130" />
  <img src="./figures/chip_combo_fork_scratch_selected.png" width="130" />
  <img src="./figures/chip_combo_fork_scratch_rot_selected.png" width="130" />
  <img src="./figures/chip_combo_scratch_scratch_rot_selected.png" width="130" />
</p>

Normal / Invalid / OOD negative 평가셋 예시:

<p align="left">
  <img src="./figures/chip_eval_normal_selected.png" width="130" />
  <img src="./figures/chip_eval_invalid_selected.png" width="130" />
  <img src="./figures/chip_ood_starburst_selected.png" width="130" />
  <img src="./figures/chip_ood_centerdonut_selected.png" width="130" />
  <img src="./figures/chip_ood_crossscratch_selected.png" width="130" />
  <img src="./figures/chip_ood_diagonalsmear_selected.png" width="130" />
</p>

**[알고리즘]** 합성 / 손실 / 선택 / 추론 네 단계로 본 과제 데이터 특성에 맞춰 본인이 직접 설계했습니다.

**(1) 합성 — CutMix 계열 채택과 Full-Cover Mixup 확장**

Grade 0-7 양자화 chip 이미지를 다루는 본 과제에서는 생성 방식 선택이 곧 label 의미 보존 문제였습니다.

- **Mixup 배제**: 입력과 label 을 함께 보간하면 Grade 0-7 사이에 실재하지 않는 중간 grade 가 만들어져 분류기가 그 값을 noise 로 학습할 위험이 있습니다.
- **Diffusion 보류**: Diffusion 으로 본 과제 수준의 chip 이미지를 생성하려면 충분한 실제 2-combo 분포가 학습 데이터로 먼저 쌓여 있어야 하는데, 본 과제는 그 데이터 자체가 부족한 상황이라 운영 적용 후보로 두지 않았습니다.
- **CutMix 계열 채택**: 영역 단위로 원값을 보존해 붙이는 CutMix 계열이 양자화 의미 보존 측면에서 적합하다고 본인이 판단해 채택했습니다 (자문: 연세대학교 인공지능학과 박은병 교수).
- **Full-Cover Mixup 확장**: 일반 CutMix 는 일부 직사각형 영역만 잘라 붙입니다. chip 내부 어디에 failure 가 올지 모르는 본 과제에서는 failure signal 이 잘릴 위험이 남아, chip 전체 grid 를 cover 하는 Full-Cover Mixup 으로 확장했습니다 (현업 Overlay dynamic sampling 경험에서 wafer 전 영역을 빠짐없이 cover 해야 sampling 누락이 없다는 아이디어를 가져옴).

**(2) 손실 — Pair Mask 와 background loss 제외**

합성 단계에서 잘라 붙인 영역 / background 영역을 구분하는 binary mask M (M_ij ∈ {0, 1}) 를 같이 만들고, 학습 loss 를 다음과 같이 정의했습니다.

```
L = Σ_ij M_ij · BCE(y_ij, ŷ_ij)
```

M_ij = 1 인 영역만 loss 에 들어가므로 background 픽셀 / bit 는 학습에서 제외되고, Normal / Invalid / OOD negative 에서 background 가 failure 로 오학습되는 경로가 끊깁니다. Pair Mask 를 빼면 Total FAR 이 100% 까지 치솟는 PoC 결과가 본 설계의 직접 근거입니다.

**(3) checkpoint 선택 — val_margin 정의**

val_margin = mean(score over positive bits) − max(score over negative bits)

평균과 최대의 차이로 정의했기에 val_f1 plateau 구간에서도 미세 변동이 남아 best epoch 이 흔들리지 않습니다. negative 측 최대를 쓴 정의 근거는 §개인별 기여 서술 에서 풀어 적었습니다. epoch-vs-test_f1 Spearman ρ 는 val_margin +0.56 / val_f1 −0.10 으로, val_margin 이 ground-truth test_f1 과 양의 일관성을 보였습니다.

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

**(4) Inference / 후속 — Threshold gate / Ensemble / Knowledge Distillation**

운영 환경 약 80% Normal 분포에 대응해, max-prob<0.55 입력을 Normal 로 강제하는 threshold gate 를 두어 운영 false-positive 를 한 단계 더 억제했습니다. 학습 단계에서는 positive target 0.85 / negative target 0.15 로 negative 측 보수성을 같이 잡았고, bit-level majority voting ensemble (champion `vote_majority_bits`) 은 SOTA 단일 모델이 현업 데이터에서 흔들릴 경우를 대비해 서로 다른 3 모델의 bit 단위 majority voting 으로 운영 안전판을 둔 구조입니다. 단일 모델이 흔들리는 cell 도 다른 두 모델 합의로 보정되며, bit_F1 **0.9941** / Total FAR **0.00%** 로 단일 대표 (0.9943) 와 동급 수준에 zero FAR 까지 확인됐습니다. Knowledge Distillation (single student) 는 CutMix 활성 batch 의 distillation loss 를 제외하는 설정으로 학생 모델 collapse 를 회피했습니다. α / T sweep 으로 KD_v7 (α=0.3, T=2) 에서 bit_F1 **0.9265** 첫 안정, KD_v12 (α=0.3, T=3) 에서 bit_F1 **0.9470** / Total FAR **0.00%** 까지 끌어올려 KD sweep 현 최고점을 확보했습니다. 같은 sweep 에서 α=0.25 (KD_v11, bit_F1 0.9192) 와 T=4 (KD_v13, 0.9347) 는 KD_v12 대비 열등해 α=0.30 / T=3 이 본 데이터 sweet spot 임을 정량으로 확인했습니다. 대표 모델보다 bit_F1 이 낮아 후속 압축 후보로만 두었습니다.

**[최적화]** 합성 단계에서는 CutMix → CutMix + Pair → FCM-PM 순서로 단계별 효과를 직접 측정했고, false-positive 와 bit_F1 의 trade-off 가 어디서 깨지는지를 아래 ablation 표로 추적했습니다.

- **cover grid sweep**: chip 분할 그룹 수 (partition count) 와 그룹 내 cell 세분화 배수 (grid multiplier) 를 범위로 sweep, **partition=3 / multiplier=1 조합이 bit_F1 0.9960** 으로 최적이었습니다.
- **분할 선택 근거**: partition 수를 키우면 chip 이 더 잘게 쪼개져 공간 다양성은 올라가지만, 본 데이터의 좁고 긴 결함 형태가 partition≥4 부터 grid 경계에 잘려 **분리력이 오히려 떨어집니다**. partition=3 부근이 본 과제 데이터에 최적이었습니다.
- **pos / neg target 선택**: 본 데이터에서는 positive target 0.85 / negative target 0.15 (symmetric) 가 bit_F1 과 FAR 안정성을 동시에 만족했습니다. 비대칭 positive target 0.95 / negative target 0.30 trial 은 별도로 검토했지만 Normal / Invalid / OOD negative 평가에서 FAR collapse 가 확인되어 채택하지 않았습니다.

**ㅁ 구현 성과**

**[정량적/정성적 성과]** (P2 성과는 **[현업 failure chip 원천 + 도메인 확률분포 기반 생성/검증]** 위에서 측정한 값입니다. 아래 성과 항목별 데이터 출처는 inline 라벨로 분리 표기합니다.)

- **기술 지표** (단계별 적용 효과):
  - 학습 ladder: BCE+Label Smoothing → Focal / ASL loss 변형 → 단순 CutMix → **FCM-PM (Full-Cover Mixup + Pair Mask) + val_margin best-model selection** 순으로 단계별 적용해 bit_F1 0.1093 → **0.9943** / Total FAR 99.47% → **0.00%** 까지 끌어올렸습니다.
  - 핵심 근거: Pair Mask 제거 시 Total FAR 이 **100%** 로 치솟아, **background loss 분리가 false-positive 억제 핵심 요인**임을 직접 확인했습니다.
  - val_margin 기반 best-model selection 이 val_f1 보다 실제 test bit_F1 을 훨씬 정확히 예측 (Spearman ρ **+0.56 vs −0.10**) — best epoch 안정성 확보.
  - 운영 안전판: max-prob threshold gate + bit-level majority voting ensemble (champion `vote_majority_bits` bit_F1 0.9941 / Total FAR 0.00%) + Knowledge Distillation single student 압축 후보.

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
  | 9 | Knowledge Distillation (KD_v7 α=0.3 T=2) | 0.9265 | 0.9785 | TBD | 0.00% | 0.00% | 0.00% | 1x | 1x | 1x | 압축 후보 — collapse 회피 첫 안정 |
  | 10 | Knowledge Distillation (KD_v12 α=0.3 T=3) | **0.9470** | TBD | TBD | **0.00%** | 0.00% | 0.00% | 1x | 1x | 1x | 압축 후보 — KD sweep 현 최고점 |

  본 표는 per class 2000 chip 합성 평가셋 기준의 잠정값이며, 추가 evaluation 이 완료되면 정식 값으로 갱신할 예정입니다. row 8 의 ensemble 은 보조 안정성 실험으로 01_career_profile.md / 02_ai_portfolio.md 의 ensemble 수치와는 동일 실험이 아닙니다. 표 row 1~7 흐름을 보면 CutMix 단독으로는 FAR 이 운영에 쓰기 어려운 구간에 남고, FCM-PM + val_margin 으로 와서야 bit_F1 0.9943 / Total FAR 0.00% 의 균형이 맞춰집니다. 제출 대표 성과는 row 7 (bit_F1 0.9943 / Total FAR 0.00%) 로 고정합니다.

- **현업 임팩트**
  - 실전 single failure chip 원천 위에 부족한 2-combo 결함을 도메인 분포로 합성해 multi-label 학습 / 평가가 가능해졌습니다. 현업에서는 2-combo label 수와 균형을 얻기 어려워 사실상 막혀 있던 분류 문제를, 반도체 도메인 (Grade 0-7 의미와 failure 위치 / 강도 / 조합 분포) 위에서 다시 푼 방법론입니다.
  - 현업 eval 환경을 얻기 어려운 상황에서 Normal / Invalid / OOD negative 평가셋을 현업 분포에 가깝게 직접 설계한 점도 본 과제 변별 포인트입니다.
  - 정량으로는 bit F1 0.9943, Normal / Invalid / OOD negative Total FAR 0.00% 로 양산 적용 전 false-positive 리스크 검증을 마쳤습니다.
  - val_margin 기반 best-model 선택은 작은 validation set 의 plateau 흔들림을 제어하는 안전판으로 같이 들어 있습니다.
  - 이 구조는 P1 의 wafer-level 판단을 chip 좌표계로 정밀화하는 후속 기반으로도 이어집니다.


**ㅁ P3. Trend Episode 데이터 생성 기반 Anomaly-detection 검증 PoC**

**ㅁ 과제 기본정보**

| 항목 | 내용 |
|------|------|
| 과제명 | Trend episode 데이터 생성 기반 Anomaly-detection 검증 PoC |
| 수행기간 | 2026년 1월 ~ 현재 |
| 참여인원 | 본인 / 관리자 / 동료 엔지니어 (공동 연구자) |

**ㅁ 과제 참여 인력 및 역할**

| NO | 성명 | Knox Id | 소속 | 역할 | 기여도 |
|----|------|---------|------|------|--------|
| 1 | 최호길 | 개인정보 비공개 | 메모리제조센터 QIE그룹 | trend episode 합성 generator 설계, Region 5종 / Noise 3종 / trend 불량 4종 + context 1종 parameter 코드화, 합성 normal 산포의 상한 / 하한을 같이 잡는 두 가지 수식 설계, 1차 Binary gate 검증 PoC 설계 / 구현 | 70% |
| 2 | 관리자 | 개인정보 비공개 | 관리조직 (공식 기록 대조) | 방향성, 일정, 리뷰 매니징 | 20% |
| 3 | 동료 엔지니어 (공동 연구자) | 개인정보 비공개 | 관련 엔지니어 조직 (공식 기록 대조) | AI 모델 실행, 데이터 정리, 실험 결과 취합 | 10% |

**ㅁ 개인별 기여 서술**

P3 의 본인 기여는 데이터를 만들어 내는 쪽입니다. 본인이 BBD담당 / Overlay담당 / CD담당으로 trend chart 를 직접 판정해 온 업무 경험에서 **mean shift** (평균 변동), **standard deviation** (산포 변동), **spike** (순간 튐), **drift** (미세 이동), **context** (다른 legend 대비 튀는 경우) 같은 불량 형태가 어느 강도에서 실제 spec out 으로 이어지는지 알고 있었고, 그 판단 기준을 synthetic trend episode generator 의 parameter 로 직접 옮겨 코드화했습니다. 1차 Binary gate 는 만들어 낸 데이터가 정상 / 이상 패턴을 학습 가능한 형태로 담고 있는지 확인하기 위한 검증용 baseline 으로 두었습니다 (실전 현업 검증과 분리). 동료 엔지니어는 AI 모델 실행, 데이터 정리, 실험 결과 취합을 공동 수행했습니다.

먼저 **Noise 분포** (Gaussian / Laplacian / Correlated) 와 **계측 밀도 영역 분리** (밀집 dense / 희박 sparse / very_sparse / thin / 공핍 missing) 로 합성 normal baseline 을 실전 환경에 최대한 가깝게 구현했고, 그 위에 본인 담당 경험에서 알고 있던 **불량 형태별 강도 구간** (mean shift / standard deviation / spike / drift / context) 을 더해 학습 가능한 데이터 자산을 만들었습니다. 합성 normal 이 실전 baseline 통계 안에 들어가면서도 abnormal 강도가 정상 산포에 묻히지 않도록 두 조건을 같이 잡았고, 구체 parameter / 식 / 단계 흐름은 [기술적 해결 방안] 과 다이어그램에 모았습니다.

**ㅁ 문제정의**

| 항목 | 내용 |
|------|------|
| 현장 난제 | trend 이상은 단순 threshold 만으로 판정하기 어렵고, 설비 산포 / hunting / drift / baseline 평탄도 / spec-in 변동 가능성을 같이 봐야 합니다. |
| 기존 방식의 한계 | 실전 abnormal data 는 양과 label 균형 확보가 어려운 위에 수작업 chart 판독까지 의존하다 보니 초보자 누락과 모니터링 시간 부담이 같이 누적됩니다. |
| 기술적 / 환경적 제약 | 실전 label 부족을 전제로 trend domain knowledge 를 합성 데이터 parameter 로 옮기는 단계가 먼저 풀려야 뒤 단계 검증이 가능합니다. |

**ㅁ 기술적 해결 방안**

본인이 잡은 흐름은 (1) **담당 경험을 generator parameter 로 코드화**, (2) **합성 normal 이 실전 baseline 통계 안에 들어가도록 정합**, (3) **baseline 분류기로 학습 가능성 검증** 세 단계입니다.

1단계는 §개인 기여 단락에 정리한 그대로 — 영역 분리 / Noise 분포 / 불량 형태별 강도 구간을 generator parameter 로 코드화. 2단계는 합성 normal 이 실전 baseline 통계 안에 들어가면서도 abnormal 강도가 정상 산포에 묻히지 않도록 두 가지 수식 (`target_std ≤ fleet_within_std × 1.2` 로 상한, `target_baseline_std = max(baseline_std, 0.01)` 로 하한) 을 같이 두어 합성 normal 의 산포를 위아래로 가두었습니다. 다른 설비 평균 산포 안에 합성 normal 을 가두면서 abnormal 강도는 최소 0.01σ 이상으로 띄워 정상 산포에 묻히지 않게 잡은 식입니다. 3단계는 1차 Binary gate (정상 / 이상) baseline 으로 만든 데이터의 학습 가능성을 점검했고, 본 baseline 은 운영 후보가 아닌 검증 도구로만 두었습니다.

전체 흐름을 도식으로 정리하면 다음과 같습니다.

```
┌─ SOURCE: 본인 BBD담당 / Overlay담당 / CD담당 trend 판정 경력 ────────────┐
│ 판단 기준 (산포 / hunting / drift / spec-in 변동) → generator parameter   │
│ 코드화 — 본 과제 데이터 자산화의 핵심                                      │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   ▼
┌─ Step 1-3: 도메인 분포 코드화 ───────────────────────────────────────────┐
│ Region 5종 (밀도): dense 70-100% / sparse 40-70% / very_sparse 20-35%     │
│                   / thin 10-20% / missing 0%                              │
│ Noise 3분포 (반도체 발생 원리 1:1 매핑):                                  │
│   Gaussian 0.80 = chamber thermal/mechanical 정상 산포                    │
│   Laplacian 0.15 = 설비 hunting 두꺼운 꼬리                                │
│   Correlated 0.05 = 후공정 align 시간축 drift                              │
│ Anomaly 5종: mean_shift / std / spike / drift / context                   │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   ▼
┌─ Step 4-5: 산포 상한 / 하한 두 수식 + Rendering ─────────────────────────┐
│ target_baseline_std = max(baseline_std, 0.01)  ← 최소 σ 하한               │
│ target_std ≤ fleet_within_std × 1.2            ← 같은 설비군 산포 정렬    │
│ → 합성 normal 은 실재 baseline 통계 안, abnormal 강도는 정상 산포 분리    │
│ Rendering: 224×224 PNG, normal 3.5K + abnormal 3.5K = 7,000 trend sample     │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   │
                                   │
                                   ▼
┌─ 1차 Binary gate (정상 / 이상) baseline ─────────────────────────────────┐
│ F1 0.9967 (TN=746/FN=1/FP=4/TP=749), normal threshold=0.9                 │
│ 5-seed best F1 0.9987 (TN=748/FN=0/FP=2/TP=750)                            │
│ val-F1 median smoothing + val-loss spike guard 학습 안정화                  │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   ▼
┌─ OUTPUT: 생성 데이터 학습 가능성 PoC 확인 ───────────────────────────────┐
│ 다음 단계: 실전 abnormal log → parameter 재보정 → unseen 일반화 검증      │
│ feedback loop 설계 진행 중                                                 │
└───────────────────────────────────────────────────────────────────────────┘
```

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
