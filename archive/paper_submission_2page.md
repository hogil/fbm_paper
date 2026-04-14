# 반도체 웨이퍼 불량 분석을 위한 도메인 지식 기반 통합 파이프라인

**2단 편집 기준 2페이지 제출용 초안**  
※ 아래 표와 성능 수치는 **초안 작성용 예시값**이며, 최종 제출 전 실제 서버 로그로 교체 필요

## 초록

Fab-out 이후 EDS test에서 생성되는 Failbit Map은 wafer 전 영역의 fail 분포를 천만 pixel 이상 규모의 고해상도 spatial information으로 표현하므로, 수율 관리와 불량 원인 분석에 핵심적으로 활용될 수 있다. 그러나 실제 분석 환경에서는 시스템 제약으로 대량의 wafer map을 전수 검토하기 어려워, wafer average나 wafer 내 일부 chip 계측값이 이상 조건을 만족하는 경우에 한해 선별적으로 확인하는 경우가 많다. 본 연구에서는 이러한 한계를 보완하기 위해 데이터 생성, 등록 불량 분류, 미등록 불량 군집화, 사용자 검토를 하나의 흐름으로 연결하는 도메인 지식 기반 통합 파이프라인을 제안하였다. 데이터 계층에서는 dual-bucket 로그 수집, Cython 기반 고속 파싱, palette-indexed PNG 및 positions JSON 생성을 통해 웨이퍼 이미지와 chip-level 좌표 및 계측값을 정합하였다. 생성되는 wafer map은 자연영상과 달리 검사 결과를 의미하는 약 20개 내외의 이산 색상만 사용하므로, 32-color palette PNG로 무손실 의미 보존과 효율적 저장이 가능하였다. 등록 불량 경로에서는 16개 클래스에 대해 Optuna 기반 학습 최적화와 ConvNeXtV2 기반 1-stage classifier 개선을 수행하여 weighted F1를 0.78에서 0.92까지 향상시켰고, 이후 Grad-CAM 기반 ROI 추출, 클래스별 spatial prior, YOLO 이차 검증을 결합한 2단계 구조를 통해 최종 0.95를 달성하였다. 미등록 불량 경로에서는 Contrastive Learning과 HDBSCAN을 적용하여 unknown defect 후보를 자동 군집화하고, 대표 샘플 및 cluster summary를 생성하여 전문가 검토와 신규 라벨 등록을 지원하였다. 또한 `BIN`, `FBT`, `QVL` 계측 정보를 UI 시각화에 활용할 뿐 아니라 향후 이미지-계측 융합 기반 multimodal defect analysis에 사용할 수 있도록 함께 저장하였다.

**Keywords:** Wafer Defect Analysis, Failbit Map, ConvNeXtV2, Grad-CAM, YOLO, Contrastive Learning, HDBSCAN, Palette PNG

---

## 1. 서론

Fab-out 이후 EDS test에서 생성되는 Failbit Map은 wafer 전 영역의 fail 분포를 천만 pixel 이상 규모의 고해상도 spatial information으로 담고 있어, 수율 관리와 불량 원인 분석에 핵심적인 역할을 할 수 있다. 실제 패턴은 center, edge ring, local, scratch와 같은 대표 유형 몇 가지로 단순화되기보다, 서로 중첩되거나 변형된 복합 형상과 난해한 경계 사례를 포함한다. 이러한 패턴은 단순 시각적 모양이 아니라 공정 이상 원인과 연결되는 공간적 의미를 가지므로, 이를 자동 분류하고 해석하는 기술은 반도체 제조 현장에서 높은 실용성을 갖는다. 그러나 실제 분석 환경에서는 시스템 및 인력 제약으로 대량의 wafer map을 전수 검토하기 어렵고, wafer average나 wafer 내 일부 chip 계측값이 이상 조건을 만족하는 경우에 한해 선별적으로 확인하는 경우가 많다. 이로 인해 전체 패턴 분포를 체계적으로 관찰하기 어렵고, unknown defect나 라벨 경계 사례를 조기에 포착하는 데에도 한계가 생긴다. 한편 개발 과정에서 세 가지 요구가 명확해졌다. 첫째, 라벨 부여는 특정 전문가만 수행할 수 있어 데이터 확보 자체가 어렵고, 대량 라벨링도 시간과 부담이 커 비효율적이다. 둘째, 신규 제품 및 공정 변화에 따라 기존 클래스 체계에 없는 unknown defect를 빠르게 식별할 수 있어야 한다. 셋째, 단순 분류 결과 확인을 넘어 wafer map, chip 좌표, 계측값, 시각화, 수동 검토를 함께 수행할 수 있는 분석 UI가 필요하다.

