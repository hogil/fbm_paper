# `fail-map` 프로젝트 분석

분석 기준 폴더: `D:\project\fail-map`  
분석 목적: 웨이퍼 Failbit Map 생성 파이프라인의 구조, 성능 최적화 포인트, 논문 서술에 활용할 수 있는 도메인 기여 요소를 정리한다.

---

## 1. 프로젝트 역할

`fail-map`은 단순 이미지 생성 스크립트가 아니라, 반도체 설비 로그와 계측 로그를 수집·매칭·가공하여 학습 및 분석에 사용할 수 있는 `wafer map image + positions JSON + measurement metadata`를 생성하는 데이터 파이프라인이다.

핵심 목적은 다음과 같다.

1. S3 호환 스토리지에서 압축된 wafer raw 파일을 자동 수집한다.
2. Bucket A와 Bucket B의 서로 다른 로그를 시간/파일명 규칙으로 매칭한다.
3. Cython 최적화 파싱으로 대량 로그를 빠르게 가공한다.
4. palette-indexed PNG 형식의 wafer image를 생성한다.
5. 칩 좌표, bin, FTN/QTN, yield/sys/LT/TM 등을 담은 positions JSON을 생성한다.
6. 이후 분류 모델, 군집화 모듈, 시각화 UI가 동일한 데이터 구조를 사용하도록 만든다.

즉, 이 프로젝트는 전체 시스템에서 `데이터 생성 및 정합 계층`에 해당한다.

---

## 2. 전체 파이프라인

`README.md`와 `docs/pipeline-overview.md` 기준으로 확인되는 전체 흐름은 아래와 같다.

```text
device_info.txt
    |
    v
Bucket A key 탐색 (.Z)
    |
    +--> Bucket B key 예측/매칭 (.gz, 시간차 -10~+10초)
    |
    v
병렬 다운로드 + 압축 해제
    |
    v
Cython / Python 파싱
    |
    +--> palette-indexed PNG 생성
    |
    +--> positions JSON 생성
            - chip rect / grid
            - bin / FTN / QTN
            - yield / sys / gd / LT / TM
            - bucket B match summary
```

논문용으로는 다음과 같이 요약하는 것이 적절하다.

- Bucket A는 primary fail map raw source
- Bucket B는 chip-level measurement source
- 두 source를 wafer/time 규칙으로 정합
- 병렬 수집과 고속 파싱을 통해 이미지와 JSON을 동시 생성

---

## 3. 핵심 구현 파일

### `fail-map-with-bucketb.py`

메인 오케스트레이션 파일이다.

- `PipelineConfig`에서 bucket 이름, thread 수, palette 색상 파일, 저장 루트 등을 관리한다.
- `run_pipeline_for_dataframe()`가 전체 실행 흐름을 제어한다.
- Bucket B 매칭 결과를 샘플 메타에 주입한 뒤 이미지 생성과 positions JSON 생성을 이어준다.
- 파일명에 `root_step_wafer_stime_yield_sys_lt_tm.png` 형식으로 메타를 반영한다.

논문 포인트:

- 단순 전처리가 아니라 `이미지 파일명 자체에 운영 메타를 실은 구조`
- `image + json` 동시 생성 구조
- Bucket B match 성공/실패 통계까지 추적하는 운영형 설계

### `utils.py`

공통 유틸리티와 성능 최적화 로직이 모여 있다.

- S3 client 생성
- 시간창 기반 폴더 선택
- 다양한 압축 포맷 해제 (`.Z`, `.gz`, `.7z`, `.zip`, `.tar`)
- 병렬 다운로드
- header 파싱
- palette 생성
- Cython fallback 로딩
- indexed PNG 원자적 저장

특히 `download_and_decompress_parallel()`은 단순 다운로드가 아니라 재귀 아카이브 해제까지 처리한다.

논문 포인트:

