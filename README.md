# Poe2Deck

![Version](https://img.shields.io/badge/Version-1.0.0-green) ![Update](https://img.shields.io/badge/Update-2024.12.14-blue) ![Compatibility](https://img.shields.io/badge/Compatible-Steam_Deck-orange) ![GitHub all releases](https://img.shields.io/github/downloads/pepsizerosugar/Poe2Deck/total?color=purple)

* 카카오게임즈 Path Of Exile 2를 스팀덱에서 조금 더 편하게 플레이 할 수 있게 하는 도구입니다.
* 카카오게임즈 Path Of Exile 2를 **❗이미 설치❗**하고 플레이 하고 있는 유저를 대상으로 합니다.
    * 혹은 **게임을 설치까지 한 경우**도 사용할 수 있습니다.
    * **이 도구는 카카오게임즈 Path Of Exile 2의 설치 도구가 아닙니다.**

## Features

- **실행 옵션 입력 (일부)자동화**: 게임 실행에 필요한 인증 토큰과 유저 아이디를 자동으로 파싱하고 설정합니다.

## 0. Change Log

### 1.0.0 (2024.12.14)

- Initial release

## 1. Getting Started

### 1-1. Installation

1. 스팀덱 데스크톱 모드 진입
2. 브라우저를 열고 [릴리즈](https://github.com/pepsizerosugar/Poe2Deck/releases)에서 최신 버전의 `Poe2Deck.zip` 파일을 다운로드.
3. 다운로드 폴더에 진입.
4. 다운로드 한 파일 위에 마우스 커서를 올린 후 `왼쪽 클릭(R2)`을 두 번 빠르게 눌러 `Ark(압축 프로그램)` 열기.
   <br>
   <img src="./resources/1. 압축 풀기.png" alt="">
   <br>
5. 압축 풀기.

### 1-2. How to Use

1. Peo2Deck-main 폴더를 한 번 클릭 후 `오른쪽 클릭(L2)`을 누르고 `여기서 터미널 열기` 클릭.
   <br>
   <img src="./resources/2. 여기서 터미널 열기.png" alt="">
   <br>
2. Konsole이 열리면 `키보드(Steam + X)`를 열고 `sh run.sh`를 입력하고 `엔터(R2)`.
   <br>
   <img src="./resources/3. 명령어 입력.png" alt="">
   <br>
3. 키보드를 닫고 `POE2Deck` 창이 열렸는지 확인.
   <br>
   <img src="./resources/4. 프로그램 열림.png" alt="">
   <br>
4. 각 옵션은 다음과 같은 역할을 함.
    1. **Run Tasks**: 인증 토큰과 유저 아이디 설정 자동화 실행.
    2. **Show log**: 작업 로그 보기.
    3. **Quit**: 프로그램 종료.

### 2. Run Tasks

1. `Run Tasks` 옵션을 `더블 클릭(R2 빠르게 두 번)` 혹은 `한 번 클릭` 후 `확인`버튼 클릭.
   <br>
   <img src="./resources/5. 작업 실행.png" alt="">
   <br>
2. 진행사항을 확인하면서, 인증 요청 브라우저가 열리면 `사용자 인증` 진행.
   <br>
   <img src="./resources/6. 인증 진행.png" alt="">
   <br>
    1. 첫 프로그램 실행이면 `카카오 로그인`을 진행하지 않아 `카카오 로그인` 진행이 필요.
    2. `카카오 보안 인증`이더라도 토큰 파싱이 가능하니 그대로 진행.
    3. `카카오 보안 인증`외 다른 보안 인증에 대해서는 아직 확인되지 않았으니, 실행하고 `에러`가 발생하면 `이슈 보고` 부탁드립니다.
4. `Steam User Selection` 창이 나타나면 옵션을 적용할 스팀 계정을 선택하고 `확인`버튼 클릭.
   <br>
   <img src="./resources/7. 스팀 유저 선택.png" alt="">
   <br>
5. 적용에 성공하면 스팀이 재시작 되면서 `완료` 창이 나타남.
   <br>
   <img src="./resources/8. 마무리.png" alt="">
   <br>
   <img src="./resources/9. 완료.png" alt="">
   <br>
    1. 조건에 따라 실행 옵션 적용되는 방식이 다르니 **❗주의❗** 바랍니다.
        1. `PathOfExile_x64_KG.exe`의 파일을 이미 `비-스팀 게임으로 등록 한` 경우. | *이미 게임 잘 하고있는 경우*
            1. 이미 등록한 게임의 실행 옵션에 값을 업데이트.
        2. 게임은 `설치`했지만, 아직 비-스팀 게임으로 `등록하지 않은` 경우. | *설치만 하고 게임을 해보지 않은 경우*
            1. `PathOfExile_x64_KG.exe`의 위치를 검색하고, 해당 파일 위치로 비-스팀 게임 `자동 등록`.
                1. 이 경우 게임 이름은 `Path Of Exile 2`로 등록되며, **❗필수❗**로 호환 옵션을 설정 해야 함.
                    1. 스팀을 열고 `Path Of Exile 2` 이름의 게임을 찾기.
                    2. `오른쪽 클릭(L2)`을 누르고 `속성` 클릭.
                    3. `속성` 창이 나타나면 `대상`과 `시작 모드`를 확인해서 실제 게임 실행 파일 위치가 맞는지 **❗꼭❗**확인.
                       <br>
                       <img src="./resources/12. 파일 위치.png" alt="">
                       <br>
                       1. `대상`에 `PathOfExile_x64_KG.exe`의 위치가 맞는지 확인.
                       2. `시작 모드`에 `PathOfExile_x64_KG.exe`가 위치하는 폴더가 맞는지 확인.
                    4. `호환` 클릭.
                    5. `강제로 특정 Steam 플레이 호환 도구 사용하기` 체크.
                    6. `옵션`에서 `Proton Experimental` 선택 후 속성 창 닫기.
                       <br>
                       <img src="./resources/11. 호환.png" alt="">
                       <br>
7. 완료 창을 닫고 `Quit` 옵션을 선택하여 프로그램 종료.

### 3. Show log

1. `Show log` 옵션을 `더블 클릭(R2 빠르게 두 번)` 혹은 `한 번 클릭` 후 `확인`버튼 클릭.
2. `터치`로 스크롤하여 작업 실행 로그를 확인.
   <br>
   <img src="./resources/10. 로그.png" alt="">
   <br>
3. `취소` 혹은 `확인`을 눌러 다시 메인 화면으로 진입.
4. `Quit` 옵션을 선택하여 프로그램 종료.
