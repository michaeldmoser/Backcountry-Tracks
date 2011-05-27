from time import sleep

def try_until(timeout, assert_callback):
    '''
    Will call assert_callback repeatly until timeout.

    timeout:: can be a floating point number to indicate fractions of a second
    '''
    wait_time = 0.01
    count = 0

    while True:
        try:
            assert_callback()
        except AssertionError:
            if count > timeout:
                raise
        else:
            return

        sleep(wait_time)
        count += wait_time

