import yagmail
import yagmail.error
from api.setting import MAIL_SET,CURRENT_PATH
from smtplib import SMTPDataError
from api.log_setting import logger
import asyncio
from os.path import join as path_join
from jinja2 import Template,FileSystemLoader,Environment
from api.db_control import getWebDBControl
import asyncio
from datetime import datetime

j2_env = Environment(loader=FileSystemLoader(path_join(CURRENT_PATH, '../template')))


def get_notice()->dict:
    async def __get_notice():
        DB = await getWebDBControl()
        res = await DB.get_notice()
        await DB.quit()
        if res:
            res['time'] = datetime.fromtimestamp(res['time']/1000.0).strftime('%Y-%m-%d %H:%M:%S')
        else:
            res = {
                'title':'无',
                'content':'无',
                'time':'无'
            }
        return res
    return asyncio.run(__get_notice())

def admin_mail(subject:str, contents:str) -> None:
    try:
        yag = yagmail.SMTP(user=MAIL_SET['account'], password=MAIL_SET['token'], host=MAIL_SET['host'])
        yag.send(to=MAIL_SET['admin'], subject=subject, contents=contents)
        logger.info('管理员邮件发送成功！')
    except Exception as e:
        logger.error(f'管理员邮件发送失败！可能是由于是邮箱设置有误->{e}')

def user_mail(subject:str, contents:str, user:str) -> bool:
    try:
        yag = yagmail.SMTP(user=MAIL_SET['account'], password=MAIL_SET['token'], host=MAIL_SET['host'])
        yag.send(to=user, subject=subject, contents=contents)
        logger.info(f'用户邮件发送成功！->{user}')
        return True
    except SMTPDataError or yagmail.error.YagInvalidEmailAddress:
        logger.error(f'用户邮件发送失败！邮箱地址可能错误。->{user}')
        return False

def user_mail_gen(title:str,info:str,code:str):
    j2_tmpl = j2_env.get_template('user_mail.html')
    return j2_tmpl.render(title=title,info=info,code=code,notice=get_notice())


def admin_mail_gen(info_list:list):
    j2_tmpl = j2_env.get_template('admin_mail.html')
    return j2_tmpl.render(info_list=info_list,notice=get_notice())

def reg_mail_gen(info:dict):
    j2_tmpl = j2_env.get_template('reg_mail.html')
    return j2_tmpl.render(info=info,notice=get_notice())

def ban_mail_gen(account:str):
    j2_tmpl = j2_env.get_template('ban_mail.html')
    return j2_tmpl.render(account=account,notice=get_notice())

def email_validate_gen(code:str):
    j2_tmpl = j2_env.get_template('email_validate.html')
    return j2_tmpl.render(code=code,notice=get_notice())
