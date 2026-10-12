# 공식 근거와 확인 범위

확인일: 2026-09-06. 원문을 복사한 매뉴얼이 아니라 작업 절차를 설계할 때 확인한 공식 자료다. 현장에서는 실제 패치 버전과 배포판에 맞춰 다시 확인한다.

| 공식 자료 | 연결되는 판단 |
|---|---|
| [Codex Build skills](https://learn.chatgpt.com/docs/build-skills) | SKILL.md, `.agents/skills`, `/skills`·명시 호출 |
| [Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | 프로젝트 지침 위치와 적용 |
| [MySQL 8.0 Online DDL](https://dev.mysql.com/doc/refman/8.0/en/innodb-online-ddl-operations.html) | DDL 알고리즘의 작업·버전 조건 |
| [MySQL 8.4 EXPLAIN](https://dev.mysql.com/doc/refman/8.4/en/explain.html) | 실행 계획과 실제 실행의 구분 |
| [MySQL 8.0 implicit commit](https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html) | DDL과 사용자 rollback |
| [MySQL 8.0 CHECK](https://dev.mysql.com/doc/refman/8.0/en/create-table-check-constraints.html) | CHECK 강제 동작과 조건 |
| [MySQL 8.4 deadlock handling](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks-handling.html) | 잠금 순서·짧은 트랜잭션·재시도 |
| [MySQL 8.4 PITR](https://dev.mysql.com/doc/refman/8.4/en/point-in-time-recovery.html) | 기준 백업과 binlog 기반 복구 |
| [MySQL 8.4 partition keys](https://dev.mysql.com/doc/refman/8.4/en/partitioning-limitations-partitioning-keys-unique-keys.html) | 파티션 키·PK·유일키 제약 |

스킬의 팀 프로필 규약, 결과 양식, 사례와 도입 절차는 이 묶음에서 제안한 운영 방식이며 Codex 내장 기능이나 MySQL의 의무 규칙이 아니다.
