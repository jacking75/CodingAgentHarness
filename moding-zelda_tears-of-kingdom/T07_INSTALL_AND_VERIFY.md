# T07: 설치·실행·복구와 통합 검증

이 문서의9파일 manifest와 통합 시험은 T07 당시 모델 기준이다. 이후 참고 이미지 기반 개선 모델12파일을 설치했다. 현재 모델에는 [WING_REFERENCE_REFINEMENT.md](WING_REFERENCE_REFINEMENT.md)의 `--revision refined` 설치·검증 명령을 사용한다. 아래 게임 실행·세이브 복원 절차는 계속 유효하다.

2026-10-16 검증. T06 기계식 날개와 Index 0·비행 액션 56노드·접지 복원 스케줄러 20노드를 유지한다. 원본 `G:\Emulators\Eden2`는 변경하지 않는다. 모든 명령은 `G:\working_zelda`에서 실행한다.

## 대상과 전제

| 항목 | 검증값 |
|---|---|
| 게임 | TotK 1.4.3 / `0100F2C0115B6000` |
| Build ID | `277178B7DBA1B6D4949A84778D4ABC58B31B34F5000000000000000000000000` |
| Eden / 펌웨어 | `278f411dad-master` / 22.5.0 |
| 설치 대상 | `runtime/Eden/user/load/0100F2C0115B6000/Wing Flight - Experimental 1.4.3` |
| 생성 결과 | `private/build/t06-mechanical` |
| 기준 해시 | `private/baselines/t06-mechanical-verified/manifest.json` |
| Player.pack SHA-256 | `b627ac5a250d7ccc122de632500d062d4b02cacb3ad3b715513eaebb1bded287` |
| 제어 | 수평 12m/s·수직 ±6m/s 목표, Approach τ=0.3초, 데드존 0.15 |

이 절차는 소유한 게임 추출물, 기존 Python 가상 환경, .NET 및 작업 도구가 준비된 현재 작업 공간을 대상으로 한다. 에뮬레이터·게임·키를 새로 설치하는 배포용 설치 프로그램이 아니다. 게임·키·세이브·추출 자산과 생성된 게임 자산은 로컬 `private`·`runtime`에만 둔다. 공개용 자산 패키지는 만들지 않았다.

## 빌드와 설치

복사본 Eden과 가상 패드를 종료한 상태에서 실행한다. 명령이 실패하면 다음 단계로 진행하지 않는다.

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/build_wings.py
.\.venv-tkvsc\Scripts\python.exe scripts/manage_flight_install.py install
.\.venv-tkvsc\Scripts\python.exe scripts/manage_flight_install.py status
.\.venv-tkvsc\Scripts\python.exe scripts/verify_wings.py
```

`build_wings.py`는 보관된 T05 비행 빌드 위에 날개를 생성한다. 설치 도구는 T06 기준의 9파일 전체 SHA-256, 추가·누락 파일, 로컬 추출 main의 Build ID를 확인한다. 새 폴더에 복사·검사한 다음 기존 설치를 보관하고 교체한다. 이전 파일을 덮어쓰거나 삭제하지 않는다. 알려진 검증본과 다른 빌드는 설치를 거부한다. 이 경우 manifest를 임의로 바꾸지 않고 변경된 빌드를 별도 검증해야 한다.

지구력 무한은 별도 모드이며 비행 모드 비활성화·롤백에 포함되지 않는다. 기존 설치가 없는 경우에만 다음 명령으로 설치한다.

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/install_infinite_stamina.py
```

T07에서는 T05도 다음 옵션으로 다시 생성해 보관본 전체와 일치함을 확인했다.

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/build_flight.py --velocity-writer cct-apply --feedback-velocity --horizontal-direct --horizontal-hold --smoothing approach --response-seconds 0.3 --controller-index 0 --ground-exit
```

전체 설치 왕복 검증을 다시 수행하려면 다음 명령을 사용한다. 기존 설치와 이전 빌드 폴더를 `private/baselines/t07-install` 아래에 보존하므로 반복할수록 백업이 추가된다.

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/verify_install_roundtrip.py
```

빈 출력 폴더에서 날개를 두 번 생성해 기준 9파일과 일치함을 검사한다. 기존 설치 교체와 비행 모드 폴더가 없는 신규 설치 각각에 대해 설치 → 비활성화 → 활성화 → 롤백을 실행한다. 신규 설치의 롤백은 설치 전의 부재 상태를 복원한다. 마지막에는 검증본을 설치해 둔다. 기존 독립 Eden 복사본을 사용하며 에뮬레이터·게임 전체를 다시 복사하지 않는다.

