## 1. 기술 분야

| 기술 분야 | 대표 적용 기법 / 방식 |
|-----------|----------------|
| Computer Vision | P1 single-label wafer/chip 이미지 처리, ConvNeXtV2 기반 wafer 분류, ROI YOLO 2-stage 보정, chip-CNN → wafer 좌표계 obj-id map 재구성, P2 chip multi-label 이미지 처리 |
| 머신러닝 | Optuna HPO, Focal Loss, Label Smoothing, Temperature scaling, HDBSCAN clustering |
| Self-Supervised Learning | P1 Unknown 검출: ConvNeXtV2 TAPT + Global contrastive learning + MoCo Queue + NV-Retriever + NeCo + HDBSCAN |
| 합성 데이터 엔지니어링 | wafer 합성, FCM-PM (Full-Cover Mixup + Pair Mask) 합성 및 손실 마스킹 구조의 본 과제 신규 적용, trend chart episode 합성 |
| AI 시스템 엔지니어링 | FastAPI/JavaScript 기반 mapviewer, pyvips/Numba, RBAC/SAML SSO, WebGL2 렌더링 |
| 파이프라인 구축 | EDS Test → S3 → fail-map → mapviewer 1시간 주기 적재를 기반으로, Failbit Map 생성, 저장, 조회 → 이미지 분석 AI 모델 (Known 2-stage 분류 / Unknown 검출) → Web App 결과 표시까지 연결하는 end-to-end 운영 파이프라인 구축. Cython hex-to-grade 100배 가속, 32-color palette PNG 75% 절감 |
| 모델 최적화 | 입력 해상도 맞춤 Grade 보존 확대 (categorical 이미지라 nearest-neighbor 사용), Known 2-stage 보정 입력 재구성 (chip-CNN 으로 chip별 결함 분류 → wafer 좌표 object id map 으로 재배치 → 최종 보정 분류기에 입력하는 P1 2차 개발), FCM-PM Pair Mask background loss masking, val_margin / best-margin 기반 checkpoint 선택, 4-bag ensemble 성능 상한 검증, KD single-model compression |

---

## 2. AI 주요 과제

> 본인의 결정적 차별성은 **반도체 역량을 AI 모델에 직접 반영해 현업 문제를 개선** 하는 흐름이며, 아래 3개 과제 모두 같은 흐름으로 진행되었습니다.

