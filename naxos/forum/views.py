from django.views.generic import ListView, CreateView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect

from braces.views import LoginRequiredMixin

from .models import Category, Thread, Post
from .forms import NewThreadForm


class TopView(LoginRequiredMixin, ListView):
    template_name = "forum/top.html"
    model = Category


class ThreadView(LoginRequiredMixin, ListView):
    template_name = "forum/threads.html"
    model = Thread

    def get_queryset(self):
        "Return threads of the current category ordered by latest post"
        c_slug = self.kwargs['category_slug']
        return Thread.objects.filter(category__slug=c_slug)

    def get_context_data(self, **kwargs):
        "Pass category from url to context"
        context = super(ThreadView, self).get_context_data(**kwargs)
        context['category'] = Category.objects.get(
            slug=self.kwargs['category_slug'])
        return context


class PostView(LoginRequiredMixin, ListView):
    template_name = "forum/posts.html"
    model = Post

    def get_queryset(self):
        "Return list of posts given thread and category slugs"
        c_slug = self.kwargs['category_slug']
        t_slug = self.kwargs['thread_slug']
        return Post.objects.filter(thread__slug=t_slug,
                                   thread__category__slug=c_slug)

    def get_context_data(self, **kwargs):
        "Pass category and thread from url to context"
        context = super(PostView, self).get_context_data(**kwargs)
        c_slug = self.kwargs['category_slug']
        t_slug = self.kwargs['thread_slug']
        context['category'] = Category.objects.get(slug=c_slug)
        context['thread'] = Thread.objects.get(slug=t_slug,
                                               category__slug=c_slug)
        return context


class NewThread(LoginRequiredMixin, CreateView):
    form_class = NewThreadForm
    template_name = 'forum/new_thread.html'

    def get_context_data(self, **kwargs):
        "Pass Category from url to context"
        context = super(NewThread, self).get_context_data(**kwargs)
        context['category'] = Category.objects.get(
            slug=self.kwargs['category_slug'])
        return context

    def form_valid(self, form):
        """ Handle thread and 1st post creation in the db"""
        # Create the thread
        t = Thread.objects.create(
            title=self.request.POST['title'],
            author=self.request.user,
            category=Category.objects.get(slug=self.kwargs['category_slug']))
        # Complete the post and save it
        form.instance.thread = t
        form.instance.author = self.request.user
        form.instance.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('forum:category', kwargs=self.kwargs)


class NewPost(LoginRequiredMixin, CreateView):
    model = Post
    fields = ('content_plain',)
    template_name = 'forum/new_post.html'

    def get_context_data(self, **kwargs):
        "Pass category and thread from url to context"
        context = super(NewPost, self).get_context_data(**kwargs)
        context['category'] = Category.objects.get(
            slug=self.kwargs['category_slug'])
        context['thread'] = Thread.objects.get(
            slug=self.kwargs['thread_slug'])
        return context

    def form_valid(self, form):
        """ Handle post creation in the db"""
        c_slug = self.kwargs['category_slug']
        t_slug = self.kwargs['thread_slug']
        t = Thread.objects.get(slug=t_slug,
                               category__slug=c_slug)
        form.instance.thread = t
        form.instance.author = self.request.user
        form.instance.save()
        t.modified, self.post_pk = form.instance.created, form.instance.pk
        t.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return (reverse_lazy('forum:thread', kwargs=self.kwargs)
                + '#' + str(self.post_pk))

# class UpdatePost(LoginRequiredMixin, UpdateView):
#     form_class = UpdateUserForm
#     template_name = 'forum/edit.html'
#     success_url = reverse_lazy('forum:thread', kwargs=self.kwargs)

#     def get_object(self):
#         return ForumUser.objects.get(username=self.request.user)

#     def get_form_kwargs(self):
#         """Pass request to form."""
#         kwargs = super(UpdateUser, self).get_form_kwargs()
#         kwargs.update({'request': self.request})
#         return kwargs
