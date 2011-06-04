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

def wait_for_start(check_if_started, exception_class):
    '''
    Repeatedly call check_if_started for upto 10 seconds. check_if_started 
    should raise and exception exception_class which will be caught. If
    either the 10 seconds has elapsed or an exception that is not exception_class
    is raised this function will fail.
    '''

    current_time = 0
    for timed in range(10):
        try:
            check_if_started()
        except exception_class:
            sleep(0.1)
            current_time += 0.1

