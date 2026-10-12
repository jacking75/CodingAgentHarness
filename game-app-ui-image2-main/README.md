# 게임 및 앱 UI Image2
`game-app-ui-image2`는 Codex 전용 스킬이다. ChatGPT Images 2의 내장 `image_gen` 도구를 사용해 게임·앱 UI 목업과 래스터 UI 자산을 만들고, 느슨한 제품 요구사항을 화면 중심 이미지 프롬프트로 변환한다. 이미지를 생성한 뒤 정보 위계와 사용성 문제를 검수하며, 한 번에 하나의 문제만 보정한다.

게임 HUD, 메뉴, 인벤토리, 온보딩, 모바일 작업 화면, 대시보드, 일러스트 패널, 텍스처, 메뉴 배경 제작에 사용한다.

## 기능

- 대상 플랫폼, 뷰포트, 플레이어·사용자 목표, 정보 위계, 시각 스타일, 상태, 안전 영역, 제약처럼 결과에 직접 영향을 주는 결정을 추출한다.
- 일반적인 아트 프롬프트 대신 간결한 `ui-mockup` 이미지 프롬프트를 만든다.
- 게임플레이 안전 영역, 터치 영역, 핵심 행동, 상태 표현을 명시해 중요한 정보가 가려지지 않게 한다.
- 생성 결과의 위계, 대비, 텍스트, 안전 영역, 시각 일관성, 금지 요소를 검수한다.
- 후속 편집에서 승인된 요소는 유지하고 식별된 문제만 변경한다.
- PC·콘솔 HUD, 모바일 작업 화면, 일러스트 메뉴 패널용 기본 레시피를 제공한다.

## 하지 않는 일

생성 화면은 기본적으로 디자인 레퍼런스다. 이 스킬은 비트맵 스크린샷을 프로덕션 UI 구현물로 바꾸지 않는다. 최종 인터랙티브 레이아웃, 접근성 동작, 현지화, 버튼, 재사용 아이콘은 프로젝트의 UI 프레임워크와 네이티브·벡터 자산으로 구현해야 한다.

이 스킬은 ChatGPT Images 2용 내장 `image_gen` 도구가 제공되는 Codex 환경을 요구한다. 도구가 없더라도 다른 제공자, API·CLI 스크립트, HTML/CSS, 텍스트 프롬프트만으로 대체하지 않는다.

## 구성

```text
game-app-ui-image2/
├── SKILL.md                        # 핵심 워크플로와 프롬프트 규칙
├── references/
│   └── prompt-recipes.md           # HUD, 모바일 화면, 메뉴 패널 레시피
├── agents/
│   └── openai.yaml                 # 선택적 Codex UI 메타데이터
├── README.md
└── LICENSE
```

## Codex CLI 설치

Codex는 저장소 스킬을 `.agents/skills/<skill-name>/SKILL.md`에서, 개인 스킬을 `~/.agents/skills/<skill-name>/SKILL.md`에서 탐색한다. 저장소 구성원과 공유할 때는 프로젝트 설치를, 모든 로컬 Codex 프로젝트에서 쓸 때는 개인 설치를 사용한다.

### Windows — 프로젝트 설치

스킬을 사용할 저장소에서 실행한다. 아래 첫 경로는 이 저장소가 `F:\github\game-app-ui-image2`에 있다고 가정한다.

```powershell
$sourcePath = 'F:\github\game-app-ui-image2'
$destinationPath = Join-Path (Get-Location) '.agents\skills\game-app-ui-image2'

New-Item -ItemType Directory -Force -Path $destinationPath | Out-Null
Copy-Item -LiteralPath "$sourcePath\SKILL.md" -Destination "$destinationPath\SKILL.md" -Force
Copy-Item -LiteralPath "$sourcePath\references" -Destination $destinationPath -Recurse -Force
Copy-Item -LiteralPath "$sourcePath\agents" -Destination $destinationPath -Recurse -Force
```

팀 전체가 워크플로를 공유해야 한다면 `.agents/skills/game-app-ui-image2/`를 커밋한다.

### Windows — 개인 설치

```powershell
$sourcePath = 'F:\github\game-app-ui-image2'
$destinationPath = Join-Path $env:USERPROFILE '.agents\skills\game-app-ui-image2'

New-Item -ItemType Directory -Force -Path $destinationPath | Out-Null
Copy-Item -LiteralPath "$sourcePath\SKILL.md" -Destination "$destinationPath\SKILL.md" -Force
Copy-Item -LiteralPath "$sourcePath\references" -Destination $destinationPath -Recurse -Force
Copy-Item -LiteralPath "$sourcePath\agents" -Destination $destinationPath -Recurse -Force
```

