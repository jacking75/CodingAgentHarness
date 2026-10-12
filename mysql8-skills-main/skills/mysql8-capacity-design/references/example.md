# 용량·샤딩·파티셔닝 설계 연습

실제 회사나 서비스 데이터가 아닌 가상 사례다. DB 접속 없이 정적 분석한다.

## 요청

```text
$mysql8-capacity-design 이 문서의 입력만 사용해 검토 또는 설계해줘.
DB에 접속하거나 SQL을 실행하지 마. 부족한 정보와 확인 가능한 사실을 구분해줘.
```

## 입력

mail의 PRIMARY KEY는 id이고 UNIQUE KEY는 request_id다. 월별 created_at 파티셔닝을 제안한다. request_id는 전체 기간에 걸쳐 중복되면 안 된다. FK도 사용 중이다. 매월 2천만 행이 늘며 보존 기간은 미정이다.

## 실제 프로젝트 호출 예시

```text
$mysql8-capacity-design 계정 우편 데이터의 월별 파티셔닝과 계정별 샤딩을 비교해줘. docs/db/workload.md의 수치만 사용해줘.
```

예시 경로는 실제 저장소 경로로 바꾼다. 다른 업무를 추가로 수행할 권한을 뜻하지 않는다.
