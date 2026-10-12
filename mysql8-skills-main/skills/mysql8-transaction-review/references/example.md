# 트랜잭션·멱등성 리뷰 연습

실제 회사나 서비스 데이터가 아닌 가상 사례다. DB 접속 없이 정적 분석한다.

## 요청

```text
$mysql8-transaction-review 이 문서의 입력만 사용해 검토 또는 설계해줘.
DB에 접속하거나 SQL을 실행하지 마. 부족한 정보와 확인 가능한 사실을 구분해줘.
```

## 입력

```text
BEGIN
SELECT received FROM mail WHERE id = :mail AND player_id = :player
if received == 0:
  UPDATE wallet SET balance = balance + 100 WHERE player_id = :player
  UPDATE mail SET received = 1 WHERE id = :mail
COMMIT
```

InnoDB, REPEATABLE READ. 두 요청이 같은 우편에 동시에 들어온다. wallet.player_id와 mail.id는 PK다.

## 실제 프로젝트 호출 예시

```text
$mysql8-transaction-review src/claim_reward 코드를 보고 동시에 수령하거나 응답이 유실되어도 중복 지급되지 않는지 검토해줘.
```

예시 경로는 실제 저장소 경로로 바꾼다. 다른 업무를 추가로 수행할 권한을 뜻하지 않는다.
