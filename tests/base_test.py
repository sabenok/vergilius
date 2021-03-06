import logging
import os
import threading
import unittest

import sys
import shutil
import tornado

import vergilius
from vergilius import consul, logger
from vergilius.components import port_allocator
from vergilius.loop.service_watcher import ServiceWatcher

# for requests headers:
# import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.DEBUG)

requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

logger.addHandler(out_hdlr)
logger.setLevel(logging.DEBUG)


def start_tornado():
    tornado.ioloop.IOLoop.instance().start()


class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(BaseTest, cls).setUpClass()
        cls.watcher = ServiceWatcher()
        cls.watcher.watch_services()

        threading.Thread(target=start_tornado).start()

    @classmethod
    def tearDownClass(cls):
        super(BaseTest, cls).tearDownClass()
        tornado.ioloop.IOLoop.instance().stop()

    def setUp(self):
        super(BaseTest, self).setUp()
        consul.kv.delete('vergilius', True)

        try:
            os.mkdir(vergilius.config.DATA_PATH)
        except OSError as e:
            print(e)

        try:
            os.mkdir(vergilius.config.NGINX_CONFIG_PATH)
            os.mkdir(os.path.join(vergilius.config.NGINX_CONFIG_PATH, 'certs'))
        except OSError as e:
            print(e)

        vergilius.Vergilius.init()

    def tearDown(self):
        super(BaseTest, self).tearDown()
        consul.kv.delete('vergilius', True)
        port_allocator.allocated = {}

        try:
            shutil.rmtree(vergilius.config.NGINX_CONFIG_PATH)
            shutil.rmtree(vergilius.config.DATA_PATH)
        except OSError as e:
            print(e)
