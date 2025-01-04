from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # 存储加密后的密码
    is_admin = models.BooleanField(default=False)  # 判断是否为管理员
    timestamp = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    # 新增字段
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', '请输入有效的手机号。')]
    )
    email = models.EmailField(unique=True, null=True, blank=True)
    nickname = models.CharField(max_length=50, null=True, blank=True, default=None)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # 除用户名和密码外不需要额外字段

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # 如果 nickname 为空，则将其设置为与 username 一致
        if not self.nickname:
            self.nickname = self.username
        super(User, self).save(*args, **kwargs)

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

import os
class ImageUpload(models.Model):
    STATUS_CHOICES = [
        ('pending', '待检测'),      # 图片已上传，但尚未处理
        ('completed', '检测完成'),   # 检测完成，结果已生成
        ('failed', '检测失败'),      # 检测过程中发生错误
    ]

    username = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 关联到用户表，支持自定义用户模型
        on_delete=models.CASCADE,  # 当用户被删除时，删除该用户的所有图片
        related_name='images'      # 设置反向关系名
    )
    image = models.ImageField(
        upload_to='uploads/%Y/%m/%d/',  # 存储路径：按日期分类存储
        max_length=255
    )
    upload_time = models.DateTimeField(auto_now_add=True)  # 自动记录上传时间
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'  # 默认状态为 "待检测"
    )
    result = models.TextField(
        null=True, blank=True,  # 检测结果可为空
        help_text='检测结果的描述，或者以JSON字符串存储'
    )
    review = models.TextField(
        null=True, blank=True,  # 评论字段可为空
        help_text='管理员或用户的评论或反馈'
    )

    def __str__(self):
        return f"Image {self.id} by {self.user.username} - {self.status}"


class Log(models.Model):
    ACTION_CHOICES = [
        ('register', '注册'),
        ('login', '登录'),
        ('upload', '图片上传'),
        ('view_result', '查看检测结果'),
        ('add_review', '添加评论'),
        ('admin_action', '管理员操作'),
    ]

    username = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 关联到用户表
        on_delete=models.CASCADE,  # 当用户被删除时，删除其操作日志
        related_name='logs'
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,  # 限制操作类型范围
        help_text='用户执行的操作类型'
    )
    imageid = models.ForeignKey(
        'ImageUpload',  # 关联到 ImageUpload 表
        on_delete=models.SET_NULL,  # 图片被删除时，imageid 设置为 NULL
        null=True, blank=True,  # 某些日志可能与具体图片无关
        related_name='logs'
    )
    timestamp = models.DateTimeField(auto_now_add=True)  # 自动记录日志创建时间
    detail = models.TextField(
        null=True, blank=True,  # 可为空
        help_text='操作的详细描述或补充信息'
    )

    def __str__(self):
        return f"[{self.timestamp}] {self.username.username} - {self.action}"
