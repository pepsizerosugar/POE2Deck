#!/bin/bash

set -o pipefail

LOG_FILE_PATH="$(dirname "$0")/tasks.log"

is_installed() {
    pacman -Q "$1" &>/dev/null
}

setup_virtualenv() {
    VENV_DIR="$(dirname "$0")/venv"

    if [ ! -d "$VENV_DIR" ]; then
        echo "# 가상 환경 생성 중..."
        python3 -m venv "$VENV_DIR"
        if [ $? -ne 0 ]; then
            echo "# 가상 환경 생성 실패"
            exit 1
        fi
    fi
    if [ ! -f "$VENV_DIR/bin/pip" ]; then
        echo "# 가상 환경에 pip 설치 중..."
        curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
        if [ $? -ne 0 ]; then
            echo "# pip 설치 스크립트 다운로드 실패"
            exit 1
        fi
        "$VENV_DIR/bin/python" /tmp/get-pip.py
        if [ $? -ne 0 ]; then
            echo "# pip 설치 실패"
            exit 1
        fi
    fi

    "$VENV_DIR/bin/pip" install --upgrade pip

    echo "# 필요한 패키지 설치 중..."
    if ! "$VENV_DIR/bin/pip" install vdf blinker==1.7.0 psutil selenium selenium-wire requests; then
        echo "# 패키지 설치 실패"
        exit 1
    fi
}

