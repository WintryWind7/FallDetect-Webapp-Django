1、创建conda环境

```bash
conda create --name falldetect python=3.11
```

![image-20241221164027883](D:\Codes\MarkDown\assets\image-20241221164027883.png)

2、安装环境

```bash
conda activate falldetect
```

```bash
conda install -c conda-forge ultralytics
```

```bash
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
```

```bash
conda install django django-cors-headers djangorestframework djangorestframework-simplejwt 
```

3、运行环境

```bash
python manage.py runserver
```