- 대규모 raw 로그를 운영 환경에서 처리할 수 있도록 `병렬 다운로드 + 다중 압축 자동 해제` 지원
- `Cython 없으면 Python fallback` 구조로 배포 유연성 확보

### `bucketb_module.py`

Bucket B 매칭과 계측값 파싱을 담당한다.

- Bucket A key를 해석해 Bucket B 후보 key를 생성한다.
- 시간 오프셋 기반 candidate 탐색과 prefix-list 매칭을 제공한다.
- 실패 시 fallback / closest time 매칭 전략까지 제공한다.
- Bucket B 내용에서 `FTN`, `QTN`, 칩별 `F=`, `Q=`, `b`를 파싱한다.
- Bucket B 기준 yield까지 계산한다.

논문 포인트:

- `서로 다른 로그 체계 간 정합`이라는 실무 난제를 해결
- `filename/time rule + prefix narrowing + closest fallback` 조합으로 검색 비용 축소
- 계측 로그를 이미지 분석 파이프라인에 결합하는 연결 고리

### `positions_module.py`

positions JSON 생성 전담 모듈이다.

- 회전 후 타일 좌표 보정
- 중심 좌표 계산
- 칩별 `rect` 생성
- FTN/QTN 값을 각 칩에 `f`, `q` 필드로 주입
- `gd`, `yield`, `sys` 계산
- Bucket B match summary 저장

논문 포인트:

- 단순 시각화용 JSON이 아니라 `chip-level annotation and measurement container`
- 이후 UI와 multimodal 분석의 핵심 연결 포맷

### `cython_functions.pyx`

hex block를 grade 문자열로 빠르게 변환하는 성능 최적화 모듈이다.

- `convert_hex_values_cython()`
- `transform_line()`
- char map 기반 변환

논문 포인트:

- 대량 로그 처리 병목을 Python이 아닌 Cython으로 완화
- 설비 로그 기반 image generation을 학습 파이프라인에 실용 수준으로 끌어올린 요소

---

## 4. 성능 및 운영 최적화 포인트

문서와 코드 기준으로 확인되는 핵심 최적화는 다음과 같다.

1. `Dual Bucket 병렬 처리`
   - Bucket A / B를 순차로 처리하지 않고 병렬 다운로드
   - README 기준 1000 파일 처리에서 naive 대비 약 60% 수준 시간

2. `Fast index / prefix-list matching`
   - Bucket B 전체를 매번 brute force로 찾지 않음
   - `YYYYMMDD/LOT_Wxx_` 단위로 좁은 prefix를 먼저 조회
   - 시간 오프셋 후보를 membership check로 빠르게 판정

3. `Cython 파싱`
   - hex -> grade 변환 병목을 Cython으로 최적화
   - Python fallback 존재

4. `병렬 다운로드 + 다중 압축 해제`
   - `.Z`, `.gz`, `.7z`, `.zip`, `.tar` 처리
   - nested archive까지 대응

5. `ProcessPool 기반 이미지 생성`
   - 로그 파싱과 이미지 생성을 분리
   - 대량 샘플 처리에 적합

논문에선 이를 `데이터 생성 파이프라인의 처리량 확보를 위한 시스템 최적화`로 표현할 수 있다.

---

## 5. palette PNG 구조의 의미 ★ 핵심 도메인 지식 적용

### 5-1. 이미지 포맷 3가지 비교 (논문 독자를 위한 배경 설명)

| 포맷 | 원리 | 특징 |
|------|------|------|
| **JPEG** | 픽셀 RGB를 DCT 주파수로 변환 후 손실 압축 | 파일 작음, 고주파 경계 뭉개짐, 색상 정보 손실 |
| **PNG (24bit)** | 픽셀마다 직접 RGB(3byte) 저장, 무손실 압축 | 화질 완벽 유지, 파일 큼 |
| **Palette-indexed PNG (8bit)** | 픽셀에 색상 직접 저장 않고 **팔레트 인덱스(1byte)** 저장, PLTE 청크에 색상표 따로 존재 | 화질 유지 + 파일 작음 + **색상표만 교체 가능** |

