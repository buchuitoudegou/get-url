import requests
import threading
import time
from bs4 import BeautifulSoup
import win_unicode_console
import csv
win_unicode_console.enable()


url = "http://www.baidu.com/s?wd={}%20网址&rsv_spt=1&rsv_iqid=0xfe59b2a80002ddc8&issp=1&f=8&rsv_bp=0&rsv_idx=2&ie=utf-8&tn=baiduhome_pg&rsv_enter=1&rsv_sug3=7&rsv_sug1=6&rsv_sug7=100"
headers = {
	'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}

target = []
results = {}
thread_list = []

def find_real_url(url):
	url = url.replace("http", "https")
	url += "&wd=&eqid=8a69aefc000038e9000000065ad16045"
	r = requests.get(url, headers = headers)
	#print(r.text)
	soup = BeautifulSoup(r.text, "html.parser")
	t = soup.find("meta", {"http-equiv":{"refresh"}})
	#print(t)
	return t.get("content")[7: len(t.get("content")) - 1]


def work(name):
	cur_url = url.format(name)
	semlock.acquire()
	try:
		time.sleep(0.4)
		target_url = ""
		r = requests.get(cur_url, headers = headers, timeout=60)
		bs = BeautifulSoup(r.text, "html.parser")
		divTarget = bs.find("div", id = "1")
		a = divTarget.find("a", target="_blank", class_="c-showurl")
		if a.text[len(a.text) - 3:len(a.text) - 1] == '..':
			target_url = find_real_url(divTarget.find("h3", class_="t").find("a").get("href"))
		else:
			target_url = a.text
		results[name] = target_url
		print(name + " succeed")
	except:
		print(name + " fail")
		results[name] = 'NOT FOUND '
	finally:
		semlock.release()


def app_target_reading():
	file_app = open("app.txt", "r")
	for i in file_app.readlines():
		target.append(i.strip())
	file_app.close()
	print("reading complete")


def dealing_with_string(string):
	if string[:5] == 'https':
		return string[8: len(string) - 1]
	elif string[:4] == 'http':
		return string[7: len(string) - 1]
	else:
		return string[: len(string) - 1]

def result_writing():
	csvfile = open('1.csv', 'w', newline = '', encoding='gbk')
	writer = csv.writer(csvfile)
	for i in results:
		results[i] = dealing_with_string(results[i])
		#results[i] = results[i].encode('gbk', 'ignore')
		line = [i, results[i]]
		try:
			writer.writerow(line)
		except:
			print(i + " encoding fail")
	csvfile.close()

semlock = threading.Semaphore(5)
if __name__ == "__main__":
	app_target_reading()
	for i in range(len(target)):
		t = threading.Thread(target = work, args=(target[i],))
		thread_list.append(t)
	for i in thread_list:
		i.start()
	for j in thread_list:
		j.join()
	print("work complete")
	result_writing()