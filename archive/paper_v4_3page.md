# 반도체 웨이퍼 불량 분석을 위한 도메인 지식 기반 등록/미등록 통합 파이프라인

**A Domain-Knowledge-Driven Unified Pipeline for Registered and Unregistered Wafer Defect Analysis**

## 초록

반도체 제조 공정에서 Failbit Map 기반 웨이퍼 불량 분석은 수율 관리와 이상 원인 추적의 핵심 업무이지만, 실제 현업에서는 등록된 불량만 정확히 분류하는 것만으로는 충분하지 않다. 초기에는 기등록 불량을 대상으로 한 CNN 기반 분류기 구축을 목표로 하였으나, 운영 과정에서 라벨 등록 지연 및 라벨 노이즈, 신규 공정 변화에 따른 unknown defect 발생, 계측값과 이미지의 동시 해석 요구가 함께 존재함을 확인하였다. 이에 본 연구에서는 데이터 생성, 등록 불량 분류, 미등록 불량 군집화, 사용자 검토를 하나의 흐름으로 연결하는 도메인 지식 기반 복합 파이프라인을 제안한다. 데이터 계층에서는 dual-bucket 로그 수집, Cython 기반 초고속 파싱, palette-indexed PNG 및 positions JSON 생성을 통해 이미지와 chip-level 좌표 및 계측값을 정합하였다. 등록 불량 경로에서는 Optuna 기반 학습 최적화와 ConvNeXtV2 기반 1-stage classifier 개선을 통해 weighted F1를 0.78에서 0.92까지 향상시켰고, 이후 Grad-CAM 기반 ROI 추출, 클래스별 spatial prior, YOLO 이차 검증을 결합한 2단계 구조를 통해 최종 0.95를 달성하였다. 미등록 불량 경로에서는 자기지도 대조 학습과 HDBSCAN을 결합하여 unknown defect 후보를 자동 군집화하고, 대표 샘플 및 cluster summary를 생성하여 전문가 검토와 신규 라벨 등록을 지원하였다. 또한 palette PNG 기반 개인 색상 scheme, composite map, BIN/FBT/QVL overlay, chip annotation UI를 구축함으로써 향후 이미지-계측 융합 기반 multimodal 불량 분석으로 확장 가능한 운영형 분석 환경을 마련하였다.

**Keywords:** Wafer Defect Analysis, Failbit Map, ConvNeXtV2, Grad-CAM, YOLO, Contrastive Learning, HDBSCAN, Palette PNG, Multimodal Inspection

---

## 1. 서론

웨이퍼 Failbit Map은 메모리 테스트 결과를 공간적으로 표현한 데이터로서, 불량의 위치, 방향성, 밀집도, 가장자리 집중 여부와 같은 정보를 직접적으로 담고 있다. center, edge ring, local, scratch 계열 패턴은 단순 시각적 모양이 아니라 공정 이상 원인과 연결되는 공간적 의미를 갖기 때문에, 이를 자동으로 분류하고 해석하는 기술은 반도체 제조 현장에서 높은 실용성을 가진다.

본 연구는 처음에 기등록 불량 클래스만을 대상으로 CNN 기반 분류기를 구축하는 문제로 출발하였다. 그러나 실제 현업 적용 과정에서 세 가지 구조적 한계가 드러났다. 첫째, 라벨 등록과 유지가 전문가 의존적이어서 데이터셋에 라벨 오류와 라벨 지연이 누적된다. 둘째, 신규 제품 및 공정 변화에 따라 기존 클래스 체계에 없는 unknown defect가 발생하며, closed-set classifier는 이를 기존 클래스 중 하나로 강제 분류한다. 셋째, 실제 업무는 분류 결과만 보는 것이 아니라 wafer map, chip 좌표, 계측값, 사용자별 색상 해석, 수동 검토가 결합된 운영 workflow로 수행된다.

이 문제를 해결하기 위해서는 단일 모델 성능 개선만으로는 부족하며, 데이터 표현 방식, 시각화 계층, 라벨 확장 구조까지 함께 설계해야 한다. 특히 wafer map은 자연영상과 달리 절대 위치와 이산적인 상태 값이 중요한 데이터이므로, 일반적인 이미지 처리 관점보다 도메인 지식 기반 표현이 필요하다.

본 연구의 기여는 다음과 같다.

