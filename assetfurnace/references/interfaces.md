# 현재 설치본의 에이전트 인터페이스

확인: 2026-10-14, AssetFurnace v0.4.3 (`/Users/heungbae/DevAI/runtimes/image-to-3dlab`). 이 버전에는 이미지→3D 생성용 전용 MCP 서버가 없으며, 기존 HTTP API와 CLI로 조작할 수 있다. Blender MCP와 연동하는 일부 스크립트는 별개다. 새 MCP 설정 없이 이 스킬의 Python 도구를 사용한다.

## 로컬 HTTP API

서버는 `http://127.0.0.1:8777`이다. 구현을 확인할 때는 설치본의 `viewer/generate_api.py`를 읽는다.

| 작업 | 인터페이스 |
|---|---|
| 설치 모델 상태 | `GET /api/catalog`, `GET /api/setup?backend=pixal3d` |
| backend 설정·기본값 | `GET /api/backends` |
| 사진→3D 제출 | `POST /api/generate`, multipart `image`와 JSON 문자열 `settings` |
| 진행 확인 | `GET /api/generate/{job_id}/status` 또는 `/events`(SSE) |
| 결과 | `GET /api/generate/{job_id}/result.glb`, `/manifest.json` |
| 명시적 취소 | `POST /api/generate/{job_id}/cancel` |
| Library·활동·연속 실행 상태 | `GET /api/assets`, `/api/activity`, `/api/chains` |
| 후처리 조건 | `GET /api/finish/capabilities` |

`settings` 예: `{"backend":"pixal3d","res":1024,"seed":42,"steps":"auto","output_name":"crate"}`. 이 버전의 HTTP API에서 steps는 `"auto"` 또는 `12`다. CLI의 `--steps 8`과 구분한다. 반환된 job ID를 저장하며 HTTP 202만으로 생성 완료라고 보고하지 않는다.

HTTP 상태는 `queued/running/cancelling/done/error/cancelled`이며 `last_event`에는 진행·오류 정보가 포함된다. 서버가 중지되면 메모리 job 조회 정보가 사라질 수 있지만 출력 파일은 남을 수 있다. 서버를 재시작하거나 중복 생성하기 전에 receipt의 `output_dir`와 출력 파일을 확인한다.

## 직접 CLI가 필요한 경우

스튜디오가 실행 중이면 HTTP를 우선 사용하여 작업 큐와 충돌 방지를 유지한다. 직접 CLI는 서버의 작업 큐를 거치지 않으므로 별도 GPU 작업과 겹치지 않는지 확인한다. 직접 생성은 사용자가 요청한 범위에서만 실행한다.

```sh
cd /Users/heungbae/DevAI/runtimes/image-to-3dlab
U2NET_HOME=/Users/heungbae/DevAI/cache/assetfurnace/rembg \
  .venv/bin/python scripts/pixal3d_generate.py /absolute/input.png \
  output/my-run/my-run.glb --steps 8 --seed 42
```

원본 사진에 배경 제거 결과가 추가로 저장될 수 있으므로 입력을 작업 폴더로 복사한 뒤 직접 CLI에 전달한다. CLI 결과는 동명의 `.json`에 SHA-256·설정·라이선스를 기록한다. `output/<run>/<run>.glb` 형식으로 저장하면 Library가 발견할 수 있다. 원본 경로가 아닌 별도 프로젝트에 GLB만 복사하면 `.svviews` 카메라 자료가 없어 Pixel Match 등 후처리에 필요한 정보가 빠질 수 있다. 단순 가져오기에는 GLB·JSON을 함께 보존하고, 후처리·재현이 필요하면 원래 run 폴더도 보존한다.

## 선택 기능

이 스킬을 만든다는 이유로 추가 설치하지 않는다. 현재 카탈로그와 capabilities가 실제 상태의 기준이다.

- **Finish / 저폴리곤·Pixel Match**: Blender 4.2 이상 필요. `viewer/finish_api.py`와 `scripts/retopo_repaint.py --help`에서 옵션을 확인한다. 설치 당시 Blender는 없었으므로 현재 상태를 재확인한다. Blender가 없으면 생성된 원본 GLB까지만 제공한다.
- **자동 리깅·애니메이션**: `autorig` 모델(SkinTokens)과 해당 도구 준비 필요. `viewer/autorig_api.py`, `viewer/rig_api.py`, `GET /api/animate/models`를 참고한다. 생성 성공을 리깅 성공으로 해석하지 않는다.
- **문장→참고 이미지→3D**: AssetFurnace의 Qwen-Image 모델 별도 준비 필요. `viewer/image_api.py`를 참고한다. DevAI에 이름이 비슷한 모델이 있다고 AssetFurnace의 가중치가 준비된 것으로 간주하지 않는다. 다른 이미지 도구를 사용자가 지정했다면 그 결과 파일을 참조 이미지로 받는다.
- **다른 3D backend**: `viewer/backend_catalog.py`에 경로·용량·조건이 있다. 준비 상태, 사용자 선택, 지역·배포 조건을 확인한 경로만 사용한다.

## 스킬 등록 위치

공통 원본은 `/Users/heungbae/DevAI/skills/assetfurnace`다. 두 CLI의 개인 스킬 폴더에서 이 원본을 참조한다. Codex는 `$assetfurnace`, Claude Code는 `/assetfurnace`로 명시적으로 호출하거나 관련 요청으로 자동 선택할 수 있다.

- Codex CLI: `~/.agents/skills/assetfurnace` (공식 사용자 스킬 위치)
- Claude Code: `~/.claude/skills/assetfurnace`

공식 문서: [OpenAI local skills](https://learn.chatgpt.com/docs/build-skills), [Claude Code skills](https://code.claude.com/docs/en/skills). 클라이언트의 sandbox·파일 접근 설정은 스킬이 변경하지 않는다. 다른 프로젝트에서 DevAI 접근이 제한되면 세션에 `/Users/heungbae/DevAI` 접근 권한을 추가한다. 전역적인 권한 우회 옵션을 사용하지 않는다.
