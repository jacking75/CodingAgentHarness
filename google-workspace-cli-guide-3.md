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

`gcloud`가 없어도 아래 순서로 웹브라우저에서 직접 설정할 수 있다. 다른 설명 글을 읽으러 갈 필요 없이, 이 문서의 **3-1부터 3-8까지** 따라 한다. 처음에는 **내 Drive와 Sheets를 읽는 연결**부터 만든다. Gmail과 Calendar를 추가하는 방법도 아래에 설명한다.

#### 3-1. 무엇을 설정하는지 먼저 이해한다

OAuth는 구글 비밀번호를 CLI에 알려 주는 대신, 구글 로그인 화면에서 필요한 접근을 허용하는 방식이다. 프로그램을 직접 개발할 필요는 없으며, 다음 네 가지를 준비하면 된다.

| 화면에 나오는 말 | 쉬운 뜻 | 이 안내에서 할 일 |
| --- | --- | --- |
| 프로젝트 | 구글 연결 설정을 담는 관리용 묶음이다. 내 Drive 폴더와는 별개다. | `나의 Workspace CLI`라는 이름으로 만든다. |
| API | 프로그램이 Drive나 Sheets를 이용하는 통로다. | Drive와 Sheets의 통로를 켠다. |
| OAuth 동의 화면 | 로그인할 때 연결 이름과 요청 권한을 보여 주는 화면이다. | 본인이 알아볼 이름과 이메일을 등록한다. |
| OAuth 클라이언트·JSON 파일 | 내 PC의 CLI가 어떤 연결 설정을 사용할지 알려 주는 등록 정보다. JSON은 그 정보를 담은 파일 형식이다. | 데스크톱 앱으로 등록하고 파일을 PC에 저장한다. |

브라우저와 CLI에서 사용할 **같은 구글 계정**을 정한다. 회사 계정은 프로젝트 생성이나 외부 앱 연결이 제한될 수 있다. 메뉴가 막히면 회사 담당자에게 허용 여부를 확인한다. 메뉴 이름은 한국어와 영어를 함께 적었으며, 화면에 따라 표현이나 위치가 조금 다를 수 있다.

#### 3-2. Google Cloud 프로젝트를 만든다

