# 스킬 선택과 사용 예시

스킬 이름을 Codex CLI 대화에서 명시해 호출한다. 예시의 파일 경로는 실제 프로젝트 경로로 바꾼다. 모든 스킬을 한 요청에 나열하지 말고 주된 업무 하나로 시작한다.

| 스킬 | 언제 필요한가 | 주요 결과 |
|---|---|---|
| [mysql8-schema-review](../skills/mysql8-schema-review/SKILL.md) | 기존 테이블 또는 변경 DDL을 코드 리뷰하거나 자료형·키·제약·문자열 정책의 문제를 찾을 때 | 스키마·DDL 리뷰 결과 |
| [mysql8-feature-design](../skills/mysql8-feature-design/SKILL.md) | 우편·인벤토리·길드·상점 같은 신규 기능의 테이블과 트랜잭션 구조를 설계할 때 | 신규 기능 DB 설계 결과 |
| [mysql8-query-tuning](../skills/mysql8-query-tuning/SKILL.md) | 느린 SQL, 실행 계획, 인덱스 후보 또는 페이지네이션을 분석할 때 | 쿼리·인덱스 개선 결과 |
| [mysql8-transaction-review](../skills/mysql8-transaction-review/SKILL.md) | 재화·보상·결제·거래의 동시성, 재시도, 중복 처리 문제를 검토할 때 | 트랜잭션·멱등성 리뷰 결과 |
| [mysql8-migration-plan](../skills/mysql8-migration-plan/SKILL.md) | 운영 테이블 변경, 대량 백필, 무중단 호환 전환을 준비할 때 | DDL 배포·마이그레이션 계획 결과 |
| [mysql8-lock-diagnosis](../skills/mysql8-lock-diagnosis/SKILL.md) | 데드락 로그나 잠금 대기로 거래·지급·업데이트가 지연될 때 | 데드락·락 대기 진단 결과 |
| [mysql8-data-access-review](../skills/mysql8-data-access-review/SKILL.md) | ORM·Repository·커넥션 풀·읽기 복제본 사용 코드를 검토할 때 | 서버 DB 접근 코드 리뷰 결과 |
| [mysql8-data-repair](../skills/mysql8-data-repair/SKILL.md) | 잘못 지급된 재화, 누락·중복 데이터, 상태 불일치를 조사하고 보정안을 만들 때 | 데이터 보정·대사 계획 결과 |
| [mysql8-capacity-design](../skills/mysql8-capacity-design/SKILL.md) | 데이터 증가, 샤드 키 선택, 파티션 전략, 확장 시점을 판단할 때 | 용량·샤딩·파티셔닝 설계 결과 |
| [mysql8-backup-recovery](../skills/mysql8-backup-recovery/SKILL.md) | 백업 정책, 시점 복구, 복원 훈련, 장애 후 복구 절차를 검토할 때 | 백업·복구 준비 검토 결과 |
| [mysql8-access-review](../skills/mysql8-access-review/SKILL.md) | 애플리케이션·운영·AI 도구 계정의 권한과 진단 자료 노출 범위를 검토할 때 | DB 권한·데이터 노출 리뷰 결과 |
| [mysql8-test-design](../skills/mysql8-test-design/SKILL.md) | DB 변경의 동시성·실패·재시도·성능 회귀를 재현하는 테스트가 필요할 때 | DB 정합성·회귀 테스트 설계 결과 |

## 스키마·DDL 리뷰

**준비할 자료:** 현재 SHOW CREATE TABLE 또는 스키마 파일, 변경 DDL, 관련 조회·쓰기 SQL. 규모·접근 패턴이 없으면 성능 판단은 제한한다.

```text
$mysql8-schema-review schema/wallet.sql을 검토해줘. balance는 유료 재화이며 정확한 정수다. 파일만 분석하고 DB에는 접속하지 마.
```

**받을 결과:** 지적 표와 수정 DDL 초안. 테이블만으로 확인할 수 없는 트랜잭션·서버 코드 검토 지점을 명시한다.

[DB 접속 없는 연습](../skills/mysql8-schema-review/references/example.md)

## 신규 기능 DB 설계

**준비할 자료:** 기능 시나리오, 엔터티 소유권, 핵심 불변식, 조회·쓰기 패턴, 예상 규모. 불명확한 조건은 가정표로 남긴다.

