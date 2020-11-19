# SvnFuck

## Introduce

* `SvnFuck` is a vulnerability exploitation tool for SVN source disclosure. and support various versions of SVN.

    And will download different versions of files in the project

* `SvnFuck` 是一款SVN源码泄露漏洞的利用工具，支持各个SVN版本。

    并且会将项目中不同版本的文件进行下载。

## Usage method

* Installation dependency

* 安装依赖

```bash
sudo pip install -r requirements.txt
```

* Start Hack

```bash
python SvnFuck.py http://example.com/.svn/
```

## File Structure

```tree
|   readme.md
|   requirements.txt
|   SvnFuck.py
|
+---data
\---lib
    |   util.py
    |   util.pyc
    |   __init__.py
    |   __init__.pyc
    |
    \---__pycache__
            util.cpython-37.pyc
            __init__.cpython-37.pyc
```
