""" Basic blog using webpy 0.3 """
import web
import BasicBlog.model
from main import refresh_web_in_real_time

### Url mappings

urls = (
    '/', 'Weibo',
    '/weibo','Weibo',
    '/xueqiu', 'Xueqiu',
    '/licaishi', 'LiCaiShi',
    '/get_new', 'GetNew',
    '/view/(\d+)', 'View',
    '/new', 'New',
    '/delete/(\d+)', 'Delete',
    '/edit/(\d+)', 'Edit',
)


### Templates
t_globals = {
    'datestr': web.datestr
}
render = web.template.render('templates', base='base', globals=t_globals)


class Xueqiu:

    def GET(self):
        """ Show page """
        posts = BasicBlog.model.get_posts_xueqiu()
        return render.index_xueqiu(posts)

class Weibo:

    def GET(self):
        """ Show page """
        posts = BasicBlog.model.get_posts_weibo()
        return render.index(posts)

class LiCaiShi:

    def GET(self):
        """ Show page """
        posts = BasicBlog.model.get_posts_licaishi()
        return render.index_licaishi(posts)

class GetNew:

    def GET(self):
        """ Show page """
        refresh_web_in_real_time()
        raise web.seeother('/')

class View:

    def GET(self, id):
        """ View single post """
        post = BasicBlog.model.get_post(int(id))
        print type(post)
        return render.view(post)


class New:

    form = web.form.Form(
        web.form.Textbox('title', web.form.notnull,
            size=30,
            description="Post title:"),
        web.form.Textarea('content', web.form.notnull,
            rows=30, cols=80,
            description="Post content:"),
        web.form.Button('Post entry'),
    )

    def GET(self):
        form = self.form()
        return render.new(form)

    def POST(self):
        form = self.form()
        if not form.validates():
            return render.new(form)
        BasicBlog.model.new_post(form.d.title, form.d.content)
        raise web.seeother('/')


class Delete:

    def POST(self, id):
        BasicBlog.model.del_post(int(id))
        raise web.seeother('/')


class Edit:

    def GET(self, id):
        post = BasicBlog.model.get_post(int(id))
        form = New.form()
        form.fill(post)
        return render.edit(post, form)


    def POST(self, id):
        form = New.form()
        post = BasicBlog.model.get_post(int(id))
        if not form.validates():
            return render.edit(post, form)
        BasicBlog.model.update_post(int(id), form.d.title, form.d.content)
        raise web.seeother('/')


app = web.application(urls, globals())

if __name__ == '__main__':
    app.run()