**Failbit Map에 JPEG가 안 되는 이유**: Grade 0~7의 경계가 뭉개지면 grade 구분 자체가 불가능해진다. 반도체 불량 맵에서 픽셀 하나의 grade 값이 달라지면 분류 결과가 달라진다.

**Failbit Map에 일반 24bit PNG가 아닌 이유**: 화질은 유지되지만, 현업 사용자마다 불량별 선호 색상이 다르다 → 사용자가 색상을 바꿀 때마다 이미지 전체를 재렌더링해야 한다 (수십만 장).

### 5-2. 팔레트 PNG의 PLTE/IDAT 분리 구조

```
PNG 파일 내부 청크 구조:
  ┌──────────┐
  │  IHDR    │  이미지 헤더 (width, height, bit_depth=8, color_type=3)
  ├──────────┤
  │  PLTE    │  팔레트 색상표 (32색 × 3byte = 96byte)  ← 색상 정의
  │          │   index 0 = #FFFFFF (Grade 0, Pass)
  │          │   index 1 = #9B9B9B (Grade 1)
  │          │   ...
  │          │   index 7 = #000000 (Grade 7, 최고불량)
  │          │   index 8~31 = 배경/테두리/BIN별 색상
  ├──────────┤
  │  IDAT    │  픽셀 데이터 (팔레트 인덱스 0~31만 저장)  ← 의미값
  │          │   픽셀값 = 색상이 아니라 "Grade 몇?" / "BIN 몇?" 의 인덱스
  ├──────────┤
  │  IEND    │
  └──────────┘
```

**핵심**: IDAT에는 어떤 색상인지가 아니라 **"이 픽셀의 의미(grade/bin)"** 만 저장된다.
색상은 PLTE에만 있으므로 **PLTE만 교체하면 IDAT 재압축 없이 색상 전환 완료**.

### 5-3. 왜 이 방식을 선택했는가 — 반도체 도메인 지식의 적용

이 설계는 단순 기술 선택이 아니라 **반도체 현장 운영 지식에서 도출**된 것이다.

**현장 상황**:
- 엔지니어마다 특정 불량 BIN에 "자신만의 색상"을 배정해 수십 년간 작업해왔다
- 같은 웨이퍼 맵이라도 A 엔지니어는 BIN 285를 빨간색으로, B 엔지니어는 파란색으로 보기를 원한다
- 불량 종류가 바뀌거나 새 BIN이 추가될 때마다 색상 체계가 바뀐다

**Palette PNG가 아니었다면**:
- 사용자 색상 변경 → 서버에서 수십만 장 이미지 재렌더링 → 수시간 대기
- 또는 클라이언트에서 픽셀별 색상값을 비교해 recolor → 정확도/속도 모두 낮음

**Palette PNG (PLTE 패치)를 사용하면**:
- PLTE 96byte만 교체 → IDAT 재압축 없음 → **거의 즉시 색상 전환**
- 동일 원본 이미지를 다양한 사용자 맞춤 색상으로 서빙 가능
- 스토리지 공간 절감까지 추가로 달성

**논문 서술 포인트**: 이것은 컴퓨터 비전 기법의 단순 적용이 아니라, *반도체 현장의 색상 커스터마이징 관행을 파악하고 그에 맞는 데이터 포맷을 설계한 도메인 지식 기반 엔지니어링*이다.

### 5-4. 32색 팔레트 인덱스 구성

