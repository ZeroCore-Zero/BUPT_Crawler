import inspect

def get_caller_file():
    caller_file = inspect.getframeinfo(inspect.currentframe().f_back).filename
    return caller_file

# 示例函数
def example_function():
    caller_file = get_caller_file()
    print("Caller file:", caller_file)

# 测试示例函数
example_function()
