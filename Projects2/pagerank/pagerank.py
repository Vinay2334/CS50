import os
import random
import re
import sys
from collections import defaultdict

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    random_prob = (1 - damping_factor) / len(corpus)
    model = dict()

    if corpus[page]:
        for link in corpus[page]:
            prob = damping_factor / len(corpus[page])
            model[link] = prob

    for link in corpus:
        if link in model:
            model[link] += random_prob
        else:
            model[link] = random_prob

    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # First sample
    page_rank = {page: 0 for page in corpus}
    current_page = random.choice(list(corpus.keys()))
    for _ in range(n):
        page_rank[current_page] += 1
        transition = transition_model(corpus, current_page, damping_factor)
        next_page = random.choices(list(transition.keys()), weights=list(transition.values()), k=1)[0]
        current_page = next_page
    page_rank = {page: rank/n for page, rank in page_rank.items()}
    return page_rank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_rank = {page:1/len(corpus) for page in corpus}
    N = len(corpus)
    convergence_threshold = 0.001

    while True:
        new_page_rank = {page: (1 - damping_factor) / N for page in corpus}
        no_link_rank = 0
        for page in corpus:
            if len(corpus[page]) == 0:
                new_page_rank[page] += page_rank[page]/N
            else:
                for link in corpus[page]:
                    new_page_rank[link] += damping_factor*page_rank[page]/len(corpus[page])
        
        for page in corpus:
            new_page_rank[page] += damping_factor * no_link_rank

        diff = max(abs(new_page_rank[page] - page_rank[page]) for page in corpus)
        if diff < convergence_threshold:
            break
        page_rank = new_page_rank
        
    return page_rank

if __name__ == "__main__":
    main()
