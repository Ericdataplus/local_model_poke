import os

class WalkthroughManager:
    def __init__(self, walkthrough_path="src/walkthrough.txt"):
        self.walkthrough_path = walkthrough_path
        self.sections = {}
        self.load_walkthrough()

    def load_walkthrough(self):
        if not os.path.exists(self.walkthrough_path):
            print(f"Warning: Walkthrough file not found at {self.walkthrough_path}")
            return

        with open(self.walkthrough_path, "r") as f:
            content = f.read()

        # Split by "SECTION"
        raw_sections = content.split("SECTION")
        for section in raw_sections:
            if not section.strip():
                continue
            
            # Parse title
            lines = section.strip().split("\n")
            title_line = lines[0].strip()
            # Remove number (e.g., "1: NEW BARK TOWN" -> "NEW BARK TOWN")
            if ":" in title_line:
                key = title_line.split(":", 1)[1].strip().lower()
            else:
                key = title_line.lower()
            
            self.sections[key] = section.strip()

    def query(self, query_text):
        """
        Returns the most relevant section based on the query.
        Simple keyword matching for now.
        """
        query_text = query_text.lower()
        
        # 1. Check for direct section match
        for key in self.sections:
            if key in query_text:
                return f"WALKTHROUGH SECTION MATCH:\n{self.sections[key]}"
        
        # 2. Check for keyword overlap
        best_section = None
        max_matches = 0
        
        for key, content in self.sections.items():
            matches = sum(1 for word in query_text.split() if word in content.lower())
            if matches > max_matches:
                max_matches = matches
                best_section = content
                
        if best_section and max_matches > 0:
            return f"RELEVANT WALKTHROUGH INFO:\n{best_section}"
            
        return "No specific walkthrough section found for that query. Try asking about a specific town or location."

    def get_section_by_location(self, location_name):
        """
        Tries to auto-retrieve a section based on the current map name.
        """
        location_name = location_name.lower()
        for key in self.sections:
            if key in location_name or location_name in key:
                return self.sections[key]
        return None
