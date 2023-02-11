from flask import Flask, request, jsonify
from search import search
import html
from filter import Filter
from storage import DBStorage

app = Flask(__name__)

#add some CSS styling
styles = """
<style>
.site {
    font-size: .8rem;
    color: green;
}

.snippet {
    font-size: .9rem;
    color: gray:
    margin-bottom: 30px;
}

.rel-button {
    cursor: pointer;
    color: blue;
}
</style>
<script>
const relevant = function(query, link){
    fetch("/relevant", {
        method: 'POST',
        headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "query": query,
            "link": link
        })
    });
}
</script>
"""


search_template = styles + """
<form action="/" method="post">
    <input type="text" name="query">
    <input type="submit" value="Search">
</form>
"""

result_template = """
<p class="site">{rank}: {link} <span class="rel-button" onclick='relevant("{query}","{link}");'>Relevant</span></p>
<a href="{link}">{title}</a>
<p class="snippet">{snippet}</p>
"""


def show_search_form():
    return search_template

def run_search(query):
    results = search(query)
    fi = Filter(results)
    results = fi.filter() #reranks our results right here
    rendered = search_template
    results["snippet"] = results["snippet"].apply(lambda x: html.escape(x)) #try to remove any html tags, make sure the browser doesn't render random HTML tags
    for index, row in results.iterrows(): #row here is a dictionary, everything we pulled from our search
        rendered += result_template.format(**row) #pass the "row" into the template
    return rendered

@app.route("/", methods=["GET", "POST"]) #url you can go to on the web server.
def search_form():
    if request.method == "POST":
        query = request.form["query"]
        return run_search(query)
    else:
        return show_search_form()

@app.route("/relevant", methods=["POST"])
def mark_relevant():
    data = request.get_json()
    query = data["query"]
    link = data["link"]
    storage = DBStorage()
    storage.update_relevance(query, link, 10) #Whenever someone marks it relevant, we will set the relevance to 10
    return jsonify(success=True) #"hey everything went ok, your result has been marked relevant"