import sys
import time
import hashlib
from time import sleep
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import random

class Zhidao:
	# 初始化文件
	def __init__(self, gjc):
		self.gjc = gjc
		self.dr = webdriver.Chrome('./plugin/chromedriver_2.36.exe')
		self.dr.maximize_window()  # 全屏
		self.url = 'https://zhidao.baidu.com'
		self.data_list = []
		# self.rand = random.randint(2,7)

	@property
	def rand(self):
		return random.randint(2,7)

	# 获取页面数据并判断
	# 获取输入框 输入内容
	def data_url(self):
		self.dr.find_element_by_id('kw').send_keys(self.gjc)
		sleep(self.rand)
		self.dr.find_element_by_id('search-btn').click()
		self.unit()
		data_list = self.get_save()
		content_list = self.get_url_data(data_list)
		self.get_data(content_list)

	# 获取url 返回所有url链接
	def get_save(self):
		sleep(self.rand)
		data_list = self.data_list
		# 获取页面数据
		all_tags = self.dr.find_element_by_class_name('list-inner')
		# 获取a标签
		a_tags = all_tags.find_elements_by_class_name('ti')
		for a_tag in a_tags:
			# 获取 a标签的 url
			url = a_tag.get_attribute('href')
			data_list.append(url)
		# 循环下一页 取出所有url
		while True:
			# sleep(self.rand)
			try:
				next_ye = self.dr.find_element_by_class_name('pager-next')
				if next_ye:
					next_ye.click()
					self.get_save()
			except Exception as r:
				break
		return data_list

	# 请求获取到的url返回答案
	def get_url_data(self,data_list):
		# print('获取答案')
		temp = []
		for url in data_list:
			self.dr.get(url)
			# 总页面
			soup = BeautifulSoup(self.dr.page_source, 'lxml')
			# 所有答案页面
			article_tag = soup.find('article',class_='qb-content')
			# 获取答案div 两个
			# sleep(self.rand)
			try:
				div_tags = article_tag.find_all('div', class_='line content')
				for div in div_tags:
					span = div.find_all('span', class_='con')
					pre = div.find_all('pre', accuse='aContent')
					p_tag = div.find_all('p')
					if span:
						for span_tag in span:
							text_data = span_tag.get_text().strip()
							if len(text_data) > 30:
								temp.append(text_data)
					if pre:
						for pre_tag in pre:
							text_data = pre_tag.get_text().strip()
							if len(text_data) > 30:
								temp.append(text_data)
					if p_tag:
						for tag in p_tag:
							text_data = tag.get_text().strip()
							if len(text_data)> 30:
								temp.append(text_data)

			except Exception as e :
				print(e)
		return temp

	# 密码加密 请求参数
	def str_encrypt(self,pwd):
		pwd = str(pwd)
		hash = hashlib.md5()
		hash.update(pwd.encode())
		return hash.hexdigest()

	# 获取答案 并返回api
	def get_data(self,temp):
		token = '4e0398e4d4bad913e24c1d0d60cc9170'
		timestamp = str(int(time.time()))

		for teme in temp:
			print(teme)
			params = {
				'user_id': 1,
				'timestamp': timestamp,
				'rand_str': self.str_encrypt(timestamp + token)
			}
			data = {
				'data':teme
			}
			url = 'http://127.0.0.1:8000/wendaku/daanku/add/0'
			ret = requests.post(url,params=params, data=data)
			# print(ret.text)

	# 定位窗口句柄
	def unit(self):
		# 定位到当前窗口句柄
		sreach_window = self.dr.current_window_handle
		all_handels = self.dr.window_handles
		new_handel = None
		for handle in all_handels:
			if handle != sreach_window:
				new_handel = handle
				break
		return new_handel

	# 关闭连接\
	def __del__(self):
		sleep(20)
		self.dr.close()

	# 启动
	def run(self):

		self.dr.get(self.url)
		self.data_url()
		# self.dr.implicitly_wait(10)  # 隐式等待30秒


if __name__ == '__main__':
	# if sys.argv[1]:
	# 	urldome = sys.argv[1]
	# else:
	# 	u	rldome = '127.0.0.1:8000'
	gjc_list = []
	with open('./wen.txt')as file_obj:
		for line in file_obj:
			gjc = line.strip()
			zhidao = Zhidao(gjc)

			zhidao.run()

