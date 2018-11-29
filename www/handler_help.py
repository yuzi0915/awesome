from coroweb import get, post
from models import User, Blog, Comment, next_id
import logging
import time, re, json, hashlib, base64, asyncio
from aiohttp import web
from apis import *
from config import configs
import markdown2

COOKIE_NAME = 'awesession'
_COOKIE_KEY = 'configs.session.secret'

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'[0-9a-f]{40}')

def check_admin(request):
    if request.__user__ is None or request.__user__.admin != 1:
        raise APIPermissionError()
def check_add(request):
    if request.__user__ is None or not request.__user__.admin :
        raise APIPermissionError()

def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp').replace('<', '&lt;').replace('>', '&gt;'),
                filter(lambda s: s.strip() != '', text.split('\n')))


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


def user2cookie(user, max_age):
    '''
    Generate cookie str bby user.
    :param user:
    :param max_age:
    :return:
    '''
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


async def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid
    :param cookie_str:
    :return:
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = await User.findAll(where='id = "%s"' % uid)
        if user is None:
            return None
        user = user[0]
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None