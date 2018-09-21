from coroweb import get,post
from models import User
import  logging

@get('/')
async def index(request):
    users= await  User.findAll()
    return {
        '__template__':'index.html',
        'users':users
    }

@get('/author')
async def author(request):
    return r'<h1>BAO</h1>'
