from app.utils import extract_div_content


def test_extract_div_content():
    div_class = (
        "top-card-layout__entity-info-container flex flex-wrap papabear:flex-nowrap"
    )
    url = "https://www.linkedin.com/jobs/view/3931418276/"
    text = extract_div_content(url, div_class)

    assert text == {
        "job_title": "Ing\u00e9nieur Data",
        "company_name": "Innova Solutions",
        "location": "Provence-Alpes-C\u00f4te d'Azur, France",
        "URL": url,
    }
