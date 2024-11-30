# README

芜湖学院（原 安徽师范大学皖江学院） 签到自动化

目前实现：

- 使用更好的日志模块loguru
- 签到端
  - 用于从数据库中提取用户数据并在规定时间内启动签到任务，完成后自动等待至下一次签到开始。
  - 对于签到次数过多的账号，将会自动停用该账号
    - 签到失败天数达到3天
  - 支持多用户同时签到
- 注册信息端
  - 提供Web页面向用户提供注册功能，将用户提交的信息保存至数据库供签到端使用
  - 为用户提供取消签到功能，用户可自行选择是否启用自动签到（是否停用）
  - 可通过API向网页推送通知信息


> 免责声明
> 
> 本代码遵循 GPL-3.0 License 协议，允许开源/免费使用和引用/修改/衍生代码的开源/免费使用，不允许修改和衍生的代码作为闭源的商业软件发布和销售，禁止使用本代码盈利，以此代码为基础的程序必须同样遵守 GPL-3.0 License 协议
> 
> 本代码仅用于学习讨论，禁止用于盈利
> 
> 他人或组织使用本代码进行的任何违法行为与本人无关

## 使用说明

> 你可以[使用docker部署](#使用docker部署)，免去下面一些步骤。

### 准备环境：

- Python3.8+

使用pip安装依赖：

```shell
pip install -r requirements.txt
```

> 注意，项目采用了[ddddocr](https://github.com/sml2h3/ddddocr)来实现验证码识别，请检查你需要部署的平台是否支持此库，参考文档：[README - ddddocr](https://github.com/sml2h3/ddddocr/blob/main/README.md)

### 配置

复制`setting_template.ini`文件并命名为`setting.ini`，然后自行参照配置文件`setting.ini`内的说明进行配置。

> 1.6.0版本之后，`auto_sign.py`强制使用Mysql以支持多用户并发签到功能，配置文件中的`choose`值只会影响到旧的签到脚本和`web_app.py`，因此如果想使用sqlite3，请参阅 [旧版本使用说明](#旧的签到脚本)

### 添加数据

#### 手动添加数据

推荐先启动`auto_sign.py`来初始化下数据库，然后再向`signInfo.db`中添加数据

> 你也可以参照`setting.py`中的`DB_INIT_SQL`来手动创建对应的表结构。

#### 使用Web端添加数据

需要Node.js环境，进入`web_app`目录下执行

```shell
npm install
npm run build
```

待前端文件打包完毕后，回到根目录执行以下指令启动Web端

```shell
python web_app.py
```

访问`http://127.0.0.1:8000`即可进行注册

### 开始自动签到

完成上面的准备步骤后，现在可以将`auto_sign.py`启动，它会自动从数据库中提取用户数据并在规定时间内启动签到任务，完成后自动等待至下一次签到开始。

每次完成签到任务，都会向每个用户发送邮件确认，并额外向管理员发送邮件汇报今日签到任务结果。

## 使用Docker部署

> docker镜像中默认使用的是支持并发版本的签到脚本，需要准备Mysql数据库

1. 准备docker环境
2. 复制`setting_template.ini`并命名为`setting.ini`，根据其中说明进行配置，需要配置mysql数据库信息，以及邮箱等
3. 配置网页端端口（可选）
   1. 自行配置环境变量`APP_PORT`
   2. 直接修改文件`docker-compose.yml`中`"${APP_PORT:-8000}:8000"`为`"${APP_PORT:-xxxx}:8000"`，其中`xxxx`是你希望修改为的端口号，例如`"${APP_PORT:-80}:8000"`，会让前端页面运行在80端口上
4. 使用指令启动`docker-compose up -d`，之后你会得到两个不同功能的容器。
5. 前往`http://127.0.0.1:8000`（默认端口为`8000`）添加需要签到的用户


## 旧的签到脚本

为了支持多用户并发签到，脚本强制使用Mysql，旧版本保留在了`resource/deprecated`下，如果你需要使用旧版本和Sqlite3，将下面所有文件覆盖到根目录即可，然后开始配置或用Docker部署。

**无论新老脚本，最终效果都取决于学校服务器**，实际测试下，即使是旧的脚本，在空闲时间段也能飞速完成所有用户的签到，与新脚本耗时相差不大。所以你可以自行选择。

## 开发说明

签到步骤：

- 根据设置的账号密码登录获取必要的Token或Cookies
- (额外)检测是否需要验证，如若需要则启动反验证码模块
- 携带必要信息查询签到任务
- 根据设置签到任务
- (额外)通知设置的账户信息签到状态


## API记录

### 登录

API:

- URL:`https://ids.uwh.edu.cn/authserver/login?service=https://ehall.uwh.edu.cn/login`
- METHOD: GET | POST
- PARAMS: NONE
- DATA: (FORM)
  - username:账号
  - password:密码（加密）
  - captcha:验证码
  - _eventId:`submit`
  - cllt:`userNameLogin`
  - dllt:`generalLogin`
  - lt: 保持为空
  - execution:来自前置页面

前置页：需要预先GET此页，包含了POST时所需的必要信息（data和cookie）

API:

- URL:`https://ehall.uwh.edu.cn/student/cas`
- METHOD: POST

上一个请求成功后携带Cookie直接访问即可，另有登录界面，需要额外密码（身份证号后六位），不推荐。

### 检查是否需要验证码

**2024-09-13时发现已不再使用，与字符验证码配套使用**

- URL:`https://ids.uwh.edu.cn/authserver/checkNeedCaptcha.htl`
- METHOD: GET
- PARAMS: 
  - username:账号
  - _: 时间戳，例如`1725687148153`

Response:

```json
{"isNeed":true}
```

其中`isNeed`为`true`则需要携带验证码才可正常登录。

### 获取验证码

#### 字符验证码

**2024-09-13时发现已不再使用**

- URL:`https://ids.uwh.edu.cn/authserver/getCaptcha.htl`
- METHOD: GET
- PARAMS: 
  - 时间戳

*时间戳直接跟随在URL后，例如`
https://ids.uwh.edu.cn/authserver/getCaptcha.htl?1725688689325`*

Response: 
`image/jpeg`图片

例如：
![](https://ids.uwh.edu.cn/authserver/getCaptcha.htl)

#### 滑块验证码

##### 请求验证码

- URL:`https://ids.uwh.edu.cn/authserver/common/openSliderCaptcha.htl`
- METHOD: GET
- PARAMS: 
  - _: 时间戳，例如`1725687148153`

Response:

```json
{
  "smallImage":"小滑块图片BASE64值",
  "bigImage":"背景缺口图片BASE64值",
  "tagWidth": 85,
  "yHeight": 0
}
```

##### 验证验证码

- URL:`https://ids.uwh.edu.cn/authserver/common/verifySliderCaptcha.htl`
- METHOD: POST
- DATA: (FORM)
  - `canvasLength`:`280`（验证码总长度，基本不变）
  - `moveLength`:    滑块移动横坐标值

Response:
成功示例：

```json
{
    "errorCode": 1,
    "errorMsg": "success"
}
```

失败示例：

```json
{
  "errorCode":0,
  "errorMsg":"error"
}
```

> **重要说明**
> 
> 通过验证码验证后，不会响应有价值的信息，也没有新的Cookies，经过验证后得知其验证流程为：
> 
> 是在之前的请求中，响应了Cookies，需要携带这些Cookies请求并验证，通过后，这些Cookies就充当了Token的角色，从而使后面的登录等操作得以正常进行。
> 
> 因此只需要在原有的流程中将请求和验证滑块验证码放置于登录前即可，不影响登陆后的一系列操作。

### 获取签到任务

API: 

- URL: 'https://ehall.uwh.edu.cn/student/content/tabledata/student/sign/stu/sign'
- METHOD: GET
- PARAMS: 见下
- RESPONSE-TYPE: (JSON)见下

Params:

```python
params_load = {
            "bSortable_0": "false",
            "bSortable_1": "true",
            "iSortingCols": "1",
            "iDisplayStart": "0",
            "iDisplayLength": "12",
            "iSortCol_0": "3",
            "sSortDir_0": "desc",
            "_t_s_": "1711441937310"
        }
```

其中`_t_s_`为13位时间戳

Response:

```json
{
    "sEcho": 1,
    "iDisplayStart": 0,
    "iDisplayLength": 12,
    "iSortColList": [2],
    "sSortDirList": ["desc"],
    "iTotalRecords": 1,
    "iTotalDisplayRecords": 1,
    "aaData": [{
        "UPDATE_COUNT": 2,
        "JSSJ": "2024-03-26 23:00:00",
        "QDFS": "1",
        "SJDM": "17112924123429681075",
        "QDCS": null,
        "VALID": "0",
        "DM": "17089192567824456997",
        "JLDM": null,
        "QDWZ_DZ": null,
        "QDLB": "晚间签到",
        "QDSJ": null,
        "UPDATE_IND": "1",
        "FBR": "张铮",
        "SUBJECT": "江北校区晚间签到",
        "KSSJ": "2024-03-26 20:30:00",
        "ISFZR": "0"
    }]
}
```

成功签到示例：

```json
{
    "code": 1,
    "msg": "成功获取签到任务",
    "info": {
        "sEcho": 1,
        "iDisplayStart": 0,
        "iDisplayLength": 12,
        "iSortColList": [2],
        "sSortDirList": ["desc"],
        "iTotalRecords": 1,
        "iTotalDisplayRecords": 1,
        "aaData": [
            {
                "UPDATE_COUNT": 2,
                "JSSJ": "2024-03-26 23:00:00",
                "QDFS": "1",
                "SJDM": "17112924123429681075",
                "QDCS": 1,
                "VALID": "1",
                "DM": "17089192567824456997",
                "JLDM": "17114572277777336296",
                "QDWZ_DZ": "中国安徽 省芜湖市鸠江区二坝镇通江大道辅路",
                "QDLB": "晚间签到",
                "QDSJ": "2024-03-26 20:47:07",
                "UPDATE_IND": "1",
                "FBR": "张铮",
                "SUBJECT": "江北 校区晚间签到",
                "KSSJ": "2024-03-26 20:30:00",
                "ISFZR": "0"
            }
        ]
    }
}
```

其中:

- `JSSJ`：签到结束时间
- `KSSJ`: 签到开始时间
- `SJDM`和`DM`: 后续签到需要用到的信息。
- `QDSJ`: 签到时间 时间格式：`YYYY-MM-DD H:M:S`
  - `null` 未签到
- `VALID`: 
  - `"0"`：未开始
  - `"1"`：已开始

### 签到

- URL: 'https://ehall.uwh.edu.cn/student/content/student/sign/stu/sign'
- METHOD: POST
- PARAMS: 
  - `_t_s_`：时间戳
- DATA: 见下
- RESPONSE-TYPE: (JSON)见下

DATA:

```python
data_form = {
  "pathFile": "",
  "dm": "17089192567824456997", # 查询签到任务中的DM
  "sjdm": "17112924123429681075",# 查询签到任务中的SJDM
  "zb": "118.26641806588259,31.362924260242725", # 坐标
  "wz": "安徽师范大学皖江学院（江北校区）附近",
  "ly": "lbs",  # 未知，此为网页端测试结果，手机端为`wis`
  "qdwzZt": "0",  # 未知
  "fwwDistance": "0",    #距离签到位置距离，最新API似乎已经废弃
  "operationType": "Update" # 签到类型，首次签到时填写`Update`不影响签到结果
}
```

*其中坐标可使用小数点后五位的精确坐标，未测试更低精度坐标是否有影响*

RESPONSE（成功签到）:

```json
{
  "errorInfoList":[],
  "result": true,
  "msg": null
}
```

## 更新日志

- 2024-11-30_Ver1.6.3:
  - 注册&更新逻辑改进
- 2024-11-04_Ver1.6.2:
  - 修改一些提示内容
  - 邮箱验证码有效期设为10分钟并增加发送限制
  - 统一使用MysqlPoolControl
- 2024-10-31_Ver1.6.1:
  - 前端提供站点信息
  - 优化前端显示内容
- 2024-10-29_Ver1.6.0:
  - 支持多用户并发签到，提升签到效率，缩减总耗时
- 2024-10-27_Ver1.5.3:
  - 修复一些问题
  - 支持Docker部署
- 2024-10-24_Ver1.5.2:
  - 优化项目结构
  - 邮件推送内容改用jinja2渲染
- 2024-09-23_Ver1.5.1:
  - 修复数据库断连问题和其它问题
- 2024-09-22_Ver1.5.0:
  - 使用ini文件作为配置文件
  - 支持选择Sqlite3或Mysql作为数据库，并在选择Mysql的情况下取消Web页的注册时间段限制
  - 坐标设置页按钮添加防抖
  - 对于已经签到过了将不会再签到
- 2024-09-15_Ver1.4.1:
  - 现在可向网页推送通知信息
- 2024-09-14_Ver1.4.0:
  - 修复接近任务开始时间异常等待至下一天的问题
  - 跟进官方，加入新的SliderPass模块专门用于解决滑块验证码，现已可正常使用
  - 取消对旧验证码（字符验证码）的请求与验证，改为验证滑块
- 2024-09-09_Ver1.3.2:
  - 修复超时导致的签到失败队列加载失败的问题
  - 修复超过签到时间后自动等待时间异常问题
- 2024-09-08_Ver1.3.1:
  - 签到位置名现在可在配置中设置
- 2024-09-07_Ver1.3.0:
  - 修复签到失败队列逻辑
  - 增加验证码的识别与验证
- 2024-09-01_Ver1.2.2:
  - 现在只会在签到失败后向指定的邮箱发送邮件
  - 现在前端提供取消签到任务的选项
- 2024-05-26_Ver1.2.1:
  - 修复因登录超时却未能加入失败队列的问题
  - 注册成功邮件恢复正常发送
- 2024-05-18_Ver1.2.0:
  - 使用React + Anti Design 重构的前端界面，提供更好更合理的注册或更新过程
  - 使用FastAPI重构的后端，更加合理的注册的流程
  - 现在会在确认账号有效且邮箱有效后进行账号注册，避免账号被恶意注册以及密码错误导致无法签到等问题
  - 增加超时机制，避免一个账号失去响应后导致整个签到队列停止
- 2024-05-15_Ver1.1.2:
  - 修复注册失败
- 2024-05-15_Ver1.1.1:
  - 部分模块引入loguru日志模块
- 2024-04-30_Ver1.1.0:
  - 新增连续签到失败自动封禁功能
- 2024-04-23_Ver1.0.2:
  - Web端时间段检测增加1s延迟以尽可能规避数据库链接抢占。
- 2024-04-22_Ver1.0.1:
  - Web端增加时间段检测，禁止在签到时间段内进行注册等数据库操作。
- 2024-04-21_Ver1.0.0:
  - 正式版本
