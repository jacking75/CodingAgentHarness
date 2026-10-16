# TotK 1.4.3 모딩 재현 안내

2026-10-16, T08. 이 작업 공간에서 실제 성공한 입력·비행·기계식 날개 구현을 재현하는 개발 문서다. 모든 PowerShell 명령은 작업 공간 루트에서 실행한다. 현재 설치는 **참고 이미지 기반 개선 모델 12파일**이다. T06/T07의 9파일 모델과 혼동하지 않는다.

T10 추가 적용 이후에는 같은12파일 중 Player.pack에 공격2배·방어+24가 병합돼 있다. 현재 상태·검사는 [TOTK_CHEATS.md](TOTK_CHEATS.md)의 T10 관리 도구를 따른다. 아래 원래 Player SHA·refined 설치/검사 절차를 재현하려면 먼저 `manage_t10_cheats.py rollback`으로 음식·내구도를 해제하고, 작업 후 `apply`로 복원한다. 기존 검증 manifest를 병합 해시로 덮어쓰지 않는다.

## 1. 대상과 재현 수준

| 항목 | 확인한 값 |
|---|---|
| 게임 / 타이틀 | 왕국의 눈물 1.4.3 / `0100F2C0115B6000` |
| 업데이트 타이틀 | `0100F2C0115B6800` |
| main NSO Build ID, 32바이트 | `277178B7DBA1B6D4949A84778D4ABC58B31B34F5000000000000000000000000` |
| Eden / 펌웨어 | `278f411dad-master` / 22.5.0 |
| 실행 복사본 | `runtime/Eden/eden.exe` |
| 변경 금지 원본 | `G:\Emulators\Eden2` |
| 현재 모드 | `runtime/Eden/user/load/0100F2C0115B6000/Wing Flight - Experimental 1.4.3` |
| 현재 기준 manifest | `private/baselines/wing-refined-verified/manifest.json` |
| Player.pack SHA-256 | `b627ac5a250d7ccc122de632500d062d4b02cacb3ad3b715513eaebb1bded287` |

현재 작업 공간의 도구·비공개 추출물·T05 기반 빌드가 있는 경우 8절부터 재현할 수 있다. 처음 준비하는 경우 2~4절을 먼저 따른다. 이 문서와 공개 코드만으로 게임 자산을 만들 수는 없다. 소유 게임·업데이트·개인 키·로컬 세이브가 필요하다. 키 획득·보호 우회·게임 다운로드 절차는 포함하지 않는다.

판정의 기준은 `TASKS.md`, 실제 설치 해시와 일치하는 좌표·영상·검사 보고다. 생성기의 `experimental-unverified-in-game`은 기본 문구다. 빌드 성공만으로 동작 성공을 판정하지 않는다.

## 2. 환경 준비와 원본 보존

분석·빌드는 Python 3.13.13의 `.venv-tkvsc`, 가상 패드·실행 관찰은 Python 3.12.9의 `.venv-gamepad`로 분리했다. .NET SDK가 `net9.0`을 빌드할 수 있어야 하며 .NET 9 런타임도 필요하다. T08 확인 시 SDK는 10.0.301이었다. 기존 환경이 있으면 재설치하지 않는다.

```powershell
uv venv --python 3.13.13 .venv-tkvsc
uv pip install --python .venv-tkvsc/Scripts/python.exe -r requirements-analysis.txt
uv venv --python 3.12.9 .venv-gamepad
$env:VGAMEPAD_SKIP_VIGEMBUS_INSTALL = 'true'
uv pip install --python .venv-gamepad/Scripts/python.exe -r requirements-gamepad.txt
uv pip install --python .venv-gamepad/Scripts/python.exe -r requirements-gamepad-eden.txt
dotnet --list-sdks
dotnet --list-runtimes
```

일반 `oead 1.3.0`은 이 게임의 BYML을 읽지 못했다. `requirements-analysis.txt`의 `tkvsc-oead==1.5`와 TKVSC 파서 계열을 사용한다. 기존 가상 환경을 새 명령으로 덮어쓰지 않는다. 가상 패드 드라이버는 [GAMEPAD_CONTROL.md](../GAMEPAD_CONTROL.md)의 서명 확인·설치 절차를 사용한다.

