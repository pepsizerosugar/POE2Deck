import shutil
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    filename="tasks.log",
    filemode="a",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


def is_command_available(command):
    """
    커맨드 사용 가능 체크
    """
    logger.debug(f"명령어 '{command}' 사용 가능 여부 확인 중...")
    result = shutil.which(command) is not None
    if result:
        logger.debug(f"명령어 '{command}'은(는) 사용 가능합니다.")
    else:
        logger.debug(f"명령어 '{command}'은(는) 사용 불가능합니다.")
    return result
