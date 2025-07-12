from fastapi import APIRouter, UploadFile, Form

from application.settings import ALIYUN_OSS
from infra.utils.file.aliyun_oss import AliyunOSS, BucketConf
from infra.utils.file.file_manage import FileManage
from infra.utils.response import SuccessResponse

app = APIRouter()

###########################################################
#    文件上传管理
###########################################################
@app.post("/upload/image/to/oss", summary="上传图片到阿里云OSS")
async def upload_image_to_oss(file: UploadFile, path: str = Form(...)):
    result = await AliyunOSS(BucketConf(**ALIYUN_OSS)).upload_image(path, file)
    return SuccessResponse(result)


@app.post("/upload/video/to/oss", summary="上传视频到阿里云OSS")
async def upload_video_to_oss(file: UploadFile, path: str = Form(...)):
    result = await AliyunOSS(BucketConf(**ALIYUN_OSS)).upload_video(path, file)
    return SuccessResponse(result)


@app.post("/upload/file/to/oss", summary="上传文件到阿里云OSS")
async def upload_file_to_oss(file: UploadFile, path: str = Form(...)):
    result = await AliyunOSS(BucketConf(**ALIYUN_OSS)).upload_file(path, file)
    return SuccessResponse(result)


@app.post("/upload/image/to/local", summary="上传图片到本地")
async def upload_image_to_local(file: UploadFile, path: str = Form(...)):
    manage = FileManage(file, path)
    path = await manage.save_image_local()
    return SuccessResponse(path)