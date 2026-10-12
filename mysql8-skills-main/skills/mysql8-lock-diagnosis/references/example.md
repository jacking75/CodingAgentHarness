# 데드락·락 대기 진단 연습

실제 회사나 서비스 데이터가 아닌 가상 사례다. DB 접속 없이 정적 분석한다.

## 요청

```text
$mysql8-lock-diagnosis 이 문서의 입력만 사용해 검토 또는 설계해줘.
DB에 접속하거나 SQL을 실행하지 마. 부족한 정보와 확인 가능한 사실을 구분해줘.
```

## 입력

T1: account 10의 X lock 보유, account 20의 X lock 대기.
T2: account 20의 X lock 보유, account 10의 X lock 대기.
코드 A는 송신자 → 수신자 순서로 갱신한다. 반대 방향 거래가 동시 실행됐다. 테이블 PK는 account_id다.

## 실제 프로젝트 호출 예시

```text
$mysql8-lock-diagnosis incidents/deadlock.md를 읽고 잠금 순서가 역전되는 지점과 코드 수정 방향을 찾아줘.
```

예시 경로는 실제 저장소 경로로 바꾼다. 다른 업무를 추가로 수행할 권한을 뜻하지 않는다.
