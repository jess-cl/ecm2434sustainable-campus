from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Suggestion
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test


@login_required
def suggestions(request):
    """Allows users to create suggestions that can be checked by game keepers or developer. These suggestions 
       could be bug reports, or new locations to add to the map."""
    if request.method == 'POST':
        content = request.POST.get('suggestion', '').strip()
        category = request.POST.get('category', None)

        # Rejects suggestions that are too short. 
        if not content or len(content) < 5:
            messages.error(request, 'Suggestion content cannot be empty or too short')
            return redirect('suggestions')

        # Rejects suggestions that are not in the predefined categories
        if not category or category not in dict(Suggestion.CATEGORY_CHOICES):
            messages.error(request, 'Please select a valid category')
            return redirect('suggestions')

        # Creates suggestion using given data from submitted form. 
        Suggestion.objects.create(
            user=request.user,
            content=content,
            category=category
        )
        messages.success(request, 'Suggestion submitted successfully!')
        return redirect('suggestions')

    return render(request, 'suggestions.html')


@login_required
def view_suggestions(request):
    """Retrieves and displays all suggestions from most recent."""
    suggestions = Suggestion.objects.all().order_by('-created_at')
    context={'suggestions': suggestions}
    return render(request, 'view_suggestions.html', context)


@login_required
def delete_suggestion(request, suggestion_id):
    """Allows users to delete suggestions. This includes allowing players to delete there own suggestions
       while gamekeepers and developers can delete all."""
    try:
        suggestion = Suggestion.objects.get(id=suggestion_id)
        # Check permissions: Current user is a submitter or a gamekeeper/developer.
        if request.user == suggestion.user or request.user.role != 'player':
            suggestion.delete()
            messages.success(request, 'Suggestion deleted successfully')
        else:
            messages.error(request, 'You do not have permission to delete this suggestion')
    except Suggestion.DoesNotExist:
        messages.error(request, 'Suggestion does not exist')
    return redirect('view_suggestions')
