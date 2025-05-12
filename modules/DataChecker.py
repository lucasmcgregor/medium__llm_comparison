from modules.DataModels import ResumeData
from typing import Union, List, Any


class DataChecker:
    """
    A class for validating and cleaning extracted resume data.
    """

    def __init__(self):
        pass

    def _is_empty(self, field):
        """
        Check if a field is null or empty.
        
        Args:
            field: Field value to check
            
        Returns:
            bool: True if field is null or empty, False otherwise
        """
        if field is None:
            return True
        if isinstance(field, str) and not field.strip():
            return True
        if isinstance(field, (list, dict)) and not field:
            return True
        return False

    def _contains_text(self, source_text: Any, search_terms: Union[str, List[str]]) -> bool:
        """
        Check if source text contains any of the specified search terms (case-insensitive).

        Args:
            source_text: Source text to search in
            search_terms: Single search term or list of terms to search for

        Returns:
            bool: True if any search term is found in source_text, False otherwise
        """
        normalized_source = str(source_text).lower()

        # Convert single string to list for unified processing
        if isinstance(search_terms, str):
            search_terms = [search_terms]

        normalized_terms = [str(term).lower() for term in search_terms]
        return any(term in normalized_source for term in normalized_terms)

    def _score_field(self, field: Any, search_terms: Union[str, List[str]], required: bool = True, check_not_empty: bool = False) -> int:
        """
        Score a field based on content matching.
        
        Args:
            field: Field value to check
            search_terms: Terms to search for in the field
            required: Whether the field is required (default: True)
            check_not_empty: If true, it just checks that there is a not None value. No matching is done.(default: False)
        
        Returns:
        int: 0 if empty, 2 if contains match, -5 if no match, -10000 if the object is none
        """
        #print(f"   >>>> Checking field={field}, terms={search_terms}, required={required}, check_empty={check_not_empty}")

        rv = 0
        if check_not_empty:

            if self._is_empty(field):
                if required:
                    rv = -5
                else:
                    rv = 0
            else:
                rv = 2
        else:
            if not self._is_empty(field):
                if self._contains_text(field, search_terms):
                    rv = 2
                elif required:
                    rv = -5
                else:
                    rv = 0

        #print(f"        score: {rv:d}")
        return rv

    def score_resume_data(self, data: ResumeData) -> int:
        """
        Score resume data against expected values.
        
        Args:
            data: ResumeData object to score
        
        Returns:
        int: Cumulative score based on field matches
        """

        if data is None:
            return -100000

        score = 0
        score += self._score_field(data.full_name, "lucas mcgregor")
        score += self._score_field(data.phone, "555.555.5555")
        score += self._score_field(data.linkedin_url, "https://www.linkedin.com/in/lucasmcgregor/")
        score += self._score_field(data.education, ["chemistry", "indiana university", "b.s."])
        score += self._score_field(data.languages, "english")
        score += self._score_field(data.languages, "german", required=False)
        score += self._score_field(data.summary, ["technology", "executive", "engineering"])
        score += self._score_field(data.summary, ["ai/ml", "scale,", "global", "transformation"], required=False)
        score += self._score_field(data.summary, ["gdpr", "hipaa", "pci", "regulated"], required=False)
        score += self._score_field(data.skills, ["Leadership", "Technology", "Operations", "Product", "Engineering"])
        score += self._score_field(data.skills, ["strategy", "board", "transformation", "enterprise", "agile", "roadmaps"], required=False)

        work_experience_count_score = -40
        if not self._is_empty(data.work_experience):
            if len(data.work_experience) == 6:
                work_experience_count_score = 15
            elif len(data.work_experience) > 4:
                work_experience_count_score = 10
            elif len(data.work_experience) > 3:
                work_experience_count_score = 6
            else:
                work_experience_count_score = 2

            # points for all work experience that contains data
            for experience in data.work_experience:
                score += self._score_field(experience.title, "", check_not_empty=True)
                score += self._score_field(experience.organization, "", check_not_empty=True)
                score += self._score_field(experience.start_date, "", check_not_empty=True)
                score += self._score_field(experience.end_date, "", required=False, check_not_empty=True)


        score += work_experience_count_score
        #print(f"    >>>> Work Experience Count Score: {work_experience_count_score:d}")

        return score