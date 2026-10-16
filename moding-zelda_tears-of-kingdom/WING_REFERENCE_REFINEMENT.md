# 참고 이미지 기반 날개 외형 개선

2026-10-16 사용자 요청으로 T08보다 먼저 진행한 외형 수정이다. T06/T07의 직육면체 패널 대신 좌우 각각 8장의 얇은 금속색 깃판, 분절 프레임, 원형 힌지, 피스톤과 주황색 포인트를 적용했다. 바깥쪽 깃판을 짧게 줄여 날개 끝이 좁아지는 외곽선을 만들었다. 전체 폭은 약4.93m다.

기존 패러세일 장착 위치·손잡이를 유지한다. 주황색은 색상 포인트이며 별도 발광 셰이더·블룸은 구현하지 않았다. 참고 이미지의 사실적 렌더링을 그대로 재현한 모델은 아니다. 원래 손잡이의 목재 외형, 지형·근접 카메라 간섭도 남는다.

## 구현과 변경 범위

- `scripts/WingModel/Mechanical.cs`: 각 깃판은 두께0.036m의 오각형 판이다. 원형 프레임·힌지는 LOD별8/5각 단면으로 생성한다. LOD0 1,304정점/800삼각형, LOD1 896정점/560삼각형이다. 각 LOD가 다음 LOD의 정점 영역을 침범하지 않도록 상한 검사도 추가했다.
- `scripts/refined_wing_textures.py`: 금속색 깃판, 어두운 프레임, 황동 관절, 주황색 스트립을 코드로 생성한다. 깃판에는 이음선·리벳·약한 브러시 무늬를 넣었다. 외부 모델·이미지 텍스처를 다운로드하지 않았다.
- 전용 `Wing_Mechanical_V01__Alb/Nrm/Spm.txtg`는 각각 원본과 같은 BC1/BC5/BC4 압축을 사용한다. 원본 TXTG 헤더를 사용하므로 생성 결과도 비공개 로컬 자산이다.
- 패러세일의 천 선택 로직이 새 텍스처를 기존 천 무늬로 덮어쓰는 문제를 확인했다. 재질 인덱스와 셰이더는 유지하면서 이름을 `Mt_Fabric`에서 `Mt_Metals`로 분리했다. 재질 문자열 길이·원본 BFRES 레이아웃을 보존한다.
- T07 대비 모델·RESTBL·보고서가 바뀌고 TXTG3파일이 추가된다. **Player.pack, Parasail.pack, AS, 애니메이션, 문양 제거 모델은 T07과 바이트가 같다.** Index0·56노드 액션·20노드 접지 스케줄러·τ0.3초는 유지한다.

## 재현

복사본 Eden과 가상 패드를 종료한 상태에서 빌드한다. 세 텍스처 템플릿은 `private/analysis/wing-texture-input`에 준비돼 있다. 재추출하지 않아도 된다.

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/build_wings.py
.\.venv-tkvsc\Scripts\python.exe scripts/manage_flight_install.py install --revision refined
.\.venv-tkvsc\Scripts\python.exe scripts/verify_refined_wings.py
```

설치 명령은 `private/baselines/wing-refined-verified/manifest.json`과 파일 전체를 대조한다. 수정 후 해시가 달라진 빌드는 기존 검증본으로 설치되지 않는다. `build_wings.py --install`은 개발 시험용 직접 설치이며 기존 manifest 검증을 대신하지 않는다.

비활성화·활성화·직전 설치 복구도 `--revision refined`를 지정한다. 기본값은 과거 T06이며 새12파일 설치를 거절하는 것이 정상이다.

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/manage_flight_install.py disable --revision refined
.\.venv-tkvsc\Scripts\python.exe scripts/manage_flight_install.py enable --revision refined
.\.venv-tkvsc\Scripts\python.exe scripts/manage_flight_install.py rollback --revision refined
```

`rollback`은 해당 설치 트랜잭션 직전 버전을 복원한다. 과거 T07 모델 자체는 `private/baselines/t07-integrated-verified/installed-mod`에 별도로 보존돼 있다. 새 모드 폴더에 T07 파일을 단순히 덮어쓰면 추가 TXTG가 남으므로 원복 시에는 폴더 전체를 교체해야 한다.

실행 준비와 종료 복구는 `T07_INSTALL_AND_VERIFY.md`를 따른다. 시각 시험 명령은 다음과 같다.

```powershell
.\.venv-gamepad\Scripts\python.exe scripts/flight_control_trial.py wing-refine-v5 --adaptive-takeoff --takeoff-clearance 9 --steps-file scripts/trials/wing_refined_visual.json --probe-position --sample-interval 0.1
```

## 시험 기록

- `wing-refine-v1`: 형상은 동작했지만 천 재질이 남아 금속 표현이 부족했다.
- `wing-refine-v2`: RGBA8 시험과 잘못된 TXTG 채널 선택이 포함된 기각본이다.
- `wing-refine-v3`: 원본 압축 계열로 복귀했지만 게임의 천 재질 덮어쓰기가 남았다. 위쪽 카메라 입력도 반대 방향이어서 수정했다.
- `wing-refine-v4`: 재질 이름 분리로 금속색·황동·주황색이 표시됐다. 위쪽 시점에서 날개 끝이 넓고 표면 줄무늬가 강해 최종본에서 조정했다.
- 최종 근거는 `private/analysis/wing-refined-verification.json`과 해시가 일치하는 `wing-refine-v5` 영상·좌표 기록이다. 이전 영상은 최종 외형의 검증 근거가 아니다.

최종 검사 통과: 좌표356개, 마지막10샘플 호버 XYZ 범위0.01452m, 모델139264바이트 독립 역압축 일치, 설치 전체12파일 해시 일치. 설치·비활성화·활성화도 확인했다. 화면은 `artifacts/wing-refined-final.png`와 `wing-refined-top.png`다. 종료 검사 `private/analysis/wing-refined-shutdown.json`에서 Eden·패드 종료, GDB·속도 복원, 세이브35파일 일치, 원본2373개 메타데이터·156개 해시 불변을 확인했다.

NSTool1.9.2의 Windows 단일 파일 추출은 출력 경로 오류로 실패했다. `prepare_refined_textures.py`는 TexToGo 디렉터리를 순서대로 읽다가 세 템플릿이 확보되면 종료하고 이번에 생성한 불필요한 중간 파일만 정리한다. 게임 전체 재추출은 하지 않는다. 텍스처 템플릿이 이미 있으면 추출을 생략한다.

검증 범위는 고정 벼랑에서 전개·상승·좌우 기울기·해제·재전개·호버와 시각 확인이다. 새 모델로 착지·물·피격·등반·다른 지역을 다시 인증하지 않는다. 과거 T07 착지 검증과 제어 코드의 동일성은 별도 사실이다.
