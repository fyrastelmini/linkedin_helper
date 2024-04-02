from app import extract_div_content


def test_extract_div_content():
    div_class = (
        "top-card-layout__entity-info-container flex flex-wrap papabear:flex-nowrap"
    )
    url = "https://www.linkedin.com/jobs/view/3872899453/"
    text = extract_div_content(url, div_class)

    assert text == {
        "job_title": "Open PhD Candidate Position at OneAngstrom",
        "company_name": "OneAngstrom",
        "location": "Grenoble, Auvergne-Rhône-Alpes, France",
        "URL": url,
    }
