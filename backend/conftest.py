import os

def pytest_configure():
    os.environ['ENVIRONMENT'] = 'test'