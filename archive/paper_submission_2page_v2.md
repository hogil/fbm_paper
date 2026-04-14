# 반도체 Failbit Map 분석을 위한 도메인 지식 기반 통합 파이프라인

**2단 편집 기준 2페이지 제출용 재작성 초안**  
※ 수치 결과 중 일부는 초안용 예시값이며, 최종 제출 전 실제 서버 로그로 교체 필요

## 초록

Fab-out 이후 EDS test에서 생성되는 Failbit Map은 wafer 전 영역의 fail spatial distribution을 고해상도로 담는 핵심 wafer-level 표현이지만, 기존 분석 환경에서는 이를 대량으로 구조화해 해석하기 어렵다. 본 연구는 등록 불량과 미등록 불량이 공존하는 실제 분석 조건을 반영하여, closed-set 분류와 open-set 군집화를 결합한 도메인 지식 기반 통합 AI 파이프라인을 제안한다. 등록 불량 경로에서는 16개 클래스를 대상으로 ConvNeXtV2 기반 global classifier를 구축하고, confidence-triggered Grad-CAM ROI enhancement와 YOLO ROI verifier를 결합하여 전역 배치 정보와 chip-level 미세 패턴을 동시에 반영하도록 설계하였다. 미등록 불량 경로에서는 local-global contrastive embedding과 HDBSCAN을 결합하여 unknown defect 후보를 자동 군집화하고, 대표 샘플 및 cluster summary를 생성하여 전문가 검토와 신규 라벨 확장을 지원하였다. 데이터 계층에서는 Bucket A fail-map 로그의 hex grade block을 Cython으로 고속 변환하고, Bucket B 계측 로그와 정합하여 positions JSON을 생성하였으며, 실제 검사 결과가 약 20개 내외의 이산 색상으로 표현된다는 특성을 이용해 32-color palette-indexed PNG를 채택함으로써 의미 보존, 용량 절감, 사용자별 recoloring을 동시에 달성하였다. 실험 결과, Optuna 기반 최적화로 validation weighted F1를 0.78에서 0.92까지 향상시켰고, 이후 선택적 ROI enhancement를 통해 최종 0.95를 달성하였다. 또한 `BIN`, `FBT`, `QVL`을 포함한 계측 메타데이터를 함께 축적하여 대화형 분석 UI와 향후 이미지-계측 융합 기반 multimodal defect analysis로 확장 가능한 기반을 마련하였다.

**Keywords:** Failbit Map, Wafer Defect Analysis, ConvNeXtV2, Grad-CAM, YOLO, Contrastive Learning, HDBSCAN, Multimodal

---

## 1. 서론

Failbit Map은 메모리 테스트 결과를 wafer 전체 공간에 투영한 표현으로, 불량의 위치, 방향성, 밀집도, 국부 패턴을 동시에 담고 있다. 실제 패턴은 몇 가지 대표 유형으로 단순화되기보다, 서로 중첩되거나 변형된 복합 형상과 난해한 경계 사례를 포함하며, 같은 형태라도 발생 위치에 따라 공정 원인이 달라질 수 있다. 따라서 Failbit Map은 단순 시각 자료가 아니라 공정 해석과 이상 원인 추적을 위한 핵심 데이터로 볼 수 있다.

그럼에도 불구하고 실제 분석 환경에서는 모든 wafer map을 mass 관점에서 연속적으로 검토하기 어렵다. 대량의 고해상도 map을 사람이 직접 보는 데 한계가 있고, 시스템상 wafer average나 wafer 내 일부 chip 수치가 이상 조건을 만족하는 경우를 우선적으로 확인하는 방식에 의존하기 쉽다. 이 경우 전체 패턴 분포를 구조적으로 파악하기 어렵고, 경계 사례나 신규 불량의 조기 포착에도 제약이 생긴다.

개발 과정에서 확인된 요구사항은 세 가지였다. 첫째, 라벨 부여는 특정 전문가만 가능하므로 데이터 확보가 어렵고, 대량 라벨링 자체가 비효율적이다. 둘째, 신규 제품 및 공정 변화에 따라 기존 클래스 체계에 없는 unknown defect를 빠르게 식별할 수 있어야 한다. 셋째, 단순 분류 결과를 넘어서 wafer map, chip 좌표, 계측값, 시각화, 수동 검토를 함께 수행할 수 있는 분석 UI가 필요하다. 이에 본 연구는 데이터 생성부터 등록 불량 분류, 미등록 불량 군집화, UI 기반 검토와 라벨 확장까지 연결되는 통합 구조를 제안한다.

---

## 2. 제안 방법

### 2.1 데이터 생성 및 표현 계층

