from coroweb import get,post
from models import User
import  logging

@get('/')
async def index(request):
    return '<h1>Awesome</h1>'

@get('/author')
async def author(request):
    return r'<h1>BAO</h1>'
