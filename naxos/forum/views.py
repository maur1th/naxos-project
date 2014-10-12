from django.views.generic import ListView, CreateView

from braces.views import LoginRequiredMixin

from .models import Category, Thread, Post
from .forms import NewThreadForm
from user.models import ForumUser


class Welcome(LoginRequiredMixin, ListView):
    template_name = "forum/welcome.html"
    model = ForumUser


class TopView(LoginRequiredMixin, ListView):
    template_name = "forum/top.html"
    model = Category


class ThreadView(LoginRequiredMixin, ListView):
    template_name = "forum/threads.html"
    model = Thread

    def get_queryset(self):
        "Return only threads of the current category"
        return Thread.objects.filter(category=Category.objects.get(
            slug=self.kwargs['category_slug']))

    def get_context_data(self, **kwargs):
        "Pass Category from url to context"
        context = super(ThreadView, self).get_context_data(**kwargs)
        context['category'] = Category.objects.get(
            slug=self.kwargs['category_slug'])
        return context


class PostView(LoginRequiredMixin, ListView):
    template_name = "forum/threads.html"
    model = Post


class NewThread(LoginRequiredMixin, CreateView):
    form_class = NewThreadForm
    fields = ('title')
    template_name = 'forum/new_thread.html'


class NewPost(LoginRequiredMixin, CreateView):
    model = Post
    fields = ()
    template_name = 'forum/new_post.html'
