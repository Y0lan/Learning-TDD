import os
import unittest
import tempfile
import src.main as main


class TestingBasicOfWebsite(unittest.TestCase):
    def test_index(self):
        tester = main.main.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 404)

    def test_database_exist(self):
        tester = os.path.exists('database.db')
        self.assertTrue(tester)


class FlaskrTestCase(unittest.TestCase):
    def canSetupDatabase(self):
        self.db_fd, main.main.config['DATABASE'] = tempfile.mkstemp()
        main.main.config['TESTING'] = True
        self.main = main.main.test_client()
        main.init_db()

    def canCloseDatabase(self):
        os.close(self.db_fd)
        os.unlink(main.main.config['DATABASE'])

    def login(self, username, password):
        return self.main.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.main.get('/logout', follow_redirects=True)

    def dbIsEmpty(self):
        return self.main.get('/logout', follow_redirects=True)

    def canLoginWithCorrectCredentials(self):
        response = self.login(
            main.main.config['USERNAME'],
            main.main.config['PASSWORD']
        )
        assert b'logged in' in response.data
        return response

    def canInputLogout(self):
        response = self.logout()
        assert b'logged out' in response.data

    def cannotLoginWithIncorrectCrendentials(self):
        response = self.login(
            main.main.config['USERNAME'] + 'thisistofalsetheusername',
            main.main.config['PASSWORD']
        )
        assert b'Invalid username' in response.data

        response = self.login(
            main.main.config['USERNAME'],
            main.main.config['PASSWORD'] + 'thisistofalsethepassword'
        )
        assert b'Invalid password' in response.data

    def canPostArticleWhenLoggedIn(self):
        self.login(
            main.main.config['USERNAME'],
            main.main.config['PASSWORD']
        )

        response = self.main.post('/add', data=dict(
            titre='<Hello World>',
            contenu='<strong> Ce texte est du HTML ! :-)</strong>'
        ), follow_redirects=True)
        assert b'Aucun articles encore poste' not in response.data
        assert b'&lt;Hello World&gt;' in response.data
        assert b'<strong> Ce texte est du HTML ! :-)</strong>' in response.data


if __name__ == '__main__':
    unittest.main()
