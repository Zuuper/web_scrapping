from selenium.common.exceptions import *


def run_selenium(function):
    try:
        return function
    except NoSuchFrameException as frame_exception:
        print(frame_exception)
    except TimeoutException as time_exception:
        raise ValueError(time_exception)