import yagmail
import yagmail.error
from api.setting import MAIL_SET,CURRENT_PATH
from smtplib import SMTPDataError
from api.log_setting import logger
from os.path import join as path_join
from jinja2 import FileSystemLoader,Environment
from api.db_control import getWebDBControl
from datetime import datetime

j2_env = Environment(loader=FileSystemLoader(path_join(CURRENT_PATH, '../template')))


async def get_notice()->dict:
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


async def admin_mail(subject:str, contents:str) -> None:
    try:
        yag = yagmail.SMTP(user=MAIL_SET['account'], password=MAIL_SET['token'], host=MAIL_SET['host'])
        yag.send(to=MAIL_SET['admin'], subject=subject, contents=contents)
        logger.info('管理员邮件发送成功！')
    except Exception as e:
        logger.error(f'管理员邮件发送失败！可能是由于是邮箱设置有误->{e}')

async def user_mail(subject:str, contents:str, user:str) -> bool:
    try:
        yag = yagmail.SMTP(user=MAIL_SET['account'], password=MAIL_SET['token'], host=MAIL_SET['host'])
        yag.send(to=user, subject=subject, contents=contents)
        logger.info(f'用户邮件发送成功！->{user}')
        return True
    except SMTPDataError or yagmail.error.YagInvalidEmailAddress:
        logger.error(f'用户邮件发送失败！邮箱地址可能错误。->{user}')
        return False

async def user_mail_gen(title:str,info:str,code:str):
    j2_tmpl = j2_env.get_template('user_mail.html')
    return j2_tmpl.render(title=title,info=info,code=code,notice=await get_notice())


async def admin_mail_gen(info_list:list):
    j2_tmpl = j2_env.get_template('admin_mail.html')
    return j2_tmpl.render(info_list=info_list,notice=await get_notice())

async def reg_mail_gen(info:dict):
    j2_tmpl = j2_env.get_template('reg_mail.html')
    return j2_tmpl.render(info=info,notice=await get_notice())

async def ban_mail_gen(account:str):
    j2_tmpl = j2_env.get_template('ban_mail.html')
    return j2_tmpl.render(account=account,notice=await get_notice())

async def email_validate_gen(code:str):
    j2_tmpl = j2_env.get_template('email_validate.html')
    return j2_tmpl.render(code=code,notice=await get_notice())
