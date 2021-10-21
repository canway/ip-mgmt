/**
* This program is named IP Management Center and it is a tool to help network administrators manage enterprise IP resource pool reasonably and conveniently.
* Copyright (C) <2021>  <Guangzhou Canway Technology Co.,Ltd.>
* Contact details: jackliu@canway.net or 11th Floor, Building A，Fengxing Plaza No. 67 Tianhe East Road Tianhe District, Guangzhou, China 510630. dengyuliu, 15927493530
* This file is part of IP management center.
* IP Management Center is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
* IP Management Center is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
* You should have received a copy of the GNU General Public License along with Canway software. If not, see <https://www.gnu.org/licenses/>.
*/
import Home from '@/views/home'
import basicLayout from '@/components/layout/basicLayout'

export const frameRouter = [
    {
        path: '/',
        name: 'Home',
        component: Home,
        meta: {
            title: '首页',
            icon: 'icon-home-shape'
        }
    },
    {
        path: '/Ip',
        name: 'IpManage',
        redirect: '/Ip/addressPool',
        component: basicLayout,
        meta: {
            title: 'IP管理',
            icon: 'icon-tree-module-shape'
        },
        children: [
            {
                path: '/Ip/addressPool',
                name: 'AddressPool',
                component: resolve => require.ensure([], () => resolve(require('@/views/Ip/addressPool'))),
                meta: {
                    title: 'IP地址池管理'
                }
            },
            {
                path: '/Ip/subnet',
                name: 'Subnet',
                component: resolve => require.ensure([], () => resolve(require('@/views/Ip/subnet'))),
                meta: {
                    title: 'IP子网管理'
                }
            },
            {
                path: '/Ip/address',
                name: 'Address',
                component: resolve => require.ensure([], () => resolve(require('@/views/Ip'))),
                meta: {
                    title: 'IP地址管理'
                }
            },
            {
                path: '/Ip/abnormal',
                name: 'AbnormalIp',
                component: resolve => require.ensure([], () => resolve(require('@/views/Ip/abnormal'))),
                meta: {
                    title: '异常IP清单'
                }
            },
            {
                path: '/Ip/offlineWhitelist',
                name: 'OfflineWhitelist',
                component: resolve => require.ensure([], () => resolve(require('@/views/Ip/offlineWhitelist'))),
                meta: {
                    title: '离线白名单'
                }
            }
        ]
    },
    {
        path: '/system',
        name: 'system',
        redirect: '/system/setting',
        component: basicLayout,
        meta: {
            title: '系统管理',
            icon: 'icon-cog-shape'
        },
        children: [
            {
                path: '/system/setting',
                name: 'systemSetting',
                component: resolve => require.ensure([], () => resolve(require('@/views/system/setting'))),
                meta: {
                    title: '系统设置'
                }
            },
            {
                path: '/system/CMDB',
                name: 'CMDBManage',
                component: resolve => require.ensure([], () => resolve(require('@/views/system/CMDB'))),
                meta: {
                    title: 'CMDB同步'
                }
            },
            {
                path: '/system/custom',
                name: 'customManage',
                component: resolve => require.ensure([], () => resolve(require('@/views/system/custom'))),
                meta: {
                    title: '自定义属性'
                }
            },
            {
                path: '/system/syncRecord',
                name: 'syncRecordManage',
                component: resolve => require.ensure([], () => resolve(require('@/views/system/syncRecord'))),
                meta: {
                    title: '同步记录'
                }
            },
            {
                path: '/system/operationRecord',
                name: 'operationRecordManage',
                component: resolve => require.ensure([], () => resolve(require('@/views/system/operationRecord'))),
                meta: {
                    title: '操作日志'
                }
            }
        ]
    }
]
