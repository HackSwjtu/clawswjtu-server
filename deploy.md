# claw-swjtu deploy

本次部署的方案是: flask+gunicorn+gevent+nginx+supervisor
## 安装pyenv
pyenv允许一台机器上配置多个版本的python环境
### 安装
```bash
sudo apt-get install curl git-core
curl -L https://raw.github.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
```

执行成功后，pyenv会安装到` ~/.pyenv` 中。可在`~/.bashrc`中添加环境变量：
```bash
export PYENV_ROOT="${HOME}/.pyenv
if [ -d "${PYENV_ROOT}" ]; then
  export PATH="${PYENV_ROOT}/bin:${PATH}"
  eval "$(pyenv init -)"
fi
```
然后执行`source ~/.bashrc`

### 使用

- `pyenv install $version`//$version为要安装的版本，如3.4.0
- `pyenv global $version` // 切换系统python版本

如果安装出错，可能是少了相关依赖：
```bash
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils
```
## virtualenv
用于分离python库
### 安装
安装pyenv的时候已完成，不需要独立安装

### 使用
- `pyenv virtualenv $version $name` //创建一个虚拟环境
- `rm -rf ~/.pyenv/versions/$name`/ //删除该环境

## 基本需求
首先我们需要一下这几个库来来帮助我们部署，建议在 virtualenv 中安装，以免感染系统

- gunicorn      //用 WSGI 的方式来启动 flask 项目

- gevent       //python 中比较好的网络库，提供更加高效的 I/O 读写

- supervisor      //守护进程，避免进程意外退出

安装方法：
`pyenv activate $name`
`pip install gunicorn gevent supervisor`

### 配置supervisor

进入项目文件夹，然后输出 supervisor 默认配置文件 `supervisor.conf `: ($name 是 virtualenv 环境的名称)
`~/.pyenv/versions/$name/bin/echo_supervisord_conf > supervisor.conf`
然后打开 supervisor.conf ，然后在文件的最后添加一下内容:
```
[program:myapp]
command=~/.pyenv/versions/$name/bin/gunicorn -k gevent -w2 -b0.0.0.0:9000 app:app  ; supervisor启动命令
directory=/home/myproject                                                ; 项目的文件夹路径
startsecs=0                                                              ; 启动时间
stopwaitsecs=0                                                            ; 终止等待时间
autostart=true                                                            ; 是否自动启动
autorestart=true                                                          ; 是否自动重启
stdout_logfile=/home/myproject/log/gunicorn.log                          ; log 日志
stderr_logfile=/home/myproject/log/gunicorn.err                          ; 错误日志
```

- command 中的是用 gunicorn 和 gevent 启用 Flask 项目的命令
- -w2 指的是 2 worker 一般设置成 2 * cpu_nums
- -b0.0.0.0:9000 指的是启动在 9000 端口
- run:app 是 Flask 项目入口，如果你用的是create_app() 方法的话， 就改成run:create_app()
- 所有目录都需要使用绝对路径

### 操作 Supervisor

- 启动 Supervisor
`~/.pyenv/versions/$name/bin/supervisord -c supervisor.conf`

- 查看 Supervisor 情况
`~/.pyenv/versions/$name/bin/supervisorctl -c supervisor.conf status`

- 重启 Supervisor
`~/.pyenv/versions/$name/bin/supervisorctl -c supervisor.conf reload`

- 启动 Supervisor 中某个 / 全部程序
`~/.pyenv/versions/$name/bin/supervisorctl -c supervisor.conf start [all][appname]`

- 关闭 Supervisor 中某个 / 全部程序
`~/.pyenv/versions/$name/bin/supervisorctl -c supervisor.conf stop [all][appname]`

配置好你的 supervisor.conf 文件后，执行启动命令，如果没打错命令基本就已经启动好了，这个时候你应该就可以访问 http://ip:9000 来访问到你的 Flask 项目

### SSL申请
SSL申请是用 [acme.sh](https://github.com/Neilpang/acme.sh) 申请的 Let‘s Encrypt ECC证书，具体安装我就不介绍了，简单说下证书的验证，采用dns的方式比较方便，而且多个dns运营商都有对应的api，比如阿里云：

首先去https://ak-console.aliyun.com/#/accesskey , 获取api key.
```
export Ali_Key="yourkey"
export Ali_Secret="yoursecret"
acme.sh --issue --dns dns_ali -d example.com -d www.example.com
```
允许过一次后阿里云的key和secret就会保存在`~/.acme.sh/account.conf`里面，下次就不需要重新输入了。

然后安装证书方式是：
```
acme.sh  --installcert  -d  mydomain.com   \
        --key-file   /etc/nginx/ssl/mydomain.key \
        --fullchain-file /etc/nginx/ssl/mydonain.cer \
        --reloadcmd  "service nginx force-reload"
```

### Nginx配置
进入 Nginx配置文件，或者`/etc/nginx/conf.d/default.conf` ，或者新建 `/etc/nginx/conf.d/myproject.conf`，修改配置文件:
- 禁止 IP 访问
```
server {
    listen       80 default_server;
    listen       [::]:80 default_server;
    server_name  _;

    location / {
        return 404;
    }
}
```
- 禁止 HTTP 访问
```
server {
    listen               80;
    server_name          www.myproject.com myproject.com;
    server_tokens        off;
    
    # 跳转至 HTTPS
    location / {
        rewrite ^/(.*)$ https://myproject.com/$1 permanent;
    }
}
```
- HTTPS设置 / 443端口设置
```
server {
    listen               443;
    server_name          www.myproject.com myproject.com;
    server_tokens        off;
  # SSL 设置
    ssl on;
    ssl_certificate      /etc/nginx/ssl/mydomain.cer;
    ssl_certificate_key  /etc/nginx/ssl/mydomain.key;
    ssl_ciphers EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5;
    ssl_prefer_server_ciphers  on;
    ssl_protocols              TLSv1 TLSv1.1 TLSv1.2;
    ssl_session_cache          shared:SSL:50m;
    ssl_session_timeout        1d;
    ssl_session_tickets        on;
    ssl_stapling               on;
    ssl_stapling_verify        on;
    resolver                   114.114.114.114 valid=300s;
    resolver_timeout           10s;  
  # NGINX 日志
    access_log                 /home/myproject/log/nginx.log;
  # 禁止非 GET HEAD POST OPTIONS 的访问
    if ($request_method !~ ^(GET|HEAD|POST|OPTIONS)$ ) {
        return           444;
    } 
 
  # 代理 Flask 端口
    location / {
        proxy_http_version       1.1;     
      # HSTS 头设置
        add_header               Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
        add_header               X-Frame-Options deny;     
        # 添加两个 Request Header
        proxy_set_header         X-Real_IP        $remote_addr;
        proxy_set_header         X-Forwarded-For  $proxy_add_x_forwarded_for;      
      # 代理 9000 端口
        proxy_pass               http://127.0.0.1:9000;
    }
}
```
然后重启nginx服务就可以了。