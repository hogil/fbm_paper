# HANDOFF — 임원 발표자료 제작 (세션 이관용)

> 이 문서를 새 Claude Code 세션(루트=`D:\project\fbm_paper`)에서 먼저 읽으면 끊김 없이 이어집니다.
> 작업 폴더: `D:\project\fbm_paper\recommendation\presentation`

## 0. 목적
- 발표자: **최호길** (메모리제조기술센터 QIE그룹 Data Science 파트). 10년 현업 + 서울대 Data Scientist 인증 + 연세대 AI 석사.
- 용도: 사내 **AI Specialist 인증 경연 임원 발표(~15분)**. 자기과시 아니라 '일·결과 중심'의 정상 기술 발표.
- 핵심 메시지: **반도체 도메인 지식을 AI 설계에 녹여, 데이터·라벨 부족이라는 현장 제약을 해결한 3개 과제(P1/P2/P3).**

## 1. 산출물 / 파일 구조 (presentation 폴더)
- `발표_AI인증_최호길.pptx` — **최종 편집가능 덱(현재 17장)**
- `발표_AI인증_최호길_best_97x93.pptx` / `spec_best_97x93.json` — 백업(내용97/디자인93 시점)
- `spec.json` — **덱 콘텐츠(데이터 주도). 이걸 고치면 덱이 바뀜**
- `build.py` — **python-pptx 엔진**(슬라이드 타입: title/section/bullets/two_col/image_grid/table/closing/flow/timeline/**cards**/**pipeline**). 화이트 배경·네이비#0F1E3D/틸#12B5B0. 약 1,750줄.
- `render_pptx.py` — PowerPoint COM→PDF→PNG 렌더 + `_contact.png` 컨택트시트(평가용)
- `PLAN.md` — 초기 24장 계획서(참고용, 현재는 17장으로 축소됨)
- `sample_spec.json` — spec 포맷/타입 예시
- 빌드: `python build.py spec.json 발표_AI인증_최호길.pptx`
- 렌더: `python render_pptx.py 발표_AI인증_최호길.pptx _render 1600 900`
- 이미지 원본: `D:\project\fbm_paper\recommendation\figures` (웨이퍼/칩/trend/논문 수식·패널)

## 2. 현재 17장 구성
1 표지 / 2 **P1·P2·P3 한눈에(cards: 썸네일+문제·접근·결과)** / 3 P1 섹션 / 4 Failbit Map이란?+문제 / 5 **데이터 파이프라인(pipeline: WHY+기술스택+적용전→후)** / 6 Known 2단계(0.78→0.95) / 7 칩 식별 지도(ablation) / 8 Unknown 발견(13→7) / 9 운영vs모델 / 10 P2 섹션 / 11 P2 문제+FCM-PM / 12 P2 성능표 / 13 P3 섹션 / 14 P3 문제+생성기 설계 / 15 P3 생성예시+결과 / 16 로드맵(timeline) / 17 마무리(closing)
*(슬라이드 번호는 spec 순서 기준이며 약간 다를 수 있음 — spec.json으로 확인)*

## 3. ★ 정확성 가드 (절대 — 원천: recommendation/portfolio.md, D:\project\fbm_paper_full\full_paper_rev087_codex.md)
- **양산 운영 중 = 데이터 변환 파이프라인 + 운영 뷰어**(2025.5~, 일 2만 wafer, 매일, 공수 90%↓·연 26억, 수율 +0.02%·97억)뿐.
- **Known/Unknown 이미지 분류 모델은 미배포**(GPU 할당 대기 2026.9). **F1 0.95 = '검증 성능'**(16class/1,500 labeled/4:1), '운영 정확도' 아님. 1,500 = Known 학습 라벨.
- **P2(bit_F1 0.9927/FAR 0%)·P3(Binary F1 0.9967) = 생성셋·PoC·미배포.** 운영/검증/PoC 구분 유지.
- **기술스택(실제 코드 기준)**: 생성(fail-map) = **Cython**(hex→Grade) + 32색 palette PNG(Pillow,75%↓) + ProcessPool. 운영뷰어(mapviewer) = **Numba**(@njit composite map) + **pyvips**(대량 이미지 로드·resize) + pyramid·cache. (포트폴리오의 "생성에 Numba/pyvips"는 틀림 — 코드와 다름)
- **수상 3건**: 2025 DS AI Best Practice Good Challenger / MTC 제안 1등급 / 2026 삼성논문상 초록 통과.
- 논문 핵심 thesis: Failbit Map을 자연영상이 아니라 **좌표 보존 표현(coordinate-preserving)** 으로 재정의.

## 4. ★ 디자인/콘텐츠 가드레일 (사용자 확정 — 위반 금지)
1. **17장 유지** — 추가·삭제 금지(품질만 개선).
2. **이미지는 figures 원본만** — 가공·생성·합성·crop·대비보정·_view/_focus/_hc/_v2 금지.
3. **웨이퍼 등 실데이터에 추측성 주석(원/화살표/색채움) 금지** — 실제 결함 좌표를 모르면 틀린 위치를 강조함(과거 edge-ring을 가운데 노란 원으로 잘못 표시 → 전부 제거함).
4. **방어적 각주·면책 문구 금지**('척도 달라 동급 비교 아님', 'F1=…정도' 정의 등). PoC/생성셋 표기는 결과 괄호로 충분.
5. **'한눈에 카드'·'데이터 파이프라인' 슬라이드는 확정본** — 구조·정확한 기술표기 보존.
6. 자기과시 슬로건 금지, 일·결과 중심. 발표자 소개·성과 stats 페이지 금지.
7. 화이트 배경·여백 최소·네이비/틸 일관, 모든 슬라이드 시각요소(글만 슬라이드 금지).

## 5. 진행 방식 (평가·수정 루프)
- 품질 향상은 **리파인 전용 워크플로우**(research/writer 없이 현재 spec만 평가→마스터수정 반복)로 함. 마스터는 spec.json·build.py를 직접 수정 가능(단 위 가드레일 준수).
- 채점은 **공정하게**(개선되면 점수↑). 직전 측정: 내용 97 / 디자인 93(둘 다 accept). 디자인은 ~90대에서 plateau.
- 남은 디자인 nit(과거 평가): slide 밀도(Unknown), 6패널 trend 상단 여백, closing 텍스트량 등.

## 6. 다음에 할 일 / 사용자 스타일
- 사용자는 **특정 슬라이드를 콕 짚어 "이거 새로 해라"** 식으로 지시함 → 그때그때 직접(또는 마스터 에이전트로) 반영.
- 무한 리파인 루프를 원하면 위 5번 방식으로 재가동(현재 spec만 대상).
- **이전 세션(루트=D:\project\exam)에서 돌던 리파인 루프(task 예: w0m5h69jl)는 이 세션 종료 시 끊김** — 필요하면 새로 리파인 루프를 띄울 것(현재 spec.json 기준).
