# TotK 1.4.3 추가 치트와 비행 모드 병합

T10, 2026-10-16. 적용 대상은 작업 공간의 독립 복사본이다. 원본 `G:\Emulators\Eden2`와 공유 원본 데이터는 변경하지 않는다. 사용자가 선택한 음식 범위는 **공격2배·방어+24 복원, 지속시간 유지**다. 다른 음식 효과·회복량·지속시간·수량을 임의로 늘리지 않는다.

## 적용 대상과 현재 구성

| 항목 | 값 |
|---|---|
| 게임 | TotK1.4.3 / `0100F2C0115B6000` |
| main Build ID | `277178B7DBA1B6D4949A84778D4ABC58B31B34F5000000000000000000000000` |
| 치트 파일명 | `277178B7DBA1B6D4.txt` |
| 기존 비행·날개 | `Wing Flight - Experimental 1.4.3`의12파일 |
| 장비 내구도 | 별도 `Infinite Equipment Durability 1.4.3/cheats` |
| 지구력 | 기존 `Infinite Stamina 1.4.3` 유지 |
| 식사 값 | 기존 비행 Player.pack의 ConditionParam 두 배열만 병합 |
| 관리 스크립트 | `scripts/manage_t10_cheats.py` |
| 백업·상태·이벤트 | `private/baselines/t10-cheats` |
| 생성 결과 | `private/build/t10-cheats` |

치트파일명의16자리 ID와 전체 NSO32바이트 Build ID를 혼동하지 않는다. 스크립트는 NSO magic과 전체 ID, 패치 대상 main.bin의 원래 명령을 먼저 확인한다. 다른 버전에는 적용하지 않는다.

## 기존 기록에서 재사용한 내용

다음 원본 문서를 읽고 로컬 보관본을 대조했다.

- `G:\Emulators\TOTK_1.4.3_모드_작업기록_2026-08-30_23-25-33.md`
- `G:\Emulators\TOTK_1.4.3_식사효과_변경_및_롤백_2026-09-04.md`
- `G:\Emulators\Switch-Emulation-Setup-Summary.md`

8월 기록의 공격1.3/1.5/1.8배·방어12/24/48보다9월의 **모든 레벨 공격2배·방어24**가 최신 값이었다. 복사해 보관한 `private/baselines/disabled-totk-mods/Meal Effects Plus 1.4.3`도 최신 값과 일치했다. 과거 문서의 숨김 부팅·파일 역검증은 전투 수치 실증이 아니므로 이번의 실제 음식 섭취·런타임 값 관찰과 구분한다.

## 장비 내구도와 방어구의 차이

