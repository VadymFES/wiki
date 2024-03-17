from django.shortcuts import render
from django.http import Http404
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        raise Http404("Page not found.")
    else:
        # Pass the entry content to the template, converting Markdown to HTML if necessary
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": content
        })
    
def search(request):
    query = request.GET.get('q', '')        
    all_entries = util.list_entries()       
    if query in all_entries:        
        return redirect('entry', title=query)       
    else:   
        matching_entries = [entry for entry in all_entries if query.lower() in entry.lower()]   
        return render(request, "encyclopedia/search_results.html", {
            "entries": matching_entries,
            "search_query": query
        })

def create(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        if util.get_entry(title) is not None:
            # An entry already exists with this title
            return render(request, "encyclopedia/create.html", {
                "error": "An entry with this title already exists.",
                "title": title,
                "content": content
            })
        else:
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('entry', args=[title]))
    return render(request, "encyclopedia/create.html")

def edit_page(request, title):
    if request.method == 'POST':
        content = request.POST.get('content')
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse('entry', args=[title]))
    else:
        content = util.get_entry(title)
        if content is None:
            return Http404("Entry does not exist.")
        else:
            return render(request, 'encyclopedia/edit_page.html', {
                'title': title,
                'content': content
            })
        


def random_page(request):
    import random
    entries = util.list_entries()
    random_entry = random.choice(entries)  # Select a random entry
    return redirect('entry', title=random_entry)

def markdown_to_html(markdown):
    import re
    # Convert headers
    markdown = re.sub(r'^(#{1,6})\s*(.*)', lambda m: f'<h{len(m.group(1))}>{m.group(2)}</h{len(m.group(1))}>', markdown, flags=re.MULTILINE)
    
    # Convert bold text
    markdown = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', markdown)

    # Convert unordered lists
    markdown = re.sub(r'^\*\s+(.*)', r'<li>\1</li>', markdown, flags=re.MULTILINE)
    markdown = re.sub(r'((<li>.*</li>\n*)+)', r'<ul>\1</ul>', markdown, flags=re.MULTILINE)

    # Convert links
    markdown = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', markdown)

    # Convert paragraphs
    markdown = re.sub(r'^(?!<li>|<ul>|<h|<a)(.*)$', r'<p>\1</p>', markdown, flags=re.MULTILINE)

    return markdown