이에 본 연구는 단일 분류 모델의 성능 개선을 넘어서 데이터 생성부터 등록 불량 분류, 미등록 불량 군집화, UI 기반 검토와 라벨 확장까지 연결되는 통합 구조를 제안한다. 특히 wafer map은 자연영상과 달리 절대 위치와 이산적인 상태 값이 중요한 데이터이므로, 본 시스템은 데이터 표현 방식 자체에 반도체 도메인 지식을 반영하였다.

---

## 2. 제안 방법

### 2.1 데이터 생성 및 표현 계층

입력 데이터는 단일 이미지 파일이 아니라 두 소스의 로그 정합 결과이다. Bucket A에는 primary fail map raw 파일이 저장되고, Bucket B에는 chip-level measurement 로그가 저장된다. 두 bucket은 wafer 식별 규칙과 시간 오프셋을 이용해 자동 매칭되며, 병렬 다운로드와 압축 해제 후 Cython 기반 파싱을 거쳐 wafer image와 positions JSON을 동시에 생성한다. positions JSON에는 `rect`, `grid_edges`, `b`, `f`, `q`와 함께 wafer-level `yield`, `sys`, `lt`, `tm`이 저장되며, 이후 분류기와 UI가 동일 좌표계를 공유하도록 한다.

본 연구에서 wafer map 저장 포맷으로 `32-color 8-bit palette-indexed PNG`를 채택한 이유도 도메인 지식에 기반한다. 실제 생성 이미지의 색상은 자연영상처럼 수천~수만 색을 쓰지 않고, grade, background, text, border, BIN 등 검사 결과를 표현하는 약 20개 내외의 이산 색상으로 구성된다. 따라서 JPEG와 같이 손실 압축을 사용할 이유가 없고, RGB PNG처럼 각 픽셀에 색값을 직접 저장할 필요도 작다. 반면 palette PNG는 픽셀에 `색`이 아니라 `의미 인덱스`를 저장하고, 실제 색상은 `PLTE`에서 정의한다. 따라서 동일한 map에 대해 `IDAT` 구조는 유지한 채 `PLTE`만 교체하여 사용자별 개인 색상 scheme을 즉시 적용할 수 있으며, 의미 보존과 저장 효율을 동시에 확보할 수 있다.

### 2.2 등록 불량 분류 경로

등록 불량 분류는 16개 클래스 closed-set 문제로 설정하였다. 실제 현장 적용에서 이론과 실제의 괴리가 가장 크게 나타난 영역이기도 하다. 웨이퍼 맵은 자연영상처럼 경계(edge)가 명확하지 않고, 전기적 노이즈가 공간적으로 뭉쳐진 형태이다. 따라서 Fine-Grained Visual Classification(FGVC) 계열 접근법을 시도하였으나, 자연영상의 텍스처·경계 구조를 가정한 방법들은 성능 향상으로 이어지지 않았다. 추가로 multi-label 분포와 라벨 노이즈가 공존하여, Focal Loss 및 class weight 조정으로 클래스 불균형 완화를 시도하였으나 효과는 제한적이었다.

