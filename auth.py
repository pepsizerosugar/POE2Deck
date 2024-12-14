import base64
import hashlib
import logging
import os
from typing import Tuple, Optional
from urllib.parse import urlparse, parse_qs

import requests
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    filename="tasks.log",
    filemode="a",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)

GAME_START_URL = "https://pubsvc.game.daum.net/gamestart/poe2.html"
SECURITY_URL = "https://security-center.game.daum.net/auth"
TOKEN_URL = "https://poe2-gamestart-web-api.game.daum.net/token/poe2"
AUTH_URL_TEMPLATE = (
    "https://poe.game.daum.net/oauth/authorize"
    "?client_id=internal"
    "&redirect_uri=https%3A%2F%2Fpoe2.game.daum.net%2Fkr/home"
    "&response_type=internal"
    "&scope=internal"
    "&state=random_state_string"
    "&code_challenge_method=S256&code_challenge={code_challenge}"
)
MAX_WAIT_TIME = 30
POLL_FREQUENCY = 0.5


def generate_code_verifier() -> str:
    """
    code_verifier 생성
    """
    verifier = (
        base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode("utf-8")
    )
    logger.debug(f"생성된 code_verifier: {verifier}")
    return verifier


def generate_code_challenge(verifier: str) -> str:
    """
    code_challenge 생성
    """
    challenge = (
        base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode("utf-8")).digest()
        )
        .rstrip(b"=")
        .decode("utf-8")
    )
    logger.debug(f"생성된 code_challenge: {challenge}")
    return challenge


def set_cookies(session: requests.Session, cookies) -> None:
    """
    Selenium 쿠키를 requests 세션에 설정
    """
    for cookie in cookies:
        session.cookies.set(cookie["name"], cookie["value"])


def create_session(driver: WebDriver) -> requests.Session:
    """
    세션 생성 및 쿠키 설정
    """
    session = requests.Session()
    selenium_cookies = driver.get_cookies()
    set_cookies(session, selenium_cookies)
    return session


def get_access_token_and_user_id_from_api(
    driver: WebDriver, session: requests.Session, txid: Optional[str] = None
) -> Tuple[Optional[str], Optional[int]]:
    """
    API를 통해 access_token, user_id 파싱
    """
    try:
        url = f"{TOKEN_URL}?actionType=user"
        headers = {
            "accept": "application/json, text/plain, */*",
            "user-agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/128.0.0.0 Whale/3.28.266.14 Safari/537.36"
            ),
            "referer": "https://pubsvc.game.daum.net/",
            "origin": "https://pubsvc.game.daum.net",
        }

        body = {
            "txId": txid,
            "code": None,
            "webdriver": bool(txid),
        }

        logger.debug(f"Request body: {body}")
        logger.debug(f"Session cookies: {session.cookies.get_dict()}")

        response = session.post(url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        logger.debug(f"Response data: {data}")

        status = data.get("status")
        if status == "NEED_SECURITYCENTER_AUTH":
            url = data.get("url")
            return process_user_security_auth(driver, session, url)
        elif status == "PASS":
            token = data.get("token")
            mid = data.get("mid")
            logger.info(f"API를 통해 token 파싱: {token}")
            logger.info(f"API를 통해 mid 파싱: {mid}")
            return token, mid
        else:
            logger.error(f"예상치 못한 status: {status}")
            return None, None
    except requests.HTTPError as http_err:
        logger.error(f"API 요청 실패: {http_err}")
    except Exception as e:
        logger.error(f"access_token, user_id 파싱 실패: {e}")
    return None, None


def wait_for_url_change(
    driver: WebDriver, target_url: str, timeout: int = MAX_WAIT_TIME
) -> bool:
    """
    특정 URL로의 변경을 기다림
    """
    try:
        WebDriverWait(driver, timeout, POLL_FREQUENCY).until(
            EC.url_contains(target_url)
        )
        return True
    except:
        return False


def process_user_security_auth(
    driver: WebDriver, session: requests.Session, url: str
) -> Tuple[Optional[str], Optional[int]]:
    """
    사용자 보안 센터 인증 처리
    """
    try:
        driver.get(url)
        logger.debug("유저 인증 진행 중...")

        if wait_for_url_change(driver, SECURITY_URL):
            selenium_cookies = driver.get_cookies()
            set_cookies(session, selenium_cookies)

            if wait_for_url_change(driver, GAME_START_URL):
                current_url = driver.current_url
                logger.debug(f"유저 인증 완료: {current_url}")

                parsed_url = urlparse(current_url)
                query_params = parse_qs(parsed_url.query)
                txid = query_params.get("txId", [None])[0]

                selenium_cookies = driver.get_cookies()
                set_cookies(session, selenium_cookies)

                logger.debug(f"리다이렉트 감지: {current_url}")
                return get_access_token_and_user_id_from_api(
                    driver, session, txid
                )
        else:
            logger.error("유저 인증 실패")
            return None, None
    except Exception as e:
        logger.error(f"token, mid 파싱 실패: {e}")
    return None, None


def process_user_auth(
    driver: WebDriver, session: requests.Session
) -> Tuple[Optional[str], Optional[int]]:
    """
    사용자 인증 처리
    """
    try:
        driver.get(GAME_START_URL)
        logger.debug("유저 인증 페이지 로드 중...")

        if wait_for_url_change(driver, GAME_START_URL):
            current_url = driver.current_url
            logger.debug(f"current_url-1: {current_url}")

            if GAME_START_URL in current_url:
                # 이미 인증 마친 상태, 혹은 카카오 인증으로 인증 필요로 하는 상태
                logger.debug("유저 인증 완료 혹은 카카오 인증 필요")
                return get_access_token_and_user_id_from_api(driver, session)
            elif SECURITY_URL in current_url:
                # 인증 필요 상태
                logger.debug("유저 인증 필요")
                return process_user_security_auth(driver, session, current_url)
        else:
            logger.error("유저 인증 실패")
            return None, None
    except Exception as e:
        logger.error(f"사용자 인증 처리 중 오류 발생: {e}")
    return None, None


def get_authorization_code(
    driver: WebDriver,
) -> Tuple[Optional[str], Optional[int]]:
    """
    access_token, user_id 파싱
    """
    try:
        logger.info("code_verifier와 code_challenge 생성")
        code_verifier = generate_code_verifier()
        code_challenge = generate_code_challenge(code_verifier)

        auth_url = AUTH_URL_TEMPLATE.format(code_challenge=code_challenge)
        logger.info("Authorization Code 획득을 위한 페이지 로딩 중...")
        driver.get(auth_url)

        if wait_for_url_change(driver, "https://poe2.game.daum.net/kr/home"):
            current_url = driver.current_url
            logger.debug(f"리다이렉트 감지: {current_url}")
            session = create_session(driver)
            return process_user_auth(driver, session)
        else:
            logger.error("Authorization Code 획득 실패")
            return None, None
    except Exception as e:
        logger.error(f"Authorization Code 획득 중 오류 발생: {e}")
    return None, None