기존 `Infinite Durability 1.4.3`에서 장비 내구도 섹션만 분리했다. 같은 파일의 지구력 섹션은 복사하지 않아 기존 지구력 모드와 중복시키지 않는다. 원래 코드는 [MyNXCheats의 해당 Build ID 파일](https://github.com/Arch9SK7/MyNXCheats/blob/main/The%20Legend%20Of%20Zelda%20Tears%20Of%20The%20Kingdom/0100F2C0115B6000/cheats/277178B7DBA1B6D4.txt)의 장비 섹션과 일치한다.

| main 상대 위치 | 확인한 원래 명령·동작 | 내구도 코드 |
|---|---|---|
| `0x21ECA9C` | `msub w8,w10,w9,w8`, 현재 값에서 소모량 차감 | 곱셈 입력을0으로 만들어 차감을 막음 |
| `0x282E58`, `0x2829F4` | `ldr w1,[x8,#8]` | 아래 보조 코드로 BL |
| `0x2BB9FE0`~`FE8` | 사용하지 않는0바이트12개 | `ldr w1,[x8,#0x18]; str w1,[x8,#8]; ret` |

이 코드의 일반 장비 경로는 무기·활·방패에 적용되지만 이번에 **소모 전후를 수치로 실증한 대표 조건은 활 사격**이다. 투척 파괴, 융합 소재 수명, 모든 무기 종류·적과의 전투를 전부 검증한 것은 아니다. 이미 손상된 장비가 최대치로 수리된다고 별도로 보장하지 않는다.

의류 방어구에는 원래 내구도가 없다. 소유 체크포인트의69개 Armor 항목은 이름·염색 값이며 `Pouch.Armor.Content.Life` 필드가 없다. 게임 저장 해시 목록과 [사용한 저장 형식 소스](https://github.com/marcrobledo/savegame-editors/blob/master/zelda-totk/zelda-totk.class.pouch.js)의 Armor 구조도 이름·색상만 가진다. 반면 Weapon/Bow/Shield는 Life 배열을 가진다. 따라서 **방어구 내구도 무한용 패치를 추가하지 않았다.** 이를 무적·방어력 증가·최대 강화로 대체하지 않는다. 방패는 의류 방어구와 별도 장비다.

## 음식 효과·상한·지속시간

Player 내부 변경 대상:

`Component/ConditionParam/Player.game__component__ConditionParam.bgyml`

| 배열 | 원래1.4.3 레벨0/1/2/3 | 적용 후0/1/2/3 |
|---|---|---|
| AttackUp | 1.0 / 1.2 / 1.3 / 1.5 | 1.0 / **2.0 / 2.0 / 2.0** |
| DefenseUp | 0 / 4 / 12 / 24 | 0 / **24 / 24 / 24** |

레벨0 기본값과 기존3단계 구조를 유지한다. 공격은 기존 최고1.5배를2배로, 방어는 기존 최고+24를 모든 유효 레벨에 적용한다. 게임 전체에서 가능한 절대 최대값을 탐색해 무제한으로 만든 작업은 아니다. 사용자가 지정한 과거 설정 복원이다. 이 파라미터는 Player의 같은 상태 효과를 공유하므로 장비에서 발생한 동일 AttackUp/DefenseUp 상태에도 영향을 줄 수 있다. 별도의 방어구 강화·새 효과를 추가한 것은 아니다.

다른 효과인 내서·방염·내한·전기 저항·이동·은밀·독기 방어·발광·회복/추가 하트·지구력 회복 등은 그대로다. 원래 음식이 가진 효과 종류와 레벨을 바꾸거나 서로 다른 버프를 동시에 유지하도록 만들지 않는다. 공격 음식 뒤 방어 음식을 먹었을 때 공격 버프가 교체되는 원래 동작도 유지한다.

음식별 지속시간은 저장 데이터의 `Pouch.Food.Content.Effect.Time` 초 단위 값이다. 시험 음식은 공격190초(3:10)·방어80초(1:20)의 레벨1 음식이었다. 적용·해제 모두 같은 원본 음식으로 시험했고 HUD 타이머가 감소했다. 30분 연장이나 무한 타이머 치트는 넣지 않았다. 원래 게임 전체 요리의 시간 상한을 변경·재인증한 것은 아니다.

## 비행 모드와 충돌 없이 병합한 방식

기존 식사 모드를 별도 폴더로 그대로 활성화하면 비행 모드와 같은 Player.pack 및 RESTBL을 교체한다. 그래서 전체 모드를 복사하지 않았다.

1. 검증된 `wing-refined-verified/installed-mod`의 Player.pack을 기준으로 잡는다.
2. 원래 dict ID3으로 해제하고 SARC의 ConditionParam만 읽는다.
3. BYML v7을 명시해 AttackUp/DefenseUp만 바꾼다. 나머지 파라미터는 값·타입을 보존한다.
4. SARC를 다시 열어 변경 엔트리가 정확히 하나인지 검사한다. 비행 액션56노드·접지 스케줄러20노드는 바이트가 같다.
5. 같은 사전으로 압축하고 payload 왕복·dict ID를 확인한다. 나머지11파일은 기준 manifest와 일치해야 한다.

BGYML은3336→3264바이트, SARC는1075876→1075804바이트로72바이트 줄었다. float 공유값 재정리 때문이며 의미상 바뀐 필드는 두 배열뿐이다. 원래 RESTBL 할당 범위를 늘리지 않으므로 현행 RESTBL을 그대로 유지했다. 기존9월 문서의 '동일 크기이면 in-place 교체' 조건은 이번 생성본에 맞지 않아 엔트리 단위 재생성 후 전체 비대상 엔트리를 비교했다.

과거 식사 모드의 IPS32에는 main `0x21238FC`의 `mov w8,#0x6e`→`mov w8,#0x200` 변경이 있었다. 이번 두 파라미터 복원에는 그 IPS를 복사하지 않았으며, 실제 음식 섭취 후2배/+24가 적용됨을 별도로 관찰했다. 나머지 Challenge Mode나 다른 네이티브 효과를 함께 적용한 것으로 해석하지 않는다.

| Player.pack | SHA-256 |
|---|---|
| 기존 날개 검증본 | `b627ac5a250d7ccc122de632500d062d4b02cacb3ad3b715513eaebb1bded287` |
| 비행+식사 병합본 | `55c6a912b90fc61193f0f2342fbb0e3143b408b7dc3ebfbee0b4938bcf494909` |

기존 build-report/wing-build-report는 원래 비행·외형 빌드 기록으로 보존한다. 현재 병합본의 해시는 T10 build/state/검증 보고를 기준으로 한다. 과거 manifest를 새 해시로 덮어쓰지 않는다.

## 적용·개별 해제·롤백

모든 변경 명령은 복사본 Eden과 가상 패드를 종료한 상태에서 실행한다. 게임 실행 중 파일을 지우는 방식으로 치트를 끄지 않는다. 네이티브 패치는 다음 실행부터 해제된다.

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/manage_t10_cheats.py build
.\.venv-tkvsc\Scripts\python.exe scripts/manage_t10_cheats.py apply
.\.venv-tkvsc\Scripts\python.exe scripts/manage_t10_cheats.py status
```

```powershell
# 원하는 작업 하나를 선택한다.
.\.venv-tkvsc\Scripts\python.exe scripts/manage_t10_cheats.py disable --component durability
.\.venv-tkvsc\Scripts\python.exe scripts/manage_t10_cheats.py apply --component durability
.\.venv-tkvsc\Scripts\python.exe scripts/manage_t10_cheats.py disable --component meals
.\.venv-tkvsc\Scripts\python.exe scripts/manage_t10_cheats.py apply --component meals
.\.venv-tkvsc\Scripts\python.exe scripts/manage_t10_cheats.py rollback
```

`rollback`은 T10의 두 효과를 끄고 원래 날개 Player.pack을 복원한다. 날개·지구력 무한은 유지한다. 비활성화한 내구도 폴더는 백업으로 이동하고 삭제하지 않는다. 원래 Player 파일·처음 wing 전체 manifest·지구력 해시·최신 상태·이벤트는 `private/baselines/t10-cheats`에 보관한다. 예상과 다른 Player·추가 파일·변경된 지구력 모드가 있으면 거절한다.

T10 음식이 켜져 있으면 `verify_refined_wings.py`, `verify_refined_shutdown.py`와 기본 refined manifest는 Player 변경을 거절하는 것이 정상이다. 기존 외형 검증을 재실행하거나 외형을 재설치할 때는 **T10 rollback→기존 날개 작업→T10 apply** 순서로 한다. 날개를 새 해시로 개발했다면 T10의 고정 기준도 새 검증 후 갱신해야 하며 임의 manifest 수정으로 우회하지 않는다.

## 실제 전후 검증

시험은 창1280×760, 기존 가상 패드, 고정 수동 세이브의 새 복원본에서 수행했다. 전역 키보드·마우스를 사용하지 않았다. 각 비교 실행은 같은 장비·음식·수량으로 시작했다.

| 조건 | 끈 상태 | 켠 상태 | 전체 롤백 후 |
|---|---|---|---|
| 장착 활 index6,3회 사격 | Life45→42 | **45→45** | **45→42** |
| 같은3회 사격 화살 | 941→938 | 941→938 | 941→938 |
| 레벨1 공격 음식 섭취 | 기본 동작/HUD 확인 | Condition1.0→**2.0** | **1.2** 복귀 |
| 레벨1 방어 음식 섭취 | — | Condition0→**24** | **4** 복귀 |
| 음식 시간 | 원본190/80초 | 유지·감소 | 유지·감소 |
| 별도 지구력 코드 | 유지 | `4040201e` | 유지 |

GDB 관찰은 매 실행 main mapping+기계어를 대조하고 이름이 Player인 상주 액터를 찾는다. Condition getter `0x4BFF14/0x19527E0`는 actor+0x228→component+0x1A8이다. component+0x158의 플레이어 상태에서 공격 float+0x98·방어 float+0x9C를 읽었다. 각각 getter `0x1B3E558`·`0x1B3E5A0`의 load 경로와 대조했다. 값은 해당1.4.3에만 유효하다. 메모리 쓰기·브레이크포인트는 사용하지 않았다.

관찰/재현 도구:

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/audit_t10_cheats.py
# 게임·임시 GDB가 준비된 상태의 읽기 전용 관찰:
.\.venv-gamepad\Scripts\python.exe scripts/t10_runtime_probe.py 새-시험-이름
.\.venv-gamepad\Scripts\python.exe scripts/flight_control_trial.py 새-활-시험 --steps-file scripts/trials/t10_bow.json
```

실행·기준 세이브 복구·GDB 설정은 [모딩 안내](TOTK_MODDING_GUIDE.md)의9절을 따른다. 메뉴 조작 `t10_ui.py`는 관찰한 시작 탭을 `--from-tab`으로 명시해야 한다. `--world`는 월드에서+메뉴를 여는 경우에만 쓴다. 메뉴를 시간만으로 추정하지 말고 캡처를 확인한다. 시험 이름을 바꿔 기존 증거를 덮어쓰지 않는다. `t10_eat_attack.json`은 기준 음식 목록의 첫 셀에서 시작할 때만 유효하다.

증거는 `artifacts/t10-bow-off/on/restored.mp4`, `t10-meal-attack-on/restored.mp4`, `t10-meal-defense-on/restored.mp4`와 동명 입력 JSON, `private/analysis/t10-*-save`, `t10-*-ui.json`, `t10-on/restored-*.json`이다. 개별 파일의 정확한 이름과 SHA는 최종 `private/analysis/t10-verification.json`에 기록한다.

## 실패·검증 범위

- 벽을 향한 근접 공격은 소모 대조군이 성립하지 않았다. 선풍기는 벼랑 쪽으로 떨어져 타격을 입증하지 못했다. 짧은 방패 서핑도 해제 상태에서 Life90을 유지했다. 이 세 시험은 내구도 성공 증거가 아니다.
- 첫 `t10-flight-on`은 방패 시험 뒤 시작 위치에서 전개 직후 지형에 재접촉했다. 초기 상승 구간은 실패이며 마지막 재전개 후 호버만 관찰됐다. `t10-flight-final`은 로딩 중 준비 상태 검사에서 비행 입력 없이 중단됐다. 기준 좌표·접지·중력·카메라를 연속3회 확인하는 `wait_t10_world.py`를 추가하고, 새 기준 세이브에서 전개 직후 ZL+전진으로 벼랑을 벗어나게 수정했다.
- 실제 전투 피해량을 적 HP로 측정한 시험은 아니다. 음식 섭취 후 엔진의 공격/방어 상태 float를 직접 읽은 결과다. 모든 적·무기·융합·특수 파괴 경로를 검증한 것은 아니다.
- 기존 비행의 외력 오차·하강 속도 차이·물/피격/등반/다른 지역 미검증·근접 카메라/지형 간섭 한계는 유지한다.

시험 중 수동 저장·음식·화살·장비 선택 변경은 비교 증거로 따로 보관하고 최종 세이브는 원래 사용자 벼랑35파일로 복구한다. 최종 상태와 합격한 통합 비행·종료 검사는 `TASKS.md`, `SESSION_HANDOFF.md`, `t10-verification.json`을 기준으로 확인한다. 게임·키·세이브·추출/생성 pack은 비공개 로컬 파일로 유지한다.

## 최종 통합·종료 결과

`scripts/verify_t10.py` 통과. 최종 비행은 `t10-flight-verified`의220좌표이며, 독립 상승 구간 변위11.196m, 마지막10샘플 호버 XYZ 범위0.00505m다. B 해제 후 공중 중력1·X 재전개 후 중력0을 확인했다. 영상·최종 화면은 `artifacts/t10-flight-verified.mp4/.json`, `t10-flight-verified-hover.png`다. 이 값은 벽시계·GDB 관찰 조건이며 기존 게임 시간 기준 속도 정확도 한계를 제거하지 않는다.

최종 설치는 내구도·식사 모두 on, 기존 날개·지구력 유지다. 같은 해시의 설치본을 `private/baselines/t10-verified/installed-wing`, `installed-equipment`에 보관하고 manifest를 대조했다. 음식·화살·장비 선택 등 시험 진행분은 남기지 않고 사용자 벼랑35파일을 복원했다. Eden·패드 종료, 임시58437 포트 종료, GDB false/6543/default true, 속도100%를 확인했다. 원본2373개 메타데이터·설정/세이브156개 SHA-256은 불변이다.

```powershell
# 최종 설치·기존 증거·종료 상태를 재검사한다. 새 게임 시험을 자동 실행하지 않는다.
.\.venv-tkvsc\Scripts\python.exe scripts/verify_t10.py
```