초기 독립 복사는 다음 스크립트로 수행했다. **현재 복사본은 이미 있으므로 다시 실행하지 않는다.** 새 작업실에서는 `scripts/prepare_lab.py` 상단의 `SOURCE`, `GAMES`, `SAVE_TARGET`을 소유 원본 위치에 맞게 검토한다.

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/prepare_lab.py
.\.venv-tkvsc\Scripts\python.exe scripts/verify_original.py
```

`prepare_lab.py`는 실행 중인 Eden이 있으면 중단한다. 원본의 세이브 junction을 실제 파일 복사로 구체화하고, 허용한 원본·세이브 경로 밖 링크와 순환을 거절한다. 복사 중 원본 크기·수정시각 불변 및 복사본 SHA-256을 확인한다. 복사본의 config·save·load를 `private/baselines`에 보관하고 기존 TotK 모드를 복사본에서만 비활성화한다. 설정의 외부 경로를 독립 복사본으로 바꾸고 reparse point가 남지 않았는지 검사한다.

중간 실패 후 임의로 `--finalize`를 실행하지 않는다. 이 옵션은 **전체 복사 manifest가 완성된 경우** 설정 마무리용이다. 근거는 `private/copy-manifest.jsonl`, `private/lab-report.json`, `private/original-verification.json` 등 초기 원본 검사 자료다. 현재 `verify_original.py`는 원본 2,373개 메타데이터와 설정·세이브 156개 해시를 비교한다.

## 3. 소유 게임과 업데이트 추출

사용 도구는 `tools/nstool/v1.9.2/nstool.exe`다. 개인 키 경로는 `runtime/Eden/user/keys/prod.keys`이며 내용을 출력하지 않는다. 키·티켓·NSP·NCA·로그는 `private` 밖으로 내보내지 않는다.

2026-10-16 C01 정리에서 NSP와 SHA-256이 일치하는 `private/analysis/base_nca`, `update_nca` 중복 추출본을 삭제했다. 기존 RomFS·ExeFS·main.bin·날개 모델/텍스처 입력은 유지했으므로 현재 빌드·검사에는 재추출이 필요 없다. 새로운 자산을 추출할 때만 base/update NSP를 각각 해당 NCA 폴더에 NSTool `-x`로 복원한다. 아래 전체 추출 스크립트는 초기 준비용이다. NCA만 복원하려면 다음 명령을 사용한다.

```powershell
.\.venv-tkvsc\Scripts\python.exe -c "import sys; sys.path.insert(0,'scripts'); from extract_game import ANALYSIS,PRIVATE,run; [((ANALYSIS/(kind+'_nca')).mkdir(exist_ok=True),run('restore-'+kind+'-nsp','-x',ANALYSIS/(kind+'_nca'),next(p for p in (PRIVATE/'games').glob('*.nsp') if title in p.name.upper()))) for kind,title in [('base','0100F2C0115B6000'),('update','0100F2C0115B6800')]]"
```

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/extract_game.py
Get-Content private/analysis/game-build.json
.\.venv-tkvsc\Scripts\python.exe scripts/unpack_nso.py private/analysis/exefs/main private/analysis/main.bin
.\.venv-tkvsc\Scripts\python.exe scripts/inspect_player.py private/analysis/romfs/Pack/Actor/Player.pack.zs --romfs private/analysis/romfs --name vanilla-player
```

`extract_game.py`는 복사 완료 보고가 있어야 실행된다. `private/games`의 base/update NSP를 각각 NCA로 풀고 가장 큰 프로그램 NCA를 선택한다. 이 선택은 이 로컬 두 패키지에 대해 확인한 방식이므로 다른 패키지 구성에는 그대로 일반화하지 않는다. base·update 티켓 둘과 `--basenca`를 함께 전달해 업데이트의 patched filesystem을 마운트한다. 업데이트 NCA만 풀면 base에 있는 파일이 빠질 수 있다.

내부 명령의 형태는 `nstool -k <복사본 키> --tik <base 티켓> --tik <update 티켓> --basenca <base NCA> --part0 <exefs 출력> <update NCA>`다. `--fstree`에서 `ZsDic.pack.zs`가 있는지 검사하며, RomFS는 `-x /1/Pack`, `/1/Logic`, `/1/AI`, `/1/AS`, `/1/System/Resource`를 디렉터리별 추출한다. 실제 명령과 결과 로그는 `private/analysis/extract-*.log`, `romfs-*.log`에 남는다.

날개용 Model·Shader가 없는 초기 환경에서만 다음 명령으로 추가 추출한다. 아래 Python 명령은 같은 스크립트의 로컬 키·티켓 처리 함수를 재사용한다.

