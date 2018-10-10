



from handler_help import *

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'[0-9a-f]{40}')

@post('/api/authenticate')
async def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email')
    if not passwd:
        logging.warning(passwd)
        raise APIValueError('passwd', 'Invalid password')
    users = await User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exit')
    user = users[0]
    # check password:
    sha1 = hashlib.sha1((user.id + ':' + passwd).encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        logging.warning('%s:%s', (user.passwd, sha1.hexdigest()))
        raise APIError('passwd', 'Invalid password')
    # authenticate ok,set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@post('/api/users')
async def api_create_users(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('eamil')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://api.okayapi.com/?s=Ext.Avatar.Show&nickname=%s&size=100' % name.strip())
    await user.save()
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/api/blogs/{id}')
async def api_get_blog(*, id):
    blog = await Blog.find(id)
    return blog


@post('/api/blogs/create')
async def api_create_blog(request, *, name, summary, content):
    for r in request:
        print(r)
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summay cannot be empty')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image,
                name=name.strip(), summary=summary.strip(), content=content.strip())
    await blog.save()
    return blog
@post('/api/blogs/{id}/update')
async def api_edit_blog(id,request, *, name, summary, content):
    for r in request:
        print(r)
    check_admin(request)
    blog = await Blog.find(id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summay cannot be empty')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty')
    blog.name = name
    blog.summary = summary
    blog.content = content
    await blog.update()
    return blog

@post('/api/blogs/{id}/delete')
async def api_delete_blog(id,request):
    check_admin(request)
    blog = await Blog.find(id)
    await blog.remove()
    return blog

@get('/api/blogs')
async def api_blogs(*, page='1'):
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    print(num)
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    logging.warning((p.offset, p.limit))
    blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)


@get('/api/users')
async def api_get_users(request, *, page='1'):
    check_admin(request)
    page_index = get_page_index(page)
    num = await User.findNumber('count(id)')
    print(num)
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    logging.warning((p.offset, p.limit))
    users = await User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, users=users)