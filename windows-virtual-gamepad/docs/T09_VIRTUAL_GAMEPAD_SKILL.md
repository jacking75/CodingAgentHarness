# T09: 범용 Windows 가상 게임패드 스킬

2026-10-16 완료. `skill-creator` 지침에 따라 기존 `GAMEPAD_CONTROL.md`, `scripts/gamepad_control.py`, `scripts/gamepad.cmd`의 검증된 방식을 분리했다. 게임·에뮬레이터 설정과 세이브 처리는 스킬에 포함하지 않았다.

## 산출물과 실제 등록

| 항목 | 위치 |
|---|---|
| 관리 원본 | `skills/windows-virtual-gamepad/SKILL.md` |
| 실제 등록 | `C:\Users\jacki\.codex\skills\windows-virtual-gamepad\SKILL.md` |
| 설치된 전용 환경 | 위 등록 폴더의 `.venv` / CPython3.12.9 x64 |
| 이전용 ZIP | `artifacts/windows-virtual-gamepad.zip` |
| 상세 설치·사용·제거 | `skills/windows-virtual-gamepad/references/operations.md` |
| 검증 절차·한계 | `skills/windows-virtual-gamepad/references/validation.md` |

새 Codex 세션에서 **`$windows-virtual-gamepad`**로 사용한다. 현재 세션의 스킬 목록이 자동 갱신되지 않으면 새 세션을 연다. 자동 선택도 기본 허용한다. 실제 등록 위치에 소스와 같은11개 리소스 파일을 SHA-256 대조해 복사했다. 등록 도구는 `CODEX_HOME/skills` 또는 사용자 홈의 `.codex/skills`를 계산하므로 다른 머신에서 위 사용자 경로를 사용하지 않는다.

작업실에서 다시 등록하거나 이전용 ZIP을 만드는 명령은 다음과 같다. ZIP은 기존 파일이 있으면 덮어쓰지 않는다.

```powershell
.\.venv-tkvsc\Scripts\python.exe skills/windows-virtual-gamepad/scripts/install_skill.py
# 원본을 수정한 뒤 검토된 등록본을 갱신할 때:
.\.venv-tkvsc\Scripts\python.exe skills/windows-virtual-gamepad/scripts/install_skill.py --update
# 최초 패키징:
.\.venv-tkvsc\Scripts\python.exe skills/windows-virtual-gamepad/scripts/install_skill.py --zip artifacts/windows-virtual-gamepad.zip
```

환경·상태·로그·인증 파일·bytecode·드라이버 실행 파일은 등록/ZIP allowlist에서 제외한다. 기존 프로젝트용 패드 스크립트는 비행 시험 재현을 위해 유지했다. 범용 버전과 통신 프로토콜·상태 경로가 다르므로 두 도구를 같은 서버처럼 섞어 호출하지 않는다.

## 다른 PC에 준비하는 절차

ZIP을 풀거나 스킬 폴더를 옮겨 대상 PC의 Codex skills 폴더에 등록한다. 이전 PC의 `.venv`와 `connection.json`을 복사하지 않는다. 스킬 폴더에서 다음 명령을 실행한다.

```powershell
.\scripts\setup.ps1 -Action doctor
.\scripts\setup.ps1 -Action environment
.\scripts\gamepad.cmd doctor
.\scripts\gamepad.cmd start
.\scripts\gamepad.cmd verify --out '<검증폴더>\xinput.json'
.\scripts\gamepad.cmd stop
```

`environment`는 명시 Python→py3.12→python→uv의 순서로 탐지하고 전용 venv를 만든다. CPython3.10~3.13 x64 범위를 검사하며 실제 검증 버전은3.12.9다. `-Python`, `-VenvPath`, `VGAMEPAD_PYTHON`으로 재정의할 수 있다. Python 설치가 없으면 위치를 추측하지 않고 설치 또는 명시 경로를 요청한다. 런처·설치기는 `-E`로 다른 Python의 PYTHONHOME/PYTHONPATH 상속을 차단한다.