결과적으로 성능 향상의 실질적 경로는 두 단계로 정리된다. 첫 단계는 ConvNeXtV2 기반 1-stage classifier에 Optuna 기반 하이퍼파라미터 탐색(learning rate, weight decay, scheduler, dropout, label smoothing, augmentation, batch size)을 적용하여 validation weighted F1 0.78 → 0.92를 달성하였다. backbone 비교에서는 EfficientNetV2, MaxViT, ViT, Swin Transformer 계열도 함께 평가하였으며, 최종적으로 ConvNeXtV2가 가장 안정적인 성능을 보였다. 실제 구현에서는 `timm.create_model("convnextv2_base.fcmae_ft_in22k_in1k_384")`를 사용하여 Hugging Face/timm 생태계의 사전학습 가중치를 불러온 뒤 wafer map 데이터로 fine-tuning하였다. 실험 데이터는 총 약 1500개, validation 약 500개 수준이었고 클래스별 샘플 수 편차도 존재하였다. 이 조건에서는 대규모 데이터에서 강점을 보이는 ViT 계열보다, 상대적으로 데이터 효율이 높은 ConvNeXtV2가 더 안정적으로 수렴하였다.

두 번째 단계는 wafer 전체 이미지가 아닌 chip 단위 crop 이미지를 YOLO에 학습시켜 미세 영역 object detection 기반 이차 검증을 수행하는 구조이다. 모든 샘플을 YOLO로 직접 처리하는 방식은 계산 비용이 크고, wafer 전체의 global 배치와 공간 맥락을 함께 보기 어렵다. 따라서 본 연구는 전체 패턴의 coarse discrimination은 1-stage classifier가 담당하고, 미세 영역 재확인이 필요한 sample만 선택적으로 YOLO에 전달하는 파이프라인을 설계하였다. 특히 샘플 수가 적은 클래스이거나 wafer 내 동일 영역, 특히 center 부근에 위치한 패턴들은 macro 관점의 전체 이미지 분류만으로는 구분이 어려웠다. 1차 분류 결과와 confidence를 바탕으로 difficult class 또는 low-confidence sample만 선별하여 Grad-CAM 기반 ROI를 추출한 뒤 YOLO 검증을 수행하고, chip object detection 관점에서 미세 패턴을 다시 확인함으로써 이러한 혼동을 줄였다. Grad-CAM dynamic ROI는 클래스별 학습 데이터에서 구한 평균 ROI 패턴(spatial prior)과 블렌딩되어 single-sample heatmap 불안정성을 보완한다. 이를 통해 최종 F1 0.95를 달성하였다.

현재 운영 설정의 핵심 threshold는 다음과 같다.

- `PRECISION_THRESHOLD = 0.80`
- `CONFIDENCE_THRESHOLD = 0.80`
- `YOLO_CONF_THRESHOLD = 0.25`
- `ROI_FOR_DIFFICULT_OR_LOWCONF_ONLY = True`

이 설정의 의미는 명확하다. 1-stage confidence가 충분히 높고 difficult class가 아니면 ROI 보강을 생략하고, confidence가 낮거나 difficult class이면 Grad-CAM ROI와 YOLO 검증을 수행한다. classifier threshold를 지나치게 낮추면 ROI 호출 비율이 과도하게 증가하고, 지나치게 높이면 교정 가능한 borderline sample을 놓친다. YOLO threshold 역시 너무 낮으면 false detection이 증가하고, 너무 높으면 small defect object를 놓칠 수 있다. 운영 실험에서는 classifier threshold를 약 0.80, YOLO threshold를 약 0.25로 둘 때 correction precision과 호출 효율 간 균형이 가장 안정적이었다.

YOLO는 standalone detector가 아니라 ROI 내부에서 defect object consistency를 확인하는 검증기로 사용된다. 따라서 YOLO 튜닝 또한 일반 object detection benchmark보다 correction precision과 false detection 억제에 초점을 맞추었다. 학습 시에는 `imgsz`, `epochs`, `batch`, `lr`, `weight_decay`, `box/cls/dfl`, `degrees`, `translate`, `scale`, `mosaic`, `mixup`, `patience` 등을 조정하였으며, classifier와 동일한 도메인 원칙에 따라 좌우·상하 반전은 배제하였다. 반전 증강은 wafer map의 방향성과 위치 의미를 훼손하기 때문이다. 손실 항목 중에서는 `cls_loss`의 영향이 가장 컸다. ROI 내부에는 보통 defect object가 1~2개 수준으로 존재하므로 위치 자체를 맞추는 `box` 항은 비교적 빨리 수렴했고, objectness에 해당하는 항도 큰 병목이 아니었다. 반면 scratch, local, arc, edge 계열처럼 형태가 유사한 객체를 어떤 class로 구분하느냐가 핵심이었기 때문에, `cls` 관련 설정을 강화했을 때 ROI correction precision과 최종 F1이 가장 안정적으로 상승하였다.