```powershell
.\.venv-tkvsc\Scripts\python.exe -c "import sys; sys.path.insert(0,'scripts'); from extract_game import ANALYSIS,run; b=max((ANALYSIS/'base_nca').glob('*.nca'),key=lambda p:p.stat().st_size); u=max((ANALYSIS/'update_nca').glob('*.nca'),key=lambda p:p.stat().st_size); c=['--tik',next((ANALYSIS/'base_nca').glob('*.tik')),'--tik',next((ANALYSIS/'update_nca').glob('*.tik')),'--basenca',b]; [( (ANALYSIS/'romfs'/d).mkdir(parents=True,exist_ok=True),run('romfs-'+d,*c,'-x','/1/'+d,ANALYSIS/'romfs'/d,u)) for d in ['Model','Shader']]"
```

최초 Model·Shader 추출에는 디스크 공간이 더 든다. 현재 작업 공간에는 이미 있다. 텍스처는 `prepare_refined_textures.py`가 필요한 세 파일만 확보한다. NSTool Windows판 단일 파일 추출의 경로 오류를 확인했으므로 이미 준비된 파일을 다시 추출하지 않는다.

Build ID는 `main`의 NSO0 magic 확인 후 `0x40:0x60`의 32바이트를 읽은 값이다. UI의 버전 문자열만으로 대체하지 않는다. `unpack_nso.py`는 NSO flags에 따른 LZ4 해제 후 text/rodata/data의 **memory offset** 위치에 배치한다. 단순 연결하면 네이티브 상대주소가 틀어진다.

## 4. 파일 포맷·압축·리소스 할당

| 형식 | 역할과 실제 처리 |
|---|---|
| `.pack.zs` | 게임 Zstd 사전으로 해제한 SARC. `oead.Sarc`, TKVSC `make_sarc_writer`로 엔트리 단위 변경 |
| AINB | AI action/scheduler 그래프. TKVSC `ainb_io`와 vendor AINB로 binary↔dict 변환 |
| BYML / `.bgyml` | 파라미터·노드 정의. `oead.byml.from_binary`, `to_binary(big_endian=False)` |
| ASB | 애니메이션 상태·선택 그래프. TKVSC `asb_io`의 읽기·쓰기 래퍼 |
| BFRES / `.mc` | 스켈레톤·메시·재질 / MeshCodec 컨테이너. 기존 레이아웃에 한정해 패치 |
| TXTG | BC1 색상·BC5 노멀·BC4 재질 텍스처. 로컬 원본 헤더를 템플릿으로 재사용 |
| RESTBL | 경로별 리소스 메모리 할당. `rstb_io.parse_rstb/build_rstb`와 CRC32 키 처리 |

사용 래퍼는 `tools/totk-vscode/python`에 있다. 작업 스크립트가 이 경로를 `sys.path`에 넣는다. 확장자만 제거하고 일반 Zstd로 일괄 재압축하지 않는다. `zstd_totk`는 논리 경로와 `Pack/ZsDic.pack.zs`로 pack/일반 zs 등의 사전을 선택한다. 원본 frame dict ID와 결과 dict ID를 비교하고 해제 후 payload가 같은지 검사한다.

**RESTBL 자체는 dictionary ID 0을 유지한다.** RESTBL을 읽어야 ZsDic를 로드할 수 있으므로 사전 의존 압축은 부팅 순환을 만든다. 빌더는 원본 checksum 여부를 유지한 독립 Zstd 압축을 사용한다. Player.pack은 원본 dict ID 3 계열을 유지한다. 정확한 값은 `build-report.json`의 `compression`에 기록된다.

SARC는 변경 대상 외 모든 엔트리 바이트를 대조한다. Player에서는 `AI/Player.action.parasailglide.module.ainb`, `AI/Player.scheduler.parasailglide.module.ainb` 두 개만 바꾼다. 패딩·정렬은 기존 writer가 처리한다. 노드 이름만 복사하지 않고 retail `AI/NodeDefinition/Node.Product.140.aidefn.byml.zs`와 TKVSC node definitions에서 입출력 타입·프로퍼티·Queries 참조를 확인한다.

RESTBL 키는 `.zs` 등을 제거한 논리 경로다. 이름 엔트리가 있으면 그 값을, 없으면 CRC32 해시 엔트리를 갱신한다. 기존 할당보다 줄이지 않는다. 비행 빌더는 action `max(0x20000, binary×16)`, scheduler `max(0x10000, binary×16)`, Player.pack `max(0x200000, SARC×4)` 하한을 사용한다. 이는 이 실험의 보수적 할당이며 모든 자원의 보편 공식이 아니다. 모델·AS·애니메이션·텍스처는 `build_wings.py`의 별도 할당을 따른다. 직렬화 후 parse/build 왕복도 확인한다.

