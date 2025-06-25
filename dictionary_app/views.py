# dictionary_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages # For Django's flash messages
from django.http import JsonResponse # For auto-complete JSON response
from .models import Word # Import your Word model
from django.db import IntegrityError # For handling unique constraint violations

# Note: No explicit load_dictionary() or save_dictionary() needed here,
# as Django's ORM handles persistence.

def add_word(request):
    if request.method == 'POST':
        word_text = request.POST.get("word", "").strip()
        definition_text = request.POST.get("definition", "").strip()

        if not word_text or not definition_text:
            messages.warning(request, "Please enter both a word and its definition.")
            return redirect(reverse('dictionary_app:add_word'))

        try:
            # Create a new word object and save it to the database
            # This automatically handles adding/updating in the 'database'
            word_obj, created = Word.objects.update_or_create(
                word=word_text.lower(), # Store lowercase for consistent lookups
                defaults={'definition': definition_text}
            )
            if created:
                messages.success(request, f"'{word_text}' added to the dictionary successfully!")
            else:
                messages.info(request, f"'{word_text}' is already in the dictionary. Definition updated.")
            return redirect(reverse('dictionary_app:add_word'))
        except IntegrityError:
            # This handles cases where word.lower() might not be unique
            # (though update_or_create handles the most common case)
            messages.error(request, f"An error occurred while adding '{word_text}'. It might already exist.")
            return redirect(reverse('dictionary_app:add_word'))
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            return redirect(reverse('dictionary_app:add_word'))

    return render(request, 'dictionary_app/add.html')

def autocomplete(request):
    query = request.GET.get("q", "").strip().lower()
    suggestions = []
    if query:
        # Use Django ORM's filter for efficient prefix matching
        # __startswith is a case-sensitive lookup, use __istartswith for case-insensitive
        # Since we store words lowercase, startswith should be fine.
        matching_words = Word.objects.filter(word__startswith=query).values_list('word', flat=True)
        suggestions = sorted(list(matching_words))[:10] # Sort and limit

    return JsonResponse(suggestions, safe=False) # safe=False allows returning a list, not just a dict

def search_word(request):
    exact_match = None
    search_term = ""

    if request.method == "POST":
        search_term = request.POST.get("search_word", "").strip()
        if not search_term:
            messages.warning(request, "Please enter a word to search.")
            return redirect(reverse('dictionary_app:search_word'))

        try:
            # Use Django ORM to get an exact match (case-insensitive)
            word_obj = Word.objects.get(word__iexact=search_term) # __iexact for case-insensitive exact match
            exact_match = {
                "word": word_obj.word, # Retrieve actual stored word (lowercase)
                "definition": word_obj.definition
            }
        except Word.DoesNotExist:
            exact_match = None # Word not found

    return render(request, 'dictionary_app/search.html', {'exact_match': exact_match, 'search_term': search_term})

def view_all_words(request):
    # Retrieve all words, already ordered alphabetically by default due to Meta.ordering
    all_items = Word.objects.all()
    # If you didn't set Meta.ordering, you'd do: Word.objects.all().order_by('word')
    
    # Transform to list of tuples for template compatibility if needed, or iterate objects directly
    # For a template, iterating over word_obj.word and word_obj.definition is usually fine.
    # We'll pass the queryset directly.
    return render(request, 'dictionary_app/view.html', {'items': all_items})