# 阿里云FC专用脚本
from auto_sign import AutoSign
from api.log_setting import logger

def handler(event, context): 
    logger.info("Aliyun FC 任务开始")
    auto_sign = AutoSign()
    auto_sign.aliyun_run()
    logger.info("Aliyun FC 任务结束")
    