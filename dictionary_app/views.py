# dictionary_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from .models import Word # Import your Word model
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required # Import login_required decorator
import requests # NEW: Import the requests library for API calls

# Define the API endpoint (consider putting this in settings.py for better management)
FREE_DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"


@login_required # <-- THIS IS CRUCIAL FOR LOGIN REQUIREMENT
def add_word(request):
    if request.method == 'POST':
        word_text = request.POST.get("word", "").strip()
        definition_text = request.POST.get("definition", "").strip()

        # --- NEW DEBUG PRINTS HERE ---
        print(f"--- Debug: word_text = '{word_text}' ---")
        print(f"--- Debug: definition_text = '{definition_text}' ---")
        print(f"--- Debug: API call condition: not definition_text ({not definition_text}) AND word_text ({bool(word_text)}) ---")
        # --- END NEW DEBUG PRINTS ---

        # If the user has NOT provided a definition AND they entered a word, try fetching from API
        if not definition_text and word_text:
            try:
                response = requests.get(f"{FREE_DICTIONARY_API_URL}{word_text}")
                response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                data = response.json()
                print("--- API Response Data ---") # NEW LINE
                print(data)                      # NEW LINE
                print("-------------------------") # NEW LINE

                # Attempt to get the first definition from the first meaning of the first entry
                if data and isinstance(data, list) and data[0].get('meanings'):
                    first_meaning = data[0]['meanings'][0]
                    if first_meaning.get('definitions'):
                        definition_text = first_meaning['definitions'][0].get('definition', '')
                        if definition_text: # Ensure definition_text is not empty after extraction
                            messages.info(request, f"Definition for '{word_text}' fetched from external API.")
                        else:
                            messages.warning(request, f"API found no specific definition text for '{word_text}'.")
                    else:
                        messages.warning(request, f"API found meanings but no definitions for '{word_text}'.")
                else:
                    messages.warning(request, f"API did not return a valid definition structure for '{word_text}'.")

                # If definition_text is still empty after API attempt, prompt user
                if not definition_text:
                    messages.warning(request, "Please enter a definition manually.")
                    return render(request, 'dictionary_app/add.html', {
                        'word_text': word_text, # Keep word in form
                        'definition_text': '' # Clear definition if API failed
                    })

            except requests.exceptions.RequestException as e:
                messages.error(request, f"Error fetching definition from API: {e}. Please enter it manually.")
                return render(request, 'dictionary_app/add.html', {
                    'word_text': word_text,
                    'definition_text': definition_text # Keep any partial definition if user had it
                })
            except (IndexError, KeyError, TypeError) as e:
                messages.warning(request, f"Could not parse definition for '{word_text}' from API response: {e}. Please enter it manually.")
                return render(request, 'dictionary_app/add.html', {
                    'word_text': word_text,
                    'definition_text': definition_text
                })

        
        # Final check if word_text or (now potentially API-fetched) definition_text is empty
        if not word_text or not definition_text:
            messages.warning(request, "Please enter both a word and its definition.")
            return render(request, 'dictionary_app/add.html', {
                'word_text': word_text,
                'definition_text': definition_text
            })

        try:
            # Assign the current logged-in user as the owner
            word_obj, created = Word.objects.update_or_create(
                word=word_text.lower(),
                owner=request.user, # NEW: Filter by owner
                defaults={'definition': definition_text}
            )
            if created:
                messages.success(request, f"'{word_text}' added to your dictionary successfully!")
            else:
                messages.info(request, f"'{word_text}' is already in your dictionary. Definition updated.")
            return redirect(reverse('dictionary_app:add_word'))
        except IntegrityError:
            messages.error(request, f"An error occurred while adding '{word_text}'. It might already exist in your dictionary.")
            return redirect(reverse('dictionary_app:add_word'))
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            return redirect(reverse('dictionary_app:add_word'))
        

    return render(request, 'dictionary_app/add.html') # Initial GET request
    
    

@login_required # <-- THIS IS CRUCIAL FOR LOGIN REQUIREMENT
def autocomplete(request):
    query = request.GET.get("q", "").strip().lower()
    suggestions = []
    if query:
        # Filter suggestions by the current user's words
        matching_words = Word.objects.filter(
            owner=request.user, # Filter by owner
            word__startswith=query
        ).values_list('word', flat=True)
        suggestions = sorted(list(matching_words))[:10]

    return JsonResponse(suggestions, safe=False)


@login_required # <-- THIS IS CRUCIAL FOR LOGIN REQUIREMENT
def search_word(request):
    exact_match = None
    search_term = ""

    if request.method == "POST":
        search_term = request.POST.get("search_word", "").strip()
        if not search_term:
            messages.warning(request, "Please enter a word to search.")
            return redirect(reverse('dictionary_app:search_word'))

        try:
            # Get an exact match for the current user's words
            word_obj = Word.objects.get(
                owner=request.user, # Filter by owner
                word__iexact=search_term
            )
            exact_match = {
                "word": word_obj.word,
                "definition": word_obj.definition
            }
        except Word.DoesNotExist:
            exact_match = None

    return render(request, 'dictionary_app/search.html', {'exact_match': exact_match, 'search_term': search_term})


@login_required # <-- THIS IS CRUCIAL FOR LOGIN REQUIREMENT
def view_all_words(request):
    # Retrieve all words belonging to the current user
    all_items = Word.objects.filter(owner=request.user)

    return render(request, 'dictionary_app/view.html', {'items': all_items})