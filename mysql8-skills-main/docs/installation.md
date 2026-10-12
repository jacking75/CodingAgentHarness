# Codex CLI 설치 및 배포

## 전제

Codex CLI 설치·로그인은 회사가 허용한 절차로 준비한다. 이 문서는 이미 CLI가 준비된 환경의 스킬 설치를 다룬다. `codex --version`으로 버전을 기록한다. 제작 환경에서 확인한 CLI는 0.153.4이며 최소 지원 버전을 뜻하지 않는다.

공식 문서 기준 프로젝트 스킬 경로는 `.agents/skills`, 개인 경로는 `$HOME/.agents/skills`다. 이 묶음은 팀이 버전을 함께 검토할 수 있는 프로젝트 설치를 우선한다. 구형 CLI에서 탐색되지 않으면 버전과 회사 업데이트 정책을 확인한다. [Codex 공식 안내](https://learn.chatgpt.com/docs/build-skills)

## Windows PowerShell: 프로젝트 설치

아래에서 `D:\Repos\YourGame`만 실제 프로젝트 루트로 바꾼다. 현재 묶음 경로가 다르면 source도 바꾼다. 폴더 전체를 중첩 복사하지 않고 스킬 디렉터리들을 `.agents/skills` 바로 아래에 넣는다.

```powershell
$dbSkillSource = 'E:\Download\codex-working\mysql8-codex-skills\skills'
$dbProjectRoot = 'D:\Repos\YourGame'
if (-not (Test-Path -LiteralPath $dbProjectRoot -PathType Container)) {
    throw '실제 프로젝트 경로를 먼저 지정해야 한다.'
}
$dbSkillTarget = Join-Path $dbProjectRoot '.agents\skills'
$dbSkillFolders = @(Get-ChildItem -LiteralPath $dbSkillSource -Directory)
foreach ($dbSkillFolder in $dbSkillFolders) {
    if (Test-Path -LiteralPath (Join-Path $dbSkillTarget $dbSkillFolder.Name)) {
        throw "동일 이름의 스킬이 이미 있다. 업데이트 절차를 확인한다: $($dbSkillFolder.Name)"
    }
}
New-Item -ItemType Directory -Path $dbSkillTarget -Force | Out-Null
foreach ($dbSkillFolder in $dbSkillFolders) {
    Copy-Item -LiteralPath $dbSkillFolder.FullName -Destination $dbSkillTarget -Recurse
}
```

선택 설치는 `$dbSkillFolders`를 다음으로 바꾸고 나머지 과정을 사용한다.

```powershell
$dbSelectedSkills = @('mysql8-schema-review', 'mysql8-query-tuning', 'mysql8-transaction-review')
$dbSkillFolders = @(Get-ChildItem -LiteralPath $dbSkillSource -Directory |
    Where-Object { $_.Name -in $dbSelectedSkills })
```

기대 경로는 `<프로젝트>/.agents/skills/mysql8-schema-review/SKILL.md`다. 개인 설치가 꼭 필요하면 대상만 `Join-Path $HOME '.agents\skills'`로 바꾼다. 같은 이름을 개인과 프로젝트에 중복 설치하지 않는다. 동일 이름이 자동 병합되거나 프로젝트 버전으로 교체된다고 가정하지 않는다.

## 팀 문서 설치

기존 `docs/db` 문서는 덮어쓰지 말고 다음 템플릿 내용을 병합한다.

| 묶음 원본 | 프로젝트 목적지 |
|---|---|
| templates/team-profile.md | docs/db/team-profile.md |
| templates/team-rules.md | docs/db/team-rules.md |
| templates/workload.md | docs/db/workload.md |
| templates/operations.md | docs/db/operations.md |

`templates/AGENTS-snippet.md`의 코드 블록 내용은 기존 프로젝트 AGENTS.md에 필요한 부분만 병합한다. AGENTS.md 전체를 교체하지 않는다. 프로필이 없어도 일반 정적 검토는 가능하지만 팀 기준 준수와 DB 접속 환경은 미확인이다.

## 확인과 첫 호출

```powershell
Set-Location -LiteralPath $dbProjectRoot
codex
```

Codex 대화 입력란에서 다음을 순서대로 사용한다. `$...`는 PowerShell 명령이 아니라 스킬 호출이다.

```text
/skills
```

```text
$mysql8-schema-review .agents/skills/mysql8-schema-review/references/example.md의
가상 입력만 검토해줘. DB 접속과 SQL 실행은 하지 마.
사용한 스킬 경로와 팀 프로필 경로 또는 미발견 상태도 알려줘.
```

스킬이 안 보이면 중첩 폴더, SKILL.md 이름, YAML name/description, 중복 설치를 확인한다. CLI를 재시작해 다시 확인한다. 자연어 자동 선택도 가능하지만 파일럿 측정 때는 명시 호출로 조건을 고정한다.

## WSL에서 사용하는 팀

WSL의 Codex는 WSL 파일 경로·홈을 사용한다. Windows의 E:는 일반적으로 `/mnt/e`로 보이지만 실제 마운트를 확인한다. WSL 프로젝트의 `.agents/skills`에 같은 스킬 폴더를 복사한다. Windows 개인 설치와 WSL 개인 설치가 자동 공유된다고 가정하지 않는다. Windows 서비스 확인은 프로필에 명시된 로컬 Windows DB를 실제 사용할 때만 적용한다.

## 업데이트와 되돌리기

1. DA가 배포 버전과 변경 이력을 확정한다. 신규 버전은 별도 경로에서 먼저 검토한다.
2. 팀은 현재 스킬·프로필을 Git에 기록하거나 `.agents/skills` 바깥에 백업한다. 같은 name의 백업을 탐색 경로 안에 두지 않는다.
3. 스킬의 변경분만 비교·적용한다. 팀 프로필과 기존 AGENTS.md는 보존한다. 이름이 바뀌거나 제거된 스킬도 확인한다.
4. `/skills` 및 연습 사례를 확인하고 스킬 버전을 팀 프로필에 기록한다.
5. 회귀가 있으면 이전 Git 버전의 스킬 폴더만 복원한다. DB 롤백 작업과는 무관하다.

제거는 설치한 `mysql8-*` 중 실제 이 묶음에서 설치한 폴더만 확인해 제거하고 AGENTS.md 참조를 정리한다. `.agents/skills` 전체를 삭제하지 않는다.

## 배포 방식

파일럿은 사내 Git 저장소에 이 Markdown 묶음을 두고 버전 태그 또는 회사 배포 저장소로 전달한다. 팀 저장소로 복사한 스킬은 자동 업데이트되지 않는다. DA가 배포하고 개발팀이 검토 후 반영한다. 외부 업로드는 이 묶음의 사용 범위에 포함하지 않는다. 정식 플러그인 패키징은 이번 범위에 포함하지 않았다.