드라이버가 없을 때만 공식 패키지를 확보하고 관리자 PowerShell에서 설치한다. 스크립트는 자동 승격·재부팅을 하지 않는다.

```powershell
.\scripts\setup.ps1 -Action fetch-driver -InstallerPath '<다운로드폴더>\ViGEmBus_1.22.0.exe'
# 관리자 PowerShell에서:
.\scripts\setup.ps1 -Action install-driver -InstallerPath '<다운로드폴더>\ViGEmBus_1.22.0.exe'
```

[ViGEmBus 공식1.22.0 릴리스](https://github.com/nefarius/ViGEmBus/releases/tag/v1.22.0)의 고정 SHA-256과 Authenticode Valid/Nefarius 서명을 검사한다. Python 의존성 설치 중 동봉된 구버전 드라이버 설치는 막는다. 패키지는1.22.0, 이 PC 내부 드라이버는1.21.442.0이다. [공식 EOL 안내](https://docs.nefarius.at/projects/ViGEm/End-of-Life/)에 따라 새 OS에서는 실제 생성·재검사가 필요하다. 스킬은 Windows x64 전용이며 Linux/macOS·ARM64 네이티브 Python은 구현하지 않았다.

## 사용과 복구

기본 표기는 Switch다. Switch A/B/X/Y는 Xbox B/A/Y/X, ZL/ZR은 LT/RT, L/R은 LB/RB다. Xbox 게임에서는 `--layout xbox`를 지정한다. JSON timeline에서는 각 step의 `layout`을 지정하며 CLI 옵션이 JSON 전체를 바꾸지 않는다. 두 스틱과 동시 버튼을 지원한다. 축은−1~1, x+오른쪽·y+위/앞이다.

```powershell
.\scripts\gamepad.cmd start
.\scripts\gamepad.cmd status
.\scripts\gamepad.cmd tap A --layout switch --ms 150
.\scripts\gamepad.cmd stick --left 0 1 --ms 300
.\scripts\gamepad.cmd validate --file '<입력.json>'
.\scripts\gamepad.cmd run --file '<입력.json>' --out '<실행결과.json>'
.\scripts\gamepad.cmd neutral
.\scripts\gamepad.cmd stop
```

입력마다 장치를 재생성하지 않는다. 시작 시 Windows 장치 열거 완료를 기다리고 고유 스틱 패턴을 XInput0~3에서 읽어 실제 슬롯을 찾은 뒤 즉시 중립으로 돌린다. GUID/슬롯을 고정하지 않는다. `doctor`와 `sdl`은 SDL 이름·GUID·index·instance ID를 열거한다. SDL·XInput·게임 내부 플레이어 번호는 별개이므로 대상 프로그램에서 장치를 선택하고 실제 반응을 확인한다.

타임라인은 step당1~5000ms, 요청당30초 이하다. 누락한 입력은 매 step 중립이며 종료·오류 시 중립으로 복원한다. 서버가 순차 실행하므로 긴 요청 도중의 neutral/stop은 대기한다. 클라이언트 Ctrl+C도 이미 접수된 입력의 즉시 취소가 아니다. 즉시 제어가 필요하면 짧은 요청을 사용한다.

상태 기본 위치는 `%LOCALAPPDATA%/CodexVirtualGamepad`이며 `--state-dir` 또는 `VGAMEPAD_STATE_DIR`로 바꾼다. 인증값이 있는 connection.json은 현재 사용자·SYSTEM만 읽도록 ACL을 제한하며 보고서·ZIP에는 넣지 않는다. 상태·로그를 확인할 때 인증 파일 내용은 출력하지 않는다. stop/neutral은 이미 종료된 상태에서도 성공한다.

제거는 먼저 같은 상태 경로로 stop하고 status=false를 확인한 뒤 등록된 스킬 폴더와 불필요한 전용 환경·상태 폴더만 정확한 절대경로를 확인해 지운다. 공유 드라이버는 스킬 제거와 별개다. 드라이버 제거를 요청한 경우에만 Windows 설치된 앱의 Nefarius Virtual Gamepad Emulation Bus Driver 또는 관리자 `setup.ps1 -Action uninstall-driver -InstallerPath <검증된EXE>`를 사용한다. 물리 패드 드라이버를 제거하지 않는다.

## 검증 결과와 근거

독립된 새 Python 환경을 `private/t09 clean environment/.venv`에 만들어 의존성 설치부터 시험했다. 상태 경로에는 공백·한글을 사용했고 현재 작업 디렉터리는 프로젝트 밖의 Windows 임시 폴더였다. 이후 사용자 등록 위치에도 새 `.venv`를 만들고 기본 런처로 설치본을 재검증했다. 일반 사용자 권한에서 동작했다.

| 시험 | 결과 |
|---|---|
| Switch/Xbox 디지털14버튼·트리거2개씩 | 두 표기 모두 XInput 전체 상태 일치 |
| 양쪽 스틱의 각 축±0.75 | 8개 상태 일치 |
| 버튼·트리거·양쪽 스틱 동시 입력 | 일치, 합계41개 검사 통과 |
| 시작 반복·타임라인·중립·종료 | 같은 서버 유지, 종료 뒤 장치수0·상태파일 제거 |
| 잘못된 입력6종·서버 직접 오류 | 실행 거절, 서버 생존·중립 유지 |
| 실제 버튼 유지 후 실행 예외 주입 | finally에서 중립 복원 |
| 등록본 기본 .cmd 런처 | start/tap/stick/run/neutral/stop/validate 및 실패 종료 코드 통과 |
| 공식 드라이버 다운로드 | 지정 SHA-256 일치·서명 Valid |
| 잘못된 드라이버 해시·비관리자 설치 시도 | 실행 전에 거절, 드라이버 변경 없음 |
| 스킬 구조·등록·패키징 | skill-creator 검사,11파일 해시 대조·allowlist 통과 |

근거는 `private/analysis/t09-live-verification.json`, `t09-installed-live-verification.json`, `t09-doctor.json`, `t09-installed-doctor.json`, `t09-delivery-verification.json`, `t08-t09-artifact-verification.json`이다. 전체 실행 검사는 `scripts/verify_t09_delivery.py`로 재현한다. 공유 드라이버를 바꾸지 않으며 게임을 종료한 상태에서 실행한다.

초기 검사에서 두 번째 가상 패드의 Windows 열거가 끝나기 전에 보낸 입력이 읽히지 않았다. 기존 방식의 열거 대기를 복원해 해결했고 슬롯은 여전히 XInput 패턴으로 확인한다. 등록본 검사에서는 uv Python3.13의 PYTHONHOME이3.12 하위 프로세스에 상속돼 SRE mismatch가 났다. `-E`로 해결했다. .cmd의 블록 내부 exit가 오류 코드를0으로 가리는 문제는 레이블 분기로 수정하고 잘못된 타임라인의 종료 코드1을 확인했다.

진단 시 Windows 실제 빌드는 `10.0.26300.0`으로 확인돼 기존2026-09-29 기록의26200과 다르다. CPU/GPU/RAM은 이번에 다시 확인하지 않았다. PnP code0·서명된 드라이버 Running·재부팅 징후 없음과 실제 XInput 검사를 확인했다.

**다른 PC, 드라이버가 전혀 없는 OS, 실제 설치·재부팅·제거 경로는 실행 검증하지 않았다.** 같은 호스트의 새 Python 환경 검증이며 완전한 클린 OS 검증은 아니다. 새 범용 도구의 게임 반응도 이번에 재검증하지 않았다. 기존 프로젝트 패드의 게임 성공 기록과 Windows 입력 성공을 구분한다.
