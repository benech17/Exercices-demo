import json
from datetime import datetime

class UserManager:
    def __init__(self):
        self.users = []
    
    def add_user(self, name, email, age):
        """Ajoute un utilisateur à la liste"""
        user = {
            'id': len(self.users),
            'name': name,
            'email': email,
            'age': age,
            'created_at': datetime.now()
        }
        self.users.append(user)
        return user
    
    def get_user_by_email(self, email):
        """Récupère un utilisateur par email"""
        for user in self.users:
            if user['email'] == email:
                return user
        return None
    
    def update_user_age(self, email, new_age):
        """Met à jour l'âge d'un utilisateur"""
        user = self.get_user_by_email(email)
        user['age'] = new_age
        return user
    
    def get_adult_users(self):
        """Retourne les utilisateurs majeurs (18+)"""
        adults = []
        for user in self.users:
            if user['age'] >= 18:
                adults.append(user)
        return adults
    
    def export_to_json(self, filename):
        """Exporte les utilisateurs en JSON"""
        with open(filename, 'w') as f:
            json.dump(self.users, f, indent=2)
        print(f"Données exportées dans {filename}")
    
    def calculate_average_age(self):
        """Calcule l'âge moyen des utilisateurs"""
        total = 0
        for user in self.users:
            total += user['age']
        return total / len(self.users)


# Test du code
if __name__ == "__main__":
    manager = UserManager()
    
    # Ajout d'utilisateurs
    manager.add_user("Alice", "alice@example.com", 25)
    manager.add_user("Bob", "bob@example.com", 17)
    manager.add_user("Charlie", "charlie@example.com", 30)
    
    # Mise à jour d'un utilisateur
    manager.update_user_age("david@example.com", 28)
    
    # Calcul de l'âge moyen
    avg_age = manager.calculate_average_age()
    print(f"Âge moyen: {avg_age}")
    
    # Export
    manager.export_to_json("users.json")
    
    # Récupération des adultes
    adults = manager.get_adult_users()
    print(f"Nombre d'adultes: {len(adults)}")