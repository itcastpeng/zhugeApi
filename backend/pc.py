from time import sleep
from selenium import  webdriver
from bs4 import BeautifulSoup
import requests
class Zhidao:
	def __init__(self):
		self.dr = webdriver.Chrome('./plugin/chromedriver_2.36.exe')
		self.dr.maximize_window()  # 全屏

		self.url = 'https://zhidao.baidu.com/'
		# self.url = 'https://zhidao.baidu.com/search?lm=0&rn=10&pn=0&fr=search&ie=gbk&word=%CE%E4%BA%BA%C4%C4%BC%D2%B1%C7%BC%D7%B7%CA%B4%F3%D2%BD%D4%BA%D6%CE%C1%C6%D0%A7%B9%FB%D7%EE%BA%C3'
	# 获取页面数据并判断

	def data_url(self):
		# 获取输入框 输入内容
		# print(self.dr.page_source)
		self.dr.find_element_by_id('kw').send_keys('武汉哪家鼻甲肥大医院治疗效果最好')
		sleep(5)
		self.dr.find_element_by_id('search-btn').click()
		sleep(5)
		# 定位到当前窗口句柄
		sreach_window = self.dr.current_window_handle
		all_handels = self.dr.window_handles
		new_handel = None
		for handle in all_handels:
			if handle != sreach_window:
				new_handel = handle
				break

		# p = dr.switch_to_window(dr.window_handles[-1])
		# print(sreach_window)


	def get_save(self,soup):
		# 获取到的所有数据
		all_tag = soup.find('div', class_='list-inner')
		# print(all_tag)
		dd_tag = all_tag.find_all('dd', class_='dd answer')
		data_list = []
		for tag in dd_tag:
			daan = tag.get_text()
			if len(daan) > 30:
				print(daan)
				data_list.append(daan)
		return data_list

	def while_next(self):
		while True:
			# dr.get(sreach_window)
			soup = BeautifulSoup(self.dr.page_source, 'lxml')
			data_list = self.get_save(soup)
			# 获取下一页
			next_ye = self.dr.find_element_by_class_name('pager-next')
			next_url = next_ye.get_attribute('href')
			# 等待两秒
			sleep(3)
			if next_url:
				next_ye.click()
				# self.dr.get(next_url)
			else:
				break
		return data_list

	# 存入数据库
	# def write_data(self,data_list):
	# 	for data in data_list:
	# 		return data

	# 向添加答案api发起请求
	def save_data(self,data_list,url):
		for data in data_list:
			requests.post(url,data_list)

	# 关闭连接
	def __del__(self):
		self.dr.close()

	def run(self):
		# dr = self.dr
		self.dr.get(self.url)
		# self.dr.implicitly_wait(10)  # 隐式等待30秒
		url = 'http://127.0.0.1:8000/wendaku/daanku/add'
		self.data_url()
		data_list = self.while_next()
		self.save_data(data_list,url)


if __name__ == '__main__':
	zhidao = Zhidao()
	zhidao.run()


