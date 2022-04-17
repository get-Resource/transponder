from flask import Flask
from flask import request
import os
import time
import random
import sys
import string
import psutil
import re
app = Flask(__name__)

# 文件存放地址
mainPath="/root/nat_traverse/transponder/outer_server/"
# ng配置文件存放地址
ngConfigPath="/etc/nginx/conf.d/"
# 你的域名
domain="peng.cn"


#添加端口映射
@app.route('/add')
def add():
    # 设置端口信息
    if os.path.exists("./port.txt") == False:
        pf=open("./port.txt",'w')
        pf.write("9000")
        pf.close
        port=9000
    else:
        portFile = open("./port.txt",'r')
        port=portFile.read()
        portFile.close()
        
    serverPort=int(port)+1
    
    # 端口信息存会文件中
    portFile = open("./port.txt",'w')
    portFile.write(str(serverPort))
    portFile.close()
    
    fileName="main" + str(serverPort)
    
    # 操作服务端 打包添加配置文件
    os.mkdir(mainPath+fileName+"s")
    os.system('cd '+mainPath+';cp -r outer_server ./'+fileName+"s;cd "+fileName+"s;cp ../outer_server "+fileName)
    fp = open(mainPath+fileName+"s/outer.config.json",'w')
    psd=random.randint(10000000000,90000000000)
    fp.write('{"InnerServerAddress": "tcp://0.0.0.0:'+str(serverPort)+'","OuterServerAddress": "unix:///var/run/'+fileName+'.sock","AuthKey": "'+str(psd)+'"}')
    fp.close()
    #操作ng  添加ng配置文件
    f=open(ngConfigPath+fileName+".conf","w")
    head=generate_random_str(6)
    conf = """
server {
	listen 80;
	server_name  %s.%s;
	access_log  /var/log/www.abc.com.access.log;
	error_log  /var/log/www.abc.com.error.log;
	location / {
		proxy_pass http://unix:/var/run/%s.sock:/;
		proxy_redirect     off;
		proxy_set_header   Host             $host;
		proxy_set_header   X-Real-IP        $remote_addr;
		proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
		proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
		proxy_max_temp_file_size 0;
		proxy_connect_timeout      90;
		proxy_send_timeout         90;
		proxy_read_timeout         90;
		proxy_buffer_size          4k;
		proxy_buffers              4 32k;
		proxy_busy_buffers_size    64k;proxy_temp_file_write_size 64k;
	}
}
"""%(head,domain,fileName)
    print(conf)
    f.write(conf)
    f.close()
    os.system("nginx -s reload")
    os.system("cd "+mainPath+fileName+"s;nohup ./"+fileName+" &")
    
    f=open("./portAll.txt","a")
    f.write(","+fileName)
    f.close()
    
    return "<h1 style='margin-bottom:30px;'>启动成功</h1><br>服务器：111.67.195.173:"+str(serverPort)+"<br>客户端域名：http://"+head+"."+domain+"<br>秘钥："+str(psd)

#删除对应的外网端口
@app.route('/kill')
def kill():
    port = request.args.get("port")
    fileName="main"+str(port)
    pid=processinfo(fileName)
    if pid==False:
        return "没有找改进程"
    os.system("kill -9 "+str(pid))
    os.system("cd "+mainPath+";rm -rf "+fileName+"s")
    os.system("cd /run;rm  "+fileName+".sock")
    os.system("cd "+ngConfigPath+";rm "+fileName+".conf;nginx -s reload")
    return "操作成功！"
    
#删除全部端口映射
@app.route('/killAll')
def killAll():
    if os.path.exists("./portAll.txt") == False:
        return "无端口映射"
    portFile = open("./portAll.txt",'r')
    portAllStr=portFile.read()
    portAllArr=portAllStr.split(",")
    myStr="<h1 style='margin-bottom:30px;'>操作成功</h1>"
    for v in portAllArr:
        if len(v) > 0:
            fileName=v
            pid=processinfo(fileName)
            if pid==False:
                myStr=myStr+"未找到进程："+fileName+"<br>"
            else :
                myStr=myStr+"成功停止进程："+fileName+"<br>"
                os.system("kill -9 "+str(pid))
            os.system("cd "+mainPath+";rm -rf "+fileName+"s")
            os.system("cd /run;rm "+fileName+".sock")
            os.system("cd "+ngConfigPath+";rm "+fileName+".conf;nginx -s reload")
    f=open("./portAll.txt","w")
    f.write("")
    f.close()
    f=open("./port.txt","w")
    f.write("9000")
    f.close()
    return myStr
    

# 获取进程ID
def processinfo(processName):
    pids = psutil.pids()
    for pid in pids:
        # print(pid)
        p = psutil.Process(pid)
        # print(p.name)
        if p.name() == processName:
            # print(pid)
            return pid  # 如果找到该进程则打印它的PID，返回true
    return False  # 没有找到该进程，返回false



# 随机生成字符串
def generate_random_str(randomlength):    
    '''    
    string.digits = 0123456789    
    string.ascii_letters = 26个小写,26个大写    
    '''    
    str_list = random.sample(string.digits + string.ascii_letters,randomlength)    				
    random_str = ''.join(str_list)    
    return random_str

if __name__ == '__main__':
    app.run(host="0.0.0.0",port="8003")
