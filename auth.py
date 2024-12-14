import base64
import hashlib
import os
import time
import requests
import logging
import json
from typing import Tuple, Optional, Dict
from urllib.parse import urlparse, parse_qs, unquote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    filename="tasks.log",
    filemode="a",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)

def generate_code_verifier() -> str:
    """
    code verifier 생성
    """
    verifier: str = (
        base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode("utf-8")
    )
    logger.debug(f"생성된 code_verifier: {verifier}")
    return verifier


def generate_code_challenge(verifier: str) -> str:
    """
    code challenge 생성
    """
    challenge: str = (
        base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode("utf-8")).digest()
        )
        .rstrip(b"=")
        .decode("utf-8")
    )
    logger.debug(f"생성된 code_challenge: {challenge}")
    return challenge


def process_user_security_auth(driver, session, url):
    try:
        driver.get(url)

        for _ in range(10):
            time.sleep(3)
            current_url: str = driver.current_url
            logger.debug(f"process_user_security_auth current_url: {current_url}")
            if "https://security-center.game.daum.net/auth" in current_url:
                logger.debug("security")

                session = requests.Session()
                selenium_cookies = driver.get_cookies()
                for cookie in selenium_cookies:
                    session.cookies.set(cookie['name'], cookie['value'])

                while True:
                    _current_url = driver.current_url
                    logger.debug(f"_current_url: {_current_url}")

                    if "https://pubsvc.game.daum.net/gamestart/poe2.html" in _current_url:
                        parsed_url = urlparse(current_url)
                        query_params = parse_qs(parsed_url.query)
                        txid: Optional[str] = query_params.get("txId", [None])[0]

                        selenium_cookies = driver.get_cookies()
                        for cookie in selenium_cookies:
                            session.cookies.set(cookie['name'], cookie['value'])

                        logger.debug(f"_current_url 리다이렉트 감지: {_current_url}")
                        return get_access_token_and_user_id_from_api(driver, session, txid)

                    time.sleep(0.5)
        else:
            logger.error("dasdssdaasddas")
            return None, None
    except Exception as e:
        logger.error(f"token, mid 파싱 실패: {e}")
    return None, None




def get_access_token_and_user_id_from_api(driver, session, txid = None) -> Tuple[Optional[str], Optional[int]]:
    """
    API를 통해 accessToken, userId 파싱
    """
    try:
        url = "https://poe2-gamestart-web-api.game.daum.net/token/poe2?actionType=user"
        headers = {
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Whale/3.28.266.14 Safari/537.36",
            "referer": "https://pubsvc.game.daum.net/",
            "origin": "https://pubsvc.game.daum.net",
        }

        body = {"txId":txid,"code":None,"webdriver":False if not txid else True}

        logger.debug(f"body: {body}")
        logger.debug(f"session cokkies: {session.cookies.get_dict()}")

        response = session.post(url, headers=headers, json=body)
        if response.status_code == 200:
            data = response.json()
            logger.debug(f"data: {data}")

            status = data.get("status")
            if status == "NEED_SECURITYCENTER_AUTH":
                url = data.get("url")
                return process_user_security_auth(driver, session, url)

            token = data.get("token")
            logger.info(f"API를 통해 token 파싱: {token}")

            mid = data.get("mid")
            logger.info(f"API를 통해 mid 파싱: {mid}")
            return token, mid
        else:
            logger.error(f"API 요청 실패: {response.status_code}")
    except Exception as e:
        logger.error(f"token, mid 파싱 실패: {e}")
    return None, None


