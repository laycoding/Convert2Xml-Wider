<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [1. 样本工具系统说明](#1-%E6%A0%B7%E6%9C%AC%E5%B7%A5%E5%85%B7%E7%B3%BB%E7%BB%9F%E8%AF%B4%E6%98%8E)
- [2. 输入输出文本格式设计](#2-%E8%BE%93%E5%85%A5%E8%BE%93%E5%87%BA%E6%96%87%E6%9C%AC%E6%A0%BC%E5%BC%8F%E8%AE%BE%E8%AE%A1)
  - [单条json定义](#%E5%8D%95%E6%9D%A1json%E5%AE%9A%E4%B9%89)
- [3. ATFlow 服务 API 设计](#3-atflow-%E6%9C%8D%E5%8A%A1-api-%E8%AE%BE%E8%AE%A1)
  - [资源地址说明(URI)](#%E8%B5%84%E6%BA%90%E5%9C%B0%E5%9D%80%E8%AF%B4%E6%98%8Euri)
  - [状态码和通用错误](#%E7%8A%B6%E6%80%81%E7%A0%81%E5%92%8C%E9%80%9A%E7%94%A8%E9%94%99%E8%AF%AF)
    - [通用错误返回](#%E9%80%9A%E7%94%A8%E9%94%99%E8%AF%AF%E8%BF%94%E5%9B%9E)
    - [Download](#download)
    - [Augment](#augment)
    - [Eval](#eval)
    - [List](#list)
    - [Get](#get)
    - [Abort](#abort)
    - [Import](#import)
    - [Mix](#mix)
- [4.架构设计和代码组织](#4%E6%9E%B6%E6%9E%84%E8%AE%BE%E8%AE%A1%E5%92%8C%E4%BB%A3%E7%A0%81%E7%BB%84%E7%BB%87)
  - [架构设计文档](#%E6%9E%B6%E6%9E%84%E8%AE%BE%E8%AE%A1%E6%96%87%E6%A1%A3)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# 1. 样本工具系统说明
atflow为机器学习提供数据集的下载，图像处理，数据集放大，数据集图片评估等功能。
# 2. 输入输出文本格式设计
* 输入输出文本每一行为一条记录，每条记录都是一条json文本，需要特殊字符转义.
```json
{"url": "http://any_url", "type": "image", "label": {"facecluster": "人脸1", "detect": {"general_d": {"bbox": [[[10, 20], [21, 31], [81, 91]], "class": "dog"}]}}, "class": {"terror": "terror", "pulp": "sexy", "general": "dog"}}}
{"url": "http://any_url_1", "type": "image", "label": {"facecluster": "人脸2", "detect": {"general_d": {"bbox": [[[10, 20], [21, 31], [81, 91]], "class": "cat"}]}}, "class": {"terror": "normal", "pulp": "normal", "general": "cat"}}}
```
## 单条json定义
* 每条json包含图片的url和标签
* 分类和聚类的标签含义由使用者定义

```
{
    "url": "http://any_url",//完整的url，或者是bucket中文件的url
    "type": "image", // "video", "text" in future
    "source_url":"http://source_url",//图片的来源，augment等操作生成的图片，来源为原图片url，下载操作的图片，来源为原url
    "ops":"augment(param1,param2...)",//图片上进行的操作，下载为download()"
    "label": // 标签汇总
    {
            "class": { // 所有分类 labels,label类型是字符串
                "pulp": "sexy",// 剑皇
                "terror": "normal", // 暴恐
                "general": "human", // ImageNet
                "places": "home", // Places365
                ...
            },
            "detect": { // 所有检测 labels
                "general_d": {
                    "bbox": [
                        { "class": "dog", "pts":[[x0,y0], [x1,y1], ... [xk, yk]]},
                    ]
                }
            },
            "facecluster": "人脸1" //人脸聚类cluster_id
        }
}
```
# 3. ATFlow 服务 API 设计
## 资源地址说明(URI)
* HTTP， 网络资源，形如：`http://host/path`、`https://host/path`
* Qiniu，存储在Qiniu KODO的文件资源，形如：`qiniu:///zone/bucket/key`

## 状态码和通用错误
|Code|意义|
|------|------|
|200|OK|
|202|Accepted,请求已经进入后台排队|
|400|Invalid Request,用户请求错误|
|401|Unauthorized,用户没有权限|
|404|Not Found,用户请求的资源不存在|
|599|服务器异常|

### 通用错误返回
```
{
    "err":"40111",//自定义错误码
    "message":"错误信息"//错误信息
}
```

### Download
```
POST v1/dataflows/download
Authorization: Qiniu <AccessKey>:<Sign>
BODY
{
    "sourceFile":<string>,
    "prefix":<string>,
    "targetFile":<string>,
    "logFile":<string>,
    "shuffle":<bool>
}

```
| FIELD | NOTE | DEFAULT | MANDATORY |
| :--- | :--- | :--- | :--- | :--- |
|sourceFile|||Y|
|prefix|下载后文件前缀，七牛协议地址||Y|
|targetFile|生成目标文件，七牛协议地址|`sourceFile前缀+/<job_name>/target.jsonlist`|N|
|logFile|生成的日志文件，七牛协议地址|`用户configuration定义的bucket1`|N|
|shuffle|是否shuffle下载后的文件||N|

```
RESPONSE
{
    "id":<string>
}
```
| FIELD | NOTE |
| :--- | :--- |
|id|job ID|

*Example*
```
POST v1/dataflows/download
Authorization: Qiniu <AccessKey>:<Sign>
BODY
{
    "sourceFile":"qiniu:///any_path/sourceFile.txt",
    "prefix":"qiniu:///prefix",
    "targetFile":"qiniu:///any_path/targetFile.txt",//optional sourceFile前缀+/<job_name>/target.jsonlist
    "logFile":"qiniu:///any_path/logFile.log"//optional 用户configuration定义的bucket+/<job_name>/<job_name>_log.jsonlist|
}
RESPONSE
{
    "id":"jobID"
}
```

### Augment(deprecated)
```
POST v1/dataflows/augment
Authorization: Qiniu <AccessKey>:<Sign>
BODY
{
    "ops":{
        "conditionalOps":[
            {
                "condition":{
                    "type":"class",//class or detect
                    "name":"pulp",// label name
                    "classes":[
                        "pulp","sexy"
                    ]
                },
                "ops":"flip;flop;",
                "times":3 //按此规则生成几分新样本
            },
            ...
        ]//可选
        "defaultOps":{
	        "ops":"rotate/[10,20]",
            "times":1
		}//不被conditionalOps处理的文件会采用defaultOps
    },
    "sourceFile":"qiniu:///any_path/sourceFile.txt",
    "prefix":"qiniu:///target_folder",
    "targetFile":"qiniu:///any_path/targetFile.txt",//optional sourceFile前缀+/<job_name>/target.jsonlist
    "logFile":"qiniu:///any_path/logFile.log",//optional 用户configuration定义的bucket+/<job_name>/<job_name>_log.jsonlist|
    "mergeSource":<bool>//optional true/false
}
RESPONSE
{
    "id":"jobID"
}
```

### Eval(deprecated)
```
POST v1/dataflows/eval
Authorization: Qiniu <AccessKey>:<Sign>
{
    "ops":"<EVAL_OPS>",
    "sourceFile":"qiniu:///any_path/sourceFile.txt",
    "targetFile":"qiniu:///any_path/targetFile.txt",
    "logFile":"qiniu:///any_path/logFile.log"//optional 用户configuration定义的bucket+/<job_name>/<job_name>_log.jsonlist|
}
RESPONSE
{
    "id":"jobID"
}
```

### List
```
GET v1/dataflows[?limit=<int>&marker=<string>]
Authorization: Qiniu <AccessKey>:<Sign>
RESPONSE
{
    "items":[
        {
            "id":"",
            "prefix":"qiniu:///target_folder",
            "sourceFile":"qiniu:///any_path/sourceFile.txt"
            "targetFile":"qiniu:///any_path/targetFile.txt"
            "logFile":"qiniu:///any_path/logFile.log",
            "createTime":"",
            "targetFileStatistics":{
                "fileCount":100,
                "class":[{
                    "name":"className",
                    "total":100,
                    "count":{
                        "class1":10,
                        "class2":90
                    }],
                "detect":[{
                    "name":"className",
                    "total":100,
                    "count":{
                        "class1":10,
                        "class2":90
                    }],
                "facecluster":{
                    "total":10000,
                    "faceMax":100,
                    "faceMin":5
                }
            }，
        },
        ...
    ]
}
```

* limit: 可选，限制结果数量，默认100，最大500。
* marker: 可选，上一次结果的位置标记，默认从 createTime 最新开始。

### Get
```
GET v1/dataflows/:jobID
Authorization: Qiniu <AccessKey>:<Sign>
RESPONSE
{
    "id":"",
    "prefix":"qiniu:///target_folder",
    "sourceFile":"qiniu:///any_path/sourceFile.txt"
    "targetFile":"qiniu:///any_path/targetFile.txt"
    "logFile":"qiniu:///any_path/logFile.log",
    "createTime":""，
    "targetFileStatistics":{
        "fileCount":100,
        "classification":[{
            "name":"className",
            "total":100,
            "count":{
                "class1":10,
                "class2":90
            }],
        "detection":[{
            "name":"className",
            "total":100,
            "count":{
                "class1":10,
                "class2":90
            }],
        "facecluster":{
            "total":10000,
            "faceMax":100,
            "faceMin":5
        }
    }，
}
```
* jobID: <string>

### Abort
```
POST v1/dataflows/:jobID/abort
Authorization: Qiniu <AccessKey>:<Sign>
RESPONSE

```
* jobID: <string>

### Import(deprecated)
```
POST v1/dataflows/import
Authorization: Qiniu <AccessKey>:<Sign>
BODY
{
    "sourceFile":"qiniu:///any_path/sourceFile.txt",
}
RESPONSE

```

### Mix
```
POST v1/dataflows/mix
Authorization: Qiniu <AccessKey>:<Sign>
<InputOp>
{
    "name": <string>,
    "type": "input",
    "preOps": [],
    "postOps": [<string>],
    "params": {
        "file": <string>
    }
}
<FilterOp>
{
    "name": <string>,
    "type": "filter",
    "preOps": [<string>],
    "postOps": [<string>],
    "params": {
        "label": <string>,
        "values": [<string>]
    }
}
<AugmentOp>
{
    "name": <string>,
    "type": "augment",
    "preOps": [<string>],
    "postOps": [<string>],
    "params": {
        "condition": [<AugmentCondition>],
        "ops":<string>
    }
}
<AugmentCondition>
{
    "label":<string>,
    "values":map[string]float
}
<OutputOp>
{
    "name": <string>,
    "type": "output",
    "preOps": [<string>],
    "postOps": [],
    "params": {
        "prefix": <string>,
        "file": <string>
    }
}

BODY
<MixRequest>
{
  "ops": [<InputOp>|<FilterOp>|<AugmentOp>|<OutputOp>],
  "logFile": <string>
}

RESPONSE
{
    "id":<string>
}
```

MixRequest

| FIELD | NOTE | DEFAULT | MANDATORY |
| :--- | :--- | :--- | :--- | :--- |
|ops|放大操作节点定义||Y|
|logFile|生成的日志文件||Y|


InputOp

| FIELD | NOTE | DEFAULT | MANDATORY |
| :--- | :--- | :--- | :--- | :--- |
|name|操作名,需要具有唯一性||Y|
|type|操作类型|input|Y|
|preOps|前置操作名,必须这些操作|[]必须位空数组|Y|
|postOps|后置操作名数组,必须存在这些操作,后置操作必须是`<FilterOp>或<AugmentOp>或<OutputOp>`||Y|
|params.file|输入文件名,七牛协议地址||Y|


FilterOp

| FIELD | NOTE | DEFAULT | MANDATORY |
| :--- | :--- | :--- | :--- | :--- |
|name|操作名,需要具有唯一性||Y|
|type|操作类型|filter|Y|
|preOps|前置操作名,必须这些操作,前置操作必须是`<InputOp>`||Y|
|postOps|后置操作名数组,必须存在这些操作,后置操作必须是`<AugmentOp>`||Y|
|params.label|过滤标签名||Y|
|params.values|过滤标签值||Y|


AugmentOp

| FIELD | NOTE | DEFAULT | MANDATORY |
| :--- | :--- | :--- | :--- | :--- |
|name|操作名,需要具有唯一性||Y|
|type|操作类型|augment|Y|
|preOps|前置操作名,必须这些操作,前置操作必须是`<InputOp>,<FilterOp>或<AugmentOp>`||Y|
|postOps|后置操作名数组,必须存在这些操作,后置操作必须是`<AugmentOp>或<OutputOp>`||Y|
|params.condition|放大条件||Y|
|params.ops|放大操作||Y|


AugmentCondition

| FIELD | NOTE | DEFAULT | MANDATORY |
| :--- | :--- | :--- | :--- | :--- |
|label|过滤标签名||Y|
|values|过滤标签值和放大倍数||Y|


OutputOp

| FIELD | NOTE | DEFAULT | MANDATORY |
| :--- | :--- | :--- | :--- | :--- |
|name|操作名,需要具有唯一性||Y|
|type|操作类型|output|Y|
|preOps|前置操作名,必须这些操作||Y|
|postOps|后置操作名数组|[]必须为空数组|Y|
|params.prefix|生成图片存放位置前缀，七牛协议地址||Y|
|params.file|输出文件，七牛协议地址||Y|


Example
```
POST v1/dataflows/mix
Authorization: Qiniu <AccessKey>:<Sign>
BODY
{
  "ops": [
    {
        "name": "source", // 作为 op 的唯一ID
        "type": "input",
        "preOps": [],  // 前置操作，对于 input 为空
        "postOps": [<OpName>, ...], // 后置操作，OpName 指 op 节点的 name 字段
        "params": {
            "file": "qiniu:///any_path/source.txt"
        }
    }
    {
        "name": "filter1",
        "type": "filter",
        "preOps": [<OpName>, ...],
        "postOps": [<OpName>, ...],
        "params": {
            "label": "class.pulp", // 过滤的标签名
            "values": ["normal", "sexy"...] // 过滤的标签值
        }
    },
    {
        "name": "flip1",
        "type": "augment",
        "preOps": [<OpName>, ...],
        "postOps": [<OpName>, ...],
        "params": {
            "condition": [
                {
                    "label":"class.pulp",
                    "values": {
                        "normal": 3, // 按此规则生成几分新样本
                        "sexy": 4,
                        ...
                    }
                },
                ...
            ],
            "ops":"flip" // 限一个变换操作
        }
    },
    {
        "name": "result",
        "type": "output",
        "preOps": [<OpName>, ...],
        "postOps": [], // 对于 output 为空
        "params": {
            "prefix": "qiniu:///target_folder",
            "file": "qiniu:///any_path/result.txt"
        }
    }
  ],
  "logFile": "qiniu:///any_path/logFile.log" // 可选
}
RESPONSE
{
    "id":<string>
}
```

说明：

* name 唯一。
* type类型：input, output, filter, augment。
* 一个 op 的输入为前置 op 的输出，一个 op 的输出为后置 op 的输入。如果有多个前置 op，则先合并输出作为输入。如果有多个后置 op，则输出分别作为后置的输入。
* 可以有多个 input，但只能有一个 output。
* 不能有循环操作（环形）。



# 4.架构设计和代码组织

## 架构设计文档

* 参考AtNet文档 [AtNet文档](https://cf.qiniu.io/pages/viewpage.action?pageId=17660870)
* Job相关 [Ava Job](Ava.job.md)

