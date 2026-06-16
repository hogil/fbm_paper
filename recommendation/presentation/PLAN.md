# 발표 자료 제작 계획 (PLAN)

> 사내 경연/AI Specialist 인증 발표 · 발표자 최호길(QIE Data Science)
> **원칙**: ① 모든 슬라이드에 시각자료(그림/다이어그램) — 글만 있는 슬라이드 금지 ② 공백 없이 꽉 채움 ③ 일·결과 중심(자기과시 X) ④ 정확성: 운영/검증/개발 분리 ⑤ 논문(rev087) 반영 ⑥ 화이트 배경·네이비/틸 액센트

## 핵심 메시지
반도체 현장의 **데이터·라벨 부족 + 수작업 판정 부담**을, **도메인 지식을 AI 설계에 녹여** 해결한 3개 과제.
P1의 학술 기여 = Failbit Map을 자연영상이 아니라 **좌표 보존 표현(coordinate-preserving representation)**으로 재정의.

## 사용 자산(figures)
- 논문 figure(권장, fbm_paper_full/figures/full_paper_rev087/ → recommendation/figures로 복사):
  `data_hex_to_grade_formula.png`(1000×610), `data_palette_png_formula.png`(1000×550),
  `roi_yolo_cascade_panel.png`(1948×653, (a)(b)(c)), `object_id_evolution_panel.png`(1530×383, (a)(b)(c)(d))
- 웨이퍼맵: `wafer_center_scratch.png` 등 7종(6400²)
- chip: `chip_eval_*`(단일 6), `chip_combo_*`(2조합 6), `chip_ood_*`(4)
- FCM-PM: `fcm_pm_panel.png`(1240×230 와이드 패널) 또는 step 6장
- trend: `trend_*` 6종(1050×675), `p3_trend_generation_formula.png`(설계 수식)

## 슬라이드 구성 (총 24장) — 각 슬라이드 [타입] + 시각자료

| # | 슬라이드 | 타입 | 시각자료 |
|---|---------|------|---------|
| 1 | **표지**: 제목 + 발표자(표지에만) | title | 대표 웨이퍼맵 |
| 2 | **배경·핵심 메시지**: 데이터·라벨 부족·수작업 부담 → 도메인 지식×AI로 해결 | bullets+image | 문제→해결 도식 |
| 3 | **P1·P2·P3 한눈에**: 과제별 문제→접근→결과 1줄 | table | 3과제 대표 썸네일 |
| | **─ P1: Failbit Map Known & Unknown (논문) ─** | | |
| 4 | P1 섹션 구분 | section | 웨이퍼 이미지 |
| 5 | **Failbit Map이란?**(비전문가용): EDS 8단계 grade 공간데이터, chip 격자 | bullets+image | wafer_center_scratch |
| 6 | **P1 문제·난제**: 조회 48매 한계·수작업·라벨 1,500장 부족·Unknown 신규불량 | bullets+image | before 도식 |
| 7 | **데이터 파이프라인**: raw log→Cython 변환(100x)→무손실 32색 PNG(75%↓)→좌표 JSON | bullets + 논문수식 2장 | hex→grade, palette PNG 수식 |
| 8 | **좌표 보존 표현(논문 핵심)**: wafer img+chip 좌표+수치+모델+검토 = 같은 좌표계 | flow | 좌표계 정렬 다이어그램 |
| 9 | **P1 알고리즘 구조**: 변환→뷰어→[Known: CNN→ROI-YOLO→chip-CNN obj-id]/[Unknown: 자기지도→HDBSCAN] | flow | 아키텍처 흐름도 |
| 10 | **Known 2-stage 상세**: 백본스캔 0.78→ConvNeXtV2 0.87→튜닝 0.92→ROI-YOLO 0.95(어려운것만 2단계) | image+표 | roi_yolo_cascade_panel (a)(b)(c) |
| 11 | **chip-CNN 불량 식별 지도(후속 개발)**: ROI-YOLO→32×32 categorical map. ablation 0.436→0.988 | image+표 | object_id_evolution_panel (a)(b)(c)(d) |
| 12 | **Unknown 발견**: 라벨없이 자기지도+HDBSCAN→2,000장→13후보→7확인(현업) | flow+image | clustering 도식 + wafer 예시 |
| 13 | **P1 결과·임팩트**: 운영=파이프라인·뷰어(일2만·매일·90%↓ 26억·수율 97억) / 모델=검증 F1 0.95·13→7(배포대기 GPU 2026.9) / 삼성논문상 | two_col | 운영 뷰어 느낌 + 수치 |
| | **─ P2: Chip 멀티라벨 (FCM-PM) ─** | | |
| 14 | P2 섹션 구분 | section | chip 결함 이미지 |
| 15 | **P2 문제**: 한 칩에 결함 여러 개(멀티라벨)·중복라벨 확보난·EDS 수치판정 한계 | bullets+image_grid | chip_eval/combo 예시 |
| 16 | **FCM-PM 상세**: single학습+FCM 합성(full-cover, partition=3)+Pair Mask→val_margin→NB reject | flow + image_grid | fcm_pm_panel 또는 6장 |
| 17 | **P2 결과**: ladder 0.109→0.9927 / FAR 0.00% | table | 성능표 + chip 썸네일 |
| | **─ P3: Trend 이상감지 (생성) ─** | | |
| 18 | P3 섹션 구분 | section | trend chart |
| 19 | **P3 문제**: 실전 이상 라벨 부족→검증 막힘·수작업 판독 | bullets+image | trend 예시 |
| 20 | **P3 생성기 설계**: 현업10년 지식→생성기(Region5/Noise3/Anomaly5)→정상산포 보정→Binary gate | image_grid + bullets | p3_trend_generation_formula |
| 21 | **P3 생성 예시 + 결과**: trend 6종 + Binary F1 0.9967(PoC) | image_grid | trend_* 6장 |
| | **─ 마무리 ─** | | |
| 22 | **공통 접근법 정리**: 도메인 지식×AI 설계로 데이터·라벨 제약 해결(3과제 공통) | flow/bullets | 통합 도식 |
| 23 | **로드맵·향후**: 완료시기 + 향후(모델배포 2026.9·chip-CNN 대체·trend 적용·multimodal) | timeline | 타임라인 |
| 24 | **수상·연구 + 마무리**: 2025 DS BP Good Challenger·MTC 1등급·2026 삼성논문상 / 비전 | closing+bullets | 간결 |

## 정확성 가드(절대 준수)
- 양산 운영 = **데이터 파이프라인 + 운영 뷰어**(일 2만·2025.5~·매일·90%↓ 26억·수율 97억)
- **모델(Known/Unknown)은 미배포** — GPU 할당 대기(2026.9). F1 0.95·13→7 = **검증/현업검토** 결과
- chip-CNN obj-id·생성 benchmark = **개발 단계**(현업 적용 전). field/benchmark/future 분리
- 1,500장 = Known 학습 라벨(16class, 4:1 split)

## 엔진/실행
- 엔진 유지: `build.py`(화이트·flow·timeline·밀도 개선 반영), `render_pptx.py`(COM 렌더+컨택트시트)
- 기존 생성물(_sample, _test, spec.json) 정리 후, 위 계획으로 **spec.json 새로 작성 → 빌드 → 평가/수정 반복**
- 평가: 내용(정확성·논문반영·기법설명 충실·공백) ∥ 디자인(시각자료 유무·공백·대비·정렬) 가차없이, 최대 8라운드
