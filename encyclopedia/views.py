from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
import random

from . import util

# search form class
class SearchQuery(forms.Form):
    query = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Search Wiki'}))

# add entry form
class EditEntryForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': 'form-control mb-4', 'placeholder': 'Entry Title'}))
    content = forms.CharField(label="Entry Content", widget=forms.Textarea(attrs={'class': 'form-control my-2', 'placeholder': 'Entry Content'}))
    edit_type = forms.CharField(label="", widget=forms.HiddenInput())

# INDEX
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form": SearchQuery
    })


# ENTRY gets the md entry if a title is found and if not, prompts user to create new entry
def entry(request, title):

    entry = util.get_entry(title)

    # if no entry found for title in URL, prompts user to create one
    if entry is None:
        no_entry_message = "No entry for " + title + " was found. Want to create one?"
        messages.add_message(request, messages.WARNING, no_entry_message)
        return render(request, "encyclopedia/entry.html", {
            "search_form": SearchQuery
        })

    # if title in URL is found, takes user to that entry's page
    return render(request, "encyclopedia/entry.html", {
        "entry": entry,
        "title": title,
        "search_form": SearchQuery
    })


# SEARCH processes a search query submitted in the sidebar search form or redirects user back to index if reached by GET
def search(request):

    # if search request received from sidebar form
    if request.method == "POST":
        
        # get query from search form
        search_query = SearchQuery(request.POST)

        #server side form validation
        if search_query.is_valid():
            #cleaned_data gets all clean data from form, and in brackets can specify which variable inside that class you want
            query = search_query.cleaned_data["query"]

            entry = util.get_entry(query)

            # if an entry was found with that title, take user to that entry's page
            if entry is not None:
                return render(request, "encyclopedia/entry.html", {
                    "entry": entry,
                    "search_form": SearchQuery
                })

            # if no entry found, search for similar results and take to search results page
            else:

                # get all entry titles
                all_titles = util.list_entries()
                title_matches = []

                # iterate through all entry titles
                for title in all_titles:

                    entry = util.get_entry(title)

                    # look for query as substring of title
                    if query.lower() in title.lower():
                        title_matches.append(title)

                    # look for query as substring of entry
                    elif query.lower() in entry.lower():
                        title_matches.append(title)

                    # look for matching first letters of query and title
                    elif query[0].lower() == title[0].lower():
                        title_matches.append(title)

                # get number of matches which will determine formatting on search results page
                num_matches = len(title_matches)
                
                return render(request, "encyclopedia/search.html", {
                    "search_form": SearchQuery,
                    "query": query,
                    "title_matches": title_matches,
                    "num_matches": num_matches
                })

        # if server side validation fails
        else:
            # send user back to their form submission, and django will automatically generate a validation error message
            return render(request, "encyclopedia/index.html", {
                "entries": util.list_entries(),
                "search_form": search_query
            })

    # search page reached by GET, so redirect to index
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form": SearchQuery
    })

def add(request):

    # if search request received from sidebar form
    if request.method == "POST":
        
        # get query from search form
        new_entry = EditEntryForm(request.POST)

        #server side form validation
        if new_entry.is_valid():
            
            title = new_entry.cleaned_data["title"] 
            edit_type = new_entry.cleaned_data["edit_type"] 

            entry = util.get_entry(title)

            # if there is no existing entry with the title
            if entry is None:

                entry = new_entry.cleaned_data["content"]
                util.save_entry(title, entry)
                messages.add_message(request, messages.SUCCESS, 'New entry added successfully!')

            # if there is an existing entry...
            else:

                # and the user is attempting to create a new entry, give error message and take to existing entry page
                if edit_type == "new":
                    entry_exists_message = "There is already an entry for " + title + "!"
                    messages.add_message(request, messages.WARNING, entry_exists_message)

                # and if user is trying to edit that existing entry, save entry content from form
                elif edit_type == "edit":
                    entry = new_entry.cleaned_data["content"] 
                    util.save_entry(title, entry)
                    messages.add_message(request, messages.SUCCESS, 'Entry edited successfully!')

        return render(request, "encyclopedia/entry.html", {
            "entry": entry,
            "search_form": SearchQuery,
            "title": title
        })

    # ADD reached by GET so take to add entry form
    # initialize edit_type as new, as_p formats form as paragraphs
    add_entry_form = EditEntryForm(initial={'edit_type': 'new'}).as_p()

    return render(request, "encyclopedia/edit.html", {
        "search_form": SearchQuery,
        "entry_form": add_entry_form,
        "form_head": "Add New Entry"
    })

# EDIT entry view
def edit(request):

    # if reached from edit button
    if request.method == "POST":
        
        # get entry title from form
        edit_request = request.POST
        title = edit_request["title"]

        # get entry content
        entry = util.get_entry(title)

        # pre-fill form with entry and title as values, as_p formats form as paragraphs
        entry_edit_form = EditEntryForm(initial={'title': title, 'content': entry, 'edit_type': 'edit'}).as_p()

        return render(request, "encyclopedia/edit.html", {
            "entry": entry,
            "search_form": SearchQuery,
            "entry_form": entry_edit_form,
            "form_head": "Edit Entry"
        })

    # reached by GET so go to index with message about needing to choose an entry to edit
    messages.add_message(request, messages.WARNING, 'Must choose an entry to edit.')
    return render(request, "encyclopedia/index.html", {
        "search_form": SearchQuery
    })

# display a RANDOM entry 
def random(request):

    # get all entry titles
    all_titles = util.list_entries()

    # generate a random integer between 0 and length of all_titles
    rando_num = random.randint(0, len(all_titles))

    # index to rando_num in list of titles
    rando_title = all_titles[rando_num]

    entry = util.get_entry(rando_title)

    return render(request, "encyclopedia/entry.html", {
            "entry": entry,
            "search_form": SearchQuery,
            "title": rando_title
        })