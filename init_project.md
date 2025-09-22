# creat project

1.初始化项目
```
uv init
```
2.添加虚拟python环境
```
uv venv
```
3.激活虚拟python环境
```
source .venv/bin/activate
```
4.添加google-adk
```
uv add google-adk
```
5.执行
```
uv run main.py
Hello from polo!
```

5.打包
```
$ uv pip install build 
Installed 2 packages in 21ms
 + build==1.3.0
 + pyproject-hooks==1.2.0

$ python -m build
dist
├── polo-0.1.0-py3-none-any.whl
└── polo-0.1.0.tar.gz
```

6.测试发布
上传到 Test PyPI 测试：
```
twine upload --repository testpypi dist/*
```
pip 安装测试：
```
pip install --index-url https://test.pypi.org/simple/ polo-cli
```

7.正式发布
在 PyPI 账户设置 → API tokens → Create token → 给包权限
```
twine upload -u __token__ -p <your-token> dist/*
```