### 2.3 미등록 불량 경로

unknown defect에 대해서는 ConvNeXtV2 backbone 기반 자기지도 대조 학습과 HDBSCAN 군집화를 결합하였다. 구현 과정에서 몇 가지 중요한 설계 판단이 성능에 직접 영향을 미쳤다.

**손실 함수 선택 — label-aware objective vs. InfoNCE.** 초기에는 특정 group을 더 강하게 묶는 label-aware contrastive objective를 시험하였다. 이 방식은 일부 기등록 group에는 유리했지만, 라벨이 없거나 패턴 다양성이 큰 unknown defect 영역에서는 오히려 임베딩 분리도가 저하되었다. 즉 특정 group에는 좋아져도 불특정 unknown 전반에는 불리한 구조였다. 따라서 최종적으로는 heterogeneous unknown 전반의 응집도를 더 안정적으로 형성하는 InfoNCE(SimCLR 계열 global-local contrastive) 구성을 유지하였다.

**Train/Test 분리 오해 해소.** 분류·검출 배경에서 접근하면 contrastive learning에도 train/test를 엄격히 분리해야 한다는 선입견이 생긴다. 그러나 contrastive learning의 직접 목표는 class prediction이 아니라 유사한 샘플을 임베딩 공간에서 가깝게 배치하는 것이다. 따라서 unknown clustering용 표현 학습에서는 데이터 커버리지가 더 중요했고, 실무적으로는 더 넓은 샘플 풀을 활용할수록 군집 안정성이 향상되었다.

**Local InfoNCE 샘플링 전략.** 문헌에서는 random point 샘플링을 권장하지만, 반도체 불량 맵에서는 웨이퍼 중심(center 계열 불량 집중)과 외곽 경계(edge 계열 불량 집중) 영역이 분류적으로 중요하다. 따라서 피처 맵을 6×6 격자(grid36_full) 기반 local anchor로 분할하고, random point 대신 위치 의미를 보존하는 structured sampling을 사용하였다. 개발 과정에서는 중심·외곽 주요 영역을 더 많이 보게 하는 편이 군집 안정성에 유리했으며, 이는 wafer map에서 위치 자체가 공정 의미를 가지기 때문이다.

**flip 미사용.** 외형이 유사하더라도 좌우·상하로 반전된 불량은 발생 공정 원인이 다른 경우가 있다. 예컨대 웨이퍼 왼쪽에 발생한 edge_loc과 오른쪽에 발생한 edge_loc은 외형상 flip 관계처럼 보이지만, 설비 레이아웃 기준으로는 서로 다른 원인을 갖는다. flip 증강을 적용하면 이를 구분할 수 없게 된다. 따라서 flip을 제외하고 소규모 회전·이동·스케일·노이즈만 사용하였다.

Global InfoNCE(Queue 16K, false-negative 마스킹 sim≥0.72) + Local InfoNCE + HDBSCAN quality filter(size≥12, prob≥0.55, persist≥0.20) 조합으로 cluster 안정성을 확보하고, medoid representative를 저장하여 전문가 검토 부담을 줄였다. cluster 후보는 UI에서 확인하고 신규 라벨로 등록하여 supervised path에 편입된다.

### 2.4 분석 UI와 multimodal 준비

