# Microsoft Agent Framework 통합 스킬 묶음

이 폴더는 C#용 Microsoft Agent Framework 자료를 하나의 스킬 묶음으로 통합한 배포 단위다. 기본 에이전트 구현부터 Provider, 워크플로, RAG, Agent Skills, MCP, A2A 및 역할별 작업 지침까지 포함한다.

## 읽는 순서

1. [SKILL.md](SKILL.md)에서 기본 에이전트, 도구, 세션, 미들웨어 패턴을 확인한다.
2. 요청에 해당하는 세부 주제만 `references/`에서 추가로 읽는다.
3. 구현·리뷰·마이그레이션 같은 역할 중심 작업은 `agents/` 문서를 참고한다.

## 구성

| 경로 | 용도 |
| --- | --- |
| [SKILL.md](SKILL.md) | 기본 에이전트 구현의 진입점 |
| [references/providers.md](references/providers.md) | Provider별 패키지, 인증, 엔드포인트, 지원 기능 |
| [references/workflows.md](references/workflows.md) | 그래프 기반 워크플로와 멀티에이전트 오케스트레이션 |
| [references/rag.md](references/rag.md) | 검색 증강 생성과 대화 메모리 |
| [references/skills-mcp-a2a.md](references/skills-mcp-a2a.md) | Agent Skills, MCP, A2A |
| [references/operational-patterns.md](references/operational-patterns.md) | 로깅, 라이프사이클, DI, 프롬프트, 대화 이력 운영 패턴 |
| [agents/](agents/) | 구현, 리뷰, 마이그레이션, 워크플로, RAG, MCP/A2A 역할별 지침 |

## 설치와 사용

필요한 대상 프로젝트에 이 폴더 전체를 복사해 상대 링크가 유지되게 한다. Codex에서 사용하는 경우 `SKILL.md`를 스킬 탐색 경로에 두고, 필요한 `references/`와 `agents/` 폴더도 함께 둔다.

```text
<target-project>/.agents/skills/ms-agent-framework/
├── SKILL.md
├── references/
└── agents/
```

특정 도구의 전용 설정 파일을 그대로 복사하기보다, 해당 도구가 요구하는 스킬 탐색 경로와 설정 형식에 맞춰 이 폴더의 상대 경로를 연결한다.

## 범위와 주의 사항

- 이 문서의 패키지·API·Provider 예시는 작성 시점의 참고 자료다. 실제 적용 전에는 대상 SDK 버전과 공식 문서를 확인한다.
- API 키, 엔드포인트, 배포 이름은 코드에 하드코딩하지 않는다.
- 외부 검색, MCP 도구 실행, 데이터 변경처럼 부작용이 있는 작업은 대상 프로젝트의 권한과 검증 절차를 따른다.
- `references/`는 별도 스킬이 아니라 `ms-agent-framework`의 주제별 보충 문서다.