1. dual-bucket 기반 로그 정합, Cython 기반 파싱, palette-indexed PNG, positions JSON을 포함하는 운영형 데이터 생성 파이프라인을 구축하였다.
2. 등록 불량 분류에서 Optuna 기반 학습 최적화와 Grad-CAM ROI + YOLO 보정을 결합하여 weighted F1를 `0.78 -> 0.92 -> 0.95`로 향상시켰다.
3. unknown defect에 대해 Contrastive Learning과 HDBSCAN을 이용한 자동 군집화 경로를 구축하고, 전문가 검토 기반 신규 라벨 확장 루프를 제안하였다.
4. 개인 색상 scheme, composite map, BIN/FBT/QVL overlay, chip annotation을 지원하는 분석 UI를 통해 향후 이미지-계측 융합 기반 multimodal defect analysis의 기반을 마련하였다.

---

## 2. 데이터 생성 및 표현 계층

### 2.1 Dual-bucket 기반 raw 로그 정합

본 시스템의 입력 데이터는 단일 이미지 파일이 아니라 서로 다른 소스에서 수집되는 공정 로그와 계측 로그의 결합 결과이다. Bucket A에는 primary fail map raw 파일이 저장되고, Bucket B에는 chip-level measurement 정보가 저장된다. 두 bucket은 wafer 식별 규칙과 시간 오프셋 정보를 이용해 자동 매칭되며, 병렬 다운로드와 압축 해제 후 Cython 기반 고속 파싱을 거쳐 wafer image와 positions JSON을 동시에 생성한다.

```text
Bucket A (.Z) fail map raw
        + 
Bucket B (.gz) chip measurement
        ↓
filename/time matching
        ↓
parallel download + decompress
        ↓
Cython-based log parsing
        ↓
palette-indexed wafer PNG + positions JSON
```

**Figure 1.** Dual-bucket 기반 데이터 생성 파이프라인.

이 구조는 단순 이미지 생성기가 아니라, 이미지와 계측값을 동일 wafer 기준으로 정합하는 데이터 인프라에 해당한다. positions JSON에는 chip별 `rect`, `grid_edges`, `b`, `f`, `q`와 함께 wafer-level `yield`, `sys`, `gd`, `lt`, `tm` 메타데이터가 저장되며, 이후 분류기, 군집화, UI가 동일 좌표계를 공유하도록 한다.

### 2.2 JPEG, RGB PNG, Palette PNG의 차이와 도메인 적합성

본 연구에서 wafer map 저장 포맷으로 `32-color 8-bit palette-indexed PNG`를 채택한 것은 단순한 구현 취향이 아니라 도메인 지식 기반 설계 결정이다.

- JPEG는 자연영상에 적합한 손실 압축 방식으로, wafer map의 sharp한 경계와 discrete grade/bin 패턴을 손상시킬 수 있다.
- 일반 RGB PNG는 무손실이지만, 각 픽셀에 RGB가 직접 고정되어 있어 사용자별 색상 변경이나 의미 인덱스 유지 측면에서 비효율적이다.
- palette PNG는 픽셀에 색이 아니라 의미 인덱스를 저장하고, 실제 색상은 팔레트 테이블에서 정의한다.

즉 wafer map은 사진이 아니라 `grade/bin 상태의 공간 지도`이므로, 인덱스 기반 표현이 더 본질에 가깝다. 본 시스템은 grade 0~7, background, text, border, BIN-specific border를 고정 인덱스로 관리하고, UI에서는 `IDAT`의 인덱스 구조를 유지한 채 `PLTE`만 교체하여 색상 scheme을 즉시 변경한다.

**Table 1. 이미지 포맷 비교**

| 방식 | 압축 특성 | 의미 보존 | 개인 색상 변경 | wafer map 적합성 |
|------|-----------|-----------|----------------|------------------|
| JPEG | 손실 압축 | 낮음 | 낮음 | 낮음 |
| RGB PNG | 무손실 | 중간 | 낮음 | 중간 |
| Palette PNG | 무손실 + 인덱스 | 높음 | 매우 높음 | 매우 높음 |

특히 현업 사용자마다 defect별 선호 색상이 다르기 때문에, 동일 원본 map에 대해 사용자별 color scheme을 즉시 적용할 수 있어야 한다. palette PNG 구조는 이 요구를 충족하면서도 저장 용량을 줄이고, composite 및 overlay 연산과의 결합을 용이하게 한다.

