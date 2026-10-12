# 서버 DB 접근 코드 리뷰 연습

실제 회사나 서비스 데이터가 아닌 가상 사례다. DB 접속 없이 정적 분석한다.

## 요청

```text
$mysql8-data-access-review 이 문서의 입력만 사용해 검토 또는 설계해줘.
DB에 접속하거나 SQL을 실행하지 마. 부족한 정보와 확인 가능한 사실을 구분해줘.
```

## 입력

```text
conn = pool.acquire()
conn.begin()
pool.execute("UPDATE wallet SET balance=balance+? WHERE player_id=?", amount, id)
conn.commit()
return replica.query("SELECT balance FROM wallet WHERE player_id=?", id)
```

예외 처리와 conn 반환 코드는 없다. pool.execute가 conn과 같은 연결을 사용한다는 보장은 없다.

## 실제 프로젝트 호출 예시

```text
$mysql8-data-access-review src/repositories 아래 MySQL 접근 코드를 리뷰해줘. 커넥션 누수와 쓰기 직후 replica 읽기를 우선 확인해줘.
```

예시 경로는 실제 저장소 경로로 바꾼다. 다른 업무를 추가로 수행할 권한을 뜻하지 않는다.
