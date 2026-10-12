# MySQL 8 · Codex CLI DA 스킬 묶음

버전: **0.1.0 파일럿** · 작성: 2026-09-06 · 문서 언어: 한국어

개발팀이 DB 설계·코드 변경을 스스로 1차 검토하고 DA팀이 중요한 판단과 공통 기준 개선에 집중하도록 만든 12개 스킬이다. MySQL 8.0.x와 8.4.x의 InnoDB를 중심으로 하며 정확한 패치 버전은 팀별로 지정한다. MySQL 호환 배포판은 별도 검증이 필요하다.

모든 배포 파일은 Markdown이다. SKILL.md의 YAML frontmatter는 Markdown 안에 포함된다. 별도 서비스·MCP·API 키·자동 DB 실행기가 없으며 Codex CLI가 필요할 때 지침을 읽는다. 설치만으로 DB에 연결되거나 권한이 생기지 않는다.

## 가장 빠른 시작

1. [설치 안내](docs/installation.md)에 따라 필요한 스킬 폴더를 프로젝트 `.agents/skills`에 복사한다. 처음에는 schema-review, query-tuning, transaction-review를 추천한다.
2. [팀별 적용 안내](docs/team-customization.md)를 읽고 템플릿 네 개를 프로젝트 `docs/db`에 복사한다. 우선 team-profile.md의 버전·경로·권한을 채운다.
3. Codex CLI에서 `/skills`로 확인하고 `$mysql8-schema-review`처럼 이름으로 호출한다.
4. [사용 시점과 예시](docs/usage-guide.md)의 실제 파일 경로를 바꿔 실행한다. 처음에는 DB 연결 없이 파일만 검토한다.
5. [피드백 양식](templates/feedback.md)에 잘못된 지적과 놓친 문제를 기록하고 [개선 절차](docs/feedback-and-release.md)를 따른다.

## 문서 안내

| 문서 | 대상과 용도 |
|---|---|
| [설치·업데이트·제거](docs/installation.md) | 개발팀 설치 담당자 |
| [전체 스킬 사용 안내](docs/usage-guide.md) | 어떤 스킬을 언제 호출할지 선택 |
| [팀별 커스터마이징](docs/team-customization.md) | 프로젝트별 기준을 공통 스킬과 분리 |
| [작업 권한과 검증](docs/execution-and-evidence.md) | 파일 검토·DB 실행·운영 변경 구분 |
| [MySQL 버전 주의점](docs/mysql-compatibility.md) | 8.0과 8.4에서 확인할 조건 |
| [평가 절차](evaluation/README.md) | DA팀의 정확도·효율 검증 |
| [평가자용 기준](evaluation/reviewer-rubric.md) | 연습 사례별 기대 행동 |
| [검증 기록](docs/validation.md) | 이 배포에서 실제 확인한 범위 |
| [공식 근거](docs/sources.md) | Codex·MySQL 원문 |
| 변경 이력 | 현재 별도 변경 이력을 제공하지 않음 |

## 구조

```text
mysql8-codex-skills/
  README.md
  skills/mysql8-*/SKILL.md
  skills/mysql8-*/references/example.md
  docs/                     # 사용·배포 가이드
  templates/                # 팀별 설정 및 결과·피드백 양식
  evaluation/               # 평가자용 절차와 기준
```

각 스킬은 개별 복사해도 동작한다. 핵심 실행·프로필 규약은 독립 배포를 위해 각 스킬에 짧게 포함되어 있으며 규약을 바꿀 때 전 스킬의 일관성을 함께 확인한다. 스킬끼리 자동 호출하거나 별도 에이전트를 생성하지 않는다. 사례의 가상 값은 회사 표준이 아니다.
