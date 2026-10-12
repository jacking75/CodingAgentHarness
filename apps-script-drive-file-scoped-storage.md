# Apps Script로 지정 Drive 폴더에 앱 파일을 읽고 쓰는 방법

실제 구현·검증 사례를 일반화한 재사용 문서다. 계정, 실제 폴더·프로젝트·배포 ID, URL, 인증 키, 로컬 경로, 파일 내용과 해시는 포함하지 않는다. 아래 식별자는 설정 이름이나 예시이며 실제 서비스 값이 아니다.

## 1. 성공한 구성

Apps Script의 **고급 Drive 서비스 v3 + `drive.file` 권한 하나**로, 기존에 지정한 Drive 폴더 아래에 앱 파일을 생성하고 다시 읽었다. 데스크톱 클라이언트는 Apps Script 웹앱만 호출했다.

```text
클라이언트
    │ HTTPS /exec 요청
    ▼
Apps Script 웹앱 — 배포자 계정으로 실행
    │ 입력·업로드 키·허용 대상·부모 경계 검증
    ▼
고급 Drive 서비스 v3 — drive.file
    ▼
사용자가 지정한 기존 폴더
    └─ 앱이 만든 대상별 폴더
         ├─ 바이너리 데이터를 담은 Base64 JSON
         └─ 메타데이터·요청 기록
```

