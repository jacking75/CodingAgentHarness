# NEW 별도 게임과 세이브

2026-10-16. 사용자가 원본 Eden2에 NEW 전용 데이터를 추가하도록 승인한 구성이다.

## 실행과 저장 위치

평소 사용하는 `G:\Emulators\Eden2\eden.exe`에서 **The Legend of Zelda Tears of the Kingdom NEW**를 선택한다. `G:\working_zelda\runtime\Eden\eden.exe`는 검증용 복사본이며 실사용에 필요하지 않다.

| 항목 | 값 |
|---|---|
| NEW ROM | `G:\Emulators\switch_roms\The Legend of Zelda Tears of the Kingdom NEW.nsp` |
| NEW 내부 ID | `0100F2C0115BE000` |
| 기존 게임 내부 ID | `0100F2C0115B6000` |
| 버전 | 1.4.3, 업데이트를 통합한 독립 NSP |
| 크기 | 17,134,260,944바이트 |
| SHA-256 | `b4893e5981f579b1188a9592ba43d0f4f59dafeb9f95d681fbcea99f51f9668f` |
| NEW 개별 설정 | `G:\Emulators\Eden2\user\config\custom\0100F2C0115BE000.ini` |
| NEW 실제 세이브 | `G:\Emulators\SaveData\0000000000000000\0C870748C8EE58A137431304F378FC59\0100F2C0115BE000` |

Eden2의 `user/nand/user/save`는 기존 외부 SaveData 연결을 사용한다. NEW의35파일은 실제 파일 복사본이며 기존 파일과 파일 ID가 다르다. 사용자 프로필은 같고 게임 ID와 세이브 소유자 ID가 달라 이후 저장은 독립적이다. NEW 설정은 기존 게임의 개별 설정을 복사해 기존 입력·그래픽 설정을 따른다. 기존 전역 설정·ROM·개별 설정·세이브·모드는 수정하지 않았다.

배치한35파일은 실제 기존 Eden2의 저장 이력이다. 최신 수동 저장은2026-10-14 23:53 마야마츠의 사당 앞이다. 과거 비행 실험의2026-10-15 동하테르 벼랑은 검증용 임시 체크포인트이며 배치한 NEW에는 남기지 않았다. 이후 사용자가 NEW에서 저장한 내용을 초기 복사본으로 자동 복원하면 안 된다.

## 통합한 변경

- 개선 기계식 날개·56노드 비행 액션·20노드 접지 복원 스케줄러를 유지했다. 설치 모드12파일 중 실제 RomFS 자산10파일을 통합했다. 나머지2파일은 빌드 보고서다.
- Player.pack에 공격2배·방어+24를 유지하며 음식 지속시간을 보존했다.
- 지구력·장비 내구도 명령을 main NSO의 다섯 지정 위치에 통합했다. 내구도 trampoline이 있는 text 마지막 페이지를 명시적으로 포함했다. 원래 모듈 이름·메모리 배치·Build ID를 유지하고 세그먼트 압축·해시를 다시 생성했다.
- NEW 전용 외부 모드나 치트 파일은 필요하지 않다. 기존 `manage_t10_cheats.py`는 작업실의 기존 ID 모드만 관리하며 NEW ROM을 변경하지 않는다.

조작은 기존 비행 모드와 같다. 공중에서 X로 전개, ZL로 상승, R로 하강, 왼쪽 스틱으로 카메라 기준 수평 이동, 중립으로 호버, B로 해제한다. 착지 후 R은 원래 투척 입력으로 돌아간다. 기존 지형·카메라 간섭 및 미검증 상황은 T10의 한계를 유지한다.

## 검증과 근거

