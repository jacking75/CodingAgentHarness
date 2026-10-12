# 쿼리·인덱스 개선 연습

실제 회사나 서비스 데이터가 아닌 가상 사례다. DB 접속 없이 정적 분석한다.

## 요청

```text
$mysql8-query-tuning 이 문서의 입력만 사용해 검토 또는 설계해줘.
DB에 접속하거나 SQL을 실행하지 마. 부족한 정보와 확인 가능한 사실을 구분해줘.
```

## 입력

```sql
SELECT id, created_at FROM mail
WHERE player_id = ? AND DATE(created_at) = '2026-09-01'
ORDER BY created_at DESC, id DESC LIMIT 50;
```

테이블: mail(id BIGINT PRIMARY KEY, player_id BIGINT NOT NULL, created_at DATETIME(6) NOT NULL). 보조 인덱스는 없다. 시간대 정책·데이터 분포·실행 계획은 제공하지 않는다.

## 실제 프로젝트 호출 예시

```text
$mysql8-query-tuning queries/mail-list.sql과 plans/mail-list.md를 보고 인덱스 후보를 제안해줘. EXPLAIN ANALYZE는 실행하지 마.
```

예시 경로는 실제 저장소 경로로 바꾼다. 다른 업무를 추가로 수행할 권한을 뜻하지 않는다.