```
인덱스  의미                   색상
0~7    Grade 0~7 (Pass→불량)  #FFFFFF, #9B9B9B, #009619, #0000FF,
                              #D91DFF, #FFFF00, #FF0000, #000000
8      배경 (bg)              #FEFEFE
9      텍스트                 #000001
10     일반 격자 테두리        #BEBEBE
11     무효칩 테두리           #FF9900 (주황)
12~17  00P BIN별 테두리        BIN 285~291 각각 고유색
18~23  00C BIN별 테두리        BIN 300, 385~390 각각 고유색
24     기타 불량(BIN≥200)     #999999
25~30  예약                   -
31     무효칩 채움             #FFFFFF
```

이 팔레트 구조 자체가 반도체 검사 BIN 체계(00P/00C, systematic 불량 BIN 목록)를 직접 인코딩한 것이다.

---

## 6. positions JSON의 의미

`positions_module.py` 기준 positions JSON은 다음 역할을 한다.

- 칩 위치와 rect 저장
- 회전 후에도 정합되는 좌표계 유지
- 칩별 `b`(bin), `f`(FTN), `q`(QTN) 저장
- wafer 메타 `yield`, `sys`, `gd`, `lt`, `tm` 저장
- Bucket B match 정보 저장

즉 positions JSON은 단순 보조 파일이 아니라,

`wafer image <-> chip geometry <-> measurement data <-> UI annotation`

를 연결하는 SSOT에 가깝다.

논문에는 `multimodal 확장을 위한 중간 표현(intermediate aligned representation)`이라고 적는 것이 적절하다.

---

## 7. 논문에 쓸 수 있는 핵심 메시지

`fail-map` 프로젝트만 놓고 봤을 때 논문에 바로 활용 가능한 메시지는 아래와 같다.

1. 본 연구는 모델 이전에 데이터 생성 및 정합 계층을 직접 설계하였다.
2. 두 개의 이질적 로그 소스를 시간/파일명 규칙으로 매칭하여 wafer image와 chip-level measurement를 통합하였다.
3. Cython과 병렬 수집 구조를 사용해 대량 로그 처리 속도를 실사용 수준으로 확보하였다.
4. palette-indexed PNG와 positions JSON을 통해 시각화, 모델 학습, 계측 정합이 동일 표현을 공유하도록 만들었다.
5. 결과적으로 본 파이프라인은 단순 이미지 생성기가 아니라, 이후 지도학습/비지도학습/UI 분석/멀티모달 확장을 가능하게 하는 기반 인프라이다.

---

## 8. 논문 반영 권장 문장

### 짧은 버전

> 본 연구에서는 먼저 dual-bucket 기반 raw 로그 수집 및 정합 파이프라인을 구축하였다. Bucket A의 fail map raw 데이터와 Bucket B의 계측 로그를 시간 및 파일명 규칙으로 자동 매칭하고, Cython 기반 초고속 파싱을 통해 palette-indexed PNG와 positions JSON을 동시에 생성하였다.

### 확장 버전

> 데이터 생성 단계에서는 S3 기반 두 로그 소스(Bucket A/B)를 시간 오프셋 및 wafer 식별 규칙으로 자동 매칭한 뒤, 병렬 다운로드와 Cython 기반 파싱을 수행하였다. 이후 grade와 BIN 의미를 보존하는 palette-indexed PNG와 칩 좌표, FTN/QTN, yield/sys/LT/TM 메타데이터를 포함한 positions JSON을 함께 생성함으로써, 시각화 UI와 분류/군집화 모델이 동일한 정합 표현을 공유하도록 하였다.

---

## 9. 다음 단계 권장

`fail-map` 분석을 바탕으로 다음 문서 작업은 아래 순서가 가장 효율적이다.

1. 이 문서 내용을 `paper_v3.md`의 데이터 생성/멀티모달 부분에 반영
2. `mapviewer` 분석으로 UI/annotation/overlay 부분 보강
3. `image_classification` 쪽에서 등록/미등록 분석 파이프라인 연결
4. 최종적으로 Figure 1을 `dual bucket + palette PNG + positions JSON` 중심으로 정식 도식화
