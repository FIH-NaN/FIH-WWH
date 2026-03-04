---
title: Wealth Wellness Hub API
language_tabs:
  - shell: Shell
  - http: HTTP
  - javascript: JavaScript
  - ruby: Ruby
  - python: Python
  - php: PHP
  - java: Java
  - go: Go
toc_footers: []
includes: []
search: true
code_clipboard: true
highlight_theme: darkula
headingLevel: 2
generator: "@tarslib/widdershins v4.0.30"

---

# Wealth Wellness Hub API

Wealth Wellness Hub - 资产管理平台 API 接口文档

Base URLs:

# Authentication

- HTTP Authentication, scheme: bearer

# Default

## POST 用户注册

POST /auth/register

> Body Parameters

```json
{
  "email": "string",
  "password": "string",
  "name": "string"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» email|body|string| yes |邮箱地址（唯一）|
|» password|body|string| yes |密码（6-20位）|
|» name|body|string| yes |用户昵称|

> Response Examples

> 201 Response

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "张三"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|创建成功|Inline|

### Responses Data Schema

## POST 用户登录

POST /auth/login

> Body Parameters

```json
{
  "email": "string",
  "password": "string"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» email|body|string| yes |none|
|» password|body|string| yes |none|

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|登录成功|None|

## GET 获取当前用户

GET /auth/me

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|None|

## GET 获取资产列表

GET /assets

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|type|query|string| no |none|
|category|query|string| no |none|
|page|query|integer| no |none|
|limit|query|integer| no |none|

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|None|

## POST 创建资产

POST /assets

> Body Parameters

```json
{
  "name": "string",
  "type": "cash",
  "value": 0,
  "currency": "string",
  "category": "string",
  "description": "string"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» name|body|string| yes |资产名称|
|» type|body|string| yes |资产类型|
|» value|body|number| yes |资产价值|
|» currency|body|string| no |币种|
|» category|body|string| no |分类|
|» description|body|string| no |描述|

#### Enum

|Name|Value|
|---|---|
|» type|cash|
|» type|stock|
|» type|fund|
|» type|crypto|
|» type|property|
|» type|other|

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|创建成功|None|

## GET 获取单个资产

GET /assets/{id}

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer| yes |none|

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|None|
|404|[Not Found](https://tools.ietf.org/html/rfc7231#section-6.5.4)|资产不存在|None|

## PUT 更新资产

PUT /assets/{id}

> Body Parameters

```json
{
  "name": "string",
  "value": 0,
  "description": "string"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer| yes |none|
|body|body|object| no |none|
|» name|body|string| no |none|
|» value|body|number| no |none|
|» description|body|string| no |none|

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|更新成功|None|

## DELETE 删除资产

DELETE /assets/{id}

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer| yes |none|

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|删除成功|None|

## GET 资产总览

GET /assets/summary

> Response Examples

> 200 Response

```json
{
  "success": true,
  "data": {
    "totalValue": 150000,
    "totalValueCNY": 780000,
    "currency": "SGD",
    "exchangeRate": {
      "SGD": 1,
      "USD": 0.74,
      "CNY": 5.2
    },
    "assetCount": 12,
    "netWorth": 130000
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### Responses Data Schema

## GET 资产分布

GET /assets/distribution

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|None|

## GET 资产趋势

GET /assets/trend

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|period|query|string| no |none|
|months|query|integer| no |none|

#### Enum

|Name|Value|
|---|---|
|period|week|
|period|month|
|period|quarter|
|period|year|

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|None|

## GET 资产健康分

GET /assets/health-score

> Response Examples

> 200 Response

```json
{
  "success": true,
  "data": {
    "score": 85,
    "grade": "A",
    "factors": [
      {
        "name": "资产分散度",
        "score": 90
      },
      {
        "name": "流动性",
        "score": 80
      },
      {
        "name": "投资回报",
        "score": 85
      }
    ]
  }
}
```

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|Inline|

### Responses Data Schema

## GET 获取交易列表

GET /transactions

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|assetId|query|integer| no |none|
|type|query|string| no |none|
|startDate|query|string| no |none|
|endDate|query|string| no |none|

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|None|

## POST 创建交易

POST /transactions

> Body Parameters

```json
{
  "assetId": 0,
  "type": "income",
  "amount": 0,
  "category": "string",
  "description": "string",
  "date": "string"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» assetId|body|integer| yes |none|
|» type|body|string| yes |none|
|» amount|body|number| yes |none|
|» category|body|string| no |none|
|» description|body|string| no |none|
|» date|body|string| no |none|

#### Enum

|Name|Value|
|---|---|
|» type|income|
|» type|expense|

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|创建成功|None|

## POST 批量导入交易

POST /transactions/import

> Body Parameters

```json
{
  "transactions": [
    {
      "assetId": 0,
      "type": "string",
      "amount": 0,
      "category": "string",
      "date": "string"
    }
  ]
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» transactions|body|[object]| no |none|
|»» assetId|body|integer| no |none|
|»» type|body|string| no |none|
|»» amount|body|number| no |none|
|»» category|body|string| no |none|
|»» date|body|string| no |none|

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|导入成功|None|

## GET 获取分类列表

GET /categories

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|type|query|string| no |none|

#### Enum

|Name|Value|
|---|---|
|type|asset|
|type|transaction|

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|成功|None|

## POST 创建分类

POST /categories

> Body Parameters

```json
{
  "name": "string",
  "type": "string",
  "icon": "string"
}
```

### Params

|Name|Location|Type|Required|Description|
|---|---|---|---|---|
|body|body|object| yes |none|
|» name|body|string| yes |none|
|» type|body|string| yes |none|
|» icon|body|string| no |none|

### Responses

|HTTP Status Code |Meaning|Description|Data schema|
|---|---|---|---|
|201|[Created](https://tools.ietf.org/html/rfc7231#section-6.3.2)|创建成功|None|

# Data Schema

