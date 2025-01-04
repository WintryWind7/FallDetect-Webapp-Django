from django.urls import path
from .views import *

urlpatterns = [
    path('templates/', TemplatesView.as_view(), name='test'),
    path('login/', LoginApi.as_view(), name='login'),
    path('register/', RegisterApi.as_view(), name='register'),
    path('users/', UserdbApi.as_view(), name='users'),
    path('images/', ImagedbApi.as_view(), name='images'),
    path('logs/', LogdbApi.as_view(), name='logs'),
    path('user/update/', UpdateUserInfoView.as_view(), name='update_user_info'),
    path('user/info/', UserInfoView.as_view(), name='user_info'),
    path('image/upload/', UploadImageApi.as_view(), name='image_upload'),
    path('image/predict/', PredictImageApi.as_view(), name='predict_image'),
    path('image/user-detection-records/', UserDetectionRecordsApi.as_view(), name='user_detection_records'),
    path('delete-row/', DeleteRowApi.as_view(), name='delete_row'),
    path('image/update-review/', UpdateReviewAPIView.as_view(), name='update-review'),

]