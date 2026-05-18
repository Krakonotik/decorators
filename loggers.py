import os
from datetime import datetime


# ---------- Простой декоратор ----------
def logger(old_function):
    def new_function(*args, **kwargs):
        call_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        func_name = old_function.__name__
        args_repr = ', '.join(map(repr, args))
        kwargs_repr = ', '.join(f"{k}={v!r}" for k, v in kwargs.items())
        all_args = ', '.join(filter(None, [args_repr, kwargs_repr]))

        result = old_function(*args, **kwargs)

        log_entry = f"{call_time} – {func_name}({all_args}) -> {result!r}\n"
        with open('main.log', 'a', encoding='utf-8') as log_file:
            log_file.write(log_entry)

        return result

    return new_function


# ---------- Параметризованный декоратор ----------
def logger_param(path):
    def __logger(old_function):
        def new_function(*args, **kwargs):
            call_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            func_name = old_function.__name__
            args_repr = ', '.join(map(repr, args))
            kwargs_repr = ', '.join(f"{k}={v!r}" for k, v in kwargs.items())
            all_args = ', '.join(filter(None, [args_repr, kwargs_repr]))

            result = old_function(*args, **kwargs)

            log_entry = f"{call_time} – {func_name}({all_args}) -> {result!r}\n"
            with open(path, 'a', encoding='utf-8') as log_file:
                log_file.write(log_entry)

            return result

        return new_function

    return __logger


# ---------- Тесты ----------
def test_1():
    path = 'main.log'
    if os.path.exists(path):
        os.remove(path)

    @logger
    def hello_world():
        return 'Hello World'

    @logger
    def summator(a, b=0):
        return a + b

    @logger
    def div(a, b):
        return a / b

    assert 'Hello World' == hello_world()
    result = summator(2, 2)
    assert isinstance(result, int)
    assert result == 4
    result = div(6, 2)
    assert result == 3

    assert os.path.exists(path)

    summator(4.3, b=2.2)
    summator(a=0, b=0)

    with open(path) as log_file:
        log_file_content = log_file.read()

    assert 'summator' in log_file_content
    for item in (4.3, 2.2, 6.5):
        assert str(item) in log_file_content


def test_2():
    paths = ('log_1.log', 'log_2.log', 'log_3.log')

    for path in paths:
        if os.path.exists(path):
            os.remove(path)

        @logger_param(path)
        def hello_world():
            return 'Hello World'

        @logger_param(path)
        def summator(a, b=0):
            return a + b

        @logger_param(path)
        def div(a, b):
            return a / b

        assert 'Hello World' == hello_world()
        result = summator(2, 2)
        assert isinstance(result, int)
        assert result == 4
        result = div(6, 2)
        assert result == 3
        summator(4.3, b=2.2)

    for path in paths:
        assert os.path.exists(path)
        with open(path) as log_file:
            log_file_content = log_file.read()
        assert 'summator' in log_file_content
        for item in (4.3, 2.2, 6.5):
            assert str(item) in log_file_content


if __name__ == '__main__':
    test_1()
    test_2()
    print("Все тесты пройдены успешно!")