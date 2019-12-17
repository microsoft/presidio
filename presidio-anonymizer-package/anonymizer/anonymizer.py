from db.domain_relation import Domain_Relation


class Anonymizer:

    def __init__(self, threshold=0.5):
        self.id_ = 0
        self.whole_table = {}
        self.map = {}
        self.domain_name = ""
        self.threshold = threshold
        self.db_conn = Domain_Relation()

    def anonymize(self, text, results, domain_name):
        """
        replace the spam to alias getting from analyzer
        :param text: text that will be anonymized
        :param results: analyzing result from analyzer
        :param domain_name: domain name given by user or by default "DEFAULT_DOMAIN"
        :param entity_link: a boolean indicator to indicate if add ids to alias
        :return: anonymized text
        """
        original_text = text
        self.domain_name = domain_name
        self.lookup_db_table()
        # for each spam phrase in the analyzer result, check if it exists in the alias table
        for entity in results:
            entity_type = entity.entity_type
            score = entity.score
            start = entity.start
            end = entity.end
            string = original_text[start:end]
            if score >= self.threshold:
                # if the spam is not detected before, add it to the alias table
                if string not in self.map:
                    self.id_ += 1
                    self.map[string] = self.domain_name + "_<" + entity_type + "_" + str(self.id_) + ">"
                    # also insert the new spam-alias into the database
                    self.db_conn.insert_domain_attr((self.domain_name, self.map[string], string))
                # replace spam to its alias
                text = text.replace(string, self.map[string])
        # update the new max_id to database
        self.db_conn.insert_max_id((self.domain_name, self.id_))
        return text

    def print_lookup_table(self):
        for k in self.map:
            print("{:<30} {:<30}".format(k, self.map[k]))

    # look up and get the mapping information in the spam table
    def lookup_db_table(self):
        lookup_table = self.db_conn.get_domain_attr_by_domain(self.domain_name)
        try:
            # assign self.id by the max_id got from the database
            self.id_ = lookup_table[0][3]
            # assign each spam-alias pair to self.map
            for row in lookup_table:
                self.map[row[2]] = row[1]
        except IndexError:
            pass
