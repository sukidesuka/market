# electron-market
币安非官方套利助手

## 如何编译客户端？
### 环境安装
1. 安装```node.js```
1. 将目录切换到代码根目录
1. 敲入命令```npm install -g cnpm```来安装```cnpm```
1. 敲入命令```cnpm install```来安装所有的依赖 
1. 敲入

### 启动编译
```
cnpm run electron:build
```

## 如何部署服务端程序？
因为币安被墙，同时为了提升下单的连接稳定性，请将服务器部署到海外，最好是美国
### 部署服务器的前置条件（强烈建议）
- 一个域名
- 对应域名的https证书

域名可以在godaddy一年十块钱买到，证书可以在阿里云、腾讯云免费签发
### 部署过程
1. 将```server_src```所有内容复制到服务器
1. 安装python的依赖库```pip3 install flask flask-cors numpy requests```
1. 运行```make_default_config.py```创建默认的配置文件
1. 在后台服务端程序```nohup python3 -u api.py &```

注：程序会在后台运行，想看log输入
```
tail nohup.out
```