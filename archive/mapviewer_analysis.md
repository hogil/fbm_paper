# `mapviewer` 프로젝트 분석

분석 기준 폴더: `D:\project\mapviewer`  
분석 목적: wafer map 시각화/검토/UI 계층의 구조를 정리하고, 논문에서 어떻게 학술적으로 서술할지 정리한다.

---

## 1. 프로젝트 역할

`mapviewer`는 단순 이미지 뷰어가 아니라, 대규모 wafer map을 빠르게 탐색하고, 개인 색상 scheme, chip annotation, composite map, BIN/FBT/QVL overlay를 결합해 현업 검토 workflow를 지원하는 운영형 분석 UI이다.

전체 파이프라인에서의 위치는 아래와 같다.

```text
fail-map
  → palette PNG + positions JSON + measurement metadata 생성
  → image_classification
      - registered defect classification
      - unknown defect clustering
  → mapviewer
      - wafer inspection
      - personalized recolor
      - chip overlay / annotation
      - BIN / FBT / QVL analysis
      - composite visualization
```

즉 `mapviewer`는 모델 결과를 단순히 표시하는 프런트엔드가 아니라, 데이터 표현 규약과 현업 해석 행위를 연결하는 `analysis and verification layer`에 해당한다.

---

## 2. 핵심 설계 요약

문서와 코드 기준으로 확인되는 핵심 설계는 다음과 같다.

1. **Pyramid 기반 대용량 이미지 렌더링**
   - `/api/image?level=...`로 필요한 해상도만 전송
   - 서버 피라미드 캐시와 브라우저 내부 피라미드를 함께 사용
   - 대형 wafer map에서도 줌/팬 응답성을 유지

2. **palette PNG 기반 개인 색상 적용**
   - 사용자별 color scheme을 `logs/color-legends.json`에서 관리
   - 원본 PNG의 `PLTE`를 메모리에서 패치하여 개인색, grade filter, bottom filter, gradient filter 적용
   - 동일한 wafer map 원본에 대해 사용자별 시각화 요구를 충족

3. **positions JSON 기반 chip overlay / annotation**
   - `coord.grid_edges`, `chips[].rect`, `chips[].b`, `chips[].f`, `chips[].q`를 직접 사용
   - wafer image와 chip-level geometry/measurement가 동일 좌표계에서 연결됨

4. **Composite / Measure Composite**
   - 다수 wafer를 같은 좌표계에 정렬해 grade composite, weighted average, measure composite 생성
   - `square_maps_data.npz` 캐시를 사용해 빠른 recolor 및 subset 재생성 수행

5. **BIN / FBT / QVL overlay**
   - 단순 이미지 색상 변경이 아니라 chip 단위의 bin/measurement 통계를 시각화
   - UI에서 이미지, 좌표, 측정값을 하나의 분석 화면에서 다룰 수 있음

---

## 3. 이미지 포맷 선택이 왜 중요한가

논문 심사자나 비개발자에게는 `JPEG`, `일반 PNG`, `palette PNG`의 차이를 짧게 설명하는 것이 필요하다. 이 포맷 선택은 단순 구현 취향이 아니라 `wafer map이 사진이 아니라 의미 인덱스 기반 지도`라는 반도체 도메인 특성을 반영한 결과이기 때문이다.

### 3.1 JPEG

- **원리**: 연속 톤 이미지를 잘 압축하기 위해 블록 단위 손실 압축을 수행한다.
- **장점**: 자연영상, 사진, 썸네일에서 용량이 작다.
- **한계**:
  - wafer map의 경계가 번지거나 block artifact가 생길 수 있다.
  - 픽셀 색이 의미를 갖는 discrete map에서는 손실 압축이 해석을 방해한다.
  - 색값이 semantic class를 직접 표현하지 못하므로 grade/bin 의미를 유지하기 어렵다.

즉 JPEG는 `사진 기반 view`에는 유리하지만, `정확한 grade/bin 의미 보존`에는 적합하지 않다.

### 3.2 일반 RGB PNG

- **원리**: 무손실 압축으로 픽셀 RGB 값을 그대로 보존한다.
- **장점**:
  - 경계가 날카로운 도형과 지도형 이미지를 깨지지 않게 저장할 수 있다.
  - JPEG보다 의미 보존이 훨씬 좋다.
- **한계**:
  - 각 픽셀에 RGB가 직접 baked되어 있어 색상 scheme을 바꾸려면 픽셀 전체를 다시 써야 한다.
  - 같은 의미의 grade map이라도 색상 변경 시 재생성 또는 전체 recolor 연산이 필요하다.
  - discrete semantic map 치고는 저장 효율이 떨어질 수 있다.