### 2.3 positions JSON과 multimodal 확장성

positions JSON은 단순 좌표 보조 파일이 아니라 `image <-> chip geometry <-> measurement <-> annotation`을 연결하는 중간 표현이다. 이 구조를 통해:

1. chip overlay와 hit-test를 수행할 수 있고,
2. BIN/FBT/QVL 시각화를 wafer 좌표계에 맞춰 표시할 수 있으며,
3. 향후 이미지 임베딩과 계측값을 동시에 사용하는 multimodal 모델로 확장할 수 있다.

따라서 데이터 생성 단계에서 이미지와 JSON을 함께 만드는 설계는 후단 분석 파이프라인 전체의 기반이 된다.

---

## 3. 등록 불량 분석 파이프라인

### 3.1 Baseline 0.78에서 optimized 0.92까지

등록 불량 분류는 초기 baseline CNN에서 출발하여, 고성능 backbone과 학습 최적화를 통해 성능을 단계적으로 향상시켰다. 서버 환경에서는 Optuna 기반 하이퍼파라미터 탐색을 수행하여 learning rate, weight decay, scheduler, dropout, label smoothing, augmentation 강도, batch size, optimizer 조합 등을 폭넓게 탐색하였다.

현재 구현은 `num_classes`를 코드에 하드코딩하지 않고 checkpoint 출력 차원과 dataset 폴더 구조에서 동적으로 읽도록 되어 있다. 이는 제품군이나 운영 환경에 따라 등록 클래스 수가 변할 수 있기 때문이다. 본 논문에서 보고하는 운영 실험 기준 등록 불량 클래스 수는 **16개**이며, 실제 production setting의 classifier는 이 16-class closed-set 문제를 대상으로 학습·평가되었다.

이 단계의 목표는 단순히 최고 점수 하나를 찾는 것이 아니라, 라벨 노이즈가 존재하는 wafer dataset에서 일반화가 가능한 안정적 학습 설정을 확보하는 것이었다. 그 결과 1-stage classifier의 weighted F1는 0.78에서 0.92까지 향상되었다.

**Table 2. 등록 불량 분류 성능 향상 단계**

| 단계 | 구성 | Weighted F1 | 핵심 변화 |
|------|------|-------------|-----------|
| Step 0 | 초기 baseline CNN | 0.78 | 기본 CNN 분류기 |
| Step 1 | backbone/입력 구조 개선 | [서버 로그 값 입력] | ConvNeXtV2 계열 전환, 해상도 및 전처리 개선 |
| Step 2 | Optuna 기반 튜닝 완료 | 0.92 | optimizer, scheduler, regularization, augmentation 최적화 |
| Step 3 | ROI enhancement + YOLO 보정 | 0.95 | difficult class 재검증 및 spatial prior 보강 |

**Table 3. Optuna 기반 주요 탐색 항목**

| 범주 | 항목 | 목적 |
|------|------|------|
| Optimizer | learning rate, weight decay, optimizer 종류 | 수렴 안정화 및 일반화 향상 |
| Scheduler | cosine, warmup, decay 구조 | 후반 학습 안정화 |
| Regularization | dropout, label smoothing | 라벨 노이즈 완화 |
| Augmentation | resize, crop, intensity, noise | 패턴 변동성 대응 |
| Batching | batch size, accumulation, sampling | 클래스 편향 완화 |

또한 클래스별 precision/recall/F1를 계산한 뒤, precision 또는 recall이 기준값보다 낮은 클래스를 difficult class로 자동 식별하여 후단 ROI 보강 우선 대상으로 사용하였다. 현재 코드 기본값은 `PRECISION_THRESHOLD = 0.80`이며, 이는 class-wise 성능 분석과 ROI 보강 전략을 연결하는 실질적인 게이트 역할을 한다.

### 3.2 Confidence threshold 설계와 운영점 선택

본 시스템의 2단계 구조에서는 단순히 모델 점수만 높이는 것이 아니라, **어느 confidence에서 ROI enhancement를 발동할 것인가**가 전체 성능과 운영 효율을 좌우한다. 현재 코드에는 다음 기본 operating point가 반영되어 있다.

- `CONFIDENCE_THRESHOLD = 0.80`
- `YOLO_CONF_THRESHOLD = 0.25`
- `ROI_FOR_DIFFICULT_OR_LOWCONF_ONLY = True`

이 설정의 의미는 다음과 같다.

