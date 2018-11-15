from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from blog.models import Comment, Post
from blog.forms import PostForm, CommentForm
# decorators are used on function based views
from django.contrib.auth.decorators import login_required
# Mixins are used for classed based views
from django.contrib.auth.mixins import LoginRequiredMixin
# waits for the post to be deleted before navigating to the new url
from django.urls import reverse_lazy
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView,
                                    DeleteView)


# Create your views here.

############################################
######### POSTS ###########################
###########################################
class AboutView(TemplateView):
    template_name = 'about.html'

class PostListView(ListView):
    model = Post

    # returns all the object from the post model, filtered by published date,
    # which is (__lte) less than or equal to timezone now and the orderedby the published date
    # -published_date = descending order
    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

class PostDetailView(DetailView):
    model = Post

class CreatePostView(LoginRequiredMixin, CreateView):
    # redirects the user to the login page, if they are not logged in
    login_url = 'accounts/login/'

    # redirects the user to the home page after the post has been created
    redirect_field_name = 'blog/post_detail.html'

    form_class = PostForm

    model = Post

class PostUpdateView(LoginRequiredMixin, UpdateView):
    # redirects the user to the login page, if they are not logged in
    login_url = 'accounts/login/'

    # redirects the user to the home page after the post has been updated
    redirect_field_name = 'blog/post_detail.html'

    form_class = PostForm

    model = Post

class PostDelteView(LoginRequiredMixin, DeleteView):
    model = Post
    # redirects the user to the home page after the post has been deleted
    success_url = reverse_lazy('post_list')

class DraftListView(LoginRequiredMixin, ListView):
    # redirects the user to the login page, if they are not logged in
    login_url = 'accounts/login/'

    # redirects the user to the home page after the post has been updated
    redirect_field_name = 'blog/post_drafts_list.html'

    model = Post

    # returns all the object from the post model, filtered by published date,
    # which is (__lte) less than or equal to timezone now and the orderedby the published date
    # -published_date = descending order
    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')


################################
########## Comments ###########
###############################

# this decorator ensures that the person is logged in before adding a comment to
# the post
@login_required
def post_publish(request,pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def add_comments_to_post(request,pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
        return render(request, 'blog/comment_form.html', {'form':form})

@login_required
def comment_approve(requst, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(requst, pk):
    comment = get_object_or_404(Comment, pk=pk)
    # save the primary key as a variable because we are deleting the pk in the
    # next line
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)