### macOS/Linux

`SKILL_SOURCE`를 복제한 저장소의 경로로 설정한다. 첫 번째 대상 경로는 프로젝트 설치, 두 번째는 개인 설치다.

```bash
SKILL_SOURCE="/path/to/game-app-ui-image2"
SKILL_DESTINATION=".agents/skills/game-app-ui-image2"

mkdir -p "$SKILL_DESTINATION"
cp "$SKILL_SOURCE/SKILL.md" "$SKILL_DESTINATION/"
cp -R "$SKILL_SOURCE/references" "$SKILL_DESTINATION/"
cp -R "$SKILL_SOURCE/agents" "$SKILL_DESTINATION/"
```

```bash
SKILL_SOURCE="/path/to/game-app-ui-image2"
SKILL_DESTINATION="$HOME/.agents/skills/game-app-ui-image2"

mkdir -p "$SKILL_DESTINATION"
cp "$SKILL_SOURCE/SKILL.md" "$SKILL_DESTINATION/"
cp -R "$SKILL_SOURCE/references" "$SKILL_DESTINATION/"
cp -R "$SKILL_SOURCE/agents" "$SKILL_DESTINATION/"
```

대상 프로젝트에서 Codex를 시작하거나 재개한 뒤 프롬프트에 `$game-app-ui-image2`를 입력한다. 요청이 스킬 설명과 명확히 일치하면 Codex가 자동 선택할 수도 있다. 새로 설치한 스킬이 보이지 않으면 Codex를 재시작한다.

## Codex CLI 사용

스킬을 명시적으로 호출한 뒤 제품 목표와 제약을 작성한다. 이 스킬은 내장 `image_gen` 도구를 통해 ChatGPT Images 2로 이미지를 실제 생성하며, 프롬프트만 반환하지 않는다. 중요하지 않은 세부 사항은 에이전트가 합리적으로 추론하게 둬도 된다.

```text
$game-app-ui-image2
```

### 게임 예시

```text
16:9 PC 액션 RPG 전투 HUD를 만들어라. 적이 보이도록 화면 중앙 60%는 비워둔다.
좌하단에 플레이어 체력·스태미나, 우하단에 스킬 8개, 상단에 보스 체력바를 배치한다.
화려한 다크 판타지 금속·가죽 시각 언어를 사용하고, 선택된 스킬 상태를 표시한다.
```

```text
세로형 모바일 로그라이크 인벤토리 화면을 설계한다. 주된 과제는 무기를 빠르게 장착하는 것이다.
비교 능력치, 희귀도, 명확한 장착 행동, 잠긴 슬롯 상태를 보여준다. 색감 있는 핸드페인팅 스타일을 사용한다.
```

```text
야간 맵용 21:9 익스트랙션 슈터 분대 HUD를 만든다. 주변 시야를 유지하고,
분대 상태는 왼쪽, 탄약·자세는 오른쪽, 중앙 내비게이션 마커는 눈에 거슬리지 않게 배치한다.
적 실루엣을 가리는 레이아웃은 피한다.
```

```text
아늑한 농장 게임의 16:9 일시 정지 메뉴를 만든다. 계속하기, 인벤토리, 지도, 설정, 나가기 항목을 포함한다.
손글씨 현장 일지 느낌을 내고, 선택 상태를 분명히 보여주며 네이티브 버튼 텍스트를 넣을 공간을 남긴다.
```

```text
PC SF 기지 건설 게임의 연구 기술 트리 화면을 만든다. 노드 가독성,
연결선, 잠김·사용 가능 상태, 방해하지 않는 상세 패널을 우선한다. 하드서피스 산업 소재를 사용한다.
```

```text
아이소메트릭 MMORPG의 퀘스트 추적기와 미니맵 처리를 설계한다. 완전한 다이에제틱 UI보다는 약한 다이에제틱 UI로 만들고,
한국어 텍스트를 지원하며 전투를 위해 뷰포트 중앙은 비워둔다.
```

```text
판타지 게임의 투명 배경 전설 아이템 카드 프레임을 만든다. 이미지 안에는 아이템 이름이나 능력치를 넣지 않고,
네이티브 UI가 표시하게 둔다. 금박 세공, 마모된 에나멜, 명확한 내부 콘텐츠 영역을 사용한다.
```