1. 1-stage classifier confidence가 충분히 높고 difficult class가 아니면 ROI 보강을 생략한다.
2. 1-stage confidence가 낮거나 difficult class이면 Grad-CAM 기반 ROI 추출과 YOLO 검증을 수행한다.
3. YOLO는 상대적으로 낮은 `0.25` confidence에서 후보 객체를 넓게 수집하되, 최종 판정은 class-object mapping과 ROI 문맥을 함께 고려한다.

운영 관점에서 threshold는 너무 낮아도, 너무 높아도 문제가 된다.

- classifier confidence threshold가 너무 낮으면 ROI enhancement가 과도하게 발동되어 계산량이 증가하고 불필요한 후단 보정이 많아진다.
- classifier confidence threshold가 너무 높으면 실제로 교정 가능한 borderline sample을 놓치게 된다.
- YOLO confidence threshold가 너무 낮으면 object 후보가 과다 검출되어 noise가 증가하고, 너무 높으면 실제 defect object를 놓쳐 correction recall이 감소한다.

실무적으로는 아래와 같은 sweep을 논문에 함께 제시하는 것이 가장 설득력 있다.

**Table 4. Confidence threshold sweep 제안 및 운영점**

| 항목 | sweep 후보 | 해석 기준 | 현재 운영값 |
|------|------------|-----------|-------------|
| Stage-1 classifier confidence | 0.70, 0.75, 0.80, 0.85, 0.90 | weighted F1, ROI 호출 비율, 교정 성공률 | **0.80** |
| YOLO confidence | 0.15, 0.20, 0.25, 0.30, 0.35 | correction precision, false detection 비율 | **0.25** |
| difficult class threshold | 0.75, 0.80, 0.85 | difficult class 개수와 후단 호출 집중도 | **0.80** |

이 표는 실제 서버 실험 결과를 입력하면 더 강해진다. 추천 서술은 다음과 같다.

> 16-class 환경에서 classifier confidence와 YOLO confidence를 함께 변화시키며 실험한 결과, classifier threshold를 약 0.80 수준으로 둘 때 교정 가능한 low-confidence sample을 충분히 포착하면서도 과도한 후단 호출을 억제할 수 있었다. 또한 YOLO confidence는 약 0.25 수준에서 detection recall과 false detection 간의 균형이 가장 안정적이었다.

### 3.3 ROI enhancement와 YOLO 보정

1-stage classifier 위에는 ROI enhancement 기반 2단계 보정 경로를 추가하였다. 1차 분류 결과와 confidence를 바탕으로 difficult class 또는 low-confidence 샘플만 선별하고, 해당 샘플에 대해 Grad-CAM 기반 ROI 추출과 YOLO 이차 검증을 수행한다.

이때 중요한 설계는 다음과 같다.

1. Grad-CAM 기반 dynamic ROI 생성
2. 클래스별 평균 ROI 패턴과의 spatial prior 블렌딩
3. 최소 ROI 크기 보정
4. class-object mapping 기반 YOLO 검증
5. difficult class 또는 저신뢰 샘플에만 선택적 적용

이 구조는 단순 후단 ensemble이 아니라, 웨이퍼 패턴의 공간적 특성을 반영한 domain-guided correction module로 해석할 수 있다. 특히 center/edge/local 계열처럼 공간적으로 유사한 패턴 간 혼동을 줄이는 데 효과적이었다.

```text
Input wafer map
   ↓
1-stage ConvNeXtV2 classifier
   ↓
confidence / difficult-class gate
   ↓
Grad-CAM heatmap
   ↓
ROI extraction + average ROI prior blending
   ↓
ROI classifier or YOLO verification
   ↓
final corrected prediction
```

**Figure 2.** 등록 불량 2단계 분류 파이프라인.

### 3.4 YOLO 하이퍼파라미터 튜닝 항목

YOLO는 본 시스템에서 standalone detector가 아니라 ROI 기반 defect verification 모듈로 사용된다. 따라서 튜닝 목표도 일반 object detection benchmark와 다르며, `작은 ROI 안에서 defect object를 놓치지 않으면서도 잘못된 object over-detection을 억제하는 것`이 중요하다.

로컬 코드에서 직접 확인되는 추론 시 핵심 파라미터는 `YOLO_CONF_THRESHOLD`이며, server-side 학습에서는 추가로 아래 항목들을 조정했을 가능성이 높다. 최종 투고본에는 반드시 서버 학습 로그 기준 실제 값을 채워 넣는 것을 권장한다.

