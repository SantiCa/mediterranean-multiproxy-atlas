"""Pure filters for the proposed MVP; sample ages and paper years are independent."""


def select(rows, *, proxy=None, age_min=None, age_max=None, paper_year_min=None, paper_year_max=None):
    if age_min is not None and age_max is not None and age_min > age_max:
        raise ValueError("age_min must not exceed age_max")
    if paper_year_min is not None and paper_year_max is not None and paper_year_min > paper_year_max:
        raise ValueError("paper_year_min must not exceed paper_year_max")
    selected = []
    for row in rows:
        if proxy is not None and row["proxy"] != proxy:
            continue
        if paper_year_min is not None and row["publication_year"] < paper_year_min:
            continue
        if paper_year_max is not None and row["publication_year"] > paper_year_max:
            continue
        if age_min is not None or age_max is not None:
            if row["age_ka_bp"] is None:
                continue
            if age_min is not None and row["age_ka_bp"] < age_min:
                continue
            if age_max is not None and row["age_ka_bp"] > age_max:
                continue
        selected.append(row)
    return selected
