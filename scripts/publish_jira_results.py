import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def build_comment(report):
    lines = ["Jenkins Automated Test Results", ""]

    passed = 0
    failed = 0
    skipped = 0

    for test in report.get("tests", []):
        outcome = test.get("outcome", "unknown")
        nodeid = test.get("nodeid", "unknown")
        test_name = nodeid.split("::")[-1]

        test_ids = test.get("metadata", {}).get(
            "test_ids", []
        )

        if outcome == "passed":
            status = "PASS"
            passed += 1
        elif outcome == "failed":
            status = "FAIL"
            failed += 1
        elif outcome == "skipped":
            status = "SKIPPED"
            skipped += 1
        else:
            status = outcome.upper()

        if not test_ids:
            test_ids = ["UNMARKED"]

        for test_id in test_ids:
            lines.append(
                f"{test_id} | {test_name} | {status}"
            )

    lines.extend([
        "",
        f"Total: {passed + failed + skipped}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        f"Skipped: {skipped}",
    ])

    build_url = os.getenv("BUILD_URL")
    if build_url:
        lines.append(f"Jenkins Build: {build_url}")

    return "\n".join(lines)


def publish_to_jira(comment):
    jira_url = os.environ["JIRA_URL"].rstrip("/")
    jira_issue = os.environ["JIRA_ISSUE"]
    jira_email = os.environ["JIRA_EMAIL"]
    jira_token = os.environ["JIRA_API_TOKEN"]

    import base64

    credentials = base64.b64encode(
        f"{jira_email}:{jira_token}".encode("utf-8")
    ).decode("ascii")

    # Jira Cloud's comment API expects
    # Atlassian Document Format (ADF).
    paragraphs = [
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": line}
            ] if line else []
        }
        for line in comment.splitlines()
    ]

    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": paragraphs,
        }
    }

    request = urllib.request.Request(
        url=(
            f"{jira_url}/rest/api/3/issue/"
            f"{jira_issue}/comment"
        ),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Basic {credentials}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(
        request, timeout=30
    ) as response:
        print(
            f"Jira comment created. HTTP {response.status}"
        )


def main():
    report_path = Path("results.json")

    if not report_path.exists():
        print("ERROR: results.json was not found.")
        sys.exit(1)

    with report_path.open(encoding="utf-8") as file:
        report = json.load(file)

    comment = build_comment(report)

    print("Generated test report:")
    print(comment)

    if "--preview" in sys.argv:
        print("\nPreview only. Nothing sent to Jira.")
        return

    required = [
        "JIRA_URL",
        "JIRA_ISSUE",
        "JIRA_EMAIL",
        "JIRA_API_TOKEN",
    ]

    missing = [
        key for key in required if not os.getenv(key)
    ]

    if missing:
        print(
            "Missing Jira configuration: "
            + ", ".join(missing)
        )
        sys.exit(1)

    try:
        publish_to_jira(comment)
    except urllib.error.HTTPError as error:
        print(
            f"Jira API returned HTTP {error.code}"
        )
        sys.exit(1)
    except urllib.error.URLError as error:
        print(f"Jira connection failed: {error.reason}")
        sys.exit(1)


if __name__ == "__main__":
    main()
