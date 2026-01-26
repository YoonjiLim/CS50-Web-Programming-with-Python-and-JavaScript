import markdown2, random
from django.shortcuts import render, redirect
from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "Page not found."
        })
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": markdown2.markdown(content)
    })

def search(request):
    query = request.GET.get("q", "").strip() 
    
    #Redirect to index if the search query is empty
    if query == "":
        return redirect("index")
    
    entries = util.list_entries()
    
    #If the query exactly matches an entry, redirect to that entry page
    for entry in entries:
        if entry.lower() == query.lower():
            return redirect("entry", title=query)
    
    #Otherwise, find all entries that contain the query as a substring
    searchResults = []
    for entry in entries:
        if query.lower() in entry.lower():
            searchResults.append(entry)

    #Render the search results page
    return render(request, "encyclopedia/search.html",{
        "query": query,
        "searchResults": searchResults
    })

def new(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        if not title or not content:
            return render(request, "encyclopedia/error.html",{
                "message":"Title and content cannot be empty."
            })
        
        if util.get_entry(title) is not None:
            return render(request, "encyclopedia/error.html", {
                "message": "An entry with this title already exists."
            })
        else:
            #To handle duplicate titles 
            content = f"# {title}\n\n{content}"
            util.save_entry(title, content)
            return redirect("entry", title=title)

    else:
        return render(request, "encyclopedia/new.html")


def edit(request, title):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        util.save_entry(title, content)
        return redirect("entry", title)
    else:
        content = util.get_entry(title)
        if content is None:
            return render(request, "encyclopedia/error.html",{
                "message":"Page Not Found"
            })
        return render(request, "encyclopedia/edit.html", {
            "title":title,
            "content":content
        })
    
def random_page(request):
    entries = util.list_entries()
    title = random.choice(entries)
    return redirect("entry", title=title)