## 실행과 조작

[README의 조작표](../README.md#현재-빌드와-조작)와 [패드 안내](../GAMEPAD_CONTROL.md)를 참고한다. 왼쪽 스틱은 수평 이동, ZL은 상승, R은 하강, 모두 놓으면 감속 후 호버다. 공중 X로 전개하고 B로 해제한다. 착지할 때 R을 놓는다. 계속 누르면 지상의 원래 투척 조작이 발생한다.

현재 플레이어 1은 가상 패드 프로필이다.

```powershell
.\scripts\gamepad.cmd start
.\.venv-gamepad\Scripts\python.exe scripts/lab_session.py launch
.\.venv-gamepad\Scripts\python.exe scripts/lab_session.py wait-ready
```

물리 패드로 전환하려면 Eden이 종료된 상태에서 `scripts/lab_gamepad_profile.py physical`을 패드 Python으로 실행한다. 가상 패드로 되돌릴 때는 가상 패드를 먼저 시작한 뒤 같은 도구의 `virtual` 명령을 사용한다. 전역 키보드·마우스 입력을 사용하지 않으며 테스트 창은 1280×760으로 유지한다.

## 비활성화·재활성화·이전 설치 복구

항상 Eden 종료 후 실행한다.

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/manage_flight_install.py disable
.\.venv-tkvsc\Scripts\python.exe scripts/manage_flight_install.py enable
.\.venv-tkvsc\Scripts\python.exe scripts/manage_flight_install.py rollback
```

각 명령은 원하는 작업 하나만 선택해 실행한다. `disable`은 비행 모드를 Eden의 load 경로 밖인 `private/baselines/t07-install/disabled-mod`로 옮긴다. `enable`은 이를 다시 활성화한다. `rollback`은 **가장 최근 설치 직전 상태**로 복원한다. 비활성화된 상태에서는 먼저 `enable`해야 롤백할 수 있다. 이전 상태도 같은 비행 모드였다면 롤백 후에도 비행 모드가 남는다. 모드를 끄는 목적이면 `disable`을 사용한다.

상태·이전 설치 경로는 `private/baselines/t07-install/state.json`, 전체 작업 기록은 `events.jsonl`에 남긴다. 보관본이 달라졌거나 대상 폴더가 충돌하면 작업을 거부한다. 원본 Eden의 설정·세이브·모드는 복구 대상으로 사용하지 않는다.

## 통합 시험 재현

이 절차는 복사본 세이브를 사용자가 지정한 벼랑 체크포인트로 복원한다. 복사본에서 새로 진행한 세이브가 필요하면 먼저 별도 보관한다. 기준은 2026-10-15 22:34 동하테르 `slot_03`, 35파일이다.

```powershell
.\.venv-gamepad\Scripts\python.exe scripts/trial_support.py restore-save
.\.venv-gamepad\Scripts\python.exe scripts/guest_input_probe.py configure
.\scripts\gamepad.cmd start
.\.venv-gamepad\Scripts\python.exe scripts/lab_session.py launch
```

GDB가 켜지면 부팅이 일시정지된다. 먼저 아래 연결·재개를 실행한 뒤 타이틀 준비를 기다린다. 포트가 아직 열리지 않았으면 잠시 후 연결 명령만 재시도한다.

```powershell
.\.venv-gamepad\Scripts\python.exe -c "import sys; sys.path.insert(0,'scripts'); from guest_input_probe import ReadProbe; p=ReadProbe(); p.close()"
.\.venv-gamepad\Scripts\python.exe scripts/lab_session.py wait-ready
.\.venv-gamepad\Scripts\python.exe scripts/trial_support.py load-menu
.\.venv-gamepad\Scripts\python.exe scripts/trial_support.py capture --name t07-world-check
```

20~35초 정도 로딩 후 화면의 월드 HUD와 기준 벼랑을 확인한다. 로딩 확인창이 남았을 때만 가상 패드의 A를 한 번 더 보낸다. 월드에 진입했음을 시간만으로 가정하지 않는다.

```powershell
.\.venv-gamepad\Scripts\python.exe scripts/flight_control_trial.py t07-integrated --steps-file scripts/trials/t07_integrated.json --adaptive-takeoff --takeoff-clearance 9 --probe-position --sample-interval 0.07
```

같은 이름으로 실행하면 기존 영상·좌표 기록을 덮어쓴다. 기존 증거를 보존하려면 먼저 별도 보관한다. 시험은 9m 이상 벼랑 이탈 및 연속 비접지 관측 후 전개하고, 약 71초 입력 동안 6방향·호버·반전·B 해제·X 재전개·하강 착지·지상 이동·점프를 연속 실행한다. 하강 끝의 B는 R 장기 유지로 발생한 지상 조준을 해제한다. 자동 시험이 R 자동 해제 기능을 구현한 것은 아니다.

실패해도 아래 종료·복구는 반드시 실행한다.

```powershell
.\.venv-gamepad\Scripts\python.exe scripts/lab_session.py close
.\scripts\gamepad.cmd stop
.\.venv-gamepad\Scripts\python.exe scripts/guest_input_probe.py restore
.\.venv-gamepad\Scripts\python.exe scripts/trial_support.py restore-save
.\.venv-tkvsc\Scripts\python.exe scripts/verify_original.py
.\.venv-tkvsc\Scripts\python.exe scripts/verify_integrated_trial.py
.\.venv-tkvsc\Scripts\python.exe scripts/verify_t07_shutdown.py
```

`gamepad.cmd stop`은 이미 종료되어 연결 파일이 없으면 오류를 출력할 수 있다. 이때 새 서버를 시작하지 말고 마지막 종료 검사에서 프로세스·연결 파일 부재를 확인한다. GDB는 네 설정을 원복하며 정상값은 `use_gdbstub=false`, 포트 `6543`, 두 `default=true`다. 속도 제한은 100%다.

## 2026-10-16 결과와 근거

| 항목 | 결과 |
|---|---|
| 재빌드·설치 | T05 전체 재빌드 일치, T06 두 번 새 빌드의 9파일 일치, 신규/교체 설치 왕복 통과 |
| 연속 통합 시험 | 1,029샘플, 단일 비행에서 6방향·호버·가감속·해제·재전개·착지 통과 |
| 수평 방향 | 정착 구간 변위와 카메라 목표 방향 cosine ≥0.99936 |
| 수평 가속 | 전진/좌측 목표 90% 도달 0.684/0.769초, 중간 속도 각각 7샘플 |
| 호버 | 6개 정착 구간 XZ 범위 최대 0.00251m, Y 범위 최대 0.04264m |
| 해제·복원 | B 후 중력1·가속 낙하, X 재전개 후 중력0·호버 |
| 착지 | 입력 시작 후 57.640초 접지, 지상 중력1·이동1.731m·점프 높이0.678m·재접지 |
| 영상 | 83.1초, 1264×721, 창1280×760, 평균 캡처 약26.15FPS; 게임 화면30FPS |

- `private/analysis/t07-install-verification.json`: 설치·빌드·롤백과 전체 파일 manifest.
- `private/analysis/t07-integrated-positions.json`: 실제 입력·좌표·카메라·중력·CCT 속도, 빌드 옵션·전체 설치 해시·실행 파일 해시·속도 설정.
- `private/analysis/t07-integration-verification.json`: 허용치 판정·입력 타임라인·입력 배치의 실제 시각·영상 정보·증거 해시.
- `artifacts/t07-integrated.mp4` 및 같은 이름 JSON: 전체 영상과 입력 요청 기록.
- `artifacts/t07-world.png`, `t07-frame-8.png`, `t07-cancel-contact.png`, `t07-final-ground.png`: 시작·날개·해제/재전개·착지 후 화면.
- `private/analysis/t07-shutdown-verification.json`: 프로세스·GDB·속도·세이브·원본 불변 종료 검사.

영상 JSON의 `video_start_seconds`는 첫 캡처 진행 통지에서 계산한 **예상값**이다. 실제 해제/재전개 화면은 약32~33.5초에서 보이며 예상 입력 시각보다 약1초대 늦다. 이 오프셋을 모든 프레임에 정확히 적용할 수 있다고 가정하지 않는다. 수치 판정은 `input_seconds`와 실제 HoldMask·스틱을 대조한다. `t07-cancel-contact.png`는 영상30초부터0.25초 간격의4열×6행이다.

검증 범위는 고정 벼랑과 아래 지면이다. 물·피격·등반·다른 지역은 미검증이다. 수직 하강은 목표−6m/s에 비해 관측 약−4.28m/s이며 이동 중 외력 오차가 남는다. GDB 비동기 관측·벽시계 측정이므로 게임 시간 기준 정밀 속도를 보장하지 않는다. 기계식 날개에는 별도 충돌체가 없어 급경사·근접 카메라에서 관통·가림이 가능하다. 이러한 한계를 제거한 것으로 완료 처리하지 않는다.
