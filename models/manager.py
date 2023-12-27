class PoliticalPartyManager:
    def __init__(self):
        self.political_parties = {}

    def insert(self, political_party):
        name = political_party.name

        if name in self.political_parties:
            raise ValueError("Political party name already exists")
        
        self.political_parties[name] = political_party

    def get(self, party_name):
        if party_name not in self.political_parties:
            raise ValueError("Political party name does not exist")
        return self.political_parties[party_name]
    
    def get_all(self):
        return self.political_parties.values()
    
    def delete(self, party_name):
        if party_name not in self.political_parties:
            raise ValueError("Political party name does not exist")
        del self.political_parties[party_name]

    def __del__(self):
        self.political_parties.clear()
