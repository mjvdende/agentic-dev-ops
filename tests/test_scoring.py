from agent_framework.scoring import KNOWN_ISSUES, score, summary


def test_known_issue_ids_are_1_to_14():
    assert [i.id for i in KNOWN_ISSUES] == list(range(1, 15))


def test_empty_report_finds_nothing():
    assert not any(score("All good, nothing found.").values())


def test_detects_specific_issues():
    found = score(
        "| 1 | app.py:19 | subprocess.run with shell=True allows command injection | Critical |\n"
        "| 2 | .gitlab-ci.yml:11 | docker login -p SuperSecret123 | High |\n"
        "| 3 | .gitlab-ci.yml:18 | curl -s https://x | bash | High |"
    )
    assert found[8] and found[11] and found[13]
    assert not found[9]


def test_previous_opencode_report_misses_app_issues():
    # Shape of the first /audit run: Dockerfile + CI only.
    found = score("Container runs as root. Unpinned base image (`python:latest`). Hardcoded `API_TOKEN` in ENV.")
    assert found[1] and found[4]
    assert not (found[8] or found[9] or found[10])


def test_summary_counts():
    out = summary(score("python:latest and debug=True"))
    assert out.startswith("Found 2/14")