## 5. 네이티브 분석과 입력 경로

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/inspect_native_nodes.py QueryPhysicsCctGetLinearVelocity ExecutePhysicsCctApplyLinearVelocity QueryApproachSpeed --output private/analysis/t08-native-nodes.txt
```

`inspect_native_nodes.py`는 main.bin의 노드 이름 문자열→AArch64 ADRP/ADD/RET GetName→vtable 참조→실행 슬롯을 찾아 Capstone으로 조사한다. 출력은 private 아래로 제한한다. 이름과 입출력 스키마가 같아도 물리 연산 의미가 같다고 가정하지 않는다.

입력은 가상 Xbox 장치→Windows XInput/SDL→게임 InputMgr→AINB Controller 쿼리 순서다. Windows 슬롯과 게임의 ControllerIndex는 별개다. T01 실측에서 게임 Index0/4는 반응했고 1~3은 0이었다. 최종 쿼리는 **ControllerIndex=0, ControllerUserName=""**다. `QueryControllerGetMask.ControllerHoldMask`를 `QueryControllerTrigMaskChecker`에 연결하므로 이름에 Trig가 있어도 누르고 있는 동안 동작한다. ZL bit2=`0x4`, R bit14=`0x4000`이다.

런타임 관찰은 `guest_input_probe.py`, `player_position_probe.py`의 GDB 읽기/정지/재개만 사용한다. 게스트 메모리 쓰기·브레이크포인트는 사용하지 않는다. main 주소는 `qOffsets`의 TextSeg fallback이 아니라 매 실행 `qRcmd mappings`의 r-x Code 후보와 main.bin **4곳×64바이트** 대조로 유일하게 식별한다.

1.4.3 전용 포인터 근거: `*(main+0x3960150)`의 InputMgr singleton, `*(main+0x3ADD238)`의 scene module. Player 검색은 scene `+0x1E8`→components `+0x58`→resident manager `+0x68`, 0x70 간격 링크와 actor 이름을 확인한다. Player XYZ는 actor `+0x2B4`다. CCT는 actor `+0x228→+0x50→+0x20→+0x10`의 outer와 `outer+8`의 impl에서 getter 경로를 따른다. 상세 코드는 `player_position_probe.py`가 기준이다. **다른 Build ID에서는 모든 상대주소·레이아웃·네이티브 코드 검증을 다시 한다.** 이전 실행의 main base·객체 주소·PID를 재사용하지 않는다.

## 6. 최종 비행 제어와 상태 복원

최종 액션은 56노드, 스케줄러는 20노드다. 원래 활공 executor와 액터 수명을 유지하며 비행 동안 중력0을 적용하고 퇴장 시1을 복원한다.

1. 왼쪽 스틱을 카메라 XZ basis로 변환한다. 전진은 `-normalizeXZ(LookVector)`, 오른쪽은 `normalizeXZ(RightVector)`다. 기본 전진 속도는 `ExecutePhysicsCctSetForwardSpeedMps(0)`으로 끈다. 목표 수평 속도12m/s, 수직은 ZL `+6`, R `-6`, 둘 다/둘 다 없음은0이다.
2. 스틱 길이 제곱 `<=0.15²`이면 평면 목표를0으로 만든 뒤 상태 보관형 `QueryApproachSpeed`로 XYZ를 보간한다. τ=0.3초, `rate=1-exp(-1/(30τ))`이고 네이티브 갱신은 `v+=(target-v)*(1-(1-rate)^VFR)`다. τ는 고정 가속도 상한이 아니다.
3. 수평은 보간 목표를 CCT Apply에 직접 전달하고 수직만 `목표Y-현재CCT.Y`를 전달한다. 상수 Apply를 매 프레임 더해 무한 가속한 실패와 구분한다. 이동 중 외력에 의한 목표 오차는 남는다.
4. 중립이면서 보간 수평 속도<=0.1m/s가 되면 그때 XZ 위치를 보관한다. `OutputOnlyOnEnter=true` 쿼리와 `12*(anchorXZ-currentXZ)`로 정지 위치를 유지한다. 감속 전 위치를 저장하면 놓은 지점으로 끌려가므로 감속 후 고정한다. 이동 writer와 호버 writer는 selector의 서로 다른 자식이다.
5. R의 원래 스카이다이빙 분기를 활공 유지 분기로 연결한다. 최상위 `IsOnGround` 분기에서 원래 **Land 액션32**로 나간다. 비접지면 기존 selector를 유지한다. 이것이 착지 후 중력0·패러세일 잔류 결함을 해결했다.

B는 원래 활공 취소·일반 낙하, 공중 X는 재전개다. 착지 뒤 R을 계속 누르면 원래 투척이 발생할 수 있으므로 놓는다. 물·피격·등반 분기를 남겼다는 정적 사실은 해당 동작의 시험 성공을 의미하지 않는다.

## 7. 기계식 날개·재질·애니메이션

`build_wings.py`는 `private/baselines/t05-lifecycle-verified/installed-mod`를 기반으로 표현 자산을 덧붙인다. 따라서 `build_flight.py`의 기본 옵션으로 새 제어를 만드는 과정과 분리된다. 현재 표현 변경은 Player.pack을 바꾸지 않는다.

로컬 패러세일의 31본·Weapon_R 바인딩·원래 손잡이를 유지한다. 천 메시를 좌우8장의 두께0.036m 깃판, 프레임·힌지·피스톤으로 바꾼다. 폭 약4.93m, LOD0 1,304정점/800삼각형, LOD1 896정점/560삼각형이다. 각 LOD의 원래 정점·인덱스 할당을 넘지 않게 검사한다. 절차적 형상은 `scripts/WingModel/Mechanical.cs`에 있다.

원본 BFRES 전체를 재저장하면 게임 전용 재질 배치가 바뀔 수 있어 모델은 정점·인덱스·본·역행렬·컬링 범위를 제한 패치한다. 애니메이션 컨테이너만 BfresLibrary로 저장한다. `Shader/ExternalBinaryString.bfres.mc`의 외부 문자열 사전이 필요하다. 문양 메시 삼각형과 cloth 반응을 제거한다.

`scripts/refined_wing_textures.py`는 BC1/BC5/BC4 템플릿으로 금속색·어두운 프레임·황동·주황색 텍스처3개를 만든다. 천 선택 로직이 `Mt_Fabric` 재질을 덮어써서 같은 길이의 `Mt_Metals`로 분리했다. 재질 인덱스·셰이더·원본 문자열 배치를 유지한다. 주황색은 색상이며 발광/블룸이 아니다.

Parasail AI8노드가 Index0의 ZL과 스틱X를 AS Blackboard `WingRise`/`WingBank`에 전달한다. AS9노드는 WingOpen 18프레임→상승 bool→좌우 bank float→중립 활공을 선택한다. Rise/Glide/Left/Right는60프레임이며 Float/Event_Pose 호환 클립을 남긴다. B 해제·착지에는 별도 접힘 클립을 만들지 않고 원래 액터 제거를 사용한다.

```powershell
# 최초 입력 준비 때만 실행한다. 현재 파일은 이미 준비돼 있다.
.\.venv-tkvsc\Scripts\python.exe scripts/prepare_wing_assets.py
.\.venv-tkvsc\Scripts\python.exe scripts/prepare_refined_textures.py
```

`.mc` 출력은 독립 Python NullCodec 디코더로139264바이트 원본 일치를 검사한다. 별도 MeshCodec 실행 파일의 NullCodec 디코딩은 구현 결함으로 실패했으며 성공한 검사로 기록하지 않는다. 상세 설명과 자산 출처는 [T06 문서](T06_MECHANICAL_WINGS.md), [개선 모델 문서](WING_REFERENCE_REFINEMENT.md)에 있다.

## 8. 빌드·설치·해제·롤백

오프라인에서 복사본 Eden과 가상 패드를 종료한 뒤 실행한다. 각 명령의 종료 코드가0인지 확인한 후 다음으로 진행한다.

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/build_wings.py
.\.venv-tkvsc\Scripts\python.exe scripts/manage_flight_install.py install --revision refined
.\.venv-tkvsc\Scripts\python.exe scripts/manage_flight_install.py status --revision refined
.\.venv-tkvsc\Scripts\python.exe scripts/verify_refined_wings.py
```

