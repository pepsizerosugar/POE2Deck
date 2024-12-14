import sys
import logging
import json

from auth import get_authorization_code, get_access_token
from chrome import kill_chrome_processes, set_driver_with_recent_profile
from steam import get_shortcuts_vdf_path, update_shortcuts, get_steam_user_personas, kill_steam_and_restart_background

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    filename="tasks.log",
    filemode="a",
    encoding="utf-8",
)

logger = logging.getLogger(__name__)


def task_kill_chrome():
    """
    Chrome 프로세스 종료
    """
    logger.info("Chrome 프로세스 종료 시도 중...")
    kill_chrome_processes()
    logger.debug("Chrome 프로세스 종료 완료.")
    print("TASK_1=1")


def task_authorization():
    """
    access_token, user_id 파싱 및 생성
    """
    logger.info("인증 절차 시작...")
    driver = set_driver_with_recent_profile()

    access_token, user_id = get_authorization_code(driver)

    if access_token is None or user_id is None:
        logger.error("인증 실패: access_token 또는 user_id가 없습니다.")
        print("TASK_2=0")
    else:
        logger.debug(f"인증 성공: access_token: {access_token}")
        logger.debug(f"획득한 user_id: {user_id}")

        print("TASK_2=1")
        print(f"ACCESS_TOKEN={access_token}")
        print(f"USER_ID={user_id}")



def task_access_token():
    """
    accessToken 파싱
    """
    logger.info("Access Token 요청 중...")
    if len(sys.argv) < 5:
        logger.error("Access Token 요청에 필요한 인자가 부족합니다.")
        print("TASK_3=0")
        sys.exit(1)

    auth_code = sys.argv[2]
    cookies_str = sys.argv[3]
    input_code_verifier = sys.argv[4]

    logger.debug(
        f"auth_code={auth_code}, cookies_str={cookies_str}, code_verifier={input_code_verifier}"
    )
    cookies = {
        c.split("=")[0].strip(): c.split("=")[1].strip()
        for c in cookies_str.split("; ")
        if "=" in c
    }

    access_token = get_access_token(auth_code, input_code_verifier, cookies)
    if access_token is None:
        logger.error("Access Token 획득 실패.")
        print("TASK_3=0")
    else:
        logger.debug(f"Access Token 획득 성공: {access_token}")
        print("TASK_3=1")
        print(f"ACCESS_TOKEN={access_token}")


def task_parse_steam_persona():
    """
    Steam 유저 데이터 파싱
    """
    logger.info("Steam 유저 데이터 가져오는 중...")
    user_personas = get_steam_user_personas()

    if user_personas is None or {}:
        logger.error("Steam 유저 데이터 가져오기.")
        print("TASK_4=0")
    else:
        logger.debug(f"Steam 유저 데이터 가져오기 성공: {user_personas}")
        print("TASK_4=1")
        print(
            "USER_PERSONAS="
            + json.dumps(user_personas, ensure_ascii=False)
        )


def task_update_shortcuts():
    """
    시작옵션에 accessToken 추가
    """
    logger.info("Steam Shortcuts 업데이트 중...")
    if len(sys.argv) < 5:
        logger.error("Shortcuts 업데이트에 필요한 인자가 부족합니다.")
        print("TASK_5=0")
        sys.exit(1)

    access_token = sys.argv[2]
    logger.debug(f"Shortcuts 업데이트 시 사용할 Access Token: {access_token}")

    user_id = sys.argv[3]
    logger.debug(f"Shortcuts 업데이트 시 사용할 User Id: {user_id}")

    user_persona = json.loads(sys.argv[4])
    logger.debug(f"Shortcuts 업데이트 시 사용할 Steam user persona: {user_persona}")

    result = update_shortcuts(
        file_path=get_shortcuts_vdf_path(next(iter(user_persona))),
        game_name="Path of Exile 2",
        launch_options=f"--kakao {access_token} {user_id}",
    )
    if result:
        logger.debug("Shortcuts 업데이트 성공.")
        print("TASK_5=1")
    else:
        logger.error("Shortcuts 업데이트 실패.")
        print("TASK_5=0")


def task_kill_steam_and_restart():
    """
    shortcuts 업데이트 후 설정 적용을 위해 steam 종료 및 재시작
    """
    logger.info("설정 적용을 위해 Steam을 종료 후 재시작합니다...")

    result = kill_steam_and_restart_background()

    if result:
        logger.debug("Steam 종료 후 재시작 성공.")
        print("TASK_6=1")
    else:
        logger.error("Steam 종료 후 재시작 실패.")
        print("TASK_6=0")



if __name__ == "__main__":
    task_name = sys.argv[1]
    logger.info(f"실행할 태스크: {task_name}")

    if task_name == "kill_chrome":
        task_kill_chrome()
    elif task_name == "authorization":
        task_authorization()
    elif task_name == "access_token":
        task_access_token()
    elif task_name == "steam_persona":
        task_parse_steam_persona()
    elif task_name == "update_shortcuts":
        task_update_shortcuts()
    elif task_name == "restart_steam":
        task_kill_steam_and_restart()
    else:
        logger.error(f"알 수 없는 태스크: {task_name}")
        sys.exit(1)
