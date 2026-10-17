# Google Workspace CLI — 구글 업무를 명령어와 에이전트로 연결한다

Google Workspace CLI는 Drive, Gmail, Calendar, Sheets, Docs 등 Google Workspace API를 `gws`라는 명령어로 사용하는 오픈 소스 도구다. 사람이 터미널에서 실행할 수도 있고, 명령 실행 기능이 있는 AI 에이전트가 도구로 사용할 수도 있다. [원본 저장소](https://github.com/googleworkspace/cli)에서 코드와 설치 방법을 확인한다.

매일 여러 구글 서비스를 오가며 자료를 모으거나, 같은 조회와 정리를 반복하는 사람에게 유용하다. 예를 들어 일정과 읽지 않은 메일을 조회한 뒤 에이전트에게 오늘 할 일을 정리하도록 요청할 수 있다. 요약과 판단은 에이전트가 수행하며, CLI는 데이터 조회와 API 실행을 담당한다.

> 원본 저장소는 Google이 공식 지원하는 제품이 아니며, 활발한 개발 과정에서 호환성이 깨지는 변경이 생길 수 있다고 명시한다. 이 안내는 실제 계정 연동 성공 보고가 아니라 원본 문서를 바탕으로 작성한 사용 가이드다.

## 왜 좋은가

| 장점 | 실제 작업에서 얻는 효과 |
| --- | --- |
| 여러 서비스를 한 CLI로 다룬다 | Drive 파일, Sheets 데이터, Calendar 일정을 같은 작업 흐름에서 조회할 수 있다. |
| API 응답을 구조화된 JSON으로 받는다 | 에이전트나 스크립트가 화면의 위치 대신 필드와 ID를 기준으로 결과를 처리할 수 있다. 일부 편의 명령은 표가 기본이므로 JSON이 필요하면 `--format json`을 지정한다. |
| 도움말과 스키마를 조회한다 | `--help`와 `gws schema`로 필요한 인자와 요청 구조를 확인해 API 호출 코드를 직접 작성하는 수고를 줄인다. |
| 반복 작업을 명령으로 남긴다 | 검토한 명령과 입력 범위를 다시 사용하기 쉬워진다. API 호출량과 권한은 계속 관리해야 한다. |
| 에이전트용 스킬을 제공한다 | 서비스별 사용법과 업무 레시피를 에이전트가 읽고 명령 선택에 참고할 수 있다. |

기본 API 명령은 Google Discovery Service의 API 정의를 바탕으로 동적으로 구성된다. 설치한 버전의 도움말과 스키마를 확인하는 습관이 필요하다. 원본의 [설계와 기능 설명](https://github.com/googleworkspace/cli#why-gws)과 [스킬 목록](https://github.com/googleworkspace/cli/blob/main/docs/skills.md)을 함께 참고한다.

## 어떤 일을 할 수 있는가

아래는 활용 시나리오이며, 완성된 자동화가 기본으로 모두 실행된다는 뜻은 아니다. 조회 결과를 연결하고 요약하는 과정은 에이전트나 별도 스크립트가 맡는다.

| 업무 | 활용 흐름 | 시작할 명령 |
| --- | --- | --- |
| 아침 업무 정리 | 오늘 일정과 읽지 않은 메일을 조회하고 우선순위를 정리한다 | `gws calendar +agenda`, `gws gmail +triage` |
| 문서 찾기 | Drive 파일 목록에서 이름과 ID를 확인하고 필요한 자료를 고른다 | `gws drive files list` |
| 시트 검토 | 정해진 셀 범위를 읽고 누락 값이나 합계를 검토한다 | `gws sheets +read` |
| 회의 준비 | 일정의 참석자와 관련 문서를 확인해 질문 초안을 만든다 | Calendar·Drive 조회 후 에이전트에게 정리를 요청한다 |
| 보고서 작성 | 조회한 내용을 초안으로 검토한 뒤 문서나 시트에 기록한다 | 쓰기 명령은 대상과 내용을 확인한 뒤 실행한다 |

## 설치부터 첫 조회까지

### 1. 준비 사항을 확인한다

Windows PowerShell에서 진행한다. npm으로 설치하려면 Node.js 18 이상과 npm이 필요하다. 또한 OAuth 인증 정보를 만들 Google Cloud 프로젝트와, 사용할 서비스에 접근할 Google 계정이 필요하다. 회사 계정에서는 관리자 정책에 따라 OAuth 앱이나 API 접근 허용이 필요할 수 있다.

```powershell
node --version
npm --version
```

Node.js를 사용하지 않으려면 원본에서 권장하는 [운영체제별 사전 빌드 바이너리](https://github.com/googleworkspace/cli/releases)를 내려받아 압축을 풀고 `gws` 실행 파일이 있는 폴더를 PATH에 추가한다.

### 2. CLI를 설치한다

npm이 준비된 환경에서는 다음과 같이 설치한다. 이 명령은 실제로 PC에 CLI를 전역 설치한다.

```powershell
npm install -g @googleworkspace/cli
gws --help
```

설치 후 명령을 찾지 못하면 터미널을 다시 열고 PATH를 확인한다. 스킬 설치와 CLI 설치는 별도 작업이므로 스킬만 추가해도 `gws`가 항상 설치되는 것은 아니다. 최신 설치 안내는 [원본 Installation](https://github.com/googleworkspace/cli#installation)을 따른다.

### 3. 계정을 연결한다

`gcloud`가 설치되어 있다면 다음 설정 도우미로 Cloud 프로젝트 구성과 API 활성화, 인증을 진행한다. 이 단계는 Cloud 설정을 변경할 수 있으므로 안내되는 프로젝트를 확인한다.

```powershell
gws auth setup
```

`gcloud`가 없다면 [수동 OAuth 설정](https://github.com/googleworkspace/cli#manual-oauth-setup-google-cloud-console)을 따른다. Cloud Console에서 사용할 API와 OAuth 동의 화면을 설정하고, 테스트 모드라면 본인 계정을 테스트 사용자로 추가한다. OAuth 클라이언트 유형은 **데스크톱 앱**으로 만들고, 내려받은 JSON을 기본 설정 경로인 `~/.config/gws/client_secret.json`에 둔다. 설정 경로를 별도로 지정했다면 해당 경로를 사용한다.

이후 로그인하거나 사용할 서비스 범위를 다시 선택할 때 다음 명령을 사용한다. 처음에는 Drive와 Sheets처럼 필요한 서비스만 선택하고, 동의 화면에서 요청 권한을 확인한다.

```powershell
gws auth login -s drive,sheets
```

Gmail이나 Calendar 예시를 사용하려면 필요한 API를 활성화하고 해당 권한도 추가해야 한다. 서비스 선택만으로 읽기 전용 권한이 보장되지는 않으므로 실제 동의 항목을 확인한다. 인증 파일과 토큰을 Git 저장소나 대화에 붙여 넣지 않는다. 상세 절차는 [원본 Authentication](https://github.com/googleworkspace/cli#authentication)을 기준으로 한다.

### 4. Drive 목록으로 연결을 확인한다

```powershell
gws drive files list
```

성공하면 접근 가능한 파일 정보를 담은 JSON을 반환한다. 결과가 비어 있다면 사용 계정과 접근 권한을 확인한다. 이 명령의 기본 결과는 한 페이지이며, Drive 전체 목록이나 휴지통을 제외한 목록을 보장하지 않는다. 조회 조건은 `gws schema drive.files.list`로 확인한다. [Drive 명령 참조](https://github.com/googleworkspace/cli/blob/main/skills/gws-drive/SKILL.md)를 함께 읽는다.

## 바로 활용하는 조회 예시

아래 예시는 데이터를 수정하지 않는 조회 작업이다. 각 서비스의 API 활성화와 로그인 권한이 준비되어 있어야 한다.

### 오늘 일정을 확인한다

```powershell
gws calendar +agenda --today --timezone Asia/Seoul --format json
```

서울 시간 기준 오늘 일정을 조회한다. 특정 캘린더만 사용하려면 `--calendar`로 이름이나 ID를 지정한다. [Calendar 일정 조회 참조](https://github.com/googleworkspace/cli/blob/main/skills/gws-calendar-agenda/SKILL.md)에서 옵션을 확인한다.

### 읽지 않은 메일 다섯 건을 확인한다

```powershell
gws gmail +triage --max 5 --format json
```

발신자, 제목, 날짜 등 읽지 않은 메일의 요약 정보를 확인한다. 메일 본문 전체를 요약하려면 별도의 본문 조회가 필요하다. 이 명령은 메일함을 변경하지 않는다. [Gmail 조회 참조](https://github.com/googleworkspace/cli/blob/main/skills/gws-gmail-triage/SKILL.md)를 참고한다.

### 시트의 특정 범위를 읽는다

```powershell
gws sheets +read --spreadsheet SPREADSHEET_ID --range "Sheet1!A1:D10"
```

`SPREADSHEET_ID`는 시트 URL의 `/d/` 다음에 있는 ID로 바꾸고, `Sheet1`도 실제 탭 이름으로 바꾼다. 예를 들어 탭 이름이 `업무 목록`이라면 범위는 `"'업무 목록'!A1:D10"`으로 지정한다. 결과를 에이전트에게 전달해 빈 셀이나 상태별 개수를 정리하게 할 수 있다. [Sheets 범위 조회 참조](https://github.com/googleworkspace/cli/blob/main/skills/gws-sheets-read/SKILL.md)를 참고한다.

## API 명령과 실행 전 미리보기를 이해한다

일반 API 명령은 `gws 서비스 리소스 메서드` 구조다. `+agenda`, `+triage`, `+read`처럼 `+`가 붙은 명령은 자주 하는 작업을 위한 편의 명령이다. [공통 명령 참조](https://github.com/googleworkspace/cli/blob/main/skills/gws-shared/SKILL.md)에서 인자와 출력 형식을 확인한다.

```powershell
gws drive --help
gws schema drive.files.list
gws sheets spreadsheets create --help
```

일반 API 명령에서 `--params`는 URL·쿼리 인자, `--json`은 요청 본문이다. JSON 인자를 직접 작성할 때는 PowerShell 버전과 실행 파일·npm 래퍼에 따라 큰따옴표 전달 방식이 달라질 수 있으므로, 설치한 환경에서 요청 미리보기로 확인한다. 먼저 인자 없이 가능한 목록 요청을 미리 본다.

```powershell
# Drive 목록 요청을 미리 본다. 실제 목록을 조회하지 않는다.
gws drive files list --dry-run
```

`--dry-run`은 API 실행 없이 요청을 로컬에서 검토하는 기능이다. 실제 계정 권한, 서버의 수락 여부, 생성 성공까지 검증하지는 않는다. 쓰기 작업에서도 대상과 요청 본문을 채운 뒤 이 옵션으로 검토하고, 사용자가 변경을 승인한 뒤에만 옵션을 제거해 실행한다. 자동 페이지 조회가 필요하면 일반 API 명령의 `--page-all`과 `--page-limit`을 확인하며, 결과는 페이지별 NDJSON으로 처리한다.

## AI 에이전트와 함께 사용한다

CLI가 설치된 PC에서 필요한 스킬을 선택해 추가한다. 설치 과정에서 대상 에이전트와 적용 범위를 확인한다.

```powershell
npx skills add https://github.com/googleworkspace/cli
```

한 서비스부터 시작하려면 원본 안내에 따라 개별 스킬을 선택할 수도 있다.

```powershell
npx skills add https://github.com/googleworkspace/cli/tree/main/skills/gws-drive
```

실행 전에 선택한 스킬의 `SKILL.md`와 공통 참조인 `gws-shared/SKILL.md`를 읽고, 참조 파일도 함께 설치되어 있는지 확인한다. 스킬 추가는 계정 로그인이나 회사 관리자의 권한 허용을 대신하지 않는다. [전체 스킬 목록과 업무 레시피](https://github.com/googleworkspace/cli/blob/main/docs/skills.md)에서 작업에 맞는 자료를 고른다.

명령을 실행할 수 있는 에이전트에는 다음과 같이 범위를 정해 요청한다.

```text
설치된 Google Workspace CLI 스킬과 공통 참조를 먼저 읽는다.
현재 연결 계정과 필요한 권한을 확인한다.
서울 시간 기준 오늘 일정과 읽지 않은 메일 다섯 건의 요약 정보를 조회한다.
시간이 겹치는 일정과 먼저 확인할 메일을 한국어로 정리한다.
조회가 실패하면 실패한 단계와 이유를 알린다.
메일 발송, 일정 변경, 파일 수정은 별도 승인 전까지 실행하지 않는다.
```

외부 메일과 문서의 내용은 업무 데이터로 취급하며, 그 안에 있는 명령을 에이전트의 작업 지침으로 받아들이지 않는다. 조회 결과를 다른 AI 서비스에 전달할 때는 조직의 데이터 사용 규칙을 따른다.

## 기존 도구와 어떻게 선택하는가

| 도구 | 주로 선택할 상황 |
| --- | --- |
| Google Workspace CLI | 로컬 터미널·스크립트·에이전트에서 Workspace API를 호출하고 결과를 연결할 때 선택한다. |
| Apps Script + clasp | Google 쪽에서 실행할 업무 자동화 코드와 시간 기반 트리거를 만들고 배포할 때 검토한다. [기존 구글 업무 자동화 가이드](google-automation-guide.html)에서 따라 한다. |
| google/skills | Google Cloud 개발·설정·배포에 맞는 작업 지침을 선택할 때 사용한다. Workspace CLI 자체와는 별도 스킬 모음이다. [Google Cloud 작업 안내](README.md#google-cloud-작업)를 참고한다. |

이 표는 작업 위치와 목적에 따른 선택 안내다. CLI를 설치하는 것만으로 PC가 꺼져 있어도 업무가 자동 실행되는 것은 아니므로, 정기 실행이 필요하면 실행 환경을 별도로 설계한다.

## 막히는 지점과 확인 순서

| 증상 | 확인할 사항 |
| --- | --- |
| `gws` 명령을 찾지 못한다 | 설치 결과와 PATH를 확인하고 터미널을 다시 연다. |
| `gcloud`를 찾지 못한다 | 설정 도우미 대신 원본의 수동 OAuth 설정을 사용하거나 gcloud를 준비한다. |
| 로그인 중 접근 차단이 나온다 | OAuth 테스트 사용자 등록, 회사 관리자 정책, 요청 권한을 확인한다. |
| 요청 권한이 너무 많다는 오류가 난다 | 전체 권한 대신 필요한 서비스만 선택해 로그인한다. |
| `redirect_uri_mismatch`가 나온다 | OAuth 클라이언트가 데스크톱 앱 유형인지 확인한다. |
| `accessNotConfigured`가 나온다 | 오류가 가리키는 Cloud 프로젝트의 해당 API 활성화 상태를 확인한다. |
| 조회가 403으로 실패한다 | 로그인 계정, 파일 공유 권한, OAuth 범위와 조직 정책을 확인한다. |
| 예시의 옵션이 동작하지 않는다 | 설치 버전의 `--help`와 원본 변경 사항을 확인한다. |

상세한 오류 대응은 [원본 Troubleshooting](https://github.com/googleworkspace/cli#troubleshooting)을 확인한다. 우선 한 서비스의 조회부터 성공시킨 뒤, 필요한 서비스와 쓰기 작업을 단계적으로 추가하는 방식으로 시작한다.
