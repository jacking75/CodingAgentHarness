# T06 기계식 날개

이 문서는 T06 당시 모델의 기록이다. 2026-10-16 참고 이미지 기반 외형 개선 이후 현재 모델·재질·검증·설치 방법은 [WING_REFERENCE_REFINEMENT.md](WING_REFERENCE_REFINEMENT.md)를 따른다.

사용자 선택은 기계식 날개다. 초기 등 부착안은 사용자가 거절했고, 최종본은 **기존 패러세일 위치·Weapon_R 소켓·손잡이**를 사용한다. 손을 든 기존 플레이어 자세와 맞추기 위해 손잡이와 지지대 메시를 유지했다. 천과 문양 메시 위에 날개를 덧씌운 것이 아니라 천 메시를 좌우 기계식 패널로 교체하고 문양 메시의 삼각형을 비활성화했다.

## 자산 연결과 출처

- `Parasail.pack.zs`의 ModelInfo → `Item_Parasail.Item_Parasail.bfres.mc`. 원래 31본 스켈레톤의 `Tail_1_L/R`을 좌우 힌지로 사용한다. 원본 손잡이는 `Skl_Root`의 rigid matrix22를 그대로 사용한다.
- ModelBindParam의 `RotTrans / Weapon_R`은 원본 바이트 그대로다. 날개 힌지는 모델 좌표 `(±0.3,0.7,0)`에 두고 전체 폭은 약4.78m다. 같은 메시를 좌우 반사해 생성하며 정점 수·LOD 인덱스 할당을 넘지 않는다.
- `Item_Parasail.anim.bfres.zs` → 원본 애니메이션 컨테이너에 생성한 7개 클립. `WingOpen`18프레임, `WingRise/Glide/Left/Right`60프레임. `Float/Event_Pose` 호환 클립을 유지한다.
- `AS/Parasail.root.asb.zs`의 `Open` → 순차 전개 → 상승 bool 분기 → 좌우 bank float 분기 → 중립 활공. 입력은 Parasail AI의 Index0 쿼리로 AS Blackboard `WingRise/WingBank`에 전달한다. AI8노드, AS9노드다. `Pose`도 유효한 클립을 가리킨다.
- 천 시뮬레이션·천 반응 경로를 제거해 기계식 패널 본과 충돌하지 않게 했다. 전개 수명·B 해제·접지 제거는 원래 패러세일 액터 수명을 사용한다. 해제·착지는 별도 접힘 클립 없이 날개 제거와 원래 플레이어 동작으로 표현한다.
- 검증된 Player.pack 전체는 T05와 바이트가 같다. 56노드 비행 액션·20노드 스케줄러·Index0·τ0.3초를 유지한다. Parasail AS/AI, 모델/애니메이션, 필요한 RESTBL만 추가 변경한다.

모델 컨테이너·재질·손잡이·스켈레톤 이름은 사용자의 소유 게임 TotK1.4.3에서 로컬 추출했다. Nintendo 독점 자산이며 재배포 라이선스가 없다. 추출물과 생성된 BFRES/팩은 `private/`와 `runtime/`에만 보관한다. 날개 패널 형상·힌지 애니메이션은 이번 작업의 절차적 생성 코드로 만들었으며 외부 모델을 내려받지 않았다.

도구 출처와 고정 리비전:

| 도구 | 소스·라이선스 | 리비전 |
|---|---|---|
| totk-meshcodec | [UltimateBomb/totk-meshcodec](https://github.com/UltimateBomb/totk-meshcodec), MIT | `032c41d18cb8399c7c01c04f0ab140689327431c` |
| BfresLibrary | [KillzXGaming/BfresLibrary](https://github.com/KillzXGaming/BfresLibrary), MIT | `31c1a0cb9f7607f8d69bbc445eacace542c2cbad` |
| MeshCodec | [dt-12345/MeshCodec](https://github.com/dt-12345/MeshCodec), GPL-2.0 및 내장 의존성 라이선스 | `b3600954872dbc2893a1bcc9e851c1e364f303ab` |

기존 TKVSC의 ASB/AINB/BYML/RESTBL/Zstd 래퍼를 재사용한다. 설치된 도구의 LICENSE 파일을 보존했다. 입력 자산 SHA-256은 `private/analysis/t06-asset-provenance.json`에 있다. `.mc` 재압축 사양의 출처는 위 totk-meshcodec 저장소의 FORMAT 문서이며 게임 실증과 별도 디코더 대조로 이번 출력도 검사했다.

## 빌드와 검증

Eden과 가상 패드를 종료한 상태에서 실행한다. 모델·Shader 디렉터리는 이번 세션에서 원본 복사 NCA+1.4.3 업데이트로 추출했다. 이미 있는 자료를 다시 추출하지 않는다.

```powershell
.\.venv-tkvsc\Scripts\python.exe scripts/prepare_wing_assets.py
.\.venv-tkvsc\Scripts\python.exe scripts/build_wings.py --install
.\.venv-tkvsc\Scripts\python.exe scripts/verify_wings.py
```

빌더는 .NET9 `scripts/WingModel`을 빌드하고 원본 BFRES의 정점·인덱스·본·역행렬·컬링 범위만 변경한다. 모델 전체를 라이브러리로 다시 저장하지 않아 게임 전용 재질 레이아웃을 보존한다. 애니메이션 컨테이너는 BfresLibrary로 저장한다. 원본 외부 문자열 사전이 반드시 필요하다.

빌드 출력은 `private/build/t06-mechanical`, 설치 위치는 기존 실험 모드 폴더다. 기반 빌드는 `private/baselines/t05-lifecycle-verified/installed-mod`다. T06을 유지할 때는 `build_wings.py`를 사용한다. `build_flight.py --install` 단독 실행은 날개 파일을 제거하는 롤백이 아니다. 깨끗한 설치·비활성화·복구 절차의 통합 검증은 T07 범위다.

검증 자료:

- `artifacts/t06-overhead.mp4/.json`: 전개, 상승, 좌우 기울기, 카메라 회전, B 해제, X 재전개. `t06-overhead-contact.png`는 1초 간격 영상 검토용이다. 입력 시각과 영상 시각은 기존 캡처 도구의 추정 차이가 있으므로 정밀 판단에는 내부 HoldMask·좌표 기록을 함께 사용한다.
- `t06-overhead-land`: 10초 하강 뒤에도 공중이었다. 착지 성공 근거에 넣지 않는다.
- `t06-overhead-land-low`: 이어서 Y303→249 하강, 접지 뒤 중력1 복원·날개 제거. 접지 후 R을 오래 유지해 원래 투척 동작이 발생했으며 저장은 하지 않았다.
- `t06-overhead-ground`: B로 자세 정리, 지상 이동 범위2.847m, 점프 Y249.188→249.864→249.188 및 재접지. 0.1초 샘플에서 수직속도 ±4.833m/s를 관찰했다. 초기 점프 충격 최고속도를 측정했다고 주장하지 않는다.
- `private/analysis/t06-wing-verification.json`: 실제 설치 파일의 SHA, Player.pack 보존, 독립 NullCodec 역압축 바이트 일치, 입력·좌표·중력·지구력 보존 명령 검사.
- 최종 시험은 모두 날개 관련 6개 파일의 실제 SHA를 원시 위치 기록에 포함한다. 빌드 보고의 기본 `unverified` 문자열보다 해시가 일치하는 이 검증 기록을 기준으로 한다.

## 확인한 한계와 기각한 시도

- 초기 `t06-first`는 Spine_2 축 불일치로 세로 날개였다. `t06-second`는 등 부착 회전을 고쳤지만 사용자 요청으로 기각했다. 둘 다 최종 외형 성공 근거가 아니다.
- 원본 MeshCodec 배포 실행 파일은 생성한 NullCodec 파일을 읽을 때 접근 위반으로 종료했다. 소스 `NullCodec::Decompress`가 남은 크기와0x40000 중 **max**를 복사하는 미검증 구현이다. 생성 파일은 게임에서 읽혔고 별도 Python 디코더로 전체139264바이트가 생성 원본과 일치했다. 해당 실행 파일의 실패를 정상 왕복검사로 보고하지 않는다.
- 날개는 표현용이다. 폭에 맞는 별도 충돌체는 추가하지 않았다. 좁은 벽·급경사에서는 패널이 지형에 들어갈 수 있고, 카메라가 벽에 밀려 캐릭터에 가까워지면 화면 일부를 가릴 수 있다. 고정 벼랑에서 이 상황을 확인했고 탁 트인 공중·회전 시점에서는 손잡이와 날개가 정상 표시됐다.
- 물·피격·벽타기·다른 지역은 T06에서 시험하지 않았다. 기존 T04/T05 제어 한계도 유지한다.