`mapviewer`는 단순 결과 표시 도구가 아니라, wafer map의 의미 인덱스 구조와 chip-level 계측값을 함께 해석하는 분석 인터페이스이다. 개인 색상 scheme, chip annotation, composite map, BIN/FBT/QVL overlay를 제공하며, positions JSON을 기반으로 chip geometry와 measurement를 동일 좌표계에 정합한다. 이 구조는 등록 불량 오분류 재검토, unknown cluster 대표 샘플 확인, 신규 라벨 등록을 하나의 workflow로 연결한다. 중요한 점은 `BIN`, `FBT`, `QVL`이 단순 UI 표시용 값이 아니라는 것이다. 본 시스템은 이를 이미지와 함께 정합 저장함으로써 향후 multimodal 학습 입력으로 직접 활용할 수 있는 데이터 자산으로 확보하였다.

**Figure 1.** 시스템 아키텍처 개념도 삽입 권장  
`fail-map → image_classification (CNN+ROI+YOLO / Contrastive+HDBSCAN) → mapviewer`

---

## 3. 실험 결과 및 논의

등록 불량 경로에서는 Optuna 기반 1-stage optimization으로 validation weighted F1 0.92를 달성하였고, ROI enhancement와 YOLO 보정을 통해 0.95까지 향상되었다. 특히 edge_loc, edge_ring, local 계열처럼 공간적으로 유사한 패턴 간 혼동과, center 부근에 모여 macro 관점에서 유사하게 보이는 패턴 간 혼동이 줄어드는 효과가 확인되었다. 서버 실험에서는 `original prediction != true`였으나 `ROI-enhanced prediction == true`로 교정된 대표 사례와 original confusion matrix, ROI-enhanced confusion matrix가 확보되어 있으며, 이는 2-stage correction의 정성·정량 근거로 활용할 수 있다.

unknown 경로에서는 pseudo-open-set 가정 하에 cluster purity 0.84, NMI 0.76, ARI 0.71, kept cluster coverage 82.3%, noise ratio 17.8% 수준의 예시 결과를 얻을 수 있었다. 이는 unknown defect 평가가 accuracy 하나로 환원되기보다, 신규 불량 후보를 얼마나 안정적으로 압축하여 전문가 검토가 가능한 구조로 제시하는가에 초점을 두어야 함을 보여준다.

**Table 1. backbone 비교 예시 (validation weighted F1)**

| Backbone | 입력 크기 | 학습 방식 | Weighted F1 |
|----------|-----------|-----------|-------------|
| EfficientNetV2-M | 384 | fine-tuning | 0.88 |
| MaxViT-Base | 384 | fine-tuning | 0.89 |
| ViT-Base/16 | 384 | fine-tuning | 0.87 |
| Swin-Base | 384 | fine-tuning | 0.90 |
| ConvNeXtV2-Base | 384 | fine-tuning | 0.92 |

**Table 1 해석.** Transformer 계열도 일정 수준의 성능을 보였으나, 총 약 1500개 규모와 클래스별 데이터 편차 조건에서는 ConvNeXtV2가 가장 안정적으로 동작하였다. wafer map처럼 경계가 약하고 noise가 누적된 패턴에서는 대규모 데이터 의존성이 큰 ViT 계열보다 ConvNeXtV2가 더 데이터 효율적이었고, 이후 ROI enhancement와 unknown contrastive 경로의 backbone도 동일 계열로 통일하였다.

**Table 2. 등록 불량 성능 향상 단계**

| 단계 | 구성 | Weighted F1 |
|------|------|-------------|
| Baseline CNN | 초기 기준 모델 | 0.78 |
| ConvNeXtV2 + Optuna | backbone 및 하이퍼파라미터 최적화 | 0.92 |
| + ROI enhancement + YOLO | 2-stage correction | 0.95 |

**Table 3. threshold 및 YOLO 설정 예시**

| 항목 | 실험 범위 | 채택값 |
|------|-----------|--------|
| Classifier confidence | 0.70 ~ 0.90 | 0.80 |
| Difficult class threshold | 0.75 ~ 0.85 | 0.80 |
| YOLO confidence | 0.15 ~ 0.35 | 0.25 |
| YOLO imgsz | 512 ~ 768 | 640 |
| YOLO batch | 8 ~ 32 | 16 |
| YOLO epochs | 50 ~ 150 | 100 |
| YOLO cls gain | 0.5 ~ 1.5 | 1.0 |

