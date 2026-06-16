from heapify import Heapify

heapify = Heapify()


@heapify.query
def get_issue(id: str) -> str:
    """Get a GitHub issue by ID."""
    return f'{{"id": "{id}", "title": "Fix auth bug", "body": "Auth module has a timeout."}}'


@heapify.mutation
def create_mr(title: str, branch: str) -> str:
    """Open a pull request with the given title and branch."""
    return f'{{"id": "1", "title": "{title}", "branch": "{branch}", "status": "opened"}}'


heapify.init()

with heapify.session() as session:
    hypothesis = heapify.hypothesize()
    print(f"\nHypothesis: {hypothesis}")

    task = heapify.get_input()
    print(f"Task: {task}")

    result1 = get_issue("123")
    print(f"Issue result: {result1}")

    result2 = create_mr("Fix auth timeout", "fix-auth")
    print(f"MR result: {result2}")

    evaluation = heapify.evaluate(f"Agent opened PR: {result2}")
    print(f"\nEvaluation: {evaluation}")

