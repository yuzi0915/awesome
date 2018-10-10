# 注册页：GET / register
#
# 登录页：GET / signin
#
# 注销页：GET / signout
#
# 首页：GET /
#
# 日志详情页：GET / blog /: blog_id




from handler_help import *

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'[0-9a-f]{40}')

@get('/')
async def index(request):
    blogs = await Blog.findAll()
    return {
        '__template__': 'blogs.html',
        'blogs': blogs,

    }


@get('/register')
async def register():
    return {
        '__template__': 'register.html'

    }


@get('/signin')
async def signin():
    return {
        '__template__': 'signin.html'
    }


@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out')
    return r


@get('/blog/{id}')
async def get_blog(id, request):
    blog = await Blog.find(id)
    comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments,

    }
