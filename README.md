# CodingAgentHarness

`CodingAgentHarness`는 코딩 에이전트가 프로젝트 작업 중 읽고 참조할 수 있는 스킬, 에이전트 역할 문서, 구현 가이드를 모아 둔 GitHub Pages 저장소다. 이 저장소 자체는 실행 애플리케이션이 아니며, 각 자료는 필요한 프로젝트로 선택적으로 복사하거나 링크해 사용한다.

웹 카탈로그: [https://jacking75.github.io/CodingAgentHarness](https://jacking75.github.io/CodingAgentHarness)

## 시작하기

1. 아래 카탈로그에서 작업에 맞는 자료를 찾는다.
2. 대상 폴더의 `SKILL.md`, `CLAUDE.md`, 또는 `README.md`를 처음부터 읽는다.
3. 문서가 참조하는 하위 자료도 함께 복사한다. 예를 들어 스킬의 `references/`, `agents/` 폴더가 있다면 해당 폴더도 보존한다.
4. 대상 프로젝트의 기존 `AGENTS.md`와 충돌하는 지침이 있는지 확인한 뒤, 프로젝트 규칙을 우선해 적용한다.

에이전트가 이 저장소를 수정하거나 자료를 가져갈 때의 공통 규칙은 [AGNNTS.md](AGNNTS.md)에 정리되어 있다.

## 자료 카탈로그

| 경로 | 종류 | 용도 |
| --- | --- | --- |
| [`csharpier/`](csharpier/) | 스킬 | C# 코드 포맷팅과 CSharpier 설정·운영 |
| [`ms-agent-framework/`](ms-agent-framework/) | 통합 스킬 묶음 | Microsoft Agent Framework 기반 C# 에이전트, Provider, 워크플로, RAG, MCP/A2A 구현 패턴 |
| [`monogame/`](monogame/) | 역할 문서 | MonoGame 아키텍처, 그래픽, 입력, 물리, 오디오 등 역할별 작업 지침 |
| [`Nextjs_Threejs/`](Nextjs_Threejs/) | 참조 문서 | Next.js와 Three.js 작업 지침 |
| [`game-app-ui-image2-main/`](game-app-ui-image2-main/) | 스킬 묶음 | 이미지 생성 도구를 이용한 게임·앱 UI 목업 및 래스터 자산 제작 |
| [`mysql8-skills-main/`](mysql8-skills-main/) | 스킬 묶음 | MySQL 8 설계, 잠금, 쿼리, 마이그레이션, 백업·복구 검토 |
| [`apps-script-drive-file-scoped-storage.md`](apps-script-drive-file-scoped-storage.md) | 참조 문서 | Google Apps Script 기반 파일 범위 Drive 저장소 설계 |

각 폴더의 세부 적용 조건, 설치 방법, 제약 사항은 해당 폴더의 문서를 기준으로 한다.

## Google Cloud 작업

Google Cloud를 사용하는 프로젝트에서는 Google의 [google/skills](https://github.com/google/skills)에서 작업에 맞는 스킬을 선택해 사용한다. 구현·설정·배포·문제 해결에 착수하기 전에 해당 스킬의 `SKILL.md` 전체와 필요한 참조 문서를 읽고 적용한다.

설치가 필요한 경우 원본 저장소의 안내에 따라 다음 명령을 사용한다. 이 명령은 Node.js의 `npx`가 필요하며, 설치 과정에서 필요한 스킬, 대상 에이전트, 설치 범위(프로젝트 또는 전역)를 선택한다.

```powershell
npx skills add google/skills
```

최신 스킬 목록과 설치 방법은 [원본 README](https://github.com/google/skills#readme)를 기준으로 한다. 적용할 때는 대상 프로젝트의 기존 지침과 승인·검증 절차를 따른다.

## 사용 원칙

- 스킬은 설명과 요청이 명확히 일치할 때만 선택한다.
- `SKILL.md`가 있다면 실행 또는 구현 전에 전체 내용을 읽는다.
- 문서의 예시 값, 경로, API 키 이름은 그대로 운영 환경에 적용하지 않는다.
- DB 변경, 외부 서비스 호출, 파일 덮어쓰기처럼 상태를 바꾸는 작업은 대상 프로젝트의 승인·검증 절차를 따른다.
- 문서가 제시하는 검증 결과는 해당 문서의 작성 시점 증거일 뿐, 새 환경에서의 성공을 보장하지 않는다.

## 저장소 구조

```text
CodingAgentHarness/
├── README.md                         # 이 카탈로그
├── AGNNTS.md                         # 이 저장소를 다루는 에이전트 지침
├── csharpier/                        # CSharpier 스킬
├── ms-agent-framework/               # Microsoft Agent Framework 스킬
├── monogame/                         # MonoGame 역할별 지침
├── game-app-ui-image2-main/          # 게임·앱 UI 이미지 스킬
├── mysql8-skills-main/               # MySQL 8 스킬 묶음
└── *.md                              # 독립 참조 문서
```

## 라이선스

루트의 [LICENSE](LICENSE)는 이 저장소에 적용되는 라이선스다. 하위 자료에 별도 라이선스가 있으면 해당 라이선스와 원저작자 고지를 우선한다.