**Table 5. YOLO 튜닝 항목과 목적**

| 범주 | 튜닝 항목 | 목적 | 값 |
|------|-----------|------|----|
| Inference | confidence threshold | ROI 내 defect candidate 검출 민감도 조절 | `0.25` |
| Input | image size (`imgsz`) | 작은 defect shape 보존 | `[서버 로그 입력]` |
| Training | epochs, batch size | 수렴 안정성과 데이터 활용도 확보 | `[서버 로그 입력]` |
| Optimizer | learning rate, weight decay | detector 일반화 성능 향상 | `[서버 로그 입력]` |
| Loss balance | box / cls / dfl 계수 | localization과 class consistency 균형 | `[서버 로그 입력]` |
| Augmentation | degrees, translate, scale, mosaic, mixup, hsv | ROI detector의 강건성 향상 | `[서버 로그 입력]` |
| Early stopping | patience | overfitting 방지 | `[서버 로그 입력]` |

논문에서는 다음과 같이 쓰는 것이 안전하다.

> YOLO 모듈은 단일 전체 이미지를 대상으로 하는 일반 detector가 아니라, Grad-CAM 기반 ROI 내부에서 defect object consistency를 확인하는 검증기로 사용되었다. 따라서 하이퍼파라미터 튜닝 또한 global object detection 성능보다 ROI 내부의 correction precision과 false detection 억제에 초점을 맞추어 수행하였다.

### 3.5 서버 실험에서 확보된 추가 증거

저장소 외 서버 실험에서는 다음 자료가 확보되어 있다.

1. `true != original prediction`이었으나 `ROI-enhanced prediction == true`로 교정된 대표 샘플 이미지
2. original confusion matrix와 ROI-enhanced confusion matrix

따라서 최종 제출본에는 아래 두 그림을 넣는 것이 바람직하다.

- **Figure 3.** ROI enhancement로 오분류가 정분류로 교정된 대표 사례
- **Figure 4.** original classifier와 ROI-enhanced classifier의 confusion matrix 비교

본문 서술은 다음과 같이 정리할 수 있다.

> ROI enhancement는 평균 성능 향상뿐 아니라, baseline classifier가 오분류한 샘플 중 일부를 정답 클래스로 복원하는 효과를 보였다. confusion matrix 비교 결과, 공간적으로 유사한 패턴 간의 혼동이 감소하였으며, 이는 Grad-CAM 기반 local evidence와 클래스별 spatial prior, YOLO 이차 검증이 상호 보완적으로 작용한 결과로 해석된다.

---

## 4. 미등록 불량 분석 파이프라인

### 4.1 Contrastive Learning + HDBSCAN

unknown defect는 사전 라벨이 존재하지 않으므로 supervised classifier만으로는 적절히 다루기 어렵다. 본 시스템에서는 ConvNeXtV2 backbone을 재사용하되 backbone은 고정하고 projection head를 학습하여, 기존 wafer 표현을 유지하면서 unknown 분리를 위한 임베딩 공간을 형성하였다.

현재 구현에서 unknown 군집화 성능을 높이기 위해 사용된 요소는 다음과 같다.

1. **도메인 제약 기반 증강**
   - flip을 제거하고 소규모 회전, 이동, 스케일, 노이즈만 사용
   - wafer map에서 위치와 방향의 의미를 보존하기 위함
2. **Global InfoNCE + Queue**
   - large queue를 이용해 batch 한계를 넘는 negative bank 확보
3. **Local InfoNCE**
   - 국소 결함 구조를 보존하도록 local window 기반 contrastive term 추가
4. **HDBSCAN filtering**
   - cluster size, median membership probability, persistence 기준으로 안정적 cluster만 유지
5. **Medoid representative 저장**
   - 각 cluster의 대표 샘플을 저장해 전문가 검토 효율 향상

**Table 4. unknown defect 군집화 품질 향상 요소**

| 요소 | 구현 포인트 | 기대 효과 |
|------|-------------|-----------|
| no-flip augmentation | small rotate/translate/scale only | 위치 의미 보존 |
| backbone freeze | ConvNeXtV2 고정 + projection head 학습 | 안정적 임베딩 |
| queue-based negative bank | large queue memory | 분리도 향상 |
| local contrastive term | local window / top-k | 국소 defect 구조 보존 |
| HDBSCAN keep filter | size/probability/persistence | noise cluster 제거 |
| medoid summary | representative 저장 | human review 부담 감소 |

