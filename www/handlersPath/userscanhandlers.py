from .handlershelp import *


@get('/')
async def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 120),
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 3600),
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 7200),
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs,
        '__user__': request.__user__
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
        '__user__': request.__user__
    }
