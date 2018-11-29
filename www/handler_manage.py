# 评论列表页：GET / manage / comments
# 日志列表页：GET / manage / blogs
# 创建日志页：GET / manage / blogs / create
# 修改日志页：GET / manage / blogs / edit
# 用户列表页：GET / manage / users

from handler_help import *

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'[0-9a-f]{40}')
@get('/manage/blogs')
async def manage_blogs(*, page='1'):
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page)
    }


@get('/manage/blogs/create')
async def manage_create_blog():
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs/create'
    }

@get('/manage/blogs/edit')
async def manage_edit_blog(*,id):
    return {
        '__template__': 'manage_blog_edit.html',
        'id': id,
        'action': '/api/blogs/%s/update'%id
    }
@get('/manage/users')
async def manage_users(*,page='1'):
    return {
        '__template__': 'manage_users.html',
        'page_index': get_page_index(page)
    }