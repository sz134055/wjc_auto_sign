import httpx
from api.pswd_encrypt import encryptAES
from lxml import etree
from time import time as getTime
from api.log_setting import logger
from api.setting import ADDRESS_NAME
import ddddocr
from io import BytesIO
from PIL import Image
import base64
from json import JSONDecodeError

class WJC:
    def __init__(self, account, pswd):
        self.headers = {
            #'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 (4714622976) cpdaily/9.4.0  wisedu/9.4.0'
            'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Mobile/15E148 Safari/604.1'
        }

        self.account = account
        self.pswd = pswd

        self.s = httpx.AsyncClient()
        self.s.follow_redirects = True
        

        self.__login_form = {
            'salt': '',
            'cap': '',
            'execution': ''
        }

    async def __pswdGen(self, pswd=None, salt=None):
        # return self.__js.call('app.encryptAES', pswd, salt)
        pswd = pswd if pswd else self.pswd
        salt = salt if salt else self.__login_form.get('salt')
        return encryptAES(pswd, salt)


    def __timeGen(self) -> str:
        return str(getTime()).replace('.','')[:13]


    async def __isNeedCap(self):
        """
        字符验证码专用（现已弃用）
        """
        try:
            res = await self.s.get('https://ids.uwh.edu.cn/authserver/checkNeedCaptcha.htl',
                headers=self.headers,
                params={
                    'username':self.account,
                    '_':self.__timeGen()
                },
                timeout=45
            )
            if res.status_code == 200:
                res_json = res.json()
                logger.info(f'[{self.account}]查询是否需要验证码成功')
                return {'code':'ok','msg':f'[{self.account}]验证是否需要验证码成功','info':{'needCap':res_json['isNeed']}}
            else:
                logger.error(f'[{self.account}]查询是否需要验证码失败 [CODE]{res.status_code}\n[CONTENT] {res.text}')
                return {'code':'fail','msg':f'[{self.account}]查询是否需要验证码失败','info':{'code':res.status_code,'content':res.text}}
        except Exception as e:
            logger.error(f'[{self.account}]查询是否需要验证码超时')
            return {'code':'fail','msg':f'[{self.account}]查询是否需要验证码超时'}

    async def __cap_gen(self):
        """
        字符验证码专用（现已弃用）
        """
        ocr = ddddocr.DdddOcr(show_ad=False)
        try:
            res = await self.s.get('https://ids.uwh.edu.cn/authserver/getCaptcha.htl?'+self.__timeGen(),headers=self.headers)
            if res.status_code == 200:
                ocr_res = ocr.classification(res.content)
                logger.info(f'[{self.account}]验证码识别成功 -> {ocr_res}')
                return {'code':'ok','msg':f'[{self.account}]验证码识别成功','info':{'cap':ocr_res}}
            else:
                raise httpx.ConnectTimeout
        except httpx.ConnectTimeout or httpx.Timeout:
            logger.error(f'[{self.account}]请求验证码失败')
            return {'code':'fail','msg':f'[{self.account}]请求验证码失败','info':{'cap':''}}
            

    async def __loginInfoGet(self):
        try:
            res = await self.s.get('https://ids.uwh.edu.cn/authserver/login?service=https://ehall.uwh.edu.cn/login', headers=self.headers,timeout=45)
        except httpx.ConnectTimeout or httpx.Timeout:
            logger.error(f'[{self.account}]请求登录信息超时')
            return {'code':'fail','msg':f'[{self.account}]请求登录息超时'}
        
        if res.status_code == 200:
            html = etree.HTML(res.text)
            try:
                self.__login_form.update({
                    'salt': html.xpath('//input[@id="pwdEncryptSalt"][1]/@value')[0],
                    'execution': html.xpath('//input[@id="execution"][1]/@value')[0]
                })
                msg = {'code': 'ok', 'msg': f'[{self.account}]成功获取加密参数', 'info': {}}
                logger.info(f"{msg['msg']}")
                return msg
            except Exception as e:
                msg = {'code': 'error', 'msg': f'[{self.account}]尝试获取加密参数出现错误，错误信息会被保存于info中', 'info': {'msg': e}}
                logger.error(f"{msg['msg']}\n{msg['info']['msg']}")
                return msg
        else:
            msg = {'code': 'fail', 'msg': f'[{self.account}]请求登录界面失败，具体信息将会被保存在info中',
                    'info': {'code': res.status_code, 'content': res.text}}
            logger.error(f"{msg['msg']}\n{msg['info']['code']}\n{msg['info']['content']}")
            return msg

    async def login(self):
        logger.info(f"[{self.account}]开始登录账号")
        if not self.account or not self.pswd:
            msg = {'code': 'fail', 'msg': '账号或密码不能为空', 'info': {}}
            logger.error(f"{msg['msg']}")
            return msg
        await self.__loginInfoGet()
        if not self.__login_form.get('salt') or not self.__login_form.get('execution'):
            msg = {'code': 'fail', 'msg': f'[{self.account}]无加密参数', 'info': {}}
            logger.error(f"{msg['msg']}")
            return msg
        
        cap = ''
        # 不再使用字符串验证码，改用滑块验证码
        # __need_cap = self.__isNeedCap()
        # if __need_cap['code'] == 'ok' and __need_cap['info']['needCap']:
        #     cap = self.__cap_gen()['info']['cap']

        data_form = {
            'username': self.account,
            'password': await self.__pswdGen(self.pswd, self.__login_form['salt']),
            'captcha': cap,
            '_eventId': 'submit',
            'cllt': 'userNameLogin',
            'dllt': 'generalLogin',
            'lt': '',
            'execution': self.__login_form['execution']
        }
        # 滑块识别
        if not await SliderPass(self.s).start():
            logger.error(f'[{self.account}]验证码通过失败')
            return {'code':'fail','msg':f'[{self.account}]验证码通过失败'}

        headers = {
            'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Mobile/15E148 Safari/604.1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.9',
        }
        try:
            res = await self.s.post('https://ids.uwh.edu.cn/authserver/login?service=https://ehall.uwh.edu.cn/login',headers=headers,data=data_form,timeout=45)
            res_cas = await self.s.post('https://ehall.uwh.edu.cn/student/cas',timeout=45)
        except httpx.ConnectTimeout or httpx.Timeout:
            logger.error(f'[{self.account}]请求登录超时')
            return {'code':'fail','msg':f'[{self.account}]请求登录超时'}
        
        # cookie = ''
        # for k,v in self.s.cookies.items():
        #     cookie += k+'='+v+';'
        msg = {'code':'ok','msg':f'[{self.account}]获取Cookies','info':{}}  # 不代表登录成功
        logger.info(f"{msg['msg']}")
        return msg
    
    async def getSignTask(self):
        api = 'https://ehall.uwh.edu.cn/student/content/tabledata/student/sign/stu/sign'
        params_load = {
            "bSortable_0": "false",
            "bSortable_1": "true",
            "iSortingCols": "1",
            "iDisplayStart": "0",
            "iDisplayLength": "12",
            "iSortCol_0": "3",
            "sSortDir_0": "desc",
            "_t_s_": self.__timeGen()
        }
        try:
            res = await self.s.get(api, params=params_load,timeout=45)
        except httpx.ConnectTimeout or httpx.Timeout:
            logger.error(f'[{self.account}]请求签到信息超时')
            return {'code':'fail','msg':f'[{self.account}]请求签到息超时'}
        
        if res.status_code == 200:
            try:
                msg = {'code': 'ok', 'msg': f'[{self.account}]成功获取签到任务', 'info': res.json()}
                logger.info(f"{msg['msg']}")
                return msg
            except JSONDecodeError:
                msg = {'code': 'fail', 'msg': f'[{self.account}]获取签到任务失败', 'info': {'code': res.status_code, 'content': res.text}}
                logger.error(f"{msg['msg']}\n{msg['info']}")
                return msg
        else:
            msg = {'code': 'fail', 'msg': f'[{self.account}]获取签到任务失败', 'info': {'code': res.status_code, 'content': res.text}}
            logger.error(f"{msg['msg']}\n{msg['info']}")
            return msg

    async def sign(self,coordinate:str,dm:str,sjdm:str):
        api = 'https://ehall.uwh.edu.cn/student/content/student/sign/stu/sign'
        params_load = {
            '_t_s_':self.__timeGen()
        }
        
        data_form = {
            "pathFile": "",
            "dm": dm,
            "sjdm": sjdm,
            "zb": coordinate,
            "wz": ADDRESS_NAME,
            "ly": "lbs",
            "qdwzZt": "0",
            "fwwDistance": "15",    #距离签到位置距离
            "operationType": "Update"
        }

        try:
            res = await self.s.post(api,params=params_load, data=data_form,headers=self.headers,timeout=45)
        # except ConnectTimeout or Timeout:
        except Exception:   # 增大异常捕获范围
            logger.error(f'[{self.account}]请求签到超时')
            return {'code':'fail','msg':f'[{self.account}]请求签到超时'}
        if res.status_code == 200:
            msg = {'code': 'ok', 'msg': f'[{self.account}]成功签到', 'info': res.json()}
            logger.info(f"{msg['msg']}")
            return msg
        else:
            msg = {'code': 'fail', 'msg': f'[{self.account}]签到失败', 'info': {'code': res.status_code, 'content': res.text}}
            logger.error(f"{msg['msg']}\n{msg['info']}")
            return msg

    async def isLoginSuccess(self) -> bool:
        if((await self.getSignTask())['code'] == 'ok'):
            return True
        return False


