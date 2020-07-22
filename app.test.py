import json
import os
import unittest
from app import app, db

DB = 'database.db'

# IHM
import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait


class TestingBasicOfWebsite(unittest.TestCase):
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_database_exist(self):
        tester = os.path.exists('database.db')
        self.assertTrue(tester)


class TestFlaskrHIMTestCase:
    @pytest.fixture
    def browser(self):
        opts = Options()
        opts.headless = False
        driver = Firefox(options=opts)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()

    def testDbIsEmpty(self):
        self.browser.get('http://localhost:5000/')
        content = self.browser.find_element_by_id('no-content').text
        assert 'Aucun article pour le moment' in content

    def testUserCanLogin(self):
        self.browser.get('http://localhost:5000/')
        button = self.browser.find_element_by_id('login')
        ActionChains(self.browser).click(button).perform()
        assert self.browser.current_url is 'http://localhost:5000/login'

    def testUserCanLogout(self):
        self.browser.get('http://localhost:5000/login')
        button = self.browser.find_element_by_id('logout')
        ActionChains(self.browser).click(button).perform()
        WebDriverWait(self.browser, 5)
        content = self.browser.page_source
        assert 'logged out' in content

    def testUserCannotLoginWithoutCorrectCredential(self):
        self.browser.get('http://localhost:5000/login')
        form = self.browser.find_element_by_id("loginform")
        user = self.browser.find_element_by_name("username")
        password = self.browser.find_element_by_name("password")
        user.send_keys('adminx')
        password.send_keys('admin')
        form.submit()
        WebDriverWait(self.browser, 5)
        content = self.browser.page_source
        assert 'Invalid username' in content

        user.send_keys('admin')
        password.send_keys('adminx')
        form.submit()
        WebDriverWait(self.browser, 5)
        content = self.browser.page_source
        assert 'Invalid password' in content

    def testUserCanLoginWithCorrectCredential(self):
        self.browser.get('http://localhost:5000/login')
        form = self.browser.find_element_by_id("loginform")
        user = self.browser.find_element_by_name("username")
        password = self.browser.find_element_by_name("password")
        user.send_keys('admin')
        password.send_keys('admin')
        form.submit()
        WebDriverWait(self.browser, 5)
        content = self.browser.page_source
        assert 'logged in' in content

    def testUserCanPostArticles(self):
        self.browser.get('http://localhost:5000/')
        form = self.browser.find_element_by_id("post_articles")
        titre = self.browser.find_element_by_name("titre article")
        contenu = self.browser.find_element_by_name("vive le TDD")
        WebDriverWait(self.browser, 5)
        content = self.browser.page_source
        assert 'titre article' in content
        assert 'vive le TDD' in content


class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                                os.path.join(basedir, DB)
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.drop_all()

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def testDbIsEmpty(self):
        response = self.app.get('/')
        self.assertIn(b'Aucun article pour le moment', response.data)

    def testCanLoginWithCorrectCredentials(self):
        response = self.login(
            app.config['USERNAME'],
            app.config['PASSWORD']
        )
        self.assertIn(b'logged in', response.data)
        return response

    def testCanInputLogout(self):
        response = self.logout()
        self.assertIn(b'logged out', response.data)

    def testCannotLoginWithIncorrectCrendentials(self):
        response = self.login(
            app.config['USERNAME'] + 'thisistofalsetheusername',
            app.config['PASSWORD']
        )
        self.assertIn(b'Invalid username', response.data)

        response = self.login(
            app.config['USERNAME'],
            app.config['PASSWORD'] + 'thisistofalsethepassword'
        )
        self.assertIn(b'Invalid password', response.data)

    def testCanPostArticleWhenLoggedIn(self):
        self.login(
            app.config['USERNAME'],
            app.config['PASSWORD']
        )

        response = self.app.post('/add', data=dict(
            titre='<Hello World>',
            contenu='<strong> Ce texte est du HTML ! :-)</strong>'
        ), follow_redirects=True)
        self.assertNotIn(b'Aucun articles encore poste', response.data)
        self.assertIn(b'&lt;Hello World&gt;', response.data)
        self.assertIn(b'<strong> Ce texte est du HTML ! :-)</strong>', response.data)

    def test_delete_message(self):
        response = self.app.get('/delete/1')
        data = json.loads(response.data)
        self.assertEqual(data['status'], 1)


if __name__ == '__main__':
    unittest.main()
