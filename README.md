## qiushi2pdf
将《求是》文章转化为pdf文件，便于打印和阅读

## System dependence
```bash
sudo apt install texlive-full
```

## How to install
1. Download source code
    ```bash
    git clone https://github.com/fengdongfa1995/qiushi2pdf.git
    ```

1. change to directory
    ```bash
    cd qiushi2pdf
    ```

1. install the package from source code
    ```bash
    pip install .
    ```

## How to use
```bash
qiushi2pdf <url>
```

example:
```bash
qiushi2pdf http://www.qstheory.cn/dukan/qs/2022-06/15/c_1128739416.htm
```

Then check the `current.pdf` in current directory! enjoy!

## How to update
repeat `How to install`.