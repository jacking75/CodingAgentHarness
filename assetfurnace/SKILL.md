---
name: assetfurnace
description: Operate the local AssetFurnace studio to turn a reference image into a textured 3D GLB with the installed Pixal3D model, track generation jobs, and verify results. Use for AssetFurnace or image-to-3dlab tasks, not generic image generation.
---

# AssetFurnace 로컬 3D

이 컴퓨터의 AssetFurnace를 기존 CLI·HTTP API로 다룬다. Claude Code와 Codex CLI에서 같은 스킬을 사용한다. 입력 사진에서 **텍스처 GLB**를 만드는 현재 준비된 경로는 `pixal3d` single-view Q8_0다. `http://127.0.0.1:8777`을 사용하며 DevAI 통합 API의 모델 ID와 혼동하지 않는다.

## 실행 도구

추가 Python 패키지가 필요 없는 JSON CLI:

```sh
python3 /Users/heungbae/DevAI/skills/assetfurnace/scripts/assetfurnace.py --help
```

설치 위치가 달라졌다면 스킬과 함께 이동한 `scripts/assetfurnace.py`를 사용한다. 도구는 스킬의 실제 파일 위치에서 DevAI 루트를 찾는다.

## 작업 순서

1. `status`로 현재 준비 상태를 확인한다. 연결이 거부되면 `start`를 실행하고 다시 확인한다. 조회만 요청받았다면 시작할 필요가 없으며, 서비스가 꺼져 있다고 보고해도 된다.
2. **사용자가 준 사진**을 입력으로 쓴다. 전체 물체가 보이는 사진, 특히 투명 배경 PNG가 적합하다. 입력이 없으면 필요한 사진을 요청한다. 텍스트만 주어졌다고 미설치 Qwen-Image를 자동 설치하거나 다른 생성 서비스로 전송하지 않는다.
3. 생성 요청이 있으면 작업 폴더 안의 새 receipt 파일을 정해 `generate`를 한 번 호출한다. 기본 `--steps auto`는 이 맥의 패치된 빌드에서 8단계다. HTTP API는 숫자 8을 받지 않으므로 `--steps 8`로 바꾸지 않는다. `12`는 더 많은 단계를 원하는 경우 사용한다. 단일 사진 해상도는 1024만 지원한다.
4. 반환된 receipt로 `job` 또는 `wait`를 호출한다. `wait`는 한 번에 최대 55초, 기본 45초다. 종료 코드 **3은 아직 실행 중**, **2는 실패/취소**이며 성공이 아니다. 진행 중에는 상태를 알리고 **같은 작업을 다시 제출하지 않는다**. receipt가 있으면 중단된 에이전트 세션에서도 같은 job 조회를 이어간다.
5. `done`이 되면 `fetch --glb`로 사용자 프로젝트의 새 경로에 GLB·동명 JSON을 저장한다. 이 명령은 GLB 구조·텍스처 존재·provenance SHA-256을 검사한다. 이미 로컬에 있는 결과는 `verify`로 검사한다. 파일 검사와 시각적 품질 확인을 구분하고, 가능하면 스튜디오의 Open GLB 또는 사용 가능한 뷰어로 확인한다.
6. 실제 backend·seed·설정, 결과 GLB와 JSON 위치, 검증 결과를 보고한다. 게임 프로젝트에 넣는 요청이면 해당 프로젝트의 에셋 규칙·스케일·재질·폴리곤 예산도 확인한다.

```sh
python3 /Users/heungbae/DevAI/skills/assetfurnace/scripts/assetfurnace.py status
python3 /Users/heungbae/DevAI/skills/assetfurnace/scripts/assetfurnace.py start
python3 /Users/heungbae/DevAI/skills/assetfurnace/scripts/assetfurnace.py generate \
  --image /absolute/reference.png --receipt work/assetfurnace-job.json --seed 42
python3 /Users/heungbae/DevAI/skills/assetfurnace/scripts/assetfurnace.py wait \
  --receipt work/assetfurnace-job.json --timeout 45
python3 /Users/heungbae/DevAI/skills/assetfurnace/scripts/assetfurnace.py fetch \
  --receipt work/assetfurnace-job.json --glb /absolute/project/assets/model.glb
```

`generate`는 사용자 파일을 로컬 스튜디오에 업로드한다. 프로세스·큐·결과 보관은 스튜디오가 담당한다. receipt에는 job ID·입력 경로·설정·실행 의도가 기록된다. 기본 의도는 개인 확인용(`showcase/private`)이다. 게임용 결과라면 `--use-case game`, 배포 범위가 명시되었다면 `--distribution public` 또는 `worldwide`로 실제 의도를 기록한다. Pixal3D의 MIT 및 포함 DINOv3 조건을 지우거나 무조건적인 상업 이용 보장으로 바꾸지 않는다.

## 운영 시 지켜야 할 사항

- `state=ready`와 `/api/setup?backend=pixal3d`의 `ready`를 확인한 뒤 실행한다. 과거 설치 기록만으로 준비됐다고 판단하지 않는다. 서버의 HTTP 409는 다른 작업이 진행 중이라는 뜻이다. 기다리며 재조회하고 그 작업을 종료하지 않는다. DevAI와 GPU를 공유하므로 동시에 무거운 생성을 실행하지 않는다.
- 제출 중 연결이 끊기면 이미 서버에서 시작됐을 수 있다. 도구가 남긴 `submission_state=unknown` receipt를 보존하고 스튜디오의 Activity·Library와 출력 폴더를 확인한다. 확인 없이 새 receipt로 자동 재제출하지 않는다. 서버 재시작 후 job ID가 조회되지 않아도 원래 출력 폴더와 기록을 먼저 확인한다.
- `cancel --receipt ...`는 **사용자가 해당 작업 취소를 요청했을 때** 사용한다. 대기 시간 초과를 이유로 취소하거나 서버 종료·다른 작업 종료·모델 강제 해제를 하지 않는다. 취소 요청 후 `job`으로 실제 종료 상태를 확인한다.
- 스킬 사용은 모델 다운로드·삭제·업데이트 허가가 아니다. 새 모델은 backend·경로·크기를 알리고 사용자가 선택한 경우에만 준비한다. 이미 선택한 Pixal3D를 매번 재확인할 필요는 없다. 한국 사용 환경에서는 기존 저장소가 제외하는 Hunyuan 경로를 대안으로 자동 선택하지 않는다.
- 입력은 변경하지 않으며 결과 경로가 존재하면 새 경로를 선택한다. GLB와 provenance JSON을 함께 보존한다. 토큰·비밀번호를 출력하거나 스킬/receipt에 저장하지 않는다. 생성 결과를 외부에 업로드하거나 배포하려면 그 요청 범위에 따라 별도로 처리한다.

## 다른 기능과 설치 복구

기존 인터페이스, 후처리·리깅·텍스트 입력의 준비 조건을 확인할 때만 [기존 인터페이스](references/interfaces.md)를 읽는다. 현재 미설치 기능은 설치되어 있는 것처럼 실행하지 않는다.

이 맥의 Pixal3D는 `GGML_METAL_EMBED_LIBRARY=ON`으로 빌드되어 전체 Xcode 없이 동작한다. 복구를 요청받으면 `/Users/heungbae/DevAI/AssetFurnace_Pixal3D_준비.command`와 [실행 지침](/Users/heungbae/DevAI/에이전트_모델_선택_및_실행_지침.md)의 11절을 참고한다. 상위 기본 bootstrap의 Xcode 점검을 보고 곧바로 Xcode를 설치하지 않는다.
