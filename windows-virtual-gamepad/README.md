# Windows 가상 게임패드

Windows x64에서 가상 Xbox 360 컨트롤러를 유지하며 버튼·스틱·JSON 입력 시퀀스를 보내는 Codex 스킬이다. 기본 버튼 이름은 Switch 기준이며 `--layout xbox`도 지원한다.

## 문서

- [SKILL.md](SKILL.md): 에이전트용 지침과 기본 사용법.
- [설치·운영·복구](references/operations.md): 환경 준비, 드라이버, 버튼 대응, 시퀀스, 제거.
- [검증 절차와 한계](references/validation.md): XInput 검사와 실제 게임 반응의 구분.
- [스킬 제작·검증 기록](docs/T09_VIRTUAL_GAMEPAD_SKILL.md): 원래 작업 공간에서 작성한 T09 문서 원문.
- [기존 프로젝트의 게임패드 문서](docs/GAMEPAD_CONTROL.md): 이전 도구와 Eden 연결에 관한 원문 기록.

`docs/`의 두 문서에 나오는 작업 공간 경로·증거 파일·이전 스크립트는 원래 프로젝트 기준이다. 이 폴더에서 실행할 때는 `SKILL.md`와 `references/`를 따른다. 이전 도구와 범용 스킬은 통신 프로토콜·상태 경로가 달라 혼용하지 않는다.

## 사용 준비

이 폴더에서 PowerShell로 실행한다. Python과 드라이버 관련 조건은 운영 문서를 따른다.

```powershell
.\scripts\setup.ps1 -Action doctor
.\scripts\setup.ps1 -Action environment
.\scripts\gamepad.cmd doctor
```

Codex에 등록하려면 준비된 Python으로 다음 명령을 실행한다. 등록 도구는 `CODEX_HOME/skills` 또는 사용자 홈의 `.codex/skills`를 사용한다.

```powershell
.\.venv\Scripts\python.exe .\scripts\install_skill.py
```

새 Codex 세션에서 `$windows-virtual-gamepad`로 사용한다. 폴더 복사와 Codex 등록은 드라이버 설치와 별개다.

## 입력과 종료

`start`와 `verify`는 실제 패드 신호를 보낸다. 게임에 연결하기 전에 검증한다.

```powershell
.\scripts\gamepad.cmd start
.\scripts\gamepad.cmd verify --out '<검증폴더>\xinput.json'
.\scripts\gamepad.cmd tap A --layout switch --ms 150
.\scripts\gamepad.cmd neutral
.\scripts\gamepad.cmd stop
```

게임의 입력 장치에서 가상 컨트롤러를 선택해야 한다. 실제 게임 반응은 별도로 확인한다.

## 복사 범위

2026-10-16 `G:\working_zelda\skills\windows-virtual-gamepad`의 리소스 11파일과 관련 문서 2파일을 원문 그대로 복사했다. README는 이 배치를 위해 추가했다. 가상환경·상태·인증 정보·로그·드라이버 실행 파일·게임 자산·세이브·비공개 검증 증거는 포함하지 않았다. 다른 PC에서 환경을 새로 준비한다.
