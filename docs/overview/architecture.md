# 架构设计

![](../resource/img/architecture.png)

这是IP管理中心的逻辑架构图，可以分为三层：

- API 
主要负责通过API网关与CMDB进行交互。
- 接入层
包含权限控制、API接口和数据统计等。
- 资源管理
IP地址池、IP子网、IP等的管理