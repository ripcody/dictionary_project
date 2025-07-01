# dictionary_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from .models import Word # Import your Word model
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required # Import login_required decorator
from django.views.decorators.csrf import csrf_exempt # TEMPORARY: For AJAX testing, REMOVE LATER!
import json # For parsing incoming JSON
import requests # Import the requests library for API calls

# Define the API endpoint (consider putting this in settings.py for better management)
FREE_DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"


@login_required # This decorator ensures only logged-in users can access this view
def add_word(request):
    # Initialize variables for GET request or if POST fails early
    word_text = ""
    definition_text = ""

    if request.method == 'POST':
        word_text = request.POST.get("word", "").strip()
        definition_text = request.POST.get("definition", "").strip() # This will now be truly empty if user leaves it blank

        # Initial validation for 'word' field itself
        if not word_text:
            messages.warning(request, "Please enter a word.")
            return render(request, 'dictionary_app/add.html', {
                'word_text': word_text, # Keep the invalid word in the form
                'definition_text': definition_text # Keep any provided definition
            })

        # Debugging prints for full form submission
        print(f"--- Debug: POST Request (Full Form Submission) ---")
        print(f"--- Debug: word_text = '{word_text}' ---")
        print(f"--- Debug: definition_text = '{definition_text}' ---")


        # IMPORTANT: The API call logic for auto-fetching is now in get_definition_ajax (JavaScript initiated)
        # This block below now simply ensures a definition (either user-provided or JavaScript-fetched) is present
        if not definition_text:
            messages.warning(request, "A definition is required. Please provide one manually or ensure the API call worked via JavaScript.")
            return render(request, 'dictionary_app/add.html', {
                'word_text': word_text,
                'definition_text': definition_text # Will be empty if API didn't fill it
            })

        try:
            # Assign the current logged-in user as the owner
            # update_or_create handles both adding new and updating existing words
            word_obj, created = Word.objects.update_or_create(
                word=word_text.lower(), # Store word in lowercase for consistency/uniqueness
                owner=request.user,     # Filter by the current logged-in user
                defaults={'definition': definition_text} # Set/update the definition
            )

            if created:
                messages.success(request, f"'{word_text}' added to your dictionary successfully!")
            else:
                messages.info(request, f"'{word_text}' is already in your dictionary. Definition updated.")

            # Redirect to the add_word page (or a different page, e.g., view_all_words)
            return redirect(reverse('dictionary_app:add_word'))

        except IntegrityError:
            # This catch is usually for unique constraints, which `update_or_create` handles well
            # if `owner` is part of the unique_together constraint.
            messages.error(request, f"An integrity error occurred while adding '{word_text}'. It might already exist for this user in an unexpected way.")
            return redirect(reverse('dictionary_app:add_word'))
        except Exception as e:
            # Catch any other unexpected errors during database interaction
            messages.error(request, f"An unexpected error occurred while saving the word: {e}")
            return redirect(reverse('dictionary_app:add_word'))

    # For initial GET requests (when the user first navigates to the page)
    # or if validation fails and we need to re-render the form.
    # Pass potentially pre-filled values to the template.
    return render(request, 'dictionary_app/add.html', {
        'word_text': word_text,
        'definition_text': definition_text
    })


@login_required # Ensure only logged-in users can use this AJAX endpoint
# @csrf_exempt # <--- !!! IMPORTANT: Temporarily enables for testing, REMOVE THIS LINE IN PRODUCTION !!!
# You will remove this line AFTER you have confirmed your JavaScript's CSRF handling works.
# The `getCookie` function in your JS combined with 'X-CSRFToken' header should make this unnecessary.
def get_definition_ajax(request):
    if request.method == 'POST':
        try:
            # Attempt to parse the request body as JSON
            data = json.loads(request.body)
            word_to_fetch = data.get('word', '').strip()

            if not word_to_fetch:
                # Return a 400 Bad Request if no word is provided
                return JsonResponse({'error': 'No word provided for definition lookup.'}, status=400)

            print(f"--- AJAX: Fetching definition for '{word_to_fetch}' ---")

            # Make the API call to the external dictionary service
            response = requests.get(f"{FREE_DICTIONARY_API_URL}{word_to_fetch}")
            # Raise an HTTPError for bad responses (4xx or 5xx)
            response.raise_for_status()

            # Parse the JSON response from the API
            api_data = response.json()
            print("--- AJAX API Response Data ---")
            print(api_data)
            print("------------------------------")

            definition = "" # Initialize definition as empty
            # Logic to extract definition based on the API's expected structure
            # This assumes the API returns a list of entries, each with 'meanings'
            if api_data and isinstance(api_data, list) and api_data[0].get('meanings'):
                first_meaning = api_data[0]['meanings'][0]
                if first_meaning.get('definitions'):
                    definition = first_meaning['definitions'][0].get('definition', '').strip()

            if definition:
                # If a definition is found, return it
                return JsonResponse({'definition': definition})
            else:
                # Handle cases where the API found the word but no clear definition,
                # or returned a specific "word not found" message.
                if isinstance(api_data, dict) and 'title' in api_data and 'message' in api_data:
                    # API specific message for word not found
                    return JsonResponse({'definition': '', 'message': api_data['message']}, status=200)
                # Generic "definition not found"
                return JsonResponse({'definition': '', 'message': 'Definition not found.'}, status=200)

        except json.JSONDecodeError:
            # Handle cases where the request body is not valid JSON
            return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
        except requests.exceptions.RequestException as e:
            # Handle network errors or non-200 HTTP responses from the external API
            print(f"--- AJAX Error: API request failed: {e} ---")
            return JsonResponse({'error': f'Failed to fetch definition from API: {e}.'}, status=500)
        except (IndexError, KeyError, TypeError) as e:
            # Handle errors if the API response structure is not as expected
            print(f"--- AJAX Error: Could not parse API response: {e} ---")
            return JsonResponse({'error': f'Could not parse definition from API response: {e}.'}, status=500)
    else:
        # Return a 405 Method Not Allowed if not a POST request
        return JsonResponse({'error': 'Only POST requests are allowed for this endpoint.'}, status=405)


@login_required # This decorator ensures only logged-in users can access this view
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


@login_required # This decorator ensures only logged-in users can access this view
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
            messages.info(request, f"'{search_term}' not found in your dictionary.")

    return render(request, 'dictionary_app/search.html', {'exact_match': exact_match, 'search_term': search_term})


@login_required # This decorator ensures only logged-in users can access this view
def view_all_words(request):
    # Retrieve all words belonging to the current user, ordered alphabetically
    all_items = Word.objects.filter(owner=request.user).order_by('word')

    return render(request, 'dictionary_app/view.html', {'items': all_items})