입력 데이터는 단일 이미지 파일이 아니라 두 소스의 설비 로그 정합 결과이다. Bucket A에는 primary fail-map raw 파일(`.Z`)이, Bucket B에는 chip-level measurement 로그(`.gz`)가 저장되며, 두 bucket은 wafer 식별 규칙과 시간 오프셋을 이용해 자동 매칭된다. 이후 병렬 다운로드와 압축 해제를 수행한 뒤, Bucket A 로그에 포함된 `X=, Y=, b=` 헤더와 뒤따르는 hex grade block을 파싱하여 chip별 fail map 타일을 복원한다. 이때 한 줄씩 반복 처리하면 병목이 크게 발생하므로, hex 문자에서 grade index로 변환하는 핵심 루프를 Cython으로 구현하여 map array 생성을 가속하였다. Bucket B에서는 `TM`, `LT`, `FTN`, `QTN` 및 chip별 `F/Q` 값을 읽어 positions JSON에 병합한다. 최종 positions JSON에는 `rect`, `grid_edges`, `b`, `f`, `q`와 함께 wafer-level `yield`, `sys`, `lt`, `tm`이 저장되어 이후 분류기와 UI가 동일 좌표계를 공유하도록 한다.

본 연구에서 wafer map 저장 포맷으로 `32-color 8-bit palette-indexed PNG`를 채택한 이유 역시 도메인 지식에 기반한다. 실제 생성 이미지의 색상은 자연영상처럼 수천 색 이상을 사용하지 않고, 검사 결과를 표현하는 약 20개 내외의 이산 색상으로 구성된다. 따라서 JPEG와 같은 손실 압축은 의미 보존 측면에서 적합하지 않고, RGB PNG도 표현 효율이 낮다. 반면 palette PNG는 픽셀에 색이 아니라 의미 인덱스를 저장하고 실제 색상 정의를 `PLTE`에서 분리 관리하므로, 동일한 map에 대해 `IDAT` 구조를 유지한 채 사용자별 색상 scheme을 즉시 적용할 수 있다. 이 구조는 UI 시각화뿐 아니라, 향후 이미지와 계측 정보를 함께 사용하는 multimodal 학습의 기반이 된다.

### 2.2 등록 불량 분류 경로

등록 불량 분류는 16개 클래스 closed-set 문제로 설정하였다. 그러나 웨이퍼 맵은 자연영상처럼 경계가 뚜렷하지 않고, 전기적 노이즈가 공간적으로 뭉쳐 형성된 상징적 패턴이 많다. 이 때문에 FGVC, Focal Loss, class weight 조정과 같은 일반적 성능 개선 전략은 제한적 효과만 보였다. 또한 mixed/multi-label 샘플과 라벨 노이즈가 존재하여, 전체 map만 보는 단일 분류기로는 미세 차이를 안정적으로 구분하기 어려웠다.

#### 2.2-1 CNN 기반 global classifier

이에 먼저 1-stage classifier를 구축하고 backbone을 비교하였다. EfficientNetV2, MaxViT, ViT, Swin Transformer, ConvNeXtV2를 동일 입력 크기에서 비교한 결과, ConvNeXtV2가 가장 안정적인 validation weighted F1를 기록하였다. 실제 구현에서는 Hugging Face `timm` 생태계의 사전학습 가중치를 활용하여 `convnextv2_base.fcmae_ft_in22k_in1k_384`를 wafer map 데이터로 fine-tuning하였다. 총 약 1500개 수준의 데이터와 클래스별 샘플 편차 조건에서는 대규모 데이터에서 강점을 보이는 ViT 계열보다, FCMAE 기반 사전학습과 convolutional inductive bias를 동시에 갖는 ConvNeXtV2가 더 데이터 효율적으로 동작하였다. 또한 384 입력 해상도에서 local, scratch, edge 계열의 미세 구조를 상대적으로 안정적으로 유지하였다. Optuna 기반 하이퍼파라미터 탐색을 통해 validation weighted F1를 0.78에서 0.92까지 향상시켰다. 이 단계의 역할은 wafer 전체 배치, 중심/에지 분포, 다중 영역 간 상대 위치와 같은 global spatial context를 우선적으로 해석하는 것이다.

#### 2.2-2 YOLO 기반 ROI enhancement

