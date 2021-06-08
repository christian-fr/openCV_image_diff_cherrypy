import requests

url = 'http://127.0.0.1:9090/upload'
files = {'ufile1': open('file.txt', 'rb'), 'ufile2': open('Clipboard02.png', 'rb')}

r = requests.post(url, files=files)

print(r)
print(r.text)