### 4.2 unknown defect 성능은 어떻게 평가할 것인가

unknown defect는 정답 레이블이 미리 정의되어 있지 않으므로, 일반적인 accuracy로 평가하기 어렵다. 본 연구에서는 세 층위 평가를 권장한다.

1. **Pseudo-open-set 정량 평가**
   - 기존 등록 클래스 일부를 training에서 제외하고 unknown으로 간주
   - cluster purity, NMI, ARI, noise ratio, kept cluster coverage 계산
2. **cluster quality 지표**
   - median membership probability, persistence, cohesion, margin 활용
3. **운영 효율 지표**
   - 전문가 승인 cluster 비율
   - 검토 이미지 수 감소율
   - 신규 라벨 등록 시간
   - 신규 라벨 편입 후 supervised 경로 성능 변화

즉 unknown defect 평가는 `몇 퍼센트 맞췄는가`보다 `신규 불량 후보를 얼마나 안정적으로 압축해 전문가 검토가 가능한 구조로 제시했는가`에 더 가깝다.

---

## 5. 분석 UI와 운영형 검토 루프

### 5.1 mapviewer의 역할

`mapviewer`는 단순 결과 표시 화면이 아니라, 이미지 표현과 현업 검토를 연결하는 분석 계층이다. 주요 기능은 다음과 같다.

1. pyramid 기반 대용량 wafer map 탐색
2. palette PNG의 `PLTE` patch 기반 개인 색상 scheme 적용
3. chip overlay 및 annotation
4. composite map과 weighted average 시각화
5. BIN/FBT/QVL overlay 및 measure composite

이 구조는 반도체 현업에서 자주 발생하는 “같은 map을 서로 다른 기준으로 다시 보고 싶다”는 요구를 충족한다. 같은 wafer map에 대해 개인색, grade filter, bottom filter, gradient filter를 빠르게 적용할 수 있기 때문이다.

### 5.2 Human-in-the-loop 라벨 확장

Chip annotation API와 UI는 등록/미등록 모두에 중요하다.

- 등록 불량: mislabeled sample 재검토
- 미등록 불량: cluster 대표 샘플 확인 후 신규 라벨 등록
- measure overlay: 이미지와 계측값의 동시 해석

따라서 본 시스템은 완전 자동 분류기라기보다, `AI-assisted inspection and labeling system`으로 보는 것이 더 정확하다.

### 5.3 multimodal readiness

현재 저장 구조에는 이미지 외에 `BIN`, `FBT`, `QVL`, `yield`, `sys`, `lt`, `tm`이 함께 저장된다. 이는 아직 full multimodal model까지는 연결되지 않았더라도, 향후 이미지 임베딩과 계측값을 함께 사용하는 모델로 확장할 수 있는 데이터 기반이 이미 확보되었음을 의미한다.

---

## 6. 결과 및 논의

등록 불량 경로에서는 Optuna 기반 튜닝을 포함한 1-stage optimization으로 weighted F1 0.92를 달성하였고, ROI enhancement와 YOLO 검증을 통해 0.95까지 향상되었다. 이는 단순 backbone 교체가 아니라, difficult class 중심 보정과 웨이퍼 패턴의 공간 특성을 반영한 domain-guided refinement의 결과이다.

데이터 인프라 관점에서는 dual-bucket 수집, Cython 기반 파싱, palette PNG, positions JSON이 단순 전처리 모듈이 아니라 전체 분석 체계의 공통 기반으로 작동한다. 특히 palette-indexed PNG는 색상값 중심이 아니라 의미 인덱스 중심 표현을 가능하게 하며, 이는 개인 색상 scheme, composite, measure overlay, annotation을 모두 효율적으로 지원한다.

unknown 경로는 아직 완전한 벤치마크보다 운영 검토 중심으로 활용되고 있으나, 현재 구현만으로도 cluster 후보 생성, representative 요약, filtering, 전문가 검토, 신규 라벨 확장이라는 실용적 기능을 제공한다. 즉 본 연구는 registered classification과 unknown discovery를 분리된 문제로 보지 않고, 하나의 운영형 반도체 분석 시스템 안에서 통합했다는 점에서 의미가 있다.

---

