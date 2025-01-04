from django.shortcuts import render
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import bcrypt
from api.models import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.Action import action
from datetime import timedelta
from django.utils.timezone import localtime
from api.detect.api import *


# Create your views here.


class TemplatesView(APIView):
    permission_classes = [IsAuthenticated]  # 是否启用用户认证

    def get(self, request):
        return Response({"不允许的访问方式！"})

    def post(self, request):
        # 接收JSON格式的请求数据并返回相同的数据
        data = request.data  # 访问请求中的JSON数据
        return Response(data, status=status.HTTP_200_OK)


class LoginApi(APIView):
    # permission_classes = [IsAuthenticated]  # 是否启用用户认证

    # def set_password(self, password):
    #     return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def get(self, request):
        return Response({"不允许的访问方式！"})

    def post(self, request):
        data = request.data  # 获取请求的JSON数据
        username = data.get('username')
        password = data.get('password')
        # print(data)
        # 尝试获取用户对象
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_404_NOT_FOUND)

        # 检查密码是否正确
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            # 根据用户类型返回不同的消息
            refresh = RefreshToken.for_user(user)
            if user.is_admin:
                message = "Admin login successful"
            else:
                message = "User login successful"
            user.last_login = timezone.now()
            action.login(username)
            user.save()
            return Response({"refresh": str(refresh),"access": str(refresh.access_token), "status": "success", "message": message}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)



class UserdbApi(APIView):
    """
    用户 API，仅支持查看
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        """
        返回所有用户信息
        """
        users = User.objects.all()
        user_list = [
            {
                "id": user.id,
                "username": user.username,
                "is_admin": user.is_admin,
                "timestamp": localtime(user.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": localtime(user.last_login).strftime("%Y-%m-%d %H:%M:%S") if user.last_login else None
            }
            for user in users
        ]
        return Response(user_list, status=status.HTTP_200_OK)


class ImagedbApi(APIView):
    """
    图片 API，仅支持查看
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        """
        返回所有图片信息
        """
        images = ImageUpload.objects.all()
        image_list = [
            {
                "id": image.id,
                "username": image.username.username,
                "image": image.image.url if image.image else None,
                "upload_time": localtime(image.upload_time).strftime("%Y-%m-%d %H:%M:%S"),
                "status": image.status,
                "result": image.result,
                "review": image.review
            }
            for image in images
        ]
        return Response(image_list, status=status.HTTP_200_OK)


