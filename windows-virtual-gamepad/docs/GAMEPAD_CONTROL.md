# Windows 게임패드 자동 조작

2026-10-15 이 PC에서 검증했다. Eden 전용 코드가 아닌 Windows 가상 Xbox 360 컨트롤러다.

## 검증 결과

- ViGEmBus 설치 및 가상 컨트롤러 생성 성공.
- Windows `XInputGetState`로 버튼 16개, 양쪽 스틱 8개 값, 마지막 중립 상태를 다시 읽어 검증했다.
- 증거: `artifacts/gamepad-xinput-verification.json`.
- Windows 입력 검증과 게임 반응 검증은 구분한다. 현재 증거 파일은 게임 반응을 검증한 결과가 아니다.
- 물리 패드는 그대로 유지한다. 가상 패드는 별도 장치이므로 사용할 게임/에뮬레이터에서 해당 장치를 선택해야 한다.

## 설치와 버전

- Python 환경: `.venv-gamepad`, Python 3.12.9.
- vgamepad: 0.1.3, 커밋 `3f910aa8bbde49a576683db74ad5e4a0879f8a80`.
- [vgamepad 공식 소스/API](https://github.com/yannbouteiller/vgamepad).
- [ViGEmBus 공식 설치 패키지 1.22.0](https://github.com/nefarius/ViGEmBus/releases/tag/v1.22.0).
- 설치 파일: `tools/gamepad/ViGEmBus_1.22.0_x64_x86_arm64.exe`.
- SHA-256: `89220A7865076B342892F98865F3499FB7C4CFD673159E89D352C360FD014C6A`.
- Authenticode 상태 `Valid`, 서명자 `Nefarius Software Solutions e.U.`를 확인했다.
- 설치 프로그램의 버전과 내부 드라이버 버전은 다를 수 있다. 1.22.0 패키지는 업데이트 프로그램을 제거한 마지막 패키지다.
- [공식 지원 종료 안내](https://docs.nefarius.at/projects/ViGEm/End-of-Life/): 유지보수는 종료되었다. 새로운 Windows 버전에서는 아래 입력 검증을 다시 수행한다.

다른 작업 폴더/PC에서 준비할 때:

```powershell
uv venv --python 3.12 .venv-gamepad
$env:VGAMEPAD_SKIP_VIGEMBUS_INSTALL = 'true'
uv pip install --python .venv-gamepad/Scripts/python.exe -r requirements-gamepad.txt
```

드라이버가 없으면 위 공식 1.22.0 패키지를 설치한다. Windows UAC 승인이 필요하다. Python 패키지에 동봉된 과거 드라이버를 자동 설치하지 않도록 위 환경 변수를 반드시 설정한다.

## 사용

프로젝트 루트에서 실행한다. 별도 드라이버 설치 이후 일반 사용자 권한으로 동작한다.

```powershell
scripts/gamepad.cmd doctor
scripts/gamepad.cmd start
scripts/gamepad.cmd status
scripts/gamepad.cmd verify --out artifacts/gamepad-xinput-verification.json
scripts/gamepad.cmd tap A --ms 120
scripts/gamepad.cmd tap X --ms 120
scripts/gamepad.cmd stick --left 0 1 --ms 1000
scripts/gamepad.cmd stick --right 1 0 --ms 300
scripts/gamepad.cmd tap L --ms 500
scripts/gamepad.cmd neutral
scripts/gamepad.cmd stop
```

`start`는 지속 프로세스에서 가상 패드 1개를 연결한다. 호출마다 장치를 다시 만들지 않는다. `stop`은 입력을 풀고 가상 패드를 연결 해제한다. 물리 패드를 삭제하거나 숨기지 않는다. 프로그램은 자동 시작 서비스로 등록하지 않는다.

스틱 x는 오른쪽이 +1, y는 위/앞이 +1이다. 한 입력은 최대 5초, 시퀀스 합계는 최대 30초다. 입력 수행 후와 오류 발생 시 중립으로 돌아간다. `verify`는 실제 버튼을 누르는 검사이므로 게임에 연결하기 전에 수행한다.

기본 버튼 표기는 **닌텐도 스위치 기준**이다. 가상 장치의 Xbox 버튼과 위치를 맞추는 변환은 도구가 수행한다.

| 명령의 스위치 버튼 | 가상 Xbox 버튼 |
|---|---|
| A | B (오른쪽) |
| B | A (아래) |
| X | Y (위) |
| Y | X (왼쪽) |
| L / R | LB / RB |
| ZL / ZR | LT / RT |
| PLUS / MINUS | Start / Back |

일반 Xbox 표기를 쓰는 게임은 `--layout xbox`를 지정한다. 장치의 VID/PID, Windows 슬롯, 버튼 위치와 게임에서 표시하는 버튼 이름을 구분한다. 게임 자체의 재매핑이 있으면 게임에서 별도로 확인한다.

정확한 순서/동시 입력은 JSON 시퀀스로 보낸다. 예를 들어 앞으로 이동하며 점프하고, 공중에서 X를 다시 누르는 입력이다. 지형에 맞는 타이밍은 게임에서 검증해야 한다.

```json
[
  {"left":[0,1],"ms":300},
  {"buttons":["X"],"left":[0,1],"ms":120},
  {"left":[0,1],"ms":600},
  {"buttons":["X"],"ms":120},
  {"ms":300}
]
```

위 내용을 파일로 저장한 뒤 `scripts/gamepad.cmd run --file 경로.json`으로 실행한다. Python에서 재사용할 때는 `scripts/gamepad_control.py`의 `request()`에 `{"action":"sequence","steps":[...]}`를 전달한다. 통신은 인증된 로컬 Windows named pipe를 사용한다.

## 게임에 연결하고 확인하는 순서

1. `start`로 가상 패드를 유지한다.
2. 게임/에뮬레이터의 입력 장치에서 새 Xbox 360 컨트롤러를 선택한다. 실제 패드와 다른 장치다.
3. A 한 번으로 메뉴 선택이 되는지 확인한다.
4. 스틱 짧은 이동과 X 한 번의 실제 동작을 확인한다.
5. 검증된 체크포인트를 저장하고 정해진 시퀀스를 실행한다.
6. 필요 없는 동안 게임을 종료하고 `stop`으로 가상 패드를 해제한다.

게임별 설정은 게임별 문서에 남긴다. 공통 도구에서 창 이름, Eden 프로세스, 게임 파일이나 세이브 경로를 사용하지 않는다.

## 발견한 문제와 복구

- `SendInput`은 키보드/마우스 입력용이며, XInput 패드 신호 생성과 구분한다. 물리 패드가 정상 인식된다는 사실만으로 자동 입력이 구현된 것은 아니다.
- 창 키 메시지를 보냈다는 사실을 게임 버튼 반응의 증거로 사용하지 않는다.
- ViGEm의 사용자 번호와 실제 Windows 슬롯이 다를 수 있고, 연결 시 물리 패드 슬롯도 바뀔 수 있다. 시작할 때 짧은 스틱 값으로 가상 장치를 식별하고 즉시 중립으로 복원한다. 새로 채워진 슬롯 번호만으로 장치를 판정하지 않는다. 수정 후 XInput 24개 검사와 중립 복원을 다시 검증했다.
- Windows venv 실행기의 PID와 실제 서버 Python PID가 달랐다. 실행기 PID 일치 대신 인증된 pipe 응답으로 준비 완료를 판정한다.
- 입력을 해제하려면 `neutral`, 가상 장치를 없애려면 `stop`을 실행한다. 다른 프로그램이 가상 패드를 사용 중이면 종료 전에 그 프로그램을 먼저 확인한다.
- 드라이버 제거는 Windows 설치된 앱의 Nefarius Virtual Gamepad Emulation Bus Driver에서 수행한다. 물리 게임패드 드라이버 제거와 구분한다.
- 서버 상태와 로그는 `private/gamepad`에 저장한다. 인증 키가 포함된 `connection.json`은 공유하지 않는다.

## 이 PC의 Eden 연결 및 복구

- 물리 패드 SDL GUID는 `030000005e040000e002000000007801`, 가상 패드는 `030000005e0400008e02000014017801`이다. SDL 장치 GUID의 이름 CRC 2바이트를 Eden과 같이 0으로 정규화한다.
- 원래 물리 패드 설정은 `private/baselines/physical-gamepad-before-virtual.ini`에 보관한다.
- 복사본 Eden을 종료한 뒤 `.venv-gamepad/Scripts/python.exe scripts/lab_gamepad_profile.py physical`로 물리 패드를 복구한다.
- 자동 시험은 `scripts/gamepad.cmd start`로 패드를 만든 뒤 `.venv-gamepad/Scripts/python.exe scripts/lab_gamepad_profile.py virtual`을 실행하고 복사본 Eden을 시작한다. SDL 열거 도구 의존성은 `requirements-gamepad-eden.txt`에 고정했다.
- SDL A/B/X/Y 입력 번호 1/0/3/2를 검증했다: `artifacts/gamepad-sdl-button-verification.json`.
- 실제 A 메뉴 선택과 벼랑에서 패러세일 전개를 검증했다: `artifacts/gamepad-baseline-glide.mp4`, `artifacts/paraglider-verified.png`.
- 원본 Eden의 설정과 파일은 변경하지 않는다. 시험이 끝나면 복사본 Eden을 닫고 가상 패드를 종료한다.

## 자동 시험 중 다른 작업

가상 게임패드 시험은 전역 키보드·마우스 입력이나 창 활성화를 사용하지 않는다. 사용자는 브라우저나 편집기 등으로 다른 작업을 해도 된다. 복사본 Eden은 `pauseWhenInBackground=false`로 설정했다.

- 게임 창은 작은 창으로 두고 최소화하지 않는다. 최소화하면 창 영상 캡처가 중단될 수 있다.
- 시험 중 사용자가 같은 게임에 물리 패드 입력을 보내면 결과가 섞일 수 있으므로 조작을 겹치지 않는다.
- 다른 게임패드 지원 게임을 동시에 실행하면 가상 패드에 반응할 수 있다.
- GPU나 CPU 사용량이 큰 작업은 프레임 속도를 바꿔 시간 기준 시험 결과에 영향을 줄 수 있다. 그런 경우 성능 상태와 함께 기록한다.