run_tasks() {
    VENV_DIR="$(dirname "$0")/venv"

    (
        echo "0"
        echo "# 가상 환경 설정 중..."
        setup_virtualenv

        echo "5"
        echo "# Chromium 설치 확인 중..."
        if is_installed chromium; then
            echo "# Chromium 이미 설치됨. 스킵..."
        else
            echo "# Chromium 설치 중..."
            if ! sudo pacman -S --noconfirm chromium; then
                echo "# Chromium 설치 실패"
            fi
        fi

        echo "10"
        echo "# Selenium 설치 확인 중..."
        if "$VENV_DIR/bin/pip" show selenium &>/dev/null; then
            echo "# Selenium 이미 설치됨. 스킵..."
        else
            echo "# Selenium 설치 중..."
            if ! "$VENV_DIR/bin/pip" install selenium; then
                echo "# Selenium 설치 실패"
                exit 1
            fi
        fi

        echo "15"
        echo "# Requests 설치 확인 중..."
        if "$VENV_DIR/bin/pip" show requests &>/dev/null; then
            echo "# Requests 이미 설치됨. 스킵..."
        else
            echo "# Requests 설치 중..."
            if ! "$VENV_DIR/bin/pip" install requests; then
                echo "# Requests 설치 실패"
                exit 1
            fi
        fi

        echo "20"
        echo "# Blinker 설치 확인 중..."
        if "$VENV_DIR/bin/pip" show blinker &>/dev/null; then
            echo "# Blinker 이미 설치됨. 스킵..."
        else
            echo "# Blinker 설치 중..."
            if ! "$VENV_DIR/bin/pip" install blinker; then
                echo "# Blinker 설치 실패"
                exit 1
            fi
        fi

        echo "25"
        echo "# Seleniumwire 설치 확인 중..."
        if "$VENV_DIR/bin/pip" show selenium-wire &>/dev/null; then
            echo "# Seleniumwire 이미 설치됨. 스킵..."
        else
            echo "# Seleniumwire 설치 중..."
            if ! "$VENV_DIR/bin/pip" install selenium-wire; then
                echo "# Seleniumwire 설치 실패"
                exit 1
            fi
        fi

        echo "30"
        echo "# Vdf 설치 확인 중..."
        if "$VENV_DIR/bin/pip" show vdf &>/dev/null; then
            echo "# Vdf 이미 설치됨. 스킵..."
        else
            echo "# Vdf 설치 중..."
            if ! "$VENV_DIR/bin/pip" install vdf; then
                echo "# Vdf 설치 실패"
                exit 1
            fi
        fi

        echo "35"
        echo "# Psutil 설치 확인 중..."
        if "$VENV_DIR/bin/pip" show psutil &>/dev/null; then
            echo "# Psutil 이미 설치됨. 스킵..."
        else
            echo "# Psutil 설치 중..."
            if ! "$VENV_DIR/bin/pip" install psutil; then
                echo "# Psutil 설치 실패"
                exit 1
            fi
        fi

        echo "40"
        echo "# 패키지 설치 완료. Chrome 프로세스 종료 시도..."
        TASK_RESULT=$("$VENV_DIR/bin/python" tasks.py kill_chrome)
        echo "$TASK_RESULT"
        if ! echo "$TASK_RESULT" | grep -q "TASK_1=1"; then
            echo "# Chrome 프로세스 종료 실패."
        fi

        echo "50"
        echo "# 브라우저 인증 진행 중...\n브라우저가 열리고 인증 후 잠시 기다려주세요."
        TASK_RESULT=$("$VENV_DIR/bin/python" tasks.py authorization)
        echo "$TASK_RESULT"
        if ! echo "$TASK_RESULT" | grep -q "TASK_2=1"; then
            echo "# Auth Code 획득 실패."
            exit 1
        fi
#         AUTH_CODE=$(echo "$TASK_RESULT" | grep "^AUTH_CODE=" | cut -d'=' -f2-)
#         AUTH_COOKIES=$(echo "$TASK_RESULT" | grep "^AUTH_COOKIES=" | cut -d'=' -f2-)
#         CODE_VERIFIER=$(echo "$TASK_RESULT" | grep "^CODE_VERIFIER=" | cut -d'=' -f2-)
#         CODE_CHALLENGE=$(echo "$TASK_RESULT" | grep "^CODE_CHALLENGE=" | cut -d'=' -f2-)
        ACCESS_TOKEN=$(echo "$TASK_RESULT" | grep "^ACCESS_TOKEN=" | cut -d'=' -f2-)
        USER_ID=$(echo "$TASK_RESULT" | grep "^USER_ID=" | cut -d'=' -f2-)

#         echo "60"
#         echo "# Access Token 요청 중..."
#         TASK_RESULT=$("$VENV_DIR/bin/python" tasks.py access_token "$AUTH_CODE" "$AUTH_COOKIES" "$CODE_VERIFIER")
#         echo "$TASK_RESULT"
#         if ! echo "$TASK_RESULT" | grep -q "TASK_3=1"; then
#             echo "# Access Token 요청 실패."
#             exit 1
#         fi
#         ACCESS_TOKEN=$(echo "$TASK_RESULT" | grep "^ACCESS_TOKEN=" | cut -d'=' -f2-)

        echo "70"
        echo "# Steam 유저 데이터 가져오는 중..."
        TASK_RESULT=$("$VENV_DIR/bin/python" tasks.py steam_persona)
        echo "$TASK_RESULT"
        USER_PERSONAS=$(echo "$TASK_RESULT" | grep "USER_PERSONAS=" | cut -d'=' -f2-)
        if ! echo "$TASK_RESULT" | grep -q "TASK_4=1"; then
            echo "# Steam 유저 데이터 가져오기 실패."
            exit 1
        fi
        if echo "$USER_PERSONAS" | jq empty 2>/dev/null; then
            echo "# 유효한 JSON 데이터 확인됨."
        else
            echo "# USER_PERSONAS에 유효하지 않은 JSON 데이터가 포함되어 있음."
            exit 1
        fi
        if [[ -n "$USER_PERSONAS" ]]; then
            options=()
            while IFS="=" read -r personaId nickname; do
                options+=("$personaId" "$nickname")
            done < <(echo "$USER_PERSONAS" | jq -r 'to_entries[] | "\(.key)=\(.value)"')

            SELECTED_PERSONA=$(zenity --list --title="Steam User Selection" \
                --text="설정을 적용할 유저 선택:" \
                --column="Persona ID" --column="Nickname" "${options[@]}" \
                --width=500 --height=300)

            if [[ ! -n "$SELECTED_PERSONA" ]]; then
                echo "# 선택 데이터 없음."
                exit 1
            fi
        else
            echo "# 유저 데이터 없음."
            exit 1
        fi

        echo "80"
        echo "# Steam Shortcuts 업데이트 중..."
        TASK_RESULT=$("$VENV_DIR/bin/python" tasks.py update_shortcuts "$ACCESS_TOKEN" "$USER_ID" "$USER_PERSONAS")
        echo "$TASK_RESULT"
        if ! echo "$TASK_RESULT" | grep -q "TASK_5=1"; then
            echo "# Shortcuts 업데이트 실패."
            exit 1
        fi

        echo "90"
        echo "# Steam 재시작 중..."
        TASK_RESULT=$("$VENV_DIR/bin/python" tasks.py restart_steam)
        echo "$TASK_RESULT"
        if ! echo "$TASK_RESULT" | grep -q "TASK_6=1"; then
            echo "# Shortcuts 업데이트 실패."
            exit 1
        fi

        echo "100"
        echo "# 작업이 완료되었습니다!"

    ) | zenity --progress \
        --title="전체 작업 진행 상황" \
        --text="작업 진행 중..." \
        --percentage=0 \
        --auto-close \
        --width=300 \
        --height=150

    EXIT_CODE=$?

    if [ "$EXIT_CODE" -eq 0 ]; then
        zenity --info --title="완료" --text="모든 작업이 성공적으로 완료되었습니다.\nSteam이 재시작 될 때 까지 기다려주세요." --width=300
    else
        zenity --error --title="오류" --text="작업 중 오류가 발생했습니다." --width=300
    fi
}

while opt=$(zenity --width=500 --height=300 --title="POE2Deck" --list --column="Options" "Run Tasks" "Show log" "Quit"); do
    case "$opt" in
        "Run Tasks" )
            run_tasks
            ;;
        "Show log" )
            if [ -f "$LOG_FILE_PATH" ]; then
                zenity --text-info --title="작업 로그" --filename="$LOG_FILE_PATH" --width=600 --height=400
            else
                zenity --error --title="로그 파일 없음" --text="작업 로그 파일이 존재하지 않습니다." --width=300
            fi
            ;;
        "Quit" )
            break
            ;;
        * )
    esac
done