class SliderPass:
    def __init__(self,s:httpx.AsyncClient):
        self.s = s
        self.headers = {
            #'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 (4714622976) cpdaily/9.4.0  wisedu/9.4.0'
            'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Mobile/15E148 Safari/604.1'
        }

    
    def __timeGen(self) -> str:
        return str(getTime()).replace('.','')[:13]

    async def __pic64_resize(self,content:str,target_width:int,target_height:int=None):
        img = Image.open(BytesIO(base64.b64decode(content)))
        if not target_height:
            target_height = int(round(float(img.size[1]) * (target_width / float(img.size[0]))))
        img = img.resize(
            (
                target_width,
                target_height
            )
            ,Image.ANTIALIAS
        )
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')  # 或者根据实际需要选择其他格式
        img_bytes.seek(0)
        
        return img_bytes.getvalue()

    def __calculate_new_position(self,original_width, new_width, original_position):
        # 计算缩放比例
        scaling_factor = new_width / original_width
        # 计算新位置
        new_position = original_position * scaling_factor

        return int(new_position)



    async def get_position(self,bgImg:str,sliderImg:str):
        det = ddddocr.DdddOcr(det=False,ocr=False,show_ad=False)
        s_bytes = BytesIO(base64.b64decode(sliderImg))
        bg_bytes = BytesIO(base64.b64decode(bgImg))

        # 第一种方法是对图片进行缩放判断，效果不太好
        # res = det.slide_match(
        #     pic64_resize(sliderImg,target_width=42)
        #     ,pic64_resize(bgImg,target_width=280,target_height=155)
        # )
        # 第二种算法基于原始图片进行判断最后根据尺寸缩放计算缩放后的位置
        res = det.slide_match(
            s_bytes.read(),
            bg_bytes.read()
        )
        res = self.__calculate_new_position(Image.open(bg_bytes).size[0],280,res['target'][0])
        return res

    async def get_slider(self) -> dict:
        try:
            res = await self.s.get('https://ids.uwh.edu.cn/authserver/common/openSliderCaptcha.htl',
                headers=self.headers,
                params={
                    '_':self.__timeGen()
                },
                timeout=45
            )
            if res.status_code == 200:
                logger.info('请求滑块验证码成功')
                return res.json()
        except Exception as e:
            logger.error(f'请求滑块验证码失败\n{e}')
            return {}

    async def verify(self,pos_x:int) -> bool:
        try:
            res = await self.s.post('https://ids.uwh.edu.cn/authserver/common/verifySliderCaptcha.htl',
                headers=self.headers,
                data={
                    'canvasLength':280,
                    'moveLength':pos_x
                },
                timeout=45
            )
            if res.status_code == 200:
                res_json = res.json()
                if res_json['errorCode']:
                    logger.info('滑块成功通过')
                    return True
                else:
                    logger.error('滑块未能通过')
                    raise Exception
            else:
                logger.error(f'{res.text}\n')
                raise Exception
        except Exception as e:
            logger.error(f'滑块验证失败\n{e}')
            return False
    async def start(self,max_try:int=3):
        cap_pass = False
        try_times = 1
        while not cap_pass or try_times > max_try:
            slider =await self.get_slider()
            if not slider:
                try_times+=1
                break
            cap_x = await self.get_position(
                bgImg=slider['bigImage'],
                sliderImg=slider['smallImage']
            )
            logger.info(f'滑块位置:{cap_x}')
            cap_pass =await self.verify(cap_x)
        return cap_pass
        
            

async def wjcAccountSignTest(account:str,pswd:str) -> bool:
    wjc = WJC(account,pswd)
    await wjc.login()
    return await wjc.isLoginSuccess()