def get_user_id_from_api(cookies: Dict[str, str]) -> Optional[int]:
    """
    API를 통해 userId를 파싱
    """
    try:
        url = "https://svc-api.game.daum.net/analytics/ga/info"
        headers = {
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Whale/3.28.266.14 Safari/537.36",
            "referer": "https://poe2.game.daum.net/",
            "origin": "https://poe2.game.daum.net",
            "cookie": "; ".join([f"{key}={value}" for key, value in cookies.items()]),
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            user_id = data.get("userId")
            logger.info(f"API를 통해 userId 파싱: {user_id}")
            return user_id
        else:
            logger.error(f"API 요청 실패: {response.status_code}")
    except Exception as e:
        logger.error(f"userId 파싱 실패: {e}")
    return None


def process_user_auth(driver):
    url = "https://pubsvc.game.daum.net/gamestart/poe2.html?actionType=user"
    driver.get(url)

    for _ in range(10):
        time.sleep(3)
        current_url: str = driver.current_url
        logger.debug(f"current_url: {current_url}")

        if "https://pubsvc.game.daum.net/gamestart/poe2.html" in current_url:
            session = requests.Session()
            selenium_cookies = driver.get_cookies()
            for cookie in selenium_cookies:
                session.cookies.set(cookie['name'], cookie['value'])
            logger.debug("pubsvc")

            return get_access_token_and_user_id_from_api(driver, session)
        elif "https://security-center.game.daum.net/auth" in current_url:
            logger.debug("security")

            session = requests.Session()
            selenium_cookies = driver.get_cookies()
            for cookie in selenium_cookies:
                session.cookies.set(cookie['name'], cookie['value'])

            while True:
                _current_url = driver.current_url
                logger.debug(f"_current_url: {_current_url}")

                if "https://pubsvc.game.daum.net/gamestart/poe2.html" in _current_url:
                    parsed_url = urlparse(current_url)
                    query_params = parse_qs(parsed_url.query)
                    txid: Optional[str] = query_params.get("txId", [None])[0]

                    selenium_cookies = driver.get_cookies()
                    for cookie in selenium_cookies:
                        session.cookies.set(cookie['name'], cookie['value'])

                    logger.debug(f"_current_url 리다이렉트 감지: {_current_url}")
                    return get_access_token_and_user_id_from_api(driver, session, txid)

                time.sleep(0.5)
    else:
        logger.error("dasdssdaasddas")
        return False


def get_authorization_code(
    driver: webdriver.Chrome,
) -> Tuple[Optional[str], Optional[int]]:
    """
    authCode, cookie, userId 파싱
    """
    logger.info("Code verifier와 Code challenge 생성")
    code_verifier: str = generate_code_verifier()
    code_challenge: str = generate_code_challenge(code_verifier)

    AUTH_URL = (
        "https://poe.game.daum.net/oauth/authorize"
        f"?client_id=internal"
        "&redirect_uri=https%3A%2F%2Fpoe2.game.daum.net%2Fkr/home"
        "&response_type=internal"
        "&scope=internal"
        "&state=random_state_string"
        f"&code_challenge_method=S256&code_challenge={code_challenge}"
    )

    logger.info("Authorization Code 획득을 위한 페이지 로딩 중...")
    driver.get(AUTH_URL)

    while True:
        current_url: str = driver.current_url
        if "https://poe2.game.daum.net/kr/home" in current_url:
            logger.debug(f"리다이렉트 감지: {current_url}")
            return process_user_auth(driver)
        time.sleep(1)


    parsed_url = urlparse(current_url)
    query_params = parse_qs(parsed_url.query)
    auth_code: Optional[str] = query_params.get("code", [None])[0]
    if not auth_code:
        logger.error("Authorization Code를 찾을 수 없습니다.")
        return None, None, code_verifier, code_challenge, None

    logger.debug(f"획득한 Authorization Code: {auth_code}")

    selenium_cookies = driver.get_cookies()
    session_cookies = {
        cookie["name"]: cookie["value"] for cookie in selenium_cookies
    }
    logger.debug(f"획득한 쿠키: {session_cookies}")

    # get_user_id_from_api(session_cookies)

    access_token, user_id = get_access_token_and_user_id_from_api(session_cookies)

    return access_token, user_id


def get_access_token(
    auth_code: str, code_verifier: str, cookies: Dict[str, str]
) -> Optional[str]:
    """
    accessToken 파싱
    """
    logger.info("Access Token 요청 중...")
    token_url = "https://poe2.game.daum.net/oauth/token"
    payload = {
        "client_id": "internal",
        "grant_type": "internal",
        "code": auth_code,
        "code_verifier": code_verifier,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "; ".join(
            [f"{key}={value}" for key, value in cookies.items()]
        ),
    }

    logger.debug(f"Access Token 요청 Payload: {payload}")
    logger.debug(f"Access Token 요청 Headers: {headers}")

    response = requests.post(
        token_url, data=payload, headers=headers, verify=False
    )
    logger.debug(f"Access Token 요청 응답 코드: {response.status_code}")
    logger.debug(f"Access Token 요청 응답: {response.text}")

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        if access_token:
            logger.debug(f"Access Token 획득 성공: {access_token}")
            return access_token
        else:
            logger.error("응답에 Access Token이 없습니다.")
    else:
        logger.error("Access Token 획득 실패")

    return None
