![](static/img/ip-mgmt.png)
---
[![license](https://img.shields.io/badge/license-GPLv3-brightgreen.svg)](LICENSE.txt)
[![Release](https://img.shields.io/badge/release-1.6.0-brightgreen.svg)](https://github.com/canway/ip-mgmt/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/canway/ip-mgmt/pulls)


IP管理中心（IP-mgmt）是协助网络管理员便捷、合理管理企业IP资源池的工具。

IP管理中心基于蓝鲸PAAS平台开发，主要服务于网络管理员，功能包括：IP地址池、子网的管理以及导入/导出，IP地址的分配、保留、回收，
能够满足网络管理员日常的工作需要，提高对网络资源的管理能力；
IP地址可以检测，检测的条件和白名单均可配置，检测为异常的IP将会被单独放置，降低了人工排查问题IP的成本，
除此之外，还提供了自动检测IP在线状态，极大的方便了原本繁琐的工作；
IP管理中心可以直接从CMDB同步模型，提高工作协同能力。

IP管理中心后台使用 Python 作为开发语言，使用 Django 开发框架；前端使用 Vue 开发页面。


## Overview
- [架构设计](docs/overview/architecture.md)
- [代码目录](docs/overview/code_structure.md)
- [使用场景](docs/overview/usecase.md)


## Features
- 多元接入支持：IP管理中心对接了蓝鲸PAAS平台用户管理、配置平台等服务。


## Getting started
- [开发环境后台部署](docs/install/dev_deploy.md)
- [开发环境前端部署](docs/install/dev_web.md)
- [正式环境源码部署](docs/install/source_code_deploy.md)
- [正式环境上传部署](docs/install/upload_pack_deploy.md)


## Version plan
- [版本日志](docs/release.md)


## Contributing
如果你有好的意见或建议，欢迎给我们提 Issues 或 Pull Requests，为嘉为开源社区贡献力量。关于IP管理中心分支管理、Issue 以及 PR 规范，
请阅读 [Contributing Guide](docs/CONTRIBUTING.md)。


## License
IP管理中心是基于 GPL-V3 协议， 详细请参考 [LICENSE](LICENSE.txt) 。