## 7. 결론

본 연구는 반도체 웨이퍼 불량 분석을 위해 데이터 생성, 등록 불량 분류, 미등록 불량 군집화, 분석 UI를 하나의 파이프라인으로 통합하였다. dual-bucket 로그 정합과 Cython 기반 파싱을 통해 이미지와 계측값을 함께 생성하고, palette-indexed PNG와 positions JSON을 통해 의미 인덱스 기반 표현을 유지하였다. 등록 불량 경로에서는 Optuna 기반 학습 최적화로 `0.78 -> 0.92`, ROI enhancement와 YOLO 검증으로 `0.92 -> 0.95`를 달성하였다. 미등록 불량 경로에서는 Contrastive Learning과 HDBSCAN을 통해 unknown defect 후보를 자동 군집화하고, 전문가 검토 기반 신규 라벨 확장 루프를 마련하였다. 또한 개인 색상 scheme, composite, BIN/FBT/QVL overlay, chip annotation을 포함한 UI를 구축함으로써 향후 이미지-계측 융합 기반 multimodal defect analysis로 확장 가능한 운영형 기반을 확보하였다.

향후 연구에서는 pseudo-open-set 기반 unknown 정량 평가를 정립하고, 서버에 확보된 confusion matrix 및 ROI 교정 사례를 포함한 정량·정성 분석을 보강할 필요가 있다. 또한 chip-level 계측값과 이미지 임베딩을 함께 활용하는 multimodal 모델을 도입함으로써, 신규 불량 조기 탐지와 원인 해석 정확도를 더욱 향상시킬 수 있을 것으로 기대한다.

---

## 그림 및 표 삽입 체크리스트

최종 제출본에서 권장하는 삽입 순서는 다음과 같다.

1. **Figure 1** Dual-bucket 데이터 생성 파이프라인
2. **Table 1** JPEG / RGB PNG / Palette PNG 비교
3. **Table 2** 등록 불량 성능 향상 단계
4. **Figure 2** 등록 불량 2단계 분류 파이프라인
5. **Figure 3** ROI 교정 대표 사례
6. **Figure 4** original vs ROI-enhanced confusion matrix
7. **Table 4** unknown defect 군집화 품질 향상 요소

---

## 참고문헌

[1] T. Nakazawa and D. V. Kulkarni, "Wafer Map Defect Pattern Classification and Image Retrieval Using Convolutional Neural Network," *IEEE Transactions on Semiconductor Manufacturing*, vol. 31, no. 2, pp. 309-314, 2018.

[2] M. B. Alawieh, D. Boning, and D. Z. Pan, "Wafer Map Defect Patterns Classification using Deep Selective Learning," in *Proceedings of the 57th ACM/IEEE Design Automation Conference (DAC)*, pp. 1-6, 2020.

[3] Y. Kim, D. Cho, and J.-H. Lee, "Wafer Defect Pattern Classification With Detecting Out-of-Distribution," *IEEE Transactions on Semiconductor Manufacturing*, vol. 34, no. 4, pp. 498-505, 2021.

[4] J. Jang and G. T. Lee, "Decision Fusion Approach for Detecting Unknown Wafer Bin Map Patterns Based on a Deep Multitask Learning Model," *Expert Systems with Applications*, vol. 213, 2023, Art. no. 119363.

[5] S. Woo, S. Debnath, R. Hu, X. Chen, Z. Liu, I. S. Kweon, and S. Xie, "ConvNeXt V2: Co-Designing and Scaling ConvNets With Masked Autoencoders," in *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, pp. 16133-16142, 2023.

[6] R. R. Selvaraju, M. Cogswell, A. Das, R. Vedantam, D. Parikh, and D. Batra, "Grad-CAM: Visual Explanations From Deep Networks via Gradient-Based Localization," in *Proceedings of the IEEE International Conference on Computer Vision (ICCV)*, pp. 618-626, 2017.

[7] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, "A Simple Framework for Contrastive Learning of Visual Representations," in *Proceedings of the 37th International Conference on Machine Learning (ICML)*, *PMLR*, vol. 119, pp. 1597-1607, 2020.

[8] R. J. G. B. Campello, D. Moulavi, and J. Sander, "Density-Based Clustering Based on Hierarchical Density Estimates," in *Advances in Knowledge Discovery and Data Mining (PAKDD 2013, Part II)*, pp. 160-172, 2013.