그러나 이 단계만으로는 center 부근에 위치한 유사 패턴이나 샘플 수가 적은 클래스의 혼동이 충분히 해소되지 않았다. 이를 보완하기 위해 2-stage ROI enhancement를 설계하였다. 1차 분류 결과와 confidence를 바탕으로 difficult class 또는 low-confidence sample만 선별하고, 해당 샘플에 대해서만 Grad-CAM 기반 ROI를 추출한 뒤 YOLO 검증을 수행한다. 이때 dynamic ROI는 클래스별 평균 ROI 패턴(spatial prior)과 블렌딩되어 single-sample heatmap의 불안정성을 보완한다. 즉, 전역적인 배치와 공간 문맥은 CNN이 보고, chip 단위 미세 패턴은 ROI 내부 object detection으로 다시 확인하는 구조이다. 모든 샘플을 YOLO로 직접 처리하지 않은 이유도 여기에 있다. 전체 wafer의 global 배치를 보는 역할과 계산 비용 측면에서 1-stage classifier가 필요하며, ROI 기반 선택적 호출이 효율적이었다.

YOLO는 standalone detector가 아니라 ROI 내부에서 defect object consistency를 확인하는 검증기로 사용되었다. 따라서 튜닝 역시 일반 object detection benchmark보다 correction precision과 false detection 억제에 초점을 맞추었다. 실제로 `box` 항보다는 `cls_loss`의 영향이 더 컸다. ROI 내부에는 보통 defect object가 1~2개 수준으로 존재하므로 위치 자체를 맞추는 항은 비교적 빠르게 수렴했지만, 형태가 유사한 객체를 어떤 class로 구분하느냐가 최종 교정 성능의 핵심이었기 때문이다. 즉, 이 단계의 목적은 새로운 물체를 찾는 detection 자체가 아니라, global classifier가 헷갈린 샘플에 대해 class decision boundary를 다시 세우는 데 있다. 이 2-stage 구조를 통해 최종 validation weighted F1는 0.95까지 향상되었다.

### 2.3 미등록 불량 경로

unknown defect에 대해서는 ConvNeXtV2 backbone 기반 자기지도 대조 학습과 HDBSCAN 군집화를 결합하였다. 초기에는 특정 known group을 강하게 묶는 label-aware contrastive objective도 시험하였으나, 일부 그룹의 응집도는 높아져도 형태 다양성이 큰 unknown 전반의 임베딩 분리도는 오히려 저하되었다. 따라서 최종적으로는 SimCLR 계열 InfoNCE 기반 global-local contrastive 구성을 유지하였다.

여기서도 일반 영상 기준 설정을 그대로 사용하지 않았다. 첫째, contrastive learning은 class label 예측이 아니라 representation space 정렬을 목표로 하므로, unknown candidate를 포함한 넓은 unlabeled set을 활용하는 것이 임베딩 coverage 확보에 유리했다. 둘째, 문헌에서 흔히 권장되는 random point local sampling 대신, wafer map에서 공정 의미가 큰 center 및 edge 영역을 보존하는 structured local anchor를 사용하였다. 셋째, 좌우·상하 반전은 적용하지 않았다. 외형이 유사하더라도 발생 위치와 방향이 달라지면 공정 원인이 달라질 수 있기 때문이다. Global InfoNCE, Local InfoNCE, HDBSCAN quality filter(size, median probability, persistence)를 조합하여 cluster 안정성을 확보하고, medoid representative를 저장하여 전문가 검토 부담을 줄였다. cluster 후보는 UI에서 확인하고 신규 라벨로 등록하여 supervised path에 편입될 수 있다.

### 2.4 분석 UI와 multimodal 준비

`mapviewer`는 단순한 결과 viewer가 아니라, wafer map의 의미 인덱스 구조와 chip-level 계측값을 함께 해석하는 분석 인터페이스이다. 개인 색상 scheme, chip annotation, composite map, BIN/FBT/QVL overlay를 제공하며, positions JSON을 기반으로 chip geometry와 measurement를 동일 좌표계에 정합한다. 즉, 등록 불량 오분류 재검토, unknown cluster 대표 샘플 확인, 신규 라벨 등록을 하나의 workflow로 연결하는 분석 환경으로 기능한다.

**Figure 1.** 시스템 아키텍처 개념도 삽입 권장  
`fail-map → image_classification (CNN+ROI+YOLO / Contrastive+HDBSCAN) → mapviewer`

---

## 3. 실험 결과 및 논의

등록 불량 경로에서는 backbone 비교 결과 ConvNeXtV2가 가장 우수한 validation weighted F1를 보였으며, Optuna 기반 최적화 이후 1-stage 기준 0.92를 달성하였다. 이후 ROI enhancement와 YOLO 보정을 통해 0.95까지 향상되었다. 특히 edge, local, center 부근 패턴처럼 macro 관점에서 유사하게 보이는 경우의 혼동 감소가 주요 성능 향상 요인이었다. 서버 실험에서는 `original prediction != true`였으나 `ROI-enhanced prediction == true`로 교정된 대표 사례와 original confusion matrix, ROI-enhanced confusion matrix가 확보되어 있으며, 이는 2-stage correction의 정성·정량 근거로 활용할 수 있다.

