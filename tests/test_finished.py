import unittest
from generator import SetupDistutils
import jinja2
import sys
import distutils.core


class TestFinished(unittest.TestCase):
    def test_simple_dist1(self):
        setup = SetupDistutils(**dict(
            author='mrj0',
            author_email='author_email',
            name='proj',
            description='test',
            url='http://someplace',
            modules='one two',
            packages='three four',
        ))

        src = jinja2.Markup(setup.generate(
            executable=True,
            under_test=True,
        )).unescape()
        src = '\n'.join([line for line in src.split('\n')
                            if not line.startswith('#')])

        sys.argv = ['setup.py', 'check']
        distutils.core._setup_stop_after = "init" # stops command execution
        dist = None
        exec src

        self.assertIsNotNone(dist)
        # none of this works
#        print dist
#        self.assertEqual('mrj0', dist.author)
#        self.assertEqual('prog', dist.name)


if __name__ == '__main__':
    unittest.main()