즉 일반 PNG는 손실은 없지만, `의미`보다 `색상 결과`를 저장하는 방식이다.

### 3.3 Palette-indexed PNG

- **원리**: 픽셀은 RGB가 아니라 `인덱스`를 저장하고, 색상은 팔레트 테이블(`PLTE`)에서 정의한다.
- **장점**:
  - 픽셀 값이 `Grade0~7`, `background`, `Normal border`, `BIN border` 같은 의미 인덱스로 유지된다.
  - `IDAT`의 인덱스 구조는 그대로 두고 `PLTE`만 바꿔도 전체 색상 scheme을 즉시 바꿀 수 있다.
  - 저장 용량이 작고, recolor가 매우 빠르며, semantic consistency가 유지된다.
- **현업 적합성**:
  - 현업 사용자마다 defect별 선호 색상이 다르다.
  - 동일한 wafer map에 대해 사람마다 다른 색상 scheme으로 빠르게 보고 싶다.
  - composite, measure overlay, 개인 palette를 모두 같은 원본 위에서 동적으로 바꿔야 한다.

따라서 palette PNG는 `사진 압축 포맷`이 아니라 `wafer 상태를 의미 인덱스로 저장하는 반도체 전용 표현 방식`에 가깝다.

### 3.4 논문용 한 문단 요약

> Wafer map은 자연영상이 아니라 grade, border, BIN과 같은 이산적 의미 단위의 공간 배치 정보로 구성된다. 따라서 본 시스템은 손실 압축 기반 JPEG나 RGB 값 자체를 저장하는 일반 PNG 대신, 의미 인덱스를 직접 보존하는 palette-indexed PNG를 채택하였다. 이 구조는 무손실 형태 보존, 저장 용량 절감, 사용자별 색상 scheme의 즉시 적용, 그리고 composite/overlay 연산의 효율적 수행을 동시에 가능하게 한다.

---

## 4. 반도체 도메인 지식이 UI 설계에 반영된 방식

`mapviewer`는 일반 이미지 뷰어가 아니라, 반도체 도메인 지식을 UI 수준까지 반영한 시스템이다.

### 4.1 개인 색상 scheme

현업 엔지니어는 defect나 grade를 인지할 때 선호 색상 체계가 다르다. 이 요구는 단순 테마 기능이 아니라, 실제 판독 속도와 분석 편의성에 영향을 준다. `mapviewer`는 사용자 로그인 ID 기준으로 color scheme을 관리하고, 동일한 indexed PNG에 대해 `PLTE patch`만으로 개인별 색 체계를 적용한다.

이 설계는 아래 문제를 해결한다.

- 같은 wafer map을 서로 다른 엔지니어가 각자 익숙한 색상으로 해석 가능
- 색상을 바꾸더라도 underlying semantic index는 변하지 않음
- 저장 파일을 중복 생성할 필요가 없음

### 4.2 chip-level geometry와 측정값 정합

Chip annotation과 measure overlay는 이미지 위에 임의로 마킹하는 기능이 아니다. `positions.json`의 `rect`, `grid_edges`, `b`, `f`, `q`를 기반으로 wafer image와 chip-level measurement를 정확히 정렬한다. 따라서 `mapviewer`는 단순 뷰어가 아니라 `image + geometry + measurement alignment interface`다.

### 4.3 BIN / FBT / QVL overlay

문서와 코드에서는 다음 구조가 확인된다.

- `BIN`: chip의 `b` 값을 기준으로 bin별 시각화
- `FBT`: chip의 `f` 값을 기준으로 threshold/ratio 시각화
- `QVL`: chip의 `q` 값을 기준으로 quality/value level 시각화

이 overlay는 원본 wafer map 위에 보조 정보를 덧그리는 수준이 아니라, 동일 wafer의 위치 정보와 측정값 정보를 함께 해석하도록 만드는 도구다. 논문에서는 이를 `multimodal inspection readiness`로 표현할 수 있다.

---

## 5. Composite Map과 Measure Composite의 의미

`mapviewer`의 composite 기능은 다수 wafer를 같은 좌표계에서 요약하는 집계 분석 도구다.

### 5.1 Grade Composite

- 여러 wafer를 합쳐 `Grade_0 ~ Grade_7` 분포를 요약
- `square_average`, `square_weighted_average` 생성
- 결과는 사용자별 composite gradient와 personal palette 배경/경계색을 사용

### 5.2 Measure Composite

- `BIN`, `FBT`, `QVL` 기준으로 여러 wafer의 chip-level measurement를 집계
- average/weighted average와 달리, 계측량 관점에서 hotspot과 분포를 확인
- recolor API를 통해 gradient filter, bin filter 적용 가능

### 5.3 왜 중요한가