unknown 경로의 목적은 closed-set accuracy를 높이는 것이 아니라, 신규 불량 후보를 얼마나 안정적으로 압축하여 전문가 검토가 가능한 구조로 제시하는가에 있다. 따라서 평가는 cluster purity, NMI, ARI, kept cluster coverage, noise ratio와 같은 open-set 군집 품질 지표로 해석하는 것이 적절하다. 본 시스템은 unknown defect를 곧바로 정답 클래스로 예측하는 대신, 검토 가능한 cluster 후보와 대표 샘플을 생성하여 라벨 확장 루프를 지원한다는 점에서 실용적 의미를 가진다.

**Table 1. backbone 비교 예시 (validation weighted F1)**

| Backbone | Input | Method | Weighted F1 |
|----------|-------|--------|-------------|
| EfficientNetV2-M | 384 | fine-tuning | 0.88 |
| MaxViT-Base | 384 | fine-tuning | 0.89 |
| ViT-Base/16 | 384 | fine-tuning | 0.87 |
| Swin-Base | 384 | fine-tuning | 0.90 |
| ConvNeXtV2-Base | 384 | fine-tuning | 0.92 |

**Table 2. 등록 불량 성능 향상 단계**

| Stage | Configuration | Weighted F1 |
|-------|---------------|-------------|
| Baseline | Initial CNN | 0.78 |
| Stage 1 | ConvNeXtV2 + Optuna | 0.92 |
| Stage 2 | + ROI enhancement + YOLO | 0.95 |

---

## 4. 결론

본 연구는 반도체 웨이퍼 불량 분석을 위해 데이터 생성, 등록 불량 분류, 미등록 불량 군집화, 분석 UI를 하나의 파이프라인으로 통합하였다. dual-bucket 로그 정합과 Cython 기반 파싱을 통해 이미지와 계측값을 함께 생성하고, palette-indexed PNG와 positions JSON 기반 표현을 구축하였다. 등록 불량 경로에서는 ConvNeXtV2와 Optuna 기반 최적화로 1-stage 성능을 향상시켰고, Grad-CAM ROI와 YOLO 이차 검증을 통해 최종 0.95를 달성하였다. 미등록 불량 경로에서는 Contrastive Learning과 HDBSCAN을 통해 unknown defect 후보를 자동 군집화하고, 전문가 검토 기반 신규 라벨 확장 구조를 마련하였다. 또한 BIN, FBT, QVL 계측값을 이미지와 함께 정합 저장함으로써, 향후 이미지-계측 융합 기반 multimodal defect analysis로 확장 가능한 기반을 확보하였다.

---

## 참고문헌

[1] T. Nakazawa and D. V. Kulkarni, "Wafer Map Defect Pattern Classification and Image Retrieval Using Convolutional Neural Network," *IEEE Transactions on Semiconductor Manufacturing*, vol. 31, no. 2, pp. 309-314, 2018.  
[2] M. B. Alawieh, D. Boning, and D. Z. Pan, "Wafer Map Defect Patterns Classification using Deep Selective Learning," in *Proc. 57th ACM/IEEE Design Automation Conference (DAC)*, pp. 1-6, 2020.  
[3] Y. Kim, D. Cho, and J.-H. Lee, "Wafer Defect Pattern Classification With Detecting Out-of-Distribution," *IEEE Transactions on Semiconductor Manufacturing*, vol. 34, no. 4, pp. 498-505, 2021.  
[4] J. Jang and G. T. Lee, "Decision Fusion Approach for Detecting Unknown Wafer Bin Map Patterns Based on a Deep Multitask Learning Model," *Expert Systems with Applications*, vol. 213, 2023.  
[5] S. Woo, S. Debnath, R. Hu, X. Chen, Z. Liu, I. S. Kweon, and S. Xie, "ConvNeXt V2: Co-Designing and Scaling ConvNets With Masked Autoencoders," in *Proc. IEEE/CVF CVPR*, pp. 16133-16142, 2023.  
[6] R. R. Selvaraju, M. Cogswell, A. Das, R. Vedantam, D. Parikh, and D. Batra, "Grad-CAM: Visual Explanations From Deep Networks via Gradient-Based Localization," in *Proc. IEEE ICCV*, pp. 618-626, 2017.  
[7] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, "A Simple Framework for Contrastive Learning of Visual Representations," in *Proc. 37th ICML*, *PMLR*, vol. 119, pp. 1597-1607, 2020.  
[8] R. J. G. B. Campello, D. Moulavi, and J. Sander, "Density-Based Clustering Based on Hierarchical Density Estimates," in *Advances in Knowledge Discovery and Data Mining (PAKDD 2013, Part II)*, pp. 160-172, 2013.  