```text
$mysql8-feature-design 보상 우편 기능을 설계해줘. 동일 우편은 한 번만 수령하고 계정별 최신 우편을 조회한다. docs/db/team-profile.md를 기준으로 설계 문서를 작성해줘.
```

**받을 결과:** 요구사항·가정표, 테이블 관계, DDL 초안, 접근 패턴 표, 트랜잭션 흐름, 검증 계획.

[DB 접속 없는 연습](../skills/mysql8-feature-design/references/example.md)

## 쿼리·인덱스 개선

**준비할 자료:** SQL과 대표 파라미터, DDL·인덱스, EXPLAIN, 테이블 크기·분포·호출 빈도. 실제 값은 마스킹한다.

```text
$mysql8-query-tuning queries/mail-list.sql과 plans/mail-list.md를 보고 인덱스 후보를 제안해줘. EXPLAIN ANALYZE는 실행하지 마.
```

**받을 결과:** 병목 가설과 근거, 수정 SQL·인덱스 후보, 결과 동등성 확인 방법, 측정 전후 표 또는 미실행 표시.

[DB 접속 없는 연습](../skills/mysql8-query-tuning/references/example.md)

## 트랜잭션·멱등성 리뷰

**준비할 자료:** SQL 순서, 서버 코드, 트랜잭션 시작·종료, 격리 수준, 요청 키 범위, 에러·재시도 처리, 외부 호출.

```text
$mysql8-transaction-review src/claim_reward 코드를 보고 동시에 수령하거나 응답이 유실되어도 중복 지급되지 않는지 검토해줘.
```

**받을 결과:** 문제 발생 인터리빙, 불변식, 수정 흐름 또는 코드, 실패·재시도 테스트. 승인된 범위에서만 코드를 수정한다.

[DB 접속 없는 연습](../skills/mysql8-transaction-review/references/example.md)

## DDL 배포·마이그레이션 계획

**준비할 자료:** 변경 전후 DDL, 정확한 버전·엔진·테이블 규모, 동시 부하, 복제 구조, 구·신 서버 호환성, 배포 도구와 작업 창.

```text
$mysql8-migration-plan 대형 account 테이블의 nickname을 NOT NULL UNIQUE로 바꾸는 배포 계획을 만들어줘. 운영 실행은 하지 마.
```

**받을 결과:** 순서별 실행 초안, 전제조건, 검증·관측 항목, 중단·재개·복구 절차. SQL은 검증 상태와 실행 대상을 표시한다.

[DB 접속 없는 연습](../skills/mysql8-migration-plan/references/example.md)

## 데드락·락 대기 진단

**준비할 자료:** 시간이 표시된 deadlock 로그, 트랜잭션별 SQL, 인덱스, 격리 수준, 관련 연결·요청 추적 정보.

```text
$mysql8-lock-diagnosis incidents/deadlock.md를 읽고 잠금 순서가 역전되는 지점과 코드 수정 방향을 찾아줘.
```

**받을 결과:** 시간선, lock cycle 또는 대기 관계, 원인 후보와 증거 수준, 수정안·재현 계획.

[DB 접속 없는 연습](../skills/mysql8-lock-diagnosis/references/example.md)

## 서버 DB 접근 코드 리뷰

**준비할 자료:** DB 접근 코드, 드라이버·ORM 버전과 설정, 커넥션 풀, 트랜잭션 API, primary/replica 라우팅.

```text
$mysql8-data-access-review src/repositories 아래 MySQL 접근 코드를 리뷰해줘. 커넥션 누수와 쓰기 직후 replica 읽기를 우선 확인해줘.
```

**받을 결과:** 코드 위치별 결함, 드라이버 의존 미확인 사항, 최소 수정안과 예외 경로 테스트.

[DB 접속 없는 연습](../skills/mysql8-data-access-review/references/example.md)

## 데이터 보정·대사 계획

**준비할 자료:** 사고 범위·시간, 원본 이벤트·원장, 관련 스키마, 정상 상태 정의, 동시 쓰기 여부, 승인된 보정 범위.

```text
$mysql8-data-repair 이벤트 보상을 두 번 받은 계정을 대사하고 보정 계획을 작성해줘. UPDATE 실행은 하지 마.
```

