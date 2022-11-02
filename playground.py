x = 'https://www.google.co.id/maps/place/Air+Terjun+Kuning/@-8.6646704,115.0332261,11.13z/data=!4m10!1m3!2m2!1swaterfall+near+bali!6e1!3m5!1s0x2dd217439e7151a7:0xe2f5f07a5ca7b19d!8m2!3d-8.491141!4d115.3574832!15sChN3YXRlcmZhbGwgbmVhciBiYWxpWhUiE3dhdGVyZmFsbCBuZWFyIGJhbGmSARJ0b3VyaXN0X2F0dHJhY3Rpb26aASRDaGREU1VoTk1HOW5TMFZKUTBGblNVTXdOSFJFVGpsQlJSQULgAQA?authuser=0&hl=id'
new_x = x.split("/")
for x in new_x:
    if x.startswith('@'):
        x = x.replace('@','')
        print(x)