- `verify_new_package.py`: 모든 NCA 섹션 헤더·PFS·IVFC 콘텐츠 해시, 변경 자산10개, NSO·NPDM·NACP의 ID와16언어 표시 이름, 세이브 소유자 ID를 검사했다. Nintendo 서명 유효성을 주장하는 검사는 아니다.
- 원본과 실행 파일 SHA-256이 같은 복사본 Eden의1280×760 창에서 NEW·1.4.3 부팅과 실제 원본 저장 이어하기를 확인했다. 읽기 전용 GDB로 다섯 패치의 런타임 일치를 확인했다.
- 실제 NEW 수동 저장은 NEW의 `slot_03/caption.sav`, `footprint.sav`, `progress.sav`만 변경했다. 기존 Eden2 세이브와 기존 lab 세이브는 그대로였다.
- 별도 임시 벼랑 저장에서 외부 NEW 모드 파일 없이115샘플·상승11.6558m·최종 호버 XYZ 범위0.04584m·해제/재전개 중력 복원을 통과했다. 실험 저장은 배치용에 쓰지 않았다.
- 배치 전후 기존2,373파일 메타데이터와156설정/세이브 SHA-256 불변 검사를 통과했다. NEW35파일은 원본과 같은 내용이며 다른 파일 ID다. 실사용 원본 Eden2 자체를 실행해 전역 설정·로그를 바꾸지는 않았다.
- 검증용 Eden·가상 패드를 종료하고 임시 GDB·검증 설정을 복원했다. 기존 T10 검사도 다시 통과했다.

상태·해시·검증·배치 보고는 `private/build/t11-new-title/`에 있다. `validation.json`, `deployment.json`, `package-verification.json`, `save-isolation-verification.json`, `flight-verification.json`이 핵심 근거다. 화면·영상은 `artifacts/t11-new-*`다. 원래 세이브 보관본은 `private/baselines/t11-original-save`, 시험 저장 보관본은 `private/analysis/t11-saved-proof`다. 게임·키·세이브·NSP·NCA는 Git이나 배포물에 포함하지 않는다.

## 생성 경로와 중간 실패

`prepare_new_title.py`가 기존 비공개 NSP에서 NCA와 전체1.4.3 RomFS304,243파일을 추출하고, 이름·ID·코드·자산을 변경했다. `build_new_romfs.py`가 Windows에서 작은 파일을 병렬로 읽어304,246파일의 단일 RomFS 이미지를 만들었다. `pack_new_title_native.py`가 Windows에서 PFS·IVFC·CNMT·NCA·NSP를 스트리밍 생성했다. WSL Ubuntu의 기존 Python cryptography는3KiB NCA 헤더의 AES-XTS 암복호화만 맡았다. `decrypt_new_headers.py`가 실제 NSP 헤더를 독립적으로 복호화하고, `verify_new_package.py`가 Windows에서 전체 콘텐츠를 재검사했다. `deploy_new_title.py`는 검증 통과 패키지와 새로운 저장·설정 경로만 추가하며 기존 파일 덮어쓰기를 거절한다.

포맷 참조는 [hacPack](https://github.com/DarkMatterCore/hacPack) 커밋 `e506cb58b7843d86df7518156debd28f3b575638`과 Eden의 로컬 조사 소스다. GPL 라이선스·원본·도구 변경 기록은 `tools/hacpack-upstream`에 보관했다. 최종 패키징은 hacPack 실행 결과를 사용하지 않았다.

초기 도구 출력의 `Content Type` 표기 파싱을 수정했다. NSO의 모듈 이름과 text 끝 빈 페이지도 실제 구조에 맞춰 보존했다. hacPack의 연결 리스트 삽입 정렬과 WSL의 많은 파일/대용량 반복 I/O에서 병목을 확인해 최종 네이티브 경로로 전환했다. 중단된 도구는 명령줄·경로를 확인한 해당 프로세스만 종료했으며, 실패한 패키지를 배치하지 않았다.

대용량 중간 자료는 이번 작업에서 생성한 사용자 Temp의 단일 `working-zelda-t11-*` 폴더에 두었다. 정리는 `cleanup_new_title_scratch.py`가 배치 성공·정확한 임시 루트·reparse point 부재를 검사한 후 그 폴더만 제거한다. 최종 정리 결과는 `private/build/t11-new-title/scratch-cleanup.json`을 따른다. 기존 C01 정리 스크립트를 재실행하지 않는다.
