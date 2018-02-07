from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from goal_journal.goals.models import Goal

from .forms import EntryForm
from .models import Entry


@login_required
def goal_journal_view(request, goal_pk=None):
    all_entries = Entry.objects.filter(goal__user=request.user)
    if goal_pk:
        goal = Goal.objects.get(pk=goal_pk)
        all_entries = all_entries.filter(goal=goal)
    paginator = Paginator(all_entries, 10)

    page = request.GET.get('page')
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        entries = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        entries = paginator.page(paginator.num_pages)
    context = {
        'entry_form': EntryForm(user=request.user),
        'goals': Goal.objects.filter(user=request.user),
        'entries': entries,
    }
    return render(request, template_name='journal/goal_journal.html', context=context)


@login_required
@require_POST
def new_entry_view(request):
    if request.method == 'POST':
        entry_form = EntryForm(request.POST, user=request.user)
        if entry_form.is_valid():
            entry_form.save()
            messages.success(request, 'You created a new entry in your goal journal.')
            return redirect('journal:goal_journal')
        else:
            messages.error(request, entry_form.errors)
            return redirect('journal:goal_journal')


@login_required
def edit_entry_view(request, entry_pk):
    entry = get_object_or_404(Entry, pk=entry_pk)
    if request.method == 'POST':
        entry_form = EntryForm(request.POST, instance=entry, user=request.user)
        if entry_form.is_valid():
            entry_form.save()
            messages.success(request, 'You updated an entry in your goal journal for {}.'.format(entry.goal.goal))
            return redirect('journal:goal_journal')
        else:
            messages.error(request, entry_form.errors)
            return redirect('journal:goal_journal')
    entry_form = EntryForm(instance=entry, user=request.user)
    context = {
        'entry': entry,
        'entry_form': entry_form,
    }
    return render(request, template_name='journal/edit_journal_entry.html', context=context)


@login_required
def delete_entry_view(request, entry_pk):
    entry = get_object_or_404(Entry, pk=entry_pk)
    entry.delete()
    messages.success(request, "You deleted the entry from '{} for {}.".format(entry.date_of_entry, entry.goal.goal))
    return redirect('journal:goal_journal')