이 기능은 `한 장의 wafer`를 보는 수준을 넘어,

- 동일 LOT 또는 조건의 wafer 집합에서 반복되는 hotspot을 찾고
- grade pattern과 measurement pattern을 비교하며
- 불량 패턴과 계측량의 상관관계를 탐색

하게 만든다.

즉 composite는 단순 시각화 보조가 아니라 `population-level pattern analysis` 도구다.

---

## 6. Chip Annotation과 Human-in-the-Loop

`mapviewer`의 chip annotation은 논문에서 중요하게 써야 한다. 이유는 이 기능이 단순 메모가 아니라 `라벨 확장과 검증 workflow`의 중심이기 때문이다.

현재 구조는 다음과 같다.

- `GET /api/chip-positions`
- `GET /api/chip-annotations`
- `POST /api/classify/chips`
- `POST /api/chip-images/extract`

즉 사용자는:

1. wafer map에서 chip 위치를 정확히 확인하고
2. 특정 chip을 선택해 class를 부여하며
3. crop 이미지를 추출하고
4. annotation JSON과 classification crop을 함께 저장할 수 있다.

이 구조는 등록 불량/미등록 불량 모두에 중요하다.

- 등록 불량: mislabel correction, hard sample review
- 미등록 불량: cluster 대표 샘플 검토 후 신규 라벨 등록

논문에서는 이를 `human-in-the-loop validation and label expansion interface`로 쓰는 것이 적절하다.

---

## 7. 논문에 바로 쓸 수 있는 핵심 메시지

### 짧은 버전

> `mapviewer`는 palette-indexed wafer PNG와 positions JSON을 기반으로 대용량 웨이퍼 맵의 고속 탐색, 사용자별 개인 색상 적용, chip annotation, composite 집계, BIN/FBT/QVL overlay를 지원하는 분석 UI이다.

### 확장 버전

> 본 시스템의 UI 계층은 단순 결과 시각화 도구가 아니라, wafer map의 의미 인덱스 구조와 chip-level 측정값을 함께 해석할 수 있도록 설계된 분석 환경이다. 구체적으로, palette-indexed PNG의 `PLTE`를 메모리에서 패치하여 사용자별 개인 색상 scheme을 즉시 반영하고, positions JSON의 chip geometry와 `BIN/FBT/QVL` 측정값을 동일 좌표계에 정합함으로써, registered classification 결과 검토와 unknown cluster 후보 검증을 하나의 인터페이스에서 수행할 수 있게 하였다.

### 포맷 선택까지 포함한 버전

> Wafer map은 자연영상이 아니라 이산적인 grade/bin 상태의 공간 배치 표현이므로, 본 시스템은 JPEG나 일반 RGB PNG 대신 의미 인덱스를 직접 저장하는 palette-indexed PNG를 채택하였다. 이를 통해 무손실 형태 보존, 저장 효율, 사용자별 즉시 recolor, composite/measure overlay의 고속 처리를 동시에 달성하였다.

---

## 8. 추천 Figure / Table

논문에 `mapviewer` 관련 그림을 넣는다면 아래 정도가 가장 효율적이다.

### Figure 후보 1

`palette PNG + positions JSON + personalized recolor + chip overlay` 개념도

```text
palette PNG (index map)
   + PLTE patch
   + positions JSON
   + F/Q/B metadata
      ↓
user-specific recolor
chip overlay
BIN / FBT / QVL visualization
```

### Figure 후보 2

`single wafer view / composite view / measure composite view` 3분할 예시

### Table 후보

`JPEG vs RGB PNG vs Palette PNG` 비교표

| 방식 | 압축 특성 | 의미 보존 | 개인색 변경 | wafer map 적합성 |
|------|-----------|-----------|-------------|------------------|
| JPEG | 손실 압축 | 낮음 | 낮음 | 낮음 |
| RGB PNG | 무손실 | 중간 | 낮음 | 중간 |
| Palette PNG | 무손실 + 인덱스 | 높음 | 매우 높음 | 매우 높음 |

---

## 9. 최종 정리

`mapviewer`는 논문에서 빼도 되는 부수적 UI가 아니라, 다음 세 가지를 증명하는 계층이다.

1. **palette PNG 설계가 실제 운영에서 왜 필요한지**
2. **image + geometry + measurement를 동일 표현으로 묶었다는 점**
3. **모델 출력이 현업 라벨링/검토 workflow와 어떻게 연결되는지**

따라서 논문에서는 UI를 상세 구현 목록으로 길게 쓰기보다, `도메인 지식 기반 표현과 human-in-the-loop 검증을 가능하게 하는 분석 인터페이스`로 요약하는 것이 가장 좋다.