빌드 출력은 이름과 달리 현재 개선 모델을 담은 `private/build/t06-mechanical`다. 설치 도구는12파일 전체 SHA-256, 추가·누락 파일, Build ID와 경로의 reparse point를 검사한다. staging 검사 후 기존 설치를 보관하고 폴더를 교체한다. 실패하면 기존 폴더를 복원한다. 코드가 달라져 해시가 바뀌면 검증본 설치를 거절하므로 기존 manifest를 임의로 고치지 않는다.

```powershell
# 원하는 작업 하나를 선택한다.
.\.venv-tkvsc\Scripts\python.exe scripts/manage_flight_install.py disable --revision refined
.\.venv-tkvsc\Scripts\python.exe scripts/manage_flight_install.py enable --revision refined
.\.venv-tkvsc\Scripts\python.exe scripts/manage_flight_install.py rollback --revision refined
```

비활성화는 load 밖으로 폴더를 보관하는 작업, rollback은 **최근 설치 직전 상태** 복원이다. 이전에도 비행 모드가 있었으면 rollback 후에도 비행 모드가 남는다. 비활성 상태에서는 enable 후 rollback한다. 개선 모델의 상태·이벤트·이전 설치는 `private/baselines/wing-refined-install` 아래에 있다. T07 모델은 별도 `t07-integrated-verified/installed-mod`에 보존돼 있다. 과거 파일만 덮어쓰면 새 TXTG가 남으므로 폴더 전체를 교체한다.

