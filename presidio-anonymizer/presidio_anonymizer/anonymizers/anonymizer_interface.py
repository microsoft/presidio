from domain.result import Location


# TODO this needs to be implemented currently a stab.
# Please notice:
# 1. the text itself should be as a param in the class implementation.
# therefore it is not in the methods signature.
# 2. Redact should use replace with empty value
# 3. Please notice the document Omri created, it impacts the implementation
# 4. We might need duplicate text objects to manage partial intersection (see doc)
class AnonymizerInterface:
    def hash(self, location: Location):
        pass

    def fpe(self, location: Location, key: str, tweak: str, decrypt: bool):
        pass

    def mask(self, location: Location, replace_with: str, chars_to_replace: int,
             from_end: bool):
        pass

    def redact(self, location: Location):
        pass

    def replace(self, location: Location, new_value: str):
        pass
