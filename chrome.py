import logging
import os
import subprocess

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from util import is_command_available

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    filename="tasks.log",
    filemode="a",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def kill_chrome_processes() -> None:
    """
    현재 실행 중인 Chrome 프로세스 종료
    """
    try:
        if is_command_available("killall"):
            subprocess.run(["killall", "chrome"], check=False)
        else:
            logger.error(
                "이 운영 체제에서 Chrome 프로세스를 종료할 수 없습니다."
            )
            raise OSError("지원되지 않는 운영 체제입니다.")
    except subprocess.CalledProcessError as e:
        logger.exception(
            "Chrome 프로세스를 종료하는 도중 오류 발생.", exc_info=e
        )
    else:
        logger.debug("Chrome 프로세스가 정상적으로 종료되었습니다.")


def get_recent_chrome_profile() -> str:
    """
    최근 사용된 Chrome 프로필 경로를 반환
    """
    profile_base = os.path.expanduser("~/.config/google-chrome")
    logger.debug(f"Chrome 프로필 경로: {profile_base}")
    return profile_base


def set_driver_with_recent_profile() -> webdriver.Chrome:
    """
    Chrome 프로필을 사용하여 Selenium WebDriver를 초기화
    """
    options = Options()
    options.add_argument("--user-data-dir=" + get_recent_chrome_profile())

    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)
    logger.debug("Selenium WebDriver 초기화 완료.")
    return driver
