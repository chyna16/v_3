from selenium import webdriver
import unittest



class NewTest(unittest.TestCase):
	def setUp(self):
		self.browser = webdriver.Firefox()
		self.browser.implicitly_wait(2)

	def tearDown(self):
		self.browser.quit()

	def test_can_start_site(self):
		self.browser.get('http://localhost:5000')
		self.assertIn('V3', self.browser.title)
		click_next = self.browser.find_element_by_css_selector(".button.btn.btn-outline.btn-success.btn-lg").click()
		click_next()

if __name__ == '__main__':
	unittest.main()
