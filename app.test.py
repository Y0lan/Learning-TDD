import os
import tempfile
import unittest
import app


class TestingBasicOfWebsite(unittest.TestCase):
    def test_index(self):
        tester = app.app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_database_exist(self):
        tester = os.path.exists('database.db')
        self.assertTrue(tester)


class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()
        app.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def testDbIsEmpty(self):
        response = self.app.get('/')
        assert b'Aucun article pour le moment' in response.data

    def testCanLoginWithCorrectCredentials(self):
        response = self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD']
        )
        assert b'logged in' in response.data
        return response

    def testCanInputLogout(self):
        response = self.logout()
        assert b'logged out' in response.data

    def testCannotLoginWithIncorrectCrendentials(self):
        response = self.login(
            app.app.config['USERNAME'] + 'thisistofalsetheusername',
            app.app.config['PASSWORD']
        )
        assert b'Invalid username' in response.data

        response = self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD'] + 'thisistofalsethepassword'
        )
        assert b'Invalid password' in response.data

    def testCanPostArticleWhenLoggedIn(self):
        self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD']
        )

        response = self.app.post('/add', data=dict(
            titre='<Hello World>',
            contenu='<strong> Ce texte est du HTML ! :-)</strong>'
        ), follow_redirects=True)
        assert b'Aucun articles encore poste' not in response.data
        assert b'&lt;Hello World&gt;' in response.data
        assert b'<strong> Ce texte est du HTML ! :-)</strong>' in response.data


if __name__ == '__main__':
    unittest.main()
