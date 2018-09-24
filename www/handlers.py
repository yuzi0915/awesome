from coroweb import get,post
from models import User,Blog,Comment,next_id
import  logging
import time,re,json,hashlib,base64,asyncio
from aiohttp import web
from apis import *
from config import configs
import markdown2
COOKIE_NAME = 'awesession'
_COOKIE_KEY = 'configs.session.secret'
def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()
def text2html(text):
    lines = map(lambda s:'<p>%s</p>' % s.replace('&','&amp').replace('<','&lt;').replace('>', '&gt;'),
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
def user2cookie(user,max_age):
    '''
    Generate cookie str bby user.
    :param user:
    :param max_age:
    :return:
    '''
    expires = str(int(time.time()+max_age))
    s = '%s-%s-%s-%s' % (user.id,user.passwd,expires,_COOKIE_KEY)
    L = [user.id,expires,hashlib.sha1(s.encode('utf-8')).hexdigest()]
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
        uid,expires,sha1 = L
        if int(expires) < time.time():
            return None
        user = await User.findAll(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid,user.passwd,expires,_COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

@get('/')
async def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 120),
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 3600),
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 7200),
    ]
    return {
        '__template__':'blogs.html',
        'blogs':blogs,
    }

@get('/register')
async def register():
    return {
        '__template__':'register.html'
    }
@get('/signin')
async def signin():
    return {
        '__template__':'signin.html'
    }
@post('/api/authenticate')
async def authenticate(*,email,passwd):
    if not email:
        raise APIValueError('email','Invalid email')
    if not passwd:
        logging.warning(passwd)
        raise APIValueError('passwd','Invalid password')
    users = await User.findAll('email=?',[email])
    if len(users) == 0:
        raise  APIValueError('email','Email not exit')
    user = users[0]
    # check password:
    sha1 = hashlib.sha1((user.id+':'+ passwd).encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        logging.warning('%s:%s',(user.passwd, sha1.hexdigest()))
        raise APIError('passwd','Invalid password')
    # authenticate ok,set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=86400,httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user,ensure_ascii=False).encode('utf-8')
    return r

@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME,'-deleted-',max_age=0,httponly=True)
    logging.info('user signed out')
    return r

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'[0-9a-f]{40}')

@post('/api/users')
async def api_get_users(*,email,name,passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('eamil')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?',[email])
    if len(users) > 0 :
        raise APIError('register:failed','email','Email is already in use')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid,passwd)
    user = User(id = uid,name=name.strip(),email=email,passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),image='http://api.okayapi.com/?s=Ext.Avatar.Show&nickname=%s&size=100' % name.strip())
    await user.save()
    r = web.Response()
    r.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=86400,httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user,ensure_ascii=False).encode('utf-8')
    return r

@get('/manage/blogs')
def manage_blogs(*,page='1'):
    return {
        '__template__':'manage_blogs.html',
        'page_index':get_page_index(page)
    }
@get('/manage/blogs/create')
def manage_create_blog():
    return {
        '__template__':'manage_blog_edit.html',
        'id':'',
        'action':'/api/blogs'
    }
@get('/blog/{id}')
async def get_blog(id):
     blog = await Blog.find(id)
     comments = await Comment.findAll('blog_id=?',[id],orderBy='created_at desc')
     for c in comments:
         c.html_content = text2html(c.content)
     blog.html_content = markdown2.markdown(blog.content)
     return {
         '__template__':'blog.html',
         'blog':blog,
         'comments':comments
     }
@get('/api/blogs/{id}')
async def api_get_blog(*,id):
    blog = await Blog.find(id)
    return blog
@post('/api/blogs/create')
async def api_create_blog(request,*,name,summary,content):
    for r in request:
        print(r)
    check_admin(request)
    if not name or name.strip():
        raise APIValueError('name','name cannot be empty')
    if not summary or not summary.strip():
        raise APIValueError('summary','summay cannot be empty')
    if not content or not content.strip():
        raise APIValueError('content','content cannot be empty')
    blog = Blog(user_id = request.__user__.id,user_name=request.__user__.name,user_image=request.__user__.image,
                name= name.strip(),summary = summary.strip(),content = content.strip())
    await blog.save()
    return blog


@get('/api/blogs')
async def api_blogs(*,page='1'):
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    print(num)
    p = Page(num,page_index)
    if num == 0:
        return dict(page = p,blogs = ())
    logging.warning((p.offset, p.limit))
    blogs = await Blog.findAll(orderBy='created_at desc',limit=(p.offset,p.limit))
    return dict(page = p,blogs=blogs)