cd ./
kill -9 $(ps aux|grep Transponder_Manage|grep -v grep|awk '{print  $2}')
nohup python transponder_manage.py >/dev/null 2>&1 &