**Table 3 해석.** ROI 검증 단계에서는 `cls_loss`가 가장 민감한 항이었다. 예시적으로 `cls` 가중을 조정하지 않은 설정에서는 ROI correction precision이 0.86 수준에 머물렀으나, class discrimination을 강화한 뒤 0.90 수준까지 개선되었고 최종 pipeline F1도 0.944에서 0.950으로 상승하였다.

---

## 4. 결론

본 연구는 반도체 웨이퍼 불량 분석을 위해 데이터 생성, 등록 불량 분류, 미등록 불량 군집화, 분석 UI를 하나의 파이프라인으로 통합하였다. dual-bucket 로그 정합과 Cython 기반 파싱을 통해 이미지와 계측값을 함께 생성하고, 약 20개 내외의 이산 색상으로 구성된 검사 결과 특성을 활용해 palette-indexed PNG와 positions JSON 기반 표현을 구축하였다. 등록 불량 경로에서는 16개 클래스에 대해 Optuna 기반 학습 최적화로 `0.78 -> 0.92`, ROI enhancement와 YOLO 검증으로 `0.92 -> 0.95`를 달성하였다. 미등록 불량 경로에서는 Contrastive Learning과 HDBSCAN을 통해 unknown defect 후보를 자동 군집화하고, 전문가 검토 기반 신규 라벨 확장 루프를 마련하였다. 또한 `BIN`, `FBT`, `QVL` 계측값을 UI 시각화뿐 아니라 향후 multimodal 학습에 사용할 수 있도록 정합 저장함으로써 이미지-계측 융합 기반 확장 가능성을 확보하였다.

향후에는 실제 서버 실험 로그를 기반으로 threshold sweep과 YOLO 튜닝 결과를 더 정교하게 정리하고, confusion matrix 및 ROI 교정 사례를 포함한 정량·정성 분석을 보강할 필요가 있다.

---

## 참고문헌

[1] T. Nakazawa and D. V. Kulkarni, "Wafer Map Defect Pattern Classification and Image Retrieval Using Convolutional Neural Network," *IEEE Transactions on Semiconductor Manufacturing*, vol. 31, no. 2, pp. 309-314, 2018.  
[2] M. B. Alawieh, D. Boning, and D. Z. Pan, "Wafer Map Defect Patterns Classification using Deep Selective Learning," in *Proc. 57th ACM/IEEE Design Automation Conference (DAC)*, pp. 1-6, 2020.  
[3] Y. Kim, D. Cho, and J.-H. Lee, "Wafer Defect Pattern Classification With Detecting Out-of-Distribution," *IEEE Transactions on Semiconductor Manufacturing*, vol. 34, no. 4, pp. 498-505, 2021.  
[4] J. Jang and G. T. Lee, "Decision Fusion Approach for Detecting Unknown Wafer Bin Map Patterns Based on a Deep Multitask Learning Model," *Expert Systems with Applications*, vol. 213, 2023.  
[5] S. Woo, S. Debnath, R. Hu, X. Chen, Z. Liu, I. S. Kweon, and S. Xie, "ConvNeXt V2: Co-Designing and Scaling ConvNets With Masked Autoencoders," in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, pp. 16133-16142, 2023.  
[6] R. R. Selvaraju, M. Cogswell, A. Das, R. Vedantam, D. Parikh, and D. Batra, "Grad-CAM: Visual Explanations From Deep Networks via Gradient-Based Localization," in *Proceedings of the IEEE International Conference on Computer Vision (ICCV)*, pp. 618-626, 2017.  
[7] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, "A Simple Framework for Contrastive Learning of Visual Representations," in *Proceedings of the 37th International Conference on Machine Learning (ICML)*, PMLR 119, pp. 1597-1607, 2020.  
[8] R. J. G. B. Campello, D. Moulavi, and J. Sander, "Density-Based Clustering Based on Hierarchical Density Estimates," in *Advances in Knowledge Discovery and Data Mining (PAKDD 2013, Part II)*, pp. 160-172, 2013.  
