from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from goal_journal.journal.forms import EntryForm

from .forms import GoalForm, NewCategoryForm, ActionForm, ActionFormSet, ActionLogForm
from .models import Category, Goal, Action, ActionLog


@login_required
def goals_list_view(request, category_pk=None):
    goals = Goal.objects.filter(user=request.user)
    context = {}
    if category_pk:
        category = get_object_or_404(Category, pk=category_pk)
        goals = goals.filter(categories=category)
        context['category'] = category
    current_goals = goals.filter(goal_achieved=False)
    achieved_goals = goals.filter(goal_achieved=True)
    categories = Category.objects.filter(user=request.user)
    context.update({
        'categories': categories,
        'current_goals': current_goals,
        'achieved_goals': achieved_goals,
    })
    return render(request, template_name='goals/goal_list.html', context=context)


@login_required
def goal_detail_view(request, goal_pk):
    goal = get_object_or_404(Goal, pk=goal_pk, user=request.user)
    active_actions = Action.objects.filter(goals=goal, action_completed=False)
    ActionLogFormSet = modelformset_factory(ActionLog, form=ActionLogForm, extra=goal.actions.count())
    action_log_formset = ActionLogFormSet(queryset=ActionLog.objects.none(), initial=[
        {'action': action.pk} for action in goal.actions.all()])
    action_log = ActionLog.objects.filter(action__in=goal.actions.all())[:5]
    context = {
        'goal': goal,
        'entry_form': EntryForm(user=request.user, initial={'goal': goal.id}),
        'active_actions': active_actions,
        'action_formset': ActionFormSet(queryset=Action.objects.none()),
        'action_log_formset': action_log_formset,
        'action_log': action_log,
    }
    return render(request, template_name='goals/goal_detail.html', context=context)


@login_required
def new_goal_view(request):
    if request.method == 'POST':
        goal_form = GoalForm(request.POST, user=request.user)
        action_formset = ActionFormSet(request.POST, queryset=Action.objects.none(), prefix='actions')
        if all([goal_form.is_valid(), action_formset.is_valid()]):
            new_goal = goal_form.save(commit=False)
            new_goal.user = request.user
            new_goal.save()
            goal_form.save_m2m()
            actions = action_formset.save(commit=False)
            for action in actions:
                # don't create duplicate action objects
                action, _ = Action.objects.get_or_create(action=action.action, user=request.user)
                action.goals.add(new_goal)
                action.save()
            messages.success(request, 'You set a new goal! Start tracking your progress by recording your actions '
                                      'below.')
            return redirect('goals:goal_detail', goal_pk=new_goal.pk)
        else:
            messages.error(request, 'Please correct the form errors below.')
            return redirect('goals:new_goal')
    goal_form = GoalForm(user=request.user)
    category_form = NewCategoryForm()
    action_formset = ActionFormSet(queryset=Action.objects.none(), prefix='actions')
    context = {
        'goal_form': goal_form,
        'category_form': category_form,
        'action_formset': action_formset,
    }
    return render(request, template_name='goals/edit_goal.html', context=context)


@require_POST
@login_required
def new_category_view(request):
    """Ajax view for creating new categories from the new/edit goal page."""
    category_form = NewCategoryForm(request.POST)
    if not category_form.is_valid():
        messages.error(request, category_form.errors)
        return redirect('goals:new_goal')
    category, _ = Category.objects.get_or_create(category=category_form.cleaned_data['category'].capitalize(),
                                                 user=request.user)
    goal_form = GoalForm(user=request.user)
    data = {
        'new_category_id': category.pk,
        'new_category': category.category.capitalize(),
        'category_field': render_to_string(
            'goals/_category_select.html',
            {'goal_form': goal_form},
            request=request
        ),
    }
    return JsonResponse(data)


