# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os
import sys
#AccessKey ID LTAI5tDDm3a1bZA1aYVj4nKp
#AccessKey Secret DM7pD3CsyToyCzG0CUKCoMRRVjX40v
from typing import List
import json
from alibabacloud_ocr_api20210707.client import Client as ocr_api20210707Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ocr_api20210707 import models as ocr_api_20210707_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


class AliOcr:
    def __init__(self):
        pass

    @staticmethod
    def create_client() -> ocr_api20210707Client:
        """
        使用AK&SK初始化账号Client
        @return: Client
        @throws Exception
        """
        # 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考。
        # 建议使用更安全的 STS 方式，更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378659.html。
        config = open_api_models.Config(
            # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID。,
            access_key_id=os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
            # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_SECRET。,
            access_key_secret=os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET']
        )
        # Endpoint 请参考 https://api.aliyun.com/product/ocr-api
        config.endpoint = f'ocr-api.cn-hangzhou.aliyuncs.com'
        return ocr_api20210707Client(config)

    @staticmethod
    def main(
        args: List[str],
    ) -> None:
        # 检查参数
        if len(args) < 1:
            print("用法: python aliy_ocr.py <图片路径>")
            return
        
        image_path = args[0]
        if not os.path.exists(image_path):
            print(f"错误: 文件 '{image_path}' 不存在")
            return
            
        client = AliOcr.create_client()
        recognize_edu_question_ocr_request = ocr_api_20210707_models.RecognizeEduQuestionOcrRequest()
        
        # 读取图片文件
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
            
        # 设置请求参数
        recognize_edu_question_ocr_request.body = image_bytes
        
        runtime = util_models.RuntimeOptions()
        try:
            # 调用API并获取返回结果
            response = client.recognize_edu_question_ocr_with_options(recognize_edu_question_ocr_request, runtime)
            # 打印返回结果
            
            resData = response.body.to_map().get('Data')
            content = json.loads(resData)
            print("识别结果:",content['content'])
            return content['content']
        except Exception as error:
            # 错误处理
            print(f"识别失败: {error.message}")
            if hasattr(error, 'data') and error.data:
                print(f"诊断建议: {error.data.get('Recommend')}")
            UtilClient.assert_as_string(error.message)

    @staticmethod
    async def main_async(
        args: List[str],
    ) -> None:
        # 检查参数
        if len(args) < 1:
            print("用法: python aliy_ocr.py <图片路径>")
            return
        
        image_path = args[0]
        if not os.path.exists(image_path):
            print(f"错误: 文件 '{image_path}' 不存在")
            return
            
        client = AliOcr.create_client()
        recognize_edu_question_ocr_request = ocr_api_20210707_models.RecognizeEduQuestionOcrRequest()
         # 读取图片文件
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
            
        # 设置请求参数
        recognize_edu_question_ocr_request.body = image_bytes
        
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            await client.recognize_edu_question_ocr_with_options_async(recognize_edu_question_ocr_request, runtime)
             # 打印返回结果
            resData = response.body.to_map().get('Data')
            content = json.loads(resData)
            print("识别结果:",content['content'])
            return content['content']
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)


if __name__ == '__main__':
    AliOcr.main(sys.argv[1:])