별도 OAuth 클라이언트 생성, Cloud 콘솔에서 표준 프로젝트 연결, 클라이언트의 Google 로그인·토큰 관리는 사용하지 않았다. Apps Script의 기본 Cloud 프로젝트와 자체 권한 승인은 사용한다. 따라서 “OAuth나 Cloud가 내부적으로 전혀 없다”는 뜻은 아니다. 고급 서비스는 인증 처리를 Apps Script에 맡길 수 있다. [공식 고급 서비스 안내](https://developers.google.com/apps-script/guides/services/advanced)

## 2. 권한을 정확히 이해한다

`drive.file`은 앱이 생성하거나 사용자에게 허용받은 파일에 대한 권한이다. 전체 Drive 권한인 `drive`와 다르다. **Google이 특정 폴더 경로만으로 접근을 제한해 주는 권한은 아니다.** [공식 Drive 권한 범위](https://developers.google.com/workspace/drive/api/guides/api-specific-auth)

이번 구현은 두 장치를 함께 사용했다.

1. Google 권한은 `drive.file`로 제한한다.
2. 서버는 지정 루트 → 등록된 앱 폴더 → 앱 파일의 부모 관계를 검사한다.

폴더 URL을 알고 있다는 사실, 실행 계정의 폴더 쓰기 권한, 앱에 부여된 파일 접근 범위는 서로 다르다. 링크 공유만으로 임의의 기존 파일을 모두 읽을 수 있다고 가정하지 않는다.

이 방식은 **기존 폴더 안에 앱이 자기 데이터를 만들고 관리하는 용도**에 맞는다. 해당 폴더에 원래 있던 문서를 전부 읽는 범용 탐색기 용도로 검증한 방식은 아니다. Google Picker로 기존 파일을 허용받는 흐름도 이번 구현에는 사용하지 않았다.

## 3. 실패했던 접근과 전환 이유

| 시도 | 실제 관찰 | 채택한 처리 |
|---|---|---|
| 내장 `DriveApp`으로 구현 | 사용한 기능의 전체 Drive 권한 승인 단계에서 ‘차단된 앱’이 표시되었다. | 고급 Drive 서비스와 명시적인 `drive.file`로 교체했다. |
| `UrlFetchApp`으로 Drive 미디어 직접 조회 | 외부 요청 권한을 추가한 구성에서도 승인이 차단되었다. | 외부 요청과 토큰 추출을 사용하는 코드를 제거했다. |
| 기존 루트에 `Drive.Files.get(rootId)` 호출 | `File not found`가 반환되었다. | 루트 메타데이터 조회를 초기화의 필수 조건에서 제거했다. |
| 같은 루트를 `parents`에 넣어 새 파일 생성 | 생성과 새 파일 읽기가 성공했다. | 지정 루트 아래 새 앱 파일의 왕복 검증을 사용했다. |
| `Drive.Files.get(fileId, {alt:'media'})`로 바이너리·일반 텍스트 읽기 | HTTP 200이어도 고급 서비스의 응답 해석이 실패했다. | 저장 본문을 JSON으로 만들었다. |
| JSON 미디어 읽기 | JSON 객체를 받아 원본 바이트를 복원할 수 있었다. | Base64·길이·SHA-256을 포함한 JSON 봉투를 채택했다. |

위 표는 이번 환경의 실측 결과다. 모든 계정에서 차단의 원인이 같거나, 부모 메타데이터 조회 없이 생성하는 동작이 모든 공유 형태에서 보장된다는 뜻은 아니다. 공유 드라이브·조직 정책·다른 계정에서는 아래 진단부터 수행한다. `drive.file`로 바꾸면 모든 ‘차단된 앱’ 문제가 해결된다고 단정하지 않는다.

## 4. Apps Script 설정

1. 실행 계정이 쓸 수 있는 기존 Drive 폴더의 ID를 준비한다.
2. Apps Script 프로젝트를 만들고 기본 Cloud 프로젝트를 유지한다.
3. 프로젝트 설정에서 `appsscript.json` 표시를 활성화한다.
4. 다음 manifest를 등록한다. 편집기의 서비스 목록에서도 Drive v3 활성화를 확인한다.
5. Script Properties에 `ROOT_FOLDER_ID`를 등록한다. 클라이언트 요청으로 루트를 바꾸지 않는다.
6. 아래 진단 함수를 편집기에서 실행하여 권한을 승인하고 생성·읽기·삭제를 확인한다.

```json
{
  "timeZone": "Etc/UTC",
  "runtimeVersion": "V8",
  "exceptionLogging": "STACKDRIVER",
  "dependencies": {
    "enabledAdvancedServices": [
      { "userSymbol": "Drive", "version": "v3", "serviceId": "drive" }
    ]
  },
  "oauthScopes": [
    "https://www.googleapis.com/auth/drive.file"
  ]
}
```

고급 Drive 서비스는 사용 전에 활성화해야 한다. 기본 Cloud 프로젝트에서는 고급 서비스 추가 시 대응 API가 자동으로 활성화되는 흐름을 사용한다. 이미 표준 Cloud 프로젝트로 연결된 프로젝트에는 다른 설정 절차가 적용될 수 있다. [고급 서비스 활성화](https://developers.google.com/apps-script/guides/services/advanced), [고급 Drive 서비스](https://developers.google.com/apps-script/advanced/drive)

코드 전체에서 `DriveApp`, `UrlFetchApp`, `ScriptApp.getOAuthToken()` 사용을 제거했는지 확인한다. manifest만 좁히고 넓은 권한이 필요한 호출을 남기면 실행이 실패한다. 사용하지 않는 과거 시험 코드도 함께 확인한다.

## 5. JSON 봉투로 바이너리 보관

예시 파일명은 `payload.bin.json`이다. 다음은 구조 설명용 예시이며 해시 자리표시자는 실제 저장 시 계산값으로 대체한다.

```json
{
  "format": "AppStorage.Base64.v1",
  "bytes": 3,
  "sha256": "<SHA256_OF_ORIGINAL_BYTES>",
  "mimeType": "application/octet-stream",
  "base64": "AQID"
}
```

쓰기 순서는 원본 바이트 → SHA-256·길이 계산 → Base64 → JSON → `application/json` Blob → `Drive.Files.create`다. `parents`는 서버 설정으로 결정한다.

읽기는 파일 메타데이터·부모·휴지통·물리 크기를 먼저 확인한 뒤 `alt:'media'`로 JSON을 받는다. 형식 버전·원본 길이·Base64 길이·문자·패딩을 검사하고, 디코딩 후 다시 인코딩한 값과 SHA-256까지 대조한다.

Base64 길이는 `4 × ceil(원본 바이트 수 / 3)`이다. 저장·전송 크기에 약 33%와 JSON 헤더가 추가된다. 원본 제한과 JSON 제한을 별도로 둔다. Base64는 암호화가 아니며 SHA-256만으로 변조자의 신원을 검증할 수는 없다.

이 저장 방식의 JSON 미디어 처리는 실환경에서 확인한 동작이다. 임의 바이너리를 Blob으로 돌려주는 API라고 가정하지 않고, 새 환경에서 진단 결과를 확인한다. Drive에서 내려받은 `.bin.json`을 바이너리 파일로 바로 열 수 없으며 앱의 복원 절차가 필요하다.

## 6. 최소 생성·읽기 진단 코드

이 예시는 이번 저장 방식을 일반화한 **편집기 실행용 진단**이다. HTTP 업로드 서버 전체가 아니다. 대상 폴더의 기존 파일은 조회하지 않으며, 자신이 새로 생성한 진단 파일 하나만 마지막에 삭제한다. 공유 권한은 변경하지 않는다.

```javascript
const FORMAT = 'AppStorage.Base64.v1';
const MAX_BYTES = 1024 * 1024; // 이 진단 예시의 제한이다.

function sha256Hex(bytes) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, bytes)
    .map(b => ((b + 256) % 256).toString(16).padStart(2, '0')).join('');
}

function probeConfiguredFolder() {
  const rootId = PropertiesService.getScriptProperties()
    .getProperty('ROOT_FOLDER_ID');
  if (!rootId || !/^[A-Za-z0-9_-]{10,200}$/.test(rootId)) {
    throw new Error('ROOT_FOLDER_ID 설정이 필요하다.');
  }

  // 0~255 모든 바이트를 Apps Script의 signed byte[]로 만든다.
  const original = Array.from({length: 256}, (_, i) => i < 128 ? i : i - 256);
  const envelope = {
    format: FORMAT,
    bytes: original.length,
    sha256: sha256Hex(original),
    mimeType: 'application/octet-stream',
    base64: Utilities.base64Encode(original)
  };
  const name = 'app-probe-' + Utilities.getUuid() + '.bin.json';
  const body = Utilities.newBlob(JSON.stringify(envelope), 'application/json', name);
  let createdId;
  try {
    // 루트 자체의 get/list를 먼저 요구하지 않는다.
    const created = Drive.Files.create({
      name: name, mimeType: 'application/json', parents: [rootId]
    }, body, {fields: 'id'});
    createdId = created.id;

    const meta = Drive.Files.get(createdId, {
      fields: 'id,mimeType,parents,trashed,size'
    });
    if (meta.id !== createdId || meta.trashed ||
        meta.mimeType !== 'application/json' ||
        !Array.isArray(meta.parents) || !meta.parents.includes(rootId)) {
      throw new Error('생성 파일의 종류·부모·휴지통 상태가 잘못되었다.');
    }
    const storedBytes = Number(meta.size);
    if (!Number.isSafeInteger(storedBytes) || storedBytes < 0 ||
        storedBytes > 4 * Math.ceil(MAX_BYTES / 3) + 1024) {
      throw new Error('저장 JSON 크기 제한을 넘었다.');
    }

    const data = Drive.Files.get(createdId, {alt: 'media'});
    if (!data || data.format !== FORMAT ||
        !Number.isSafeInteger(data.bytes) || data.bytes < 0 ||
        data.bytes > MAX_BYTES || typeof data.base64 !== 'string' ||
        data.base64.length !== 4 * Math.ceil(data.bytes / 3) ||
        !/^[A-Za-z0-9+/]*={0,2}$/.test(data.base64) ||
        typeof data.sha256 !== 'string' || !/^[0-9a-f]{64}$/.test(data.sha256) ||
        data.mimeType !== 'application/octet-stream') {
      throw new Error('저장 형식이 잘못되었다.');
    }
    const restored = Utilities.base64Decode(data.base64);
    if (restored.length !== data.bytes ||
        Utilities.base64Encode(restored) !== data.base64 ||
        sha256Hex(restored) !== data.sha256 ||
        data.sha256 !== envelope.sha256) {
      throw new Error('원본 바이트 검증에 실패했다.');
    }
    console.log('지정 폴더의 생성·읽기·바이트 일치 검증 성공');
  } finally {
    if (createdId) Drive.Files.remove(createdId);
  }
}
```

Google 응답 유실로 생성 ID를 받지 못하면 진단 파일이 남을 수 있다. 이때 기존 파일을 일괄 삭제하지 않고 진단 이름을 확인하여 처리한다. 이 예시의 자동 삭제는 임시 진단 파일에만 적용한다. 실제 저장 자료에는 보존·정리 정책을 별도로 둔다.

## 7. 실제 앱에 붙인 구조

최소 진단이 성공하면 저장 계층을 감싸는 함수를 만들고, 상위 기능에서 Drive API를 직접 호출하지 않도록 구성한다.

| 계층 | 처리 |
|---|---|
| 서버 설정 | 루트 ID, 허용 대상 목록, 대상별 앱 폴더 ID, 업로드 키 검증값을 Script Properties에 저장한다. |
| 폴더 생성 | 지정 루트 아래에 앱의 대상별 폴더를 만들고 ID를 보존한다. 기존 등록이 있으면 같은 폴더를 검증하여 사용한다. |
| 읽기·쓰기 경계 | 앱 폴더의 부모가 지정 루트인지, 파일의 부모가 앱 폴더인지 매 작업에서 검사한다. 휴지통·이동·접근 거부를 빈 저장소로 취급하지 않는다. |
| 목록 조회 | 앱 폴더 ID를 부모 조건에 넣는다. 이름의 역슬래시·작은따옴표를 이스케이프하고 모든 페이지를 처리한다. 중복·반복 커서를 거부한다. |
| 저장 형식 | 바이너리뿐 아니라 메타데이터·예약 파일도 같은 JSON 봉투로 저장했다. 원래 바이트 수·형식은 appProperties에도 기록하여 대조했다. |
| 클라이언트 계약 | 저장 표현만 바꾸고 클라이언트가 받는 원래 파일 바이트·메타데이터 형식은 유지했다. |
| 공개 공유 | 기존 루트의 공유 설정을 보존했다. 앱 파일 직접 공개가 필요한 경우만 앱이 만든 항목의 권한을 처리한다. |

파일명만 믿고 접근하지 않는다. 외부 요청에는 논리적인 대상·스냅샷 ID를 받고 실제 Drive 파일 ID와 부모는 서버가 결정한다. 앱이 접근할 수 있는 파일이라도 지정 폴더 밖으로 이동했으면 거부한다. 이 부모 검사는 애플리케이션 정책이며 Google 권한 자체를 폴더 전용으로 바꾸지 않는다.

## 8. 웹앱 배포와 클라이언트 호출

편집기 진단과 별개로 `doGet`·`doPost` 핸들러를 구현한 뒤 웹앱으로 배포한다. 이번 앱은 ‘실행 사용자: 나’, 로그인 없이 접근할 수 있는 배포를 사용했다. 클라이언트에는 정식 `/exec` URL을 넣는다. `/dev`는 편집 권한이 있는 사용자의 개발 확인용이다. 소스를 수정한 뒤에는 배포가 새 버전을 사용하도록 갱신한다. [공식 웹앱 배포 안내](https://developers.google.com/apps-script/guides/web)

이번 앱은 읽기를 익명 허용하고 쓰기는 별도의 업로드 키로 인증했다. 이 정책은 공개해도 되는 자료를 공유하는 앱의 선택이다. 비공개 자료에는 읽기 인증도 설계한다. 웹앱의 접근 정책과 Drive 파일의 링크 공유 정책은 별개이며, 웹앱이 읽어 반환하는 구조만으로도 클라이언트 다운로드를 구현할 수 있다.

업로드 키는 충분히 긴 암호학적 난수로 생성하고 요청 JSON 본문에만 넣었다. URL·로그에는 넣지 않았다. 서버에는 SHA-256 검증값만 저장하고 원문 설정을 제거했다. Windows 클라이언트는 현재 사용자 DPAPI로 보호했다. 다른 Windows 사용자가 만든 DPAPI 파일은 읽지 못하므로 배포 대상 사용자로 키를 저장해야 한다.

ContentService 응답은 `script.googleusercontent.com`으로 리디렉션될 수 있다. 클라이언트가 이 응답 경로를 처리해야 한다. [공식 Content Service 안내](https://developers.google.com/apps-script/guides/content)

이번 클라이언트는 자동 쿠키·리디렉션을 끄고, 검증한 HTTPS Google 응답 주소의 302/303만 GET으로 따라갔다. 업로드 키·POST 본문을 리디렉션 주소로 다시 보내지 않았다. HTTP 200이어도 로그인 HTML·오류 HTML이면 실패로 처리하고 JSON의 버전·성공 여부·데이터 구조를 확인했다.

## 9. 중복 업로드와 충돌 처리

Drive 저장 형식을 바꿔도 동기화의 확정 규칙은 별도로 필요하다. 이번 구현은 다음 순서를 사용했다.

1. 요청 ID·스냅샷 ID·원본 해시·기대 원격 스냅샷 ID를 받는다.
2. 서버의 Script Lock 안에서 현재 포인터와 기대 ID를 비교한다.
3. 다르면 충돌을 반환하고 기존 최신본을 유지한다.
4. 새 데이터·메타데이터를 기록하고 검증한 뒤 최신 포인터를 마지막에 갱신한다.
5. 응답이 유실되면 같은 요청 ID·바이트로 확정 여부를 조회한다.
6. 과거 성공 요청의 재전송은 같은 결과를 반환하며 최신본을 과거로 되돌리지 않는다.

Drive 파일 생성과 Script Properties 갱신은 하나의 트랜잭션이 아니다. 생성만 된 미확정 후보를 보존하고 최신 포인터에서 이어지는 자료만 확정본으로 다뤘다. 단순히 파일이 존재하거나 이름이 같다는 이유로 업로드 성공을 판단하지 않았다.

## 10. 다음 구현에서 확인할 순서

1. 요구 사항을 ‘앱이 만드는 파일 관리’와 ‘기존 임의 파일 읽기’로 구분한다.
2. 기본 Apps Script 프로젝트에 Drive v3·drive.file만 설정한다.
3. 실제 계정·대상 폴더로 최소 진단을 실행한다.
4. 승인 실패 시 요청 범위와 남아 있는 과거 호출을 확인한다. 계정 보안 설정 변경이나 전체 Drive 권한 확대부터 시도하지 않는다.
5. 바이너리·한글 텍스트·빈 데이터의 JSON 왕복을 확인한다.
6. 폴더 이동·휴지통·권한 거부·손상 JSON·크기 초과를 거부하는지 확인한다.
7. 웹앱 배포 후 로그인·쿠키 없는 클라이언트에서 읽기와 리디렉션을 확인한다.
8. 잘못된 키 거부, 정상 쓰기, 동일 요청 재시도, 오래된 부모 충돌, 이력을 확인한다.
9. 실제 자료는 독립 백업 후 업로드하고 복제 폴더에 내려받아 해시를 비교한다.
10. 다른 PC·동시 요청·실제 응답 유실·최대 크기·할당량 경계를 별도로 검증한다.

이번에는 실제 웹앱의 쓰기·익명 읽기·키 거부·재시도·충돌·이력과 실제 파일의 복제본 복원까지 확인했다. 모든 계정 정책, 공유 드라이브, 대용량 경계, 두 PC 실사용, 실제 동시 경합까지 검증한 결과로 확대하지 않는다.
