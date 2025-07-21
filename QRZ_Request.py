from urllib import request
from urllib.request import urlopen
from urllib.error import HTTPError,URLError
import ssl
import requests
import json
import socket
from bs4 import BeautifulSoup





USER_HEADER = {
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding': 'gzip, deflate, sdch',
			'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
			'Connection': 'keep-alive',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
			'Origin': 'https://logbook.qrz.com',
			'Referer': 'https://logbook.qrz.com',
			'Upgrade-Insecure-Requests': '1'
		}

def login(username,password):
	try:
		postUrl = 'https://www.qrz.com/login'
		session = requests.session()
		postdata1 = {
			'login_ref': 'https://www.qrz.com/',
			'username': username,
			'password': password,
			'2fcode': '',
			'target': '/',
			'flush': '0'
		}
		login_resp=session.post(postUrl, data=postdata1, headers=USER_HEADER)
	except Exception as err:
		raise err
	else:
		return session

def deal_request_qsl(session,qso_id,qso_with,qso_start_date):
	try:
		band_list=['20m','15m','10m','12m','30m','40m','17m','80m','6m','70cm']
		time_list = [
    		'00:00', '00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30',
    		'04:00', '04:30', '05:00', '05:30', '06:00', '06:30', '07:00', '07:30',
    		'08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
    		'12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30',
    		'16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
    		'20:00', '20:30', '21:00', '21:30', '22:00', '22:30', '23:00', '23:30','24:00'
		]
		for band in band_list:
			for time in time_list:
				getUrl='https://logbook.qrz.com/?op=chconf;call1=BI1FQO;call2=%s;band1=%s;band2=%s;mode1=FT8;mode2=FT8;start_date=%s;start_time=%s;prop_mode=;originqso=%s'%(qso_with,band,band,qso_start_date,time,qso_id)
				response1 = session.get(getUrl, headers=USER_HEADER)
				result=json.loads(response1.text)
				result['band']=band
				result['time']=time
				result['date']=qso_start_date
				result['callsign']=qso_with
				print(result)
				if result['conf']=='1':
					break
			if result['conf']=='1':
				break
		
		print(qso_with,qso_start_date)
		print("找到啦！！！")
	except Exception as err:
		raise err
def get_request_info(session,qso_id):
	try:
		
		Url='https://logbook.qrz.com/logbook/'
		data={
			'frm':'6',
			'sbook':'0',
			'op':'confirm',
			'nocache':'0',
			'bookid':'342657',
			'qso':qso_id
		}
		response1 = session.post(Url, headers=USER_HEADER,data=data)
		#print(response1.text)
		soup = BeautifulSoup(response1.text, 'html.parser')
		qso_with = soup.find("span", class_="fb blue ui-call2z").text.strip()
		qso_start_date = soup.find("input", {"id": "start_date"})["value"]
		print(qso_with,qso_start_date)
		return qso_with,qso_start_date
	except Exception as err:
		raise err

def check_qrz_request(username,password,qso_id):
	try:
		session=login(username,password)
		qso_with,qso_start_date=get_request_info(session,qso_id)
		deal_request_qsl(session,qso_id,qso_with,qso_start_date)
		
	except Exception as err:
		raise err



if __name__ == '__main__':
	check_qrz_request("1291577923")