1. [Google Cloud Console 열기](https://console.cloud.google.com/)를 눌러 설정 화면을 연다. 이 링크는 설명 글이 아니라 실제로 설정할 웹사이트다.
2. 오른쪽 위 계정 사진을 눌러 사용할 이메일이 맞는지 확인한다. 처음 방문했다면 이용약관 안내를 읽고 동의 여부를 선택한다.
3. 화면 위쪽의 **프로젝트 선택**(Select a project) 또는 현재 프로젝트 이름을 누른다.
4. 열린 창에서 **새 프로젝트**(New project)를 누른다. 보이지 않으면 왼쪽 위 **☰ → IAM 및 관리자(IAM & Admin) → 프로젝트 만들기**(Create a project)로 들어간다.
5. 프로젝트 이름에 `나의 Workspace CLI`를 입력한다. 프로젝트 ID는 자동 생성된 값을 그대로 사용해도 된다.
6. 개인 계정에서 조직·위치가 **조직 없음**(No organization)으로 표시되면 그대로 진행한다. 회사 계정은 회사에서 허용한 조직·위치를 선택한다.
7. **만들기**(Create)를 누르고 생성이 끝날 때까지 기다린다. 다시 위쪽 프로젝트 선택을 눌러 방금 만든 프로젝트를 선택한다.

**완료 확인:** 화면 위쪽에 `나의 Workspace CLI`가 표시된다. 이후 API와 로그인 설정도 모두 이 프로젝트에서 진행한다. 이미 사용할 프로젝트를 가지고 있다면 새로 만드는 대신 그 프로젝트를 선택한다.

이 절차에서 결제 계정 연결을 필수 단계로 안내하지는 않는다. 사용 기능과 조직 정책에 따라 결제 설정이 요구될 수 있으므로, 결제나 무료 체험 신청 화면이 나오면 내용을 확인한 뒤 결정한다.

#### 3-3. Drive와 Sheets API를 켠다

1. 왼쪽 위 **☰ → API 및 서비스(APIs & Services) → 라이브러리**(Library)로 들어간다.
2. 검색창에 `Google Drive API`를 입력하고 같은 이름의 항목을 선택한다.
3. **사용**(Enable)을 누른다. 이미 **관리**(Manage)가 보이면 켜져 있는 상태다.
4. 라이브러리로 돌아가 `Google Sheets API`를 검색하고, 같은 방법으로 **사용**(Enable)을 누른다.
5. **API 및 서비스 → 사용 설정된 API 및 서비스**(Enabled APIs & services)에서 두 API를 확인한다.

**완료 확인:** 목록에 `Google Drive API`와 `Google Sheets API`가 보인다. API를 켜는 것만으로 내 파일을 읽도록 허용한 것은 아니다. 다음 단계에서 사용할 사람과 접근 권한을 정한다.

#### 3-4. 로그인할 때 표시할 이름과 이메일을 등록한다

1. 왼쪽 위 **☰ → Google 인증 플랫폼(Google Auth platform) → 브랜딩**(Branding)으로 들어간다. **API 및 서비스 → OAuth 동의 화면**(OAuth consent screen)을 눌러 같은 설정으로 이동할 수도 있다.
2. 처음이라면 **시작하기**(Get started)를 누른다. 이미 설정되어 있다면 기존 브랜딩 정보와 다음 단계의 대상·테스트 사용자를 확인한다.
3. **앱 정보**(App Information)를 다음과 같이 입력한다.

| 입력 항목 | 입력할 내용 |
| --- | --- |
| 앱 이름(App name) | `나의 Workspace CLI`를 입력한다. 나중에 구글 로그인 화면에 보이는 이름이다. |
| 사용자 지원 이메일(User support email) | 본인의 이메일을 선택한다. |
| 대상(Audience) | 개인 계정으로 본인만 시험할 때는 **외부**(External)를 선택한다. 외부를 고르는 것만으로 앱이 공개되는 것은 아니다. |
| 연락처 정보(Contact Information) | 설정 관련 안내를 받을 본인의 이메일을 입력한다. |

4. 각 화면에서 **다음**(Next)을 누르고, 마지막에 정책을 읽고 동의 여부를 선택한 뒤 **계속(Continue) → 만들기**(Create)를 누른다.

회사에서 **내부**(Internal) 앱을 사용하도록 정했다면 그 지침을 따른다. 내부 앱은 해당 조직의 계정만 사용할 수 있으므로 개인 Gmail 계정으로 로그인하면 안 된다.

**완료 확인:** Google 인증 플랫폼에서 브랜딩, 대상, 데이터 액세스 등의 메뉴를 열 수 있다.

#### 3-5. 본인을 테스트 사용자로 등록한다

**외부**(External)로 설정했다면 이 단계를 진행한다. 본인 혼자 사용하더라도 빠뜨리면 로그인이 차단될 수 있다.

1. Google 인증 플랫폼의 **대상**(Audience) 메뉴를 연다.
2. 게시 상태가 **테스트**(Testing)인지 확인한다. 이 연습에서는 **앱 게시**(Publish app)를 누를 필요가 없다.
3. **테스트 사용자(Test users) → 사용자 추가**(Add users)를 누른다.
4. CLI에서 로그인할 본인의 구글 이메일을 입력하고 **저장**(Save)을 누른다.

**완료 확인:** 테스트 사용자 목록에 정확한 이메일이 보인다. 이메일을 입력만 하고 저장하지 않은 상태로 다음 단계에 넘어가지 않는다.

#### 3-6. 처음 사용할 읽기 권한을 등록한다

권한 범위(scope)는 프로그램에 어디까지 허용할지 정하는 항목이다. 처음에는 파일과 시트를 바꾸지 않는 **읽기 전용**으로 연습한다.

1. Google 인증 플랫폼의 **데이터 액세스**(Data Access)를 연다.
2. **범위 추가 또는 삭제**(Add or Remove Scopes)를 누른다.
3. 검색·필터로 아래 두 범위를 찾고 선택한다. 목록에 없다면 **범위 수동 추가**(Manually add scopes) 입력란에 아래 주소를 한 줄씩 넣고 **표에 추가**(Add to table)를 누른다.

```text
https://www.googleapis.com/auth/drive.readonly
https://www.googleapis.com/auth/spreadsheets.readonly
```

4. **업데이트**(Update) 후 **저장**(Save)을 눌러 반영한다.

첫 번째는 Drive 파일을 읽는 권한이며, 두 번째는 시트 내용을 읽는 권한이다. 읽기 전용도 파일의 내용을 볼 수 있는 권한이므로 본인이 사용할 계정에서만 진행한다. 민감한 범위 등의 분류가 표시될 수 있지만, 이 안내에서는 전체 공개나 검증 신청으로 넘어가지 않는다.

**완료 확인:** 데이터 액세스에 위 두 범위가 표시된다. 이 화면에 등록한 것만으로 권한 허용이 끝나지는 않으며, 3-8에서 본인이 로그인해 다시 동의한다.

#### 3-7. 데스크톱 앱을 등록하고 인증 파일을 저장한다

1. Google 인증 플랫폼의 **클라이언트(Clients) → 클라이언트 만들기**(Create client)를 누른다. 이전 화면 구성에서는 **API 및 서비스 → 사용자 인증 정보(Credentials) → 사용자 인증 정보 만들기 → OAuth 클라이언트 ID**로 들어간다.
2. 애플리케이션 유형은 **데스크톱 앱**(Desktop app)으로 선택한다.
3. 이름은 `내 PC Workspace CLI`로 입력하고 **만들기**(Create)를 누른다. 웹 애플리케이션용 리디렉션 주소를 입력하라는 화면이라면 앱 유형을 다시 확인한다.
4. 생성 완료 창의 **JSON 다운로드**(Download JSON)를 누른다. 보이지 않으면 클라이언트 목록에서 방금 만든 항목의 다운로드 버튼을 찾는다.
5. 브라우저의 다운로드 목록이나 Windows의 **다운로드** 폴더에서 내려받은 `.json` 파일을 찾는다. 보통 `client_secret_…json`처럼 긴 이름이다. 파일 내용을 직접 고칠 필요는 없다.

이제 파일을 CLI가 찾는 폴더에 둔다. 아래는 **Windows에서 처음 설치한 기본 설정**을 기준으로 한다.

1. 키보드에서 **Windows 키 + R**을 누르고 `%USERPROFILE%`을 입력한 뒤 Enter를 누른다. 내 사용자 폴더가 열린다.
2. 그 안에 `.config`라는 폴더를 만든다. 이미 있으면 해당 폴더를 연다. 이어서 그 안에 `gws` 폴더를 만들고 연다.
3. 다운로드한 JSON 파일을 이 `gws` 폴더에 복사한다.
4. 탐색기에서 파일 확장자를 표시한다. Windows 11은 **보기 → 표시 → 파일 확장명**, Windows 10은 **보기 → 파일 확장명**을 선택한다.
5. 복사한 파일 이름을 `client_secret.json`으로 바꾼다. `client_secret.json.json`이나 `client_secret.json.txt`가 되지 않게 확인한다.

```text
내 사용자 폴더
└─ .config
   └─ gws
      └─ client_secret.json
```

예를 들어 Windows 사용자 폴더가 `C:\Users\minsu`라면 최종 위치는 `C:\Users\minsu\.config\gws\client_secret.json`이다. 여기서 `minsu`는 설명용 이름이므로 본인의 폴더 이름을 사용한다. Windows 키 + R에 `%USERPROFILE%\.config\gws`를 입력하면 해당 폴더를 바로 열 수 있다.

**완료 확인:** 위 폴더 안에 이름이 정확한 `client_secret.json` 파일이 보인다. 파일 내용을 대화창에 붙여 넣거나 GitHub에 올리지 않는다. 이전에 `GOOGLE_WORKSPACE_CLI_CONFIG_DIR`로 설정 폴더를 바꾼 사용자라면 그 폴더를 사용한다. 기존 설치의 저장 위치가 달랐다면 인증 파일을 임의로 이동하기 전에 현재 설정을 확인한다.

#### 3-8. PowerShell에서 로그인하고 첫 조회를 한다

1. CLI를 설치할 때 사용한 PowerShell 창으로 돌아간다. 창을 닫았다면 시작 메뉴에서 **PowerShell**을 검색해 연다.
2. 아래 명령을 **한 줄 전체** 복사해 붙여 넣고 Enter를 누른다. 앞에서 등록한 Drive·Sheets 읽기 권한만 요청하는 명령이다.

```powershell
gws auth login --scopes "https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/spreadsheets.readonly"
```

3. 브라우저가 열리면 3-5에서 등록한 계정을 선택한다. 자동으로 열리지 않으면 PowerShell에 표시된 로그인 주소를 복사해 브라우저 주소창에서 연다. 완료될 때까지 PowerShell 창은 열어 둔다.
4. `나의 Workspace CLI`처럼 본인이 설정한 앱 이름과 요청 권한을 확인한다. **Google에서 확인하지 않은 앱**이라는 안내가 나오면 본인이 만든 앱·선택한 계정이 맞는지 먼저 확인한다. 맞는 경우 화면에서 제공하는 **계속**(Continue) 또는 **고급(Advanced) → 해당 앱으로 이동**을 선택한다. 회사 정책으로 차단되어 진행 항목이 없으면 담당자에게 문의한다.
5. 권한별 체크박스가 있다면 앞에서 요청한 읽기 권한을 확인해 선택하고 **계속**(Continue) 또는 **허용**(Allow)을 누른다.
6. 브라우저에 완료 안내가 나오고 PowerShell의 로그인 명령이 끝나면 다음 명령을 실행한다.

```powershell
gws drive files list
```

**완료 확인:** 파일 정보를 담은 결과가 나오면 연결된 상태다. 파일이 없는 계정은 목록이 비어 있을 수 있다. 비밀번호를 PowerShell에 직접 입력하거나 JSON 파일에 적을 필요는 없다. 이후에는 보통 조회 명령을 바로 쓰며, 인증 만료나 권한 변경으로 다시 로그인이 필요하면 같은 로그인 명령을 실행한다.

#### Gmail·Calendar나 쓰기 작업을 나중에 추가한다

처음 연결에는 Drive·Sheets 읽기 권한만 포함했으므로 아래의 Gmail·Calendar 예시는 아직 사용할 수 없다. 다음 순서로 필요한 서비스만 추가한다.

1. 3-3과 같은 API 라이브러리에서 메일을 사용하려면 **Gmail API**, 일정을 사용하려면 **Google Calendar API**를 켠다.
2. 3-6의 데이터 액세스에서 메일 조회에는 `https://www.googleapis.com/auth/gmail.readonly`, 일정 조회에는 `https://www.googleapis.com/auth/calendar.readonly`를 추가한다.
3. Drive·Sheets와 두 서비스를 모두 읽으려면 다음 명령으로 다시 로그인하고 추가 권한에 동의한다. 새 로그인에는 필요한 기존 범위도 함께 넣는다.

```powershell
gws auth login --scopes "https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/spreadsheets.readonly,https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/calendar.readonly"
```

메일 발송, 시트 수정, 일정 변경에는 각각 쓰기 권한이 추가로 필요하다. 읽기 권한으로 연습을 마친 뒤, 수행할 작업과 변경 대상을 정하고 필요한 권한만 추가한다.

로그인이 막히면 다음 표에서 **막힌 단계부터** 확인한다.

| 막힌 지점 | 이 문서에서 다시 확인할 곳 |
| --- | --- |
| 프로젝트를 만들 수 없거나 메뉴 접근이 막힌다 | 3-2에서 로그인 계정과 조직을 확인하고, 회사 계정은 담당자에게 프로젝트 생성 권한을 문의한다. |
| 인증 파일을 찾지 못한다 | 3-7의 저장 폴더·파일명·확장자를 확인한다. |
| `redirect_uri_mismatch`가 나온다 | 3-7에서 데스크톱 앱으로 만들었는지 확인한다. |
| 로그인 중 `access_denied`나 접근 차단이 나온다 | 3-5의 테스트 사용자 이메일과 실제 로그인 계정이 같은지 확인한다. 조직 정책 차단은 관리자에게 문의한다. |
| `accessNotConfigured`가 나온다 | 3-3에서 인증 파일을 만든 프로젝트의 해당 API를 켰는지 확인한다. |
| 로그인은 되었지만 조회가 403으로 실패한다 | 3-6과 3-8의 읽기 권한, 선택 계정, 해당 파일 접근 권한을 확인한다. |

설명 확인 근거는 [Google의 프로젝트 생성 안내](https://developers.google.com/workspace/guides/create-project), [API 활성화 안내](https://developers.google.com/workspace/guides/enable-apis), [동의 화면 설정 안내](https://developers.google.com/workspace/guides/configure-oauth-consent), [클라이언트 생성 안내](https://developers.google.com/workspace/guides/create-credentials), [CLI 인증 구현](https://github.com/googleworkspace/cli/blob/main/crates/google-workspace-cli/src/auth_commands.rs)이다. 위 절차를 따라 하는 데 이 참고 글을 따로 읽을 필요는 없다.

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
| `gcloud`를 찾지 못한다 | 이 문서의 3-1부터 3-8까지 웹브라우저 수동 설정을 진행한다. |
| 로그인 중 접근 차단이 나온다 | OAuth 테스트 사용자 등록, 회사 관리자 정책, 요청 권한을 확인한다. |
| 요청 권한이 너무 많다는 오류가 난다 | 전체 권한 대신 필요한 서비스만 선택해 로그인한다. |
| `redirect_uri_mismatch`가 나온다 | OAuth 클라이언트가 데스크톱 앱 유형인지 확인한다. |
| `accessNotConfigured`가 나온다 | 오류가 가리키는 Cloud 프로젝트의 해당 API 활성화 상태를 확인한다. |
| 조회가 403으로 실패한다 | 로그인 계정, 파일 공유 권한, OAuth 범위와 조직 정책을 확인한다. |
| 예시의 옵션이 동작하지 않는다 | 설치 버전의 `--help`와 원본 변경 사항을 확인한다. |

상세한 오류 대응은 [원본 Troubleshooting](https://github.com/googleworkspace/cli#troubleshooting)을 확인한다. 우선 한 서비스의 조회부터 성공시킨 뒤, 필요한 서비스와 쓰기 작업을 단계적으로 추가하는 방식으로 시작한다.
