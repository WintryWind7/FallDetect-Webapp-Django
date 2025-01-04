from .models import *

class Action(object):
    def __init__(self):
        pass

    def login(self, username):
        """
        用户登录操作。
        :param username: 用户名（字符串）
        """
        try:
            # 获取用户对象（假设用户名是唯一的）
            self.user = User.objects.get(username=username)
            # 记录登录日志
            self._log(action='login', detail=f'用户 {username} 登录成功')
            return True
        except User.DoesNotExist:
            # 如果用户不存在
            return False

    def register(self, username, password, is_admin=False):
        """
        用户注册操作。
        :param username: 用户名（字符串）
        :param password: 用户密码（明文，后续需要加密存储）
        :param is_admin: 是否是管理员（布尔值）
        """
        if User.objects.filter(username=username).exists():
            return False

        # 创建新用户
        self.user = User.objects.create(
            username=username,
            password=self._encrypt_password(password),  # 加密密码存储
            is_admin=is_admin
        )
        # 记录注册日志
        self._log(action='register', detail=f'用户 {username} 注册成功')
        return True

    def _log(self, action, detail):
        """
        内部方法：记录操作日志。
        :param action: 操作类型（如 'login', 'register'）
        :param detail: 操作的详细描述
        """
        if not self.user:
            raise ValueError("无法记录日志：未设置用户对象")
        Log.objects.create(
            username=self.user,
            action=action,
            detail=detail
        )

    @staticmethod
    def _encrypt_password(password):
        """
        加密用户密码（使用 bcrypt）。
        :param password: 明文密码
        :return: 加密后的密码
        """
        import bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

action = Action()