| 과제명 | 과제 개요 및 규모 | 담당 역할 | 수행 업무 | 성과 / 검증 근거 | 과제 관련 도메인 / AI 기술 / 모델 / 방법론 |
|--------|---------------|-----------|----------|----------|-----------------------------------|
| **P1. Failbit Map AI 분류 시스템** | single-label wafer/chip 이미지 처리 + Known 2-stage + Unknown contrastive.<br>• 데이터 파이프라인 + mapviewer: **[양산 운영]**<br>• ROI YOLO 2-stage: **[사내 실전 검증 완료]**<br>• chip-CNN obj-id map 재구성: **[추가 생성 데이터, 개발 중]** | 본인 70% / 현업 엔지니어 20% / 관리자 10% | Cython hex-to-grade 변환, 32-color palette PNG 저장, mapviewer 운영, ConvNeXtV2 backbone 선정 및 HPO, ROI YOLO 2-stage 보정, Unknown self-supervised embedding 및 HDBSCAN grouping, chip-CNN → wafer 좌표계 obj-id map 기반 Stage 2 보정 구조 개발 | **[실전 현업 데이터]** Known weighted F1 0.95.<br>**[실전 현업 데이터]** Unknown 5일 10,000장 학습 + 별도 1일 2,000장 적용 → 13 후보 중 7개 실제 불량 현업 확인 (정량 metric 없음).<br>**[양산 운영]** 사내 failbitmap 서비스 12일 누적 2,317 요청.<br>**[추가 생성 데이터, 개발 중]** chip 분류기 보조 개발 지표 (2-stage 통합 성과 아님): val_f1 0.9946 / test_f1 0.9872 / 5-seed 0.9838±0.0092 | ConvNeXtV2, ROI YOLO 2-stage, chip-CNN obj-id map 재구성, ConvNeXtV2-base TAPT, Global InfoNCE, MoCo Queue, NV-Retriever, NeCo, HDBSCAN, Cython, palette-indexed PNG |
| **P2. Chip multi-label classification** | **본인이 FCM-PM (Full-Cover Mixup + Pair Mask) 합성 및 손실 마스킹 구조를 본 과제에 신규 적용**한 chip multi-label 과제입니다. chip 내부 불량 위치를 사전에 알 수 없는 현업 특성을 반영해, 일부 영역만 자르는 기존 CutMix 한계를 보완하여 **chip 전체 grid 를 cover 하는 Full-Cover Mixup + 합성 background loss 를 제외하는 Pair Mask** 를 결합했습니다 (Pair Mask 제거 시 FAR 100% 로 전면 오판). 이후 val_margin checkpoint 선택, ensemble/KD 압축으로 운영 후보를 최적화했습니다. **[추가 생성 데이터, PoC, 양산 적용 후보 검증 중]** | 본인 90% / 관리자 10% | CutMix 계열 선정, CutMix + Pair Mask background loss masking, FCM-PM 합성 및 손실 마스킹 구조의 본 과제 신규 적용, single 4 → 16+ multi-label / OOD 평가 구성, val_f1 → val_margin / best-margin checkpoint 선택 기준 전환, Label Smoothing 및 Temperature scaling 적용, 비대칭 pos/neg target (pt=0.95 / nt=0.30) sweep, 4-bag ensemble 성능 상한 확인, KD single-model 압축 | **[추가 생성 chip 데이터, PoC]** FCM-PM 적용 대표 모델은 bit F1 **0.9943** (보고 요약 0.99대)이며, Normal/Invalid/OOD negative 평가에서 false-positive **0건**을 확인했습니다. Pair Mask 제거 시 FAR **100%** 로 전면 오판되어 FCM-PM 의 background loss masking 이 성패를 가르는 핵심 장치임을 확인했습니다. val_margin 은 eval bit F1 과 Spearman ρ **+0.56** 으로 정렬되어 val_f1 (ρ **-0.10**) 대비 best-model 선택 신호를 개선했습니다. 4-bag ensemble 은 bit F1 **0.9953** / FAR **0.00%** 로 성능 상한을 확인했고, KD single 은 bit F1 **0.9872** / FAR **0.5%** 에서 1× 추론 후보를 확보했습니다. | Multi-label chip classification, CutMix, CutMix + Pair Mask, FCM-PM, Pair Mask background loss masking, val_margin / best-margin checkpoint 선택, asymmetric pos/neg target, Label Smoothing, Temperature scaling, 4-bag ensemble, Knowledge Distillation |
| **P3. Anomaly-detection** | 현업 도메인 자산의 합성 코드화 + trend / semi image / EDS / engineer history multi-modal 동시 개발. Region 5종 / Noise 3종 / 일반 trend 불량 4종 + context 1종 / Fleet enforcement floor 합성 generator 직접 설계. **[합성 trend chart, PoC]** | 본인 90% / 관리자 10% | Region 5종, Noise 3종, 불량 5종 trend 합성 generator 설계, fleet_std 비례 anomaly 강도 하한 보정, val-F1 median smoothing + val-loss spike guard 기반 checkpoint hunting 제어, Binary gate + Type classifier 2-stage 운영 구조 설계, multi-modal 통합 방향 설계 | **[합성 trend chart, PoC]** Binary F1 0.9967, Abnormal Recall 0.9987, 5-seed sweep 0.9944~0.9988. 실전 현업 데이터 검증 미실시이며, 본 과제의 핵심은 metric 이 아닌 도메인 자산 코드화 + multi-modal 개발입니다. | Region 5종 계측 밀도 코드화, Noise 3종 설비 모드 매핑 (Gaussian(산포) / Laplacian(헌팅) / corr(drift)), 불량 5종 trend 형상 카탈로그, val-F1 median smoothing, val-loss spike guard, Fleet enforcement floor, Binary gate + Type classifier |

---

## 3. 포트폴리오

| # | 프로젝트 | 기간 | 내용 | 리딩 규모 | 담당 업무 | 관리 / 설계 / 개발 비중 |
|---|----------|------|------|-----------|----------|----------------------|
| P1 | Failbit Map AI 분류 시스템 (single-label Known + Unknown) | 2022년 ~ 현재 | fail-map 파이프라인, mapviewer, Known 2-stage, Unknown self-supervised 검출, chip-CNN → wafer 좌표계 obj-id map 기반 Stage 2 보정 구조 | DRAM 전제품 라인 운영 + 12일 누적 2,317 요청 + single-label 이미지 처리 AI 모델 PoC | 데이터 파이프라인 구축, Web App 운영, AI 모델 설계, 개발, 검증 | 관리 10% / 설계 40% / 개발 50% |
| P2 | Chip multi-label classification (CutMix → CutMix + Pair Mask → FCM-PM) | 2025년 ~ 현재 | FCM-PM 신규 적용, multi-label 평가셋 구성, Pair Mask 제거 비교, val_margin 기준 도입, ensemble/KD 운영화 후보 검증 | single 4 학습 → 16+ multi-label / OOD 평가 + FCM-PM 대표 모델 / 4-bag ensemble / KD 성능-비용 비교 | 합성 및 손실 마스킹 구조 구성, 학습 및 평가 체계 구축, 모델 선택 기준 및 운영 후보 검증 | 관리 20% / 설계 40% / 개발 40% |
| P3 | Anomaly-detection (도메인 episode 합성) | 2025년 ~ 현재 | trend episode 합성, Region/Noise/불량 type 코드화, val-F1 median smoothing + val-loss spike guard 기반 checkpoint hunting 제어, 2-stage 운영 구조, multi-modal Orchestration Agent 방향 설계 | normal 750 + abnormal 5종 각 150 = 총 1,500 sample 합성 trend chart 평가셋 + multi-modal 통합 개발 **(합성 PoC, 양산 미실시 / multi-modal 동시 개발 진행 중)** | 합성 generator 설계, 학습 안정화, anomaly 유형 분류 구조 설계 | 관리 5% / 설계 50% / 개발 45% |