class LogdbApi(APIView):
    """
    日志 API，仅支持查看
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        """
        返回所有日志信息
        """
        logs = Log.objects.all().order_by('-timestamp')
        log_list = [
            {
                "id": log.id,
                "username": log.username.username,
                "action": log.action,
                "timestamp": localtime(log.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                "detail": log.detail
            }
            for log in logs
        ]
        return Response(log_list, status=status.HTTP_200_OK)


class RegisterApi(APIView):
    """
    用户注册 API
    """

    def get(self, request):
        return Response({"status": "error", "message": "不允许的访问方式！"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request):
        # 获取请求的JSON数据
        data = request.data
        username = data.get("username")
        password = data.get("password")

        # 检查是否提供了用户名和密码
        if not username or not password:
            return Response(
                {"status": "error", "message": "用户名和密码不能为空！"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return Response(
                {"status": "error", "message": "用户名已存在，请选择其他用户名！"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 使用 bcrypt 加密密码
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # 创建用户
        try:
            user = User.objects.create(
                username=username,
                password=hashed_password,  # 加密后的密码
            )
            user.save()
        except Exception as e:
            return Response(
                {"status": "error", "message": f"注册失败，请联系管理员！错误：{str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 返回成功信息
        return Response(
            {
                "status": "success",
                "message": "注册成功，请使用新用户名登录！",
                "data": {
                    "username": username,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class UpdateUserInfoView(APIView):
    permission_classes = [IsAuthenticated]  # 仅允许已登录用户访问

    def put(self, request):
        user = request.user  # 获取当前登录用户
        data = request.data

        # 更新字段
        if 'phone_number' in data:
            user.phone_number = data['phone_number']
        if 'email' in data:
            user.email = data['email']
        if 'nickname' in data:
            user.nickname = data['nickname']

        # 保存用户信息
        try:
            user.save()
            return Response({"message": "用户信息更新成功"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

from .serializers import UserInfoSerializer
class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]  # 确保只有已登录用户可以访问

    def get(self, request):
        user = request.user  # 获取当前登录用户
        print(user)
        serializer = UserInfoSerializer(user)
        return Response(serializer.data)


class UploadImageApi(APIView):
    permission_classes = [IsAuthenticated]  # 仅允许登录用户上传图片

    def post(self, request):
        """
        处理图片上传。
        请求体应包含图片文件，并将其存储，同时标记为待检测状态。
        同时记录上传操作的日志。
        """
        user = request.user  # 获取当前登录用户
        image_file = request.FILES.get('image')  # 获取图片文件

        if not image_file:
            return Response({"error": "未找到图片文件，请上传图片"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 保存图片到数据库
            uploaded_image = ImageUpload.objects.create(
                username=user,
                image=image_file,
                status='pending',  # 设置状态为 "待检测"
            )

            # 创建操作日志
            Log.objects.create(
                username=user,
                action='upload',
                imageid=uploaded_image,
                detail=f"用户 {user.username} 上传了图片，标记为待检测"
            )

            return Response({
                "message": "图片上传成功，已设置为待检测状态",
                "image_id": uploaded_image.id,
                "upload_time": uploaded_image.upload_time,
                "status": uploaded_image.status,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"图片上传失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from PIL import Image  # 用于加载图片（如果需要）
import numpy as np  # 用于图像数据处理
class PredictImageApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        使用 YOLO 对图片进行目标检测，并返回预测结果的 JSON 数据。
        请求参数应包含 image_id。
        """
        image_id = request.data.get('image_id')

        if not image_id:
            return Response({"error": "必须提供 image_id 参数"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 获取图片记录
            uploaded_image = ImageUpload.objects.get(id=image_id, username=request.user)

            # 获取图片文件路径
            image_path = uploaded_image.image.path  # 获取图片的实际文件路径
            if not os.path.exists(image_path):
                return Response({"error": "图片文件不存在"}, status=status.HTTP_404_NOT_FOUND)

            # 调用外部的预测函数
            detected_objects = predict(image_path)

            # 更新数据库记录
            uploaded_image.status = 'completed'
            uploaded_image.result = f"{detected_objects}"
            uploaded_image.save()

            # 记录日志
            Log.objects.create(
                username=request.user,
                action='view_result',
                imageid=uploaded_image,
                detail=f"用户 {request.user.username} 对图片 {image_id} 进行了目标检测，得到结果 {len(detected_objects)} 个"
            )

            # 返回 JSON 格式的预测结果
            return Response({
                "message": "目标检测完成",
                "image_id": image_id,
                "detected_objects": detected_objects
            }, status=status.HTTP_200_OK)
        except ImageUpload.DoesNotExist:
            return Response({"error": "指定的图片不存在或无权访问"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"预测过程中发生错误: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDetectionRecordsApi(APIView):
    """
    用户检测记录 API，仅返回当前用户的数据
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        返回当前用户的图片检测记录
        """
        # 只查询属于当前用户的 ImageUpload 数据
        user_images = ImageUpload.objects.filter(username=request.user)

        # 构造 JSON 响应
        image_list = [
            {
                "id": image.id,
                "image": image.image.url if image.image else None,
                "upload_time": localtime(image.upload_time).strftime("%Y-%m-%d %H:%M:%S"),
                "status": image.status,
                "result": image.result,
                "review": image.review
            }
            for image in user_images
        ]
        # print(image_list)
        return Response(image_list, status=status.HTTP_200_OK)


from django.shortcuts import get_object_or_404
class DeleteRowApi(APIView):
    """
    删除动态表格行的 API
    """
    permission_classes = [IsAuthenticated]

    # 支持的表格与模型映射
    TABLE_MODEL_MAPPING = {
        "Users": User,
        "Images": ImageUpload,
        "Logs": Log,
    }

    def post(self, request):
        """
        删除指定表格中的记录
        """
        table_name = request.data.get("table")
        row_id = request.data.get("id")

        # 检查请求中的必要参数
        if not table_name or not row_id:
            return Response({"error": "必须提供表格名称和记录ID"}, status=status.HTTP_400_BAD_REQUEST)

        # 检查表格名称是否有效
        if table_name not in self.TABLE_MODEL_MAPPING:
            return Response({"error": "无效的表格名称"}, status=status.HTTP_400_BAD_REQUEST)

        model = self.TABLE_MODEL_MAPPING[table_name]

        # 删除记录
        try:
            instance = get_object_or_404(model, id=row_id)

            # 如果是 Users 表，需要额外权限检查
            if table_name == "Users":
                # 检查是否尝试删除自身
                if int(row_id) == request.user.id:
                    return Response({"error": "您不能删除自己的用户记录"}, status=status.HTTP_400_BAD_REQUEST)

            instance.delete()
            return Response({"status": "success", "message": "记录删除成功"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"删除记录时发生错误: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateReviewAPIView(APIView):
    def post(self, request):
        try:
            # 获取请求数据
            record_id = request.data.get('id')  # ImageUpload 的 ID
            username = request.data.get('username')  # 用户名
            review = request.data.get('review')  # 更新的评论内容

            if not record_id or not username or review is None:
                return Response({"error": "缺少必要的参数"}, status=status.HTTP_400_BAD_REQUEST)

            # 确认用户存在
            user = User.objects.get(username=username)  # 根据用户名查询用户

            # 查询记录
            upload_image = ImageUpload.objects.get(id=record_id, username=user)

            # 更新 review 字段
            upload_image.review = review
            upload_image.save()

            return Response({"message": "审核信息更新成功"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)
        except ImageUpload.DoesNotExist:
            return Response({"error": "图片记录不存在"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"服务器内部错误: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)