제어만 재생성하는 정확한 옵션은 다음과 같다. 결과는 별도 `private/build/Wing Flight - Experimental 1.4.3`이며 설치하지 않고 기준 T05와 비교한다. `build_flight.py --install`은 날개를 제거하는 롤백이 아니다.

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/build_flight.py --velocity-writer cct-apply --feedback-velocity --horizontal-direct --horizontal-hold --smoothing approach --response-seconds 0.3 --controller-index 0 --ground-exit
```

지구력 무한은 별도 모드다. 기존 설치가 없을 때만 `scripts/install_infinite_stamina.py`를 실행한다. 비행 모드 해제·롤백은 이를 해제하지 않는다. 같은 Player.pack·RESTBL을 교체하는 다른 모드는 자동 병합하지 않는다.

## 9. 실행·관찰·종료 재현

현재 준비된 벼랑 세이브를 복원한다. 새 진행이 필요하면 먼저 복사본 세이브를 따로 보관한다. 기준은 동하테르 **2026-10-15 22:34 slot_03**, 35파일, XYZ `(1665.193115,339.451141,2844.975830)`다.

```powershell
.\.venv-gamepad\Scripts\python.exe scripts/trial_support.py restore-save
.\.venv-gamepad\Scripts\python.exe scripts/guest_input_probe.py configure
.\scripts\gamepad.cmd start
.\.venv-gamepad\Scripts\python.exe scripts/lab_session.py launch
.\.venv-gamepad\Scripts\python.exe -c "import sys; sys.path.insert(0,'scripts'); from guest_input_probe import ReadProbe; p=ReadProbe(); p.close()"
.\.venv-gamepad\Scripts\python.exe scripts/lab_session.py wait-ready
.\.venv-gamepad\Scripts\python.exe scripts/trial_support.py load-menu
.\.venv-gamepad\Scripts\python.exe scripts/trial_support.py capture --name t08-world-check
```

GDB 부팅 정지는 ReadProbe 연결/close로 재개한다. 포트가 열리기 전에 연결이 실패했다면 준비 상태를 확인하고 재연결한다. 게임 창은1280×760, 실제 캡처1264×721을 유지한다. 전역 키·마우스·전체 화면을 사용하지 않는다. 타이틀/로드 확인창이 남았으면 가상 패드 A로 진행하고, **월드 HUD와 벼랑 화면**을 직접 확인한다. 수동 로드 목록은 자동 저장과 혼동하지 않고 위 날짜를 선택하며 확인창 취소에서 UP→A로 불러온다.

새 시험 이름을 사용해 기존 증거를 보존한다. 최종 외형 시험을 재현하는 입력은 다음과 같다.

```powershell
.\.venv-gamepad\Scripts\python.exe scripts/flight_control_trial.py t08-refined-replay --adaptive-takeoff --takeoff-clearance 9 --steps-file scripts/trials/wing_refined_visual.json --probe-position --sample-interval 0.1
```

이륙은 단순 고정 시간이 아니라 기준 위치에서9m 이탈과 연속 비접지를 관찰한다. 지형이 바뀌면9m도 그대로 적용하지 않는다. 첫 캡처 프레임 이후 입력한다. 원시 `private/analysis/<시험명>-positions.json`에는 설치 전체 해시·내부 HoldMask·카메라·좌표·CCT·중력·관찰 시간을 남긴다. `artifacts/<시험명>.mp4/.json`은 영상과 입력이다.

실패해도 다음 종료·복구를 수행한다.

```powershell
.\.venv-gamepad\Scripts\python.exe scripts/lab_session.py close
.\scripts\gamepad.cmd stop
.\.venv-gamepad\Scripts\python.exe scripts/guest_input_probe.py restore
.\.venv-gamepad\Scripts\python.exe scripts/trial_support.py restore-save
.\.venv-tkvsc\Scripts\python.exe scripts/verify_refined_wings.py --trial t08-refined-replay
.\.venv-tkvsc\Scripts\python.exe scripts/verify_refined_shutdown.py
```

새 시험이 불완전하면 해당 `verify_refined_wings`가 실패하는 것이 정상이다. 이때 기존 성공 보고를 새 시험 성공으로 해석하지 않는다. 기존 시험만 재검사하려면 기본 trial `wing-refine-v5`를 사용한다. 종료 검사는 복사본·패드 종료, 포트58437 미리스닝, GDB false/6543/default true, 속도100%, 세이브35파일·원본 불변·설치 manifest를 검사한다.

## 10. 성공 근거·실패 원인·한계

| 단계 | 확인한 결과 / 증거 |
|---|---|
| 입력 T01 | Index0/4의 ZL/R/4방향과 중립. `live-controller-probe.json` |
| 수직 T02 | +5.949m/s 상승, 중립 안정, 하강 약−4.303m/s. `t02-vertical-verification.json` |
| 수평 T03 | 카메라 회전116.15도 전후 cosine≥0.99725, 노이즈 포함17.953초 XZ 범위0.02258m |
| 가감속 T04 | τ0.3초의 상승/전진/좌측90% 도달0.758/0.571/0.677초. `t04-smoothing-verification.json` |
| 복원 T05 | 착지·중력1·지상 이동/점프, B/X·메뉴·수동 재로드 후 재비행. `t05-lifecycle-verification.json` |
| T07 이전 모델 통합 | 1,029좌표·83.1초, 6방향/호버/착지, 설치 왕복. `t07-integration-verification.json` |
| 현재 개선 모델 | 356좌표, 마지막10샘플 XYZ 범위0.01452m, 전개/상승/bank/해제/재전개. `wing-refined-verification.json` |

JSON은 모두 `private/analysis` 아래다. 현재 화면은 `artifacts/wing-refined-final.png`, `wing-refined-top.png`, 영상은 `wing-refine-v5.mp4`다. 개선 모델의 Player·Parasail pack·AS·애니메이션·문양 제거 모델이 T07과 같다는 것은 바이트 비교로 확인했다. **개선 모델의 착지 시험을 새로 수행했다는 뜻은 아니다.**

| 실패·오판 | 원인과 채택한 해결 |
|---|---|
| 작은 HUD·일반 활공을 비행 성공으로 오판 | 과거 판정 취소. 원본 프레임과 내부 입력·좌표·해시로 재검증 |
| ControllerIndex1은 움직이지 않음 | 게임 내부0/4와 Windows 슬롯을 구분, Index0 채택 |
| CCT SetLinearVelocity로 전개 실패 | setter 상수 반복을 중단하고 Apply+Y피드백 채택 |
| Apply 상수로 가속 누적 | 매 프레임 현재 Y 차감 |
| 기본 전진과 목표의 충돌·중립 표류 | native forward0, 수평직접, 감속 뒤 XZ 위치 피드백 |
| 착지 뒤 날개·중력0 잔류 | scheduler 최상위 접지 분기→기존 Land32 |
| 천 무늬가 새 텍스처를 덮음 | `Mt_Fabric`→`Mt_Metals`, 원래 BC 압축 계열 유지 |
| 등 부착 날개·초기 세로 날개 | 사용자 선택에 따라 기각. 패러세일 위치·손잡이 유지 |
| 오래된 주소·qOffsets fallback | 매 실행 mapping+native bytes 대조 |

측정 속도는 벽시계·비동기 GDB 기준이며 게임 시간 기준 정밀 속도는 보장하지 않는다. 하강 목표−6에 비해 약−4.28~−4.35m/s가 관측됐고 이동 중 외력 오차도 남는다. T04의15FPS 시험은 에뮬레이터50% 속도·입력시간2배 조건이며 독립적인 모든 가변 dt 검증이 아니다. 영상 입력 예상 시각에는 약1초대 차이가 있어 정밀 판정은 실제 입력·좌표 시간을 사용한다.

고정 벼랑·아래 지면 외의 물·피격·등반·다른 지역은 미검증이다. 날개 충돌체·발광은 추가하지 않았다. 지형 관통·벽 근처 카메라 가림·원래 목재 손잡이·R 착지 뒤 투척은 남는다. 실패 시 같은 시험을 근거 없이 반복하지 않고 설치 해시·입력 경로·접지·로드 화면 중 어느 단계가 달랐는지 먼저 기록한다.

## 11. 도구 출처·라이선스·비공개 경계

리비전은 이 작업실 보관본의 값이다. 새 버전으로 교체한 결과를 같은 검증으로 취급하지 않는다. 도구의 LICENSE와 내장 의존성 고지를 유지한다.

| 도구 | 사용 버전·리비전 | 출처 / 라이선스 |
|---|---|---|
| NSTool | 1.9.2 | [jakcron/nstool](https://github.com/jakcron/nstool/releases/tag/v1.9.2), 로컬 `tools/nstool/source/LICENSE` |
| TKVSC | `ad95386db004207d21e19767d37a72394a893187` | [BladesawStudios/totk-vscode](https://github.com/BladesawStudios/totk-vscode), GPL-3.0 계열; vendor 별도 고지 |
| tkvsc-oead | 1.5 | [PyPI](https://pypi.org/project/tkvsc-oead/1.5/), 패키지 메타데이터 GPLv2+ |
| totk-meshcodec | `032c41d18cb8399c7c01c04f0ab140689327431c` | [UltimateBomb](https://github.com/UltimateBomb/totk-meshcodec), MIT |
| BfresLibrary | `31c1a0cb9f7607f8d69bbc445eacace542c2cbad` | [KillzXGaming](https://github.com/KillzXGaming/BfresLibrary), MIT 및 포함 DLL 고지 |
| MeshCodec | `b3600954872dbc2893a1bcc9e851c1e364f303ab` | [dt-12345](https://github.com/dt-12345/MeshCodec), GPL-2.0 및 내장 의존성 |
| Capstone / LZ4 | 5.0.9 / 4.4.5 | [Capstone](https://github.com/capstone-engine/capstone), [python-lz4](https://github.com/python-lz4/python-lz4), 배포 패키지 BSD 계열 고지 |
| zstandard / PyYAML / mmh3 | 0.25.0 / 6.0.3 / 5.3.1 | [python-zstandard](https://github.com/indygreg/python-zstandard) / [PyYAML](https://github.com/yaml/pyyaml) / [mmh3](https://github.com/hajimes/mmh3), 해당 배포본 LICENSE |
| vgamepad | 0.1.3, `3f910aa8bbde49a576683db74ad5e4a0879f8a80` | [공식 저장소](https://github.com/yannbouteiller/vgamepad), MIT |
| ViGEmBus 설치 패키지 | 1.22.0 | [공식 릴리스](https://github.com/nefarius/ViGEmBus/releases/tag/v1.22.0), BSD-3-Clause 계열; 서명 확인 후 설치 |
| pygame-ce | 2.5.6 | [pygame-ce](https://github.com/pygame-community/pygame-ce), LGPL 계열 및 SDL 고지 |

ViGEmBus는 [공식 EOL 안내](https://docs.nefarius.at/projects/ViGEm/End-of-Life/)가 있는 종료 프로젝트다. 새 Windows 환경에서는 실제 생성·XInput 재검사를 수행한다. 설치 패키지1.22.0과 내부 드라이버 버전은 다를 수 있다. 현재 스킬의 설치 스크립트도 패키지 SHA와 Authenticode를 별도 확인한다.

lotuskit의 오래된 버전별 주소를1.4.3에 적용하지 않았다. 초기 조사 도구와 문서에 나온 추천 도구 전부를 실행 의존성으로 추가하지 않는다. 게임·키·티켓·세이브·추출 main/pack/BFRES/TXTG·생성 모드도 Nintendo 원본을 포함하므로 Git·배포물에 넣지 않는다. 공개 가능한 자체 코드·문서와 비공개 자산은 구분하되 이 문서가 제3자 라이선스를 바꾸지는 않는다.

## 12. 다음 세션에서 확인할 결과

현재 빌드를 유지하려면 `status --revision refined`와 `verify_refined_wings.py`, `verify_refined_shutdown.py`를 실행한다. 제어/외형을 수정했다면 새 trial 이름·설치 전체 해시·입력·좌표·영상을 먼저 남기고 검증 범위만 갱신한다. `TASKS.md`와 `SESSION_HANDOFF.md`에 실제 완료 결과·남은 한계·다음 행동을 기록한다. T09의 범용 스킬은 게임별 프로필·세이브 복구와 분리해 사용한다.