### 앱 예시

```text
세로형 모바일 피트니스 앱의 운동 시작 화면을 설계한다. 주된 행동은 운동 시작이다.
운동 시간, 목표 심박 구간, 최근 완료 연속 기록을 보여준다. 주 CTA는 엄지손가락이 닿기 쉽게 배치한다.
```

```text
게임 팀용 데스크톱 프로젝트 관리 대시보드를 만든다. 빌드 상태, 진행 중 장애,
현재 스프린트 마일스톤, 팀 블로커를 우선한다. 절제된 다크 테마와 명확한 심각도 색상을 사용한다.
```

```text
수취인, 금액, 수수료, 최종 확인 행동을 포함하는 뱅킹 앱 이체 확인 화면을 설계한다.
잔액 부족 오류 상태를 보여준다. 높은 대비를 사용하고 장식적 시각 잡음은 피한다.
```

```text
하나의 방을 제어하는 스마트 홈 모바일 화면을 만든다. 주된 과제는 조명과 온도 변경이다.
색상에만 의존하지 않고 온라인, 오프라인, 기기 변경 진행 상태를 보여준다.
```

```text
새 분석 워크스페이스용 엔터프라이즈 SaaS 빈 상태 화면을 만든다. 첫 유효 행동을 설명하고,
가져오기 CTA와 샘플 데이터 CTA를 제공한다. 판매 지향적이지 않고 차분한 시각으로 구성한다.
```

```text
태블릿용 식단 계획 앱의 주간 캘린더 화면을 설계한다. 드래그 대상이 시각적으로 명확해야 하며,
식단 필터를 보여주고 긴 현지화 메뉴 이름을 표시할 공간을 확보한다.
```

### 보정 예시

첫 시안을 생성한 뒤 승인된 결정이 유지되도록 한 번에 하나의 보정만 요청한다.

```text
레이아웃, 팔레트, 아이콘 스타일, 정보 위계는 그대로 유지한다. 퀘스트 추적기를 오른쪽 안전 영역에서 8% 안쪽으로 옮기고,
배경 대비를 높이며 장식용 나침반만 제거한다.
```

```text
승인된 모든 패널은 유지한다. 선택된 스킬 표현만 색각 이상 사용자도 읽을 수 있는 더 강한 고대비 상태로 바꾼다.
텍스트나 새 컨트롤은 추가하지 않는다.
```

```text
인벤토리 레이아웃과 스타일은 유지한다. 두 줄의 한국어 아이템 이름과 세 자리 능력치가 잘리지 않게,
아이템 카드 영역만 변경한다.
```

```text
모바일 화면의 시각 시스템은 유지한다. 비활성화된 주 CTA와 진행 피드백만 포함한 로딩 상태를 만들고,
기존 콘텐츠의 위치는 전부 그대로 둔다.
```

## 권장 검수 체크리스트

생성 화면이나 자산을 확정하기 전에 다음을 확인한다.

- 핵심 게임플레이 행동 또는 사용자 과제가 가장 우선적으로 보이는지 확인한다.
- 게임플레이 안전 영역, 기기 컷아웃, 터치 영역을 지키는지 확인한다.
- 정상, 선택, 비활성화, 오류 상태가 필요한 곳에서 시각적으로 구분되는지 확인한다.
- 텍스트가 정확하고 읽기 쉬우며 현지화에 안전하고 의미 전달을 텍스트 하나에만 의존하지 않는지 확인한다.
- 의도한 사용 환경에서 대비와 그룹화가 충분한지 확인한다.
- 다른 게임이나 제품의 브랜드 UI를 모방하지 않는지 확인한다.
- 비트맵 장식과 인터랙티브·반응형이어야 하는 코드·네이티브 컴포넌트가 분리되는지 확인한다.

## 설치된 사본 업데이트

이 저장소의 새 버전을 받은 뒤 설치 섹션의 해당 복사 명령을 다시 실행한다. `-Force`로 복사하거나 파일을 덮어쓰기 전에 로컬 수정 사항을 검토해 보존한다.

## 참고 자료

- [Codex 스킬 문서](https://learn.chatgpt.com/docs/build-skills)
- [GPT Image 2 문서](https://developers.openai.com/api/docs/models/gpt-image-2)

## 라이선스

이 프로젝트는 MIT 라이선스로 배포한다. 자세한 내용은 [LICENSE](LICENSE)를 참고한다.
