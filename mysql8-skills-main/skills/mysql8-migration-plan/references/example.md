# DDL 배포·마이그레이션 계획 연습

실제 회사나 서비스 데이터가 아닌 가상 사례다. DB 접속 없이 정적 분석한다.

## 요청

```text
$mysql8-migration-plan 이 문서의 입력만 사용해 검토 또는 설계해줘.
DB에 접속하거나 SQL을 실행하지 마. 부족한 정보와 확인 가능한 사실을 구분해줘.
```

## 입력

대상 버전은 “MySQL 8”로만 제공됐다. account는 약 1억 행이며 nickname VARCHAR(40) NULL이다. 제안은 BEGIN; ALTER TABLE account MODIFY nickname VARCHAR(40) NOT NULL, ADD UNIQUE KEY uq_nickname(nickname); ROLLBACK; 이다. 무중단이고 문제 시 롤백 가능하다고 작성자가 주장한다.

## 실제 프로젝트 호출 예시

```text
$mysql8-migration-plan 대형 account 테이블의 nickname을 NOT NULL UNIQUE로 바꾸는 배포 계획을 만들어줘. 운영 실행은 하지 마.
```

예시 경로는 실제 저장소 경로로 바꾼다. 다른 업무를 추가로 수행할 권한을 뜻하지 않는다.
