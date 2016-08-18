from selenium import webdriver
import unittest

class PageTests(unittest.TestCase):
	def setUp(self):
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(2)

	def tearDown(self):
		self.browser.quit()

	def test_index_title(self):
		self.browser.get('http://localhost:5000')
		self.assertIn('V3', self.browser.title)
		# click_next = self.browser.find_element_by_css_selector(".button.btn.btn-outline.btn-success.btn-lg").click()
		# click_next()

	def test_index_header(self):
		self.browser.get('http://localhost:5000')
		header = self.browser.find_element_by_tag_name("h3")
		print(header)

	def test_dashboard_title(self):
		self.browser.get('http://localhost:5000/dashboard')
		self.assertIn('Dashboard', self.browser.title)

	def test_result_title(self):
		self.browser.get('http://127.0.0.1:5000/result?repo_name=mcshake&to_date=2014-12-23&analysis=metrics&from_date=2014-10-24&location=NULL')
		self.assertIn('Result', self.browser.title)



if __name__ == '__main__':
	unittest.main()