**받을 결과:** 대사 근거, 대상 조회 SQL, 보정·검증 초안, 재실행·중단·복구 계획과 미정 판단.

[DB 접속 없는 연습](../skills/mysql8-data-repair/references/example.md)

## 용량·샤딩·파티셔닝 설계

**준비할 자료:** 현재 크기·인덱스 크기, 성장률·보존 기간, 피크 읽기·쓰기, 키 분포, 쿼리, 인프라 한계와 복제 구성.

```text
$mysql8-capacity-design 계정 우편 데이터의 월별 파티셔닝과 계정별 샤딩을 비교해줘. docs/db/workload.md의 수치만 사용해줘.
```

**받을 결과:** 가정과 용량 계산, 후보 비교, 키·일관성 위험, 확장 조건 및 검증 계획.

[DB 접속 없는 연습](../skills/mysql8-capacity-design/references/example.md)

## 백업·복구 준비 검토

**준비할 자료:** RPO/RTO, 백업 방식·최근 성공 시각, binlog 보존·연속성, 암호화 키 접근 경로, 복제·GTID 구조, 복구 도구·버전.

```text
$mysql8-backup-recovery 백업 정책과 최근 복원 훈련 기록을 검토해줘. RPO 10분, RTO 1시간 달성 여부를 증거 기준으로 판단해줘.
```

**받을 결과:** 복구 경로·의존 자료, 누락된 증거, 단계별 복원 훈련, RPO/RTO 측정표.

[DB 접속 없는 연습](../skills/mysql8-backup-recovery/references/example.md)

## DB 권한·데이터 노출 리뷰

**준비할 자료:** 마스킹된 GRANT·역할 정보, 업무별 필요한 명령, 접속 경로·TLS·비밀 관리 정책, 로그·덤프 취급 기준.

```text
$mysql8-access-review AI 진단 계정의 GRANT 초안을 검토해줘. 필요한 것은 특정 게임 DB의 메타데이터와 집계 지표 조회다.
```

**받을 결과:** 업무별 권한 매핑, 과도/부족 권한, 연결·노출 위험, 변경 초안과 검증 계획.

[DB 접속 없는 연습](../skills/mysql8-access-review/references/example.md)

## DB 정합성·회귀 테스트 설계

**준비할 자료:** 검증할 요구사항·변경 코드·DDL, 대상 버전·설정, 기존 테스트 프레임워크, 격리 DB와 실행 권한.

```text
$mysql8-test-design 우편 보상 수령의 중복 요청 테스트를 설계해줘. 먼저 DB에 연결하지 말고 두 연결의 실행 순서와 assertion을 문서화해줘.
```

**받을 결과:** 불변식별 시나리오 표, fixture·동시 실행 절차, assertion, 실행 결과 또는 명확한 미실행 사유.

[DB 접속 없는 연습](../skills/mysql8-test-design/references/example.md)

## 업무별 권장 순서

- 신규 기능: feature-design → schema-review → transaction-review. 각 단계의 결과를 다음 단계 입력으로 전달한다.
- 기존 SQL 지연: query-tuning. 연결 풀·replica 문제가 보이면 data-access-review, 락 대기가 보이면 lock-diagnosis로 이어간다.
- 운영 변경 준비: schema-review → migration-plan → test-design. 이 순서는 배포 승인을 뜻하지 않는다.
- 데이터 사고: data-repair로 대사·보정안을 만들고 필요하면 backup-recovery로 복원 경로를 검토한다.

## 좋은 요청의 공통 형식

```text
$mysql8-schema-review
대상: schema/player.sql과 migrations/20260906_add_name.sql
팀 프로필: docs/db/team-profile.md
목적: 닉네임 중복 제한 추가
허용 범위: 파일 분석과 수정안 문서 작성. DB 접속·DDL 실행은 하지 않는다.
출력: 확정 문제와 미확인 사항을 나누고 각 문제에 근거를 붙인다.
```

개발 수정을 원하면 “수정안을 실제 파일에 반영하고 기존 테스트를 실행해줘”라고 범위를 명시한다. DB 실험이 필요하면 격리 대상·허용 작업·제한도 함께 지정한다. 스킬 호출만으로 운영 실행을 승인한 것으로 해석하지 않는다.