@login_required
def edit_goal_view(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal_form = GoalForm(request.POST, user=request.user, instance=goal)
        action_formset = ActionFormSet(request.POST, queryset=Action.objects.filter(goals=goal), prefix='actions')
        if all([goal_form.is_valid(), action_formset.is_valid()]):
            goal = goal_form.save()
            actions = action_formset.save(commit=False)
            for action in actions:
                action.user = request.user
                action.save()
                if action not in goal.actions.all():
                    goal.actions.add(action)
            messages.success(request, 'Your changes have been saved!')
            return redirect('goals:goal_detail', goal_pk=goal.pk)
        else:
            messages.error(request, 'Please correct the form errors below.')
            return redirect('goals:edit_goal', pk=goal.pk)
    goal_form = GoalForm(user=request.user, instance=goal)
    category_form = NewCategoryForm()
    action_formset = ActionFormSet(queryset=Action.objects.filter(goals=goal), prefix='actions')
    context = {
        'edit': True,
        'goal': goal,
        'goal_form': goal_form,
        'category_form': category_form,
        'action_formset': action_formset,
    }
    return render(request, template_name='goals/edit_goal.html', context=context)


@login_required
@require_POST
def delete_goal_view(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    goal.delete()
    messages.success(request, "You deleted the goal {}.".format(goal.goal))
    return redirect('goals:goal_list')


@login_required
@require_POST
def goal_achieved_view(request, pk):
    goal = get_object_or_404(Goal, pk=pk, user=request.user)
    goal.goal_achieved = True
    goal.save()
    messages.success(request, "CONGRATS! You achieved your goal: '{}'.".format(goal.goal))
    return redirect('goals:goal_list')


@login_required
@require_POST
def new_action_view(request, goal_pk):
    goal = get_object_or_404(Goal, pk=goal_pk, user=request.user)
    action_formset = ActionFormSet(request.POST, queryset=Action.objects.none())
    if not action_formset.is_valid():
        messages.error(request, action_formset.errors)
        return redirect('goals:goal_detail', goal_pk=goal_pk)
    actions = action_formset.save(commit=False)
    for action in actions:
        # don't create duplicate action objects
        action, _ = Action.objects.get_or_create(action=action.action, user=request.user)
        action.goals.add(goal)
        action.save()
    messages.success(request, 'Your actions for this goal have been updated.')
    return redirect('goals:goal_detail', goal_pk=goal.pk)


@login_required
def manage_action_view(request, action_pk, goal_pk):
    goal = get_object_or_404(Goal, pk=goal_pk, user=request.user)
    action = get_object_or_404(Action, pk=action_pk, user=request.user)
    if request.method == 'POST':
        action_form = ActionForm(request.POST, instance=action, user=request.user)
        if action_form.is_valid():
            action = action_form.save(commit=False)
            for new_goal in action_form.cleaned_data['goals']:
                action.goals.add(new_goal)
            action.save()
            if action.action_completed:
                messages.success(request, 'Nice work! You completed one of your actions for this goal.')
            else:
                messages.success(request, 'You updated your action for this goal')
            return redirect('goals:goal_detail', goal_pk=goal.pk)
        else:
            messages.error(request, action_form.errors)
            return redirect('goals:manage_action', goal_pk=goal_pk, action_pk=action_pk)
    action_form = ActionForm(instance=action, user=request.user)
    action_log_form = ActionLogForm()
    context = {
        'goal': goal,
        'action': action,
        'action_form': action_form,
        'action_log_form': action_log_form
    }
    return render(request, template_name='goals/action.html', context=context)


@login_required
@require_POST
def delete_action_view(request, action_pk, goal_pk):
    goal = get_object_or_404(Goal, pk=goal_pk, user=request.user)
    action = get_object_or_404(Action, pk=action_pk, user=request.user)
    action.delete()
    messages.success(request, "You deleted the action {} from {}.".format(action.action, goal.goal))
    return redirect('goals:goal_detail', goal_pk=goal_pk)


@login_required
def action_log_list_view(request, goal_pk):
    goal = get_object_or_404(Goal, pk=goal_pk, user=request.user)
    action_log_all = ActionLog.objects.filter(action__goals=goal)
    paginator = Paginator(action_log_all, 10)
    page = request.GET.get('page')
    try:
        action_log = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        action_log = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        action_log = paginator.page(paginator.num_pages)
    context = {
        'goal': goal,
        'action_log': action_log,
    }
    return render(request, template_name='goals/action_log.html', context=context)


@login_required
@require_POST
def action_log_view(request, goal_pk):
    """AJAX view for logging actions and updating action log"""
    goal = get_object_or_404(Goal, pk=goal_pk, user=request.user)
    ActionLogFormSet = modelformset_factory(ActionLog, form=ActionLogForm, extra=goal.actions.count())
    action_log_formset = ActionLogFormSet(request.POST)
    if not action_log_formset.is_valid():
        messages.error(request, action_log_formset.errors)
        return redirect('journal:goal_journal', goal_pk=goal_pk)
    instances = action_log_formset.save(commit=False)
    for action_log in instances:
        if action_log.action_status is not None:
            action_log.save()
            break  # we only update one action on the formset at a time
    data = {
        'action_id': action_log.action.pk,
        'action_status': action_log.get_action_status_display(),
        'action_status_class': action_log.get_action_status_class(),
        'action_log_entry': render_to_string(
            'goals/_action_log_item.html',
            {'action_recorded': action_log, 'goal': goal},
            request=request
        ),
    }
    return JsonResponse(data)

