kill -9 $(ps aux|grep inner_server|grep -v grep|awk '{print  $2}')
kill -9 $(ps aux|grep outer_server|grep -v grep|awk '{print  $2}')