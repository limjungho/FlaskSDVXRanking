import requests
import re
import time
import random
import sqlite3

login_info = {'id': 'osuplayer', 'pw': 'osunumber1'}
user_list = ['howlingsoul', 'hansolr', 'eden', 'eseiker', 'rkn04', 'wmr04219', 'eric9709', 'haze0618',
	'skrea1492', 'pursefire', 'cloud', 'raison0215', 'reica', 'hoxy', 'chyo259', '60fail', 'nalch147',
	'pxero', 'gks2476','sk443123','min3492']

def volforce_user(username):
	if username not in user_list:
		raise Exception('id not WF user')
	with requests.Session() as s:
		login_req = s.post('http://anzuinfo.me/login_check.php', data=login_info)
		profile_page = s.get('http://anzuinfo.me/profile.html?search_id={}'.format(username))
		p = re.compile('[0-9][0-9]\.[0-9][0-9]')
		m = p.findall(profile_page.text)[0]
		return m

def volforce_user_all():
	result = {}
	with requests.Session() as s:
		login_req = s.post('http://anzuinfo.me/login_check.php', data=login_info)
		for username in user_list:
			profile_page = s.get('http://anzuinfo.me/profile.html?search_id={}'.format(username))
			p = re.compile('[0-9][0-9]\.[0-9][0-9]')
			m = p.findall(profile_page.text)[0]
			result[username] = m
			time.sleep(0.1)
	return result
'''
dic = volforce_user_all()
conn = sqlite3.connect("SDVXRanking.db")
cur = conn.cursor()

for key, val in dic.items():
	sql = "update UserInfo SET VolForce = ? where UserID = ?;"
	cur.execute(sql, (val, key))

conn.commit()
conn.close()
'''