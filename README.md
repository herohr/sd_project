# API文档

## 用户

### 用户注册  /user/register

**POST表单**

| 表单项      | 数据类型           | 示例                                 |
| -------- | -------------- | ---------------------------------- |
| username | string(64)     | "test"                             |
| password | string(32)-MD5 | "34819d7beeabb9260a5c854bc85b3e44" |
| email    | string(64)     | "test@test.email"                  |

**响应**

| 响应码  | 解释       | json内容                                   |
| ---- | -------- | ---------------------------------------- |
| 200  | 注册成功     | {}                                       |
| 400  | 某项输入太长   | {<br />"reason": "...",<br />"tags": ["username", ...]} |
| 409  | 用户名已存在   | {<br />"reason":"..."}                   |
| 405  | HTTP方法错误 | {"reason":"..."}                         |

### 用户登陆、鉴权 /user/login

**POST表单**

| 表单项      | 数据类型           | 示例                                 |
| -------- | -------------- | ---------------------------------- |
| username | string(64)     | "test"                             |
| password | string(32)-MD5 | "34819d7beeabb9260a5c854bc85b3e44' |

**响应**

| 响应码  | 解释           | json内容                                   |
| ---- | ------------ | ---------------------------------------- |
| 200  | 登陆成功，返回身份识别码 | {"authorization":"26be104b-1544-3a1d-bbda-76d5b32be521"} |
| 400  | 用户名或密码错误     | {"reason":"..."}                         |
| 405  | HTTP方法错误     | {"reason":"..."}                         |

### 用户初始个人信息 /user/info/initial

**POST表单**

| 表单项           | 数据类型       | 示例                                     |
| ------------- | ---------- | -------------------------------------- |
| authorization | string     | “26be104b-1544-3a1d-bbda-76d5b32be521” |
| nickname      | string(64) | "petty"                                |
| sex           | string(8)  | "male" / "female"                      |
| age           | integer    | 18                                     |
| college       | string(64) | "陕西师范大学"                               |

