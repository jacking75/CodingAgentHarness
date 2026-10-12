# 스키마·DDL 리뷰 연습

실제 회사나 서비스 데이터가 아닌 가상 사례다. DB 접속 없이 정적 분석한다.

## 요청

```text
$mysql8-schema-review 이 문서의 입력만 사용해 검토 또는 설계해줘.
DB에 접속하거나 SQL을 실행하지 마. 부족한 정보와 확인 가능한 사실을 구분해줘.
```

## 입력

```sql
CREATE TABLE wallet (
  player_id BIGINT NOT NULL,
  balance FLOAT NOT NULL DEFAULT 0,
  request_id VARCHAR(64) NULL,
  UNIQUE KEY uq_request (request_id)
) ENGINE=InnoDB;
```

요구사항: 플레이어별 지갑은 하나다. 유료 재화는 정확한 정수이며 요청 식별자는 중복 지급 방지용이라고 작성자가 주장한다. 다른 코드와 팀 규칙은 제공하지 않는다.

## 실제 프로젝트 호출 예시

```text
$mysql8-schema-review schema/wallet.sql을 검토해줘. balance는 유료 재화이며 정확한 정수다. 파일만 분석하고 DB에는 접속하지 마.
```

예시 경로는 실제 저장소 경로로 바꾼다. 다른 업무를 추가로 수행할 권한을 뜻하지 않는다.
