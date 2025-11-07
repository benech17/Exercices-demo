import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import hashlib
import random
import string

class EcommerceOrderManager:
    """
    Gestionnaire de commandes pour une plateforme e-commerce
    Gère les commandes, les paiements, les promotions et les stocks
    """
    
    def __init__(self, tax_rate: float = 0.20):
        self.orders = {}
        self.products = {}
        self.customers = {}
        self.promo_codes = {}
        self.tax_rate = tax_rate
        self.order_counter = 1000
        self.payment_methods = ['credit_card', 'paypal', 'bank_transfer', 'crypto']
        self.valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded']
    
    def add_product(self, product_id: str, name: str, price: float, stock: int, category: str = 'general') -> Dict:
        """Ajoute un produit au catalogue"""
        if price < 0:
            raise ValueError("Le prix ne peut pas être négatif")
        
        if stock < 0:
            raise ValueError("Le stock ne peut pas être négatif")
        
        if product_id in self.products:
            raise ValueError(f"Le produit {product_id} existe déjà")
        
        product = {
            'id': product_id,
            'name': name,
            'price': price,
            'stock': stock,
            'category': category,
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }
        
        self.products[product_id] = product
        return product
    
    def update_stock(self, product_id: str, quantity: int) -> int:
        """Met à jour le stock d'un produit"""
        if product_id not in self.products:
            raise ValueError(f"Produit {product_id} introuvable")
        
        new_stock = self.products[product_id]['stock'] + quantity
        
        if new_stock < 0:
            raise ValueError("Stock insuffisant pour cette opération")
        
        self.products[product_id]['stock'] = new_stock
        return new_stock
    
    def register_customer(self, email: str, name: str, address: str, phone: str) -> Dict:
        """Enregistre un nouveau client"""
        if not self.validate_email(email):
            raise ValueError("Email invalide")
        
        if not self.validate_phone(phone):
            raise ValueError("Numéro de téléphone invalide")
        
        if email in self.customers:
            raise ValueError(f"Le client {email} existe déjà")
        
        customer_id = self.generate_customer_id(email)
        
        customer = {
            'id': customer_id,
            'email': email,
            'name': name,
            'address': address,
            'phone': phone,
            'registered_at': datetime.now().isoformat(),
            'loyalty_points': 0,
            'total_orders': 0,
            'total_spent': 0.0,
            'tier': 'bronze'
        }
        
        self.customers[email] = customer
        return customer
    
    def validate_email(self, email: str) -> bool:
        """Valide le format d'un email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone: str) -> bool:
        """Valide le format d'un numéro de téléphone français"""
        cleaned = phone.replace(' ', '').replace('.', '').replace('-', '')
        pattern = r'^(0|\+33)[1-9][0-9]{8}$'
        return bool(re.match(pattern, cleaned))
    
    def generate_customer_id(self, email: str) -> str:
        """Génère un ID unique pour un client basé sur son email"""
        hash_obj = hashlib.md5(email.encode())
        return 'CUST-' + hash_obj.hexdigest()[:10].upper()
    
    def create_promo_code(self, code: str, discount_percent: float, min_amount: float = 0, 
                         max_uses: int = None, expiry_date: datetime = None) -> Dict:
        """Crée un code promo"""
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("Le pourcentage de réduction doit être entre 0 et 100")
        
        if code in self.promo_codes:
            raise ValueError(f"Le code promo {code} existe déjà")
        
        promo = {
            'code': code.upper(),
            'discount_percent': discount_percent,
            'min_amount': min_amount,
            'max_uses': max_uses,
            'current_uses': 0,
            'expiry_date': expiry_date.isoformat() if expiry_date else None,
            'is_active': True
        }
        
        self.promo_codes[code.upper()] = promo
        return promo
    
    def validate_promo_code(self, code: str, order_amount: float) -> Tuple[bool, str, float]:
        """Valide un code promo et retourne la réduction applicable"""
        code = code.upper()
        
        if code not in self.promo_codes:
            return False, "Code promo invalide", 0.0
        
        promo = self.promo_codes[code]
        
        if not promo['is_active']:
            return False, "Code promo désactivé", 0.0
        
        if promo['expiry_date']:
            expiry = datetime.fromisoformat(promo['expiry_date'])
            if datetime.now() > expiry:
                return False, "Code promo expiré", 0.0
        
        if promo['max_uses'] and promo['current_uses'] >= promo['max_uses']:
            return False, "Code promo épuisé", 0.0
        
        if order_amount < promo['min_amount']:
            return False, f"Montant minimum de {promo['min_amount']}€ requis", 0.0
        
        discount = order_amount * (promo['discount_percent'] / 100)
        return True, "Code promo valide", discount
    
    def create_order(self, customer_email: str, items: List[Dict], 
                    promo_code: Optional[str] = None, 
                    shipping_address: Optional[str] = None) -> Dict:
        """Crée une nouvelle commande"""
        if customer_email not in self.customers:
            raise ValueError(f"Client {customer_email} introuvable")
        
        if not items:
            raise ValueError("La commande doit contenir au moins un article")
        
        # Vérifier la disponibilité des produits
        for item in items:
            product_id = item['product_id']
            quantity = item['quantity']
            
            if product_id not in self.products:
                raise ValueError(f"Produit {product_id} introuvable")
            
            if not self.products[product_id]['is_active']:
                raise ValueError(f"Produit {product_id} non disponible")
            
            if self.products[product_id]['stock'] < quantity:
                raise ValueError(f"Stock insuffisant pour {product_id}")
        
        # Calculer le sous-total
        subtotal = 0.0
        order_items = []
        
        for item in items:
            product = self.products[item['product_id']]
            item_total = product['price'] * item['quantity']
            subtotal += item_total
            
            order_items.append({
                'product_id': product['id'],
                'product_name': product['name'],
                'quantity': item['quantity'],
                'unit_price': product['price'],
                'total': item_total
            })
        
        # Appliquer le code promo
        discount = 0.0
        promo_applied = None
        
        if promo_code:
            valid, message, discount_amount = self.validate_promo_code(promo_code, subtotal)
            if valid:
                discount = discount_amount
                promo_applied = promo_code.upper()
                self.promo_codes[promo_applied]['current_uses'] += 1
        
        # Calculer les frais de livraison
        shipping_cost = self.calculate_shipping_cost(subtotal, customer_email)
        
        # Calculer le total avec taxes
        amount_after_discount = subtotal - discount
        tax_amount = amount_after_discount * self.tax_rate
        total = amount_after_discount + tax_amount + shipping_cost
        
        # Générer l'ID de commande
        order_id = f"ORD-{self.order_counter}"
        self.order_counter += 1
        
        # Créer la commande
        order = {
            'id': order_id,
            'customer_email': customer_email,
            'customer_id': self.customers[customer_email]['id'],
            'items': order_items,
            'subtotal': round(subtotal, 2),
            'discount': round(discount, 2),
            'promo_code': promo_applied,
            'shipping_cost': round(shipping_cost, 2),
            'tax_amount': round(tax_amount, 2),
            'total': round(total, 2),
            'status': 'pending',
            'payment_status': 'unpaid',
            'payment_method': None,
            'shipping_address': shipping_address or self.customers[customer_email]['address'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'tracking_number': None
        }
        
        self.orders[order_id] = order
        
        # Déduire du stock
        for item in items:
            self.update_stock(item['product_id'], -item['quantity'])
        
        return order
    
    def calculate_shipping_cost(self, order_amount: float, customer_email: str) -> float:
        """Calcule les frais de livraison en fonction du montant et du tier client"""
        customer = self.customers[customer_email]
        
        # Livraison gratuite au-dessus de 50€
        if order_amount >= 50:
            return 0.0
        
        # Réduction selon le tier
        base_cost = 5.99
        
        if customer['tier'] == 'gold':
            return 0.0
        elif customer['tier'] == 'silver':
            return base_cost * 0.5
        else:  # bronze
            return base_cost
    
    def process_payment(self, order_id: str, payment_method: str, 
                       payment_details: Dict) -> Dict:
        """Traite le paiement d'une commande"""
        if order_id not in self.orders:
            raise ValueError(f"Commande {order_id} introuvable")
        
        if payment_method not in self.payment_methods:
            raise ValueError(f"Méthode de paiement {payment_method} non supportée")
        
        order = self.orders[order_id]
        
        if order['payment_status'] == 'paid':
            raise ValueError("Cette commande a déjà été payée")
        
        if order['status'] == 'cancelled':
            raise ValueError("Impossible de payer une commande annulée")
        
        # Simuler la validation du paiement
        payment_success = self.validate_payment(payment_method, payment_details, order['total'])
        
        if payment_success:
            order['payment_status'] = 'paid'
            order['payment_method'] = payment_method
            order['status'] = 'confirmed'
            order['updated_at'] = datetime.now().isoformat()
            order['paid_at'] = datetime.now().isoformat()
            
            # Mettre à jour les statistiques client
            customer = self.customers[order['customer_email']]
            customer['total_orders'] += 1
            customer['total_spent'] += order['total']
            
            # Ajouter des points de fidélité (1 point par euro)
            loyalty_points = int(order['total'])
            customer['loyalty_points'] += loyalty_points
            
            # Mettre à jour le tier si nécessaire
            self.update_customer_tier(order['customer_email'])
            
            return {
                'success': True,
                'order_id': order_id,
                'payment_method': payment_method,
                'amount': order['total'],
                'loyalty_points_earned': loyalty_points
            }
        else:
            return {
                'success': False,
                'order_id': order_id,
                'error': 'Paiement refusé'
            }
    
    def validate_payment(self, payment_method: str, payment_details: Dict, amount: float) -> bool:
        """Valide un paiement (simulation)"""
        if payment_method == 'credit_card':
            card_number = payment_details.get('card_number', '')
            cvv = payment_details.get('cvv', '')
            
            # Validation basique
            if len(card_number) != 16 or not card_number.isdigit():
                return False
            
            if len(cvv) != 3 or not cvv.isdigit():
                return False
            
            # Simuler un échec aléatoire de 5%
            return random.random() > 0.05
        
        elif payment_method == 'paypal':
            email = payment_details.get('email', '')
            return self.validate_email(email)
        
        elif payment_method == 'bank_transfer':
            iban = payment_details.get('iban', '')
            return len(iban) >= 15
        
        elif payment_method == 'crypto':
            wallet = payment_details.get('wallet_address', '')
            return len(wallet) >= 26
        
        return False
    
    def update_customer_tier(self, customer_email: str):
        """Met à jour le tier d'un client en fonction de ses dépenses"""
        customer = self.customers[customer_email]
        total_spent = customer['total_spent']
        
        if total_spent >= 1000:
            customer['tier'] = 'gold'
        elif total_spent >= 500:
            customer['tier'] = 'silver'
        else:
            customer['tier'] = 'bronze'
    
    def update_order_status(self, order_id: str, new_status: str, 
                           tracking_number: Optional[str] = None) -> Dict:
        """Met à jour le statut d'une commande"""
        if order_id not in self.orders:
            raise ValueError(f"Commande {order_id} introuvable")
        
        if new_status not in self.valid_statuses:
            raise ValueError(f"Statut {new_status} invalide")
        
        order = self.orders[order_id]
        old_status = order['status']
        
        # Vérifier les transitions de statut valides
        if not self.is_valid_status_transition(old_status, new_status):
            raise ValueError(f"Transition de {old_status} à {new_status} non autorisée")
        
        order['status'] = new_status
        order['updated_at'] = datetime.now().isoformat()
        
        if tracking_number:
            order['tracking_number'] = tracking_number
        
        if new_status == 'shipped':
            order['shipped_at'] = datetime.now().isoformat()
        
        if new_status == 'delivered':
            order['delivered_at'] = datetime.now().isoformat()
        
        return order
    
    def is_valid_status_transition(self, old_status: str, new_status: str) -> bool:
        """Vérifie si une transition de statut est valide"""
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered', 'cancelled'],
            'delivered': ['refunded'],
            'cancelled': [],
            'refunded': []
        }
        
        return new_status in valid_transitions.get(old_status, [])
    
    def cancel_order(self, order_id: str, reason: str) -> Dict:
        """Annule une commande et remet en stock les produits"""
        if order_id not in self.orders:
            raise ValueError(f"Commande {order_id} introuvable")
        
        order = self.orders[order_id]
        
        if order['status'] in ['delivered', 'cancelled', 'refunded']:
            raise ValueError(f"Impossible d'annuler une commande {order['status']}")
        
        # Remettre les produits en stock
        for item in order['items']:
            self.update_stock(item['product_id'], item['quantity'])
        
        # Si la commande était payée, marquer pour remboursement
        if order['payment_status'] == 'paid':
            order['payment_status'] = 'refund_pending'
        
        order['status'] = 'cancelled'
        order['cancellation_reason'] = reason
        order['cancelled_at'] = datetime.now().isoformat()
        order['updated_at'] = datetime.now().isoformat()
        
        return order
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Récupère une commande par son ID"""
        return self.orders.get(order_id)
    
    def get_customer_orders(self, customer_email: str) -> List[Dict]:
        """Récupère toutes les commandes d'un client"""
        if customer_email not in self.customers:
            raise ValueError(f"Client {customer_email} introuvable")
        
        customer_orders = [
            order for order in self.orders.values()
            if order['customer_email'] == customer_email
        ]
        
        return sorted(customer_orders, key=lambda x: x['created_at'], reverse=True)
    
    def get_orders_by_status(self, status: str) -> List[Dict]:
        """Récupère toutes les commandes par statut"""
        if status not in self.valid_statuses:
            raise ValueError(f"Statut {status} invalide")
        
        return [order for order in self.orders.values() if order['status'] == status]
    
    def calculate_revenue(self, start_date: datetime, end_date: datetime) -> Dict:
        """Calcule le chiffre d'affaires sur une période"""
        total_revenue = 0.0
        total_orders = 0
        total_items = 0
        
        for order in self.orders.values():
            order_date = datetime.fromisoformat(order['created_at'])
            
            if start_date <= order_date <= end_date:
                if order['payment_status'] == 'paid' and order['status'] not in ['cancelled', 'refunded']:
                    total_revenue += order['total']
                    total_orders += 1
                    total_items += sum(item['quantity'] for item in order['items'])
        
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
        
        return {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_revenue': round(total_revenue, 2),
            'total_orders': total_orders,
            'total_items_sold': total_items,
            'average_order_value': round(avg_order_value, 2)
        }
    
    def get_best_selling_products(self, limit: int = 10) -> List[Dict]:
        """Récupère les produits les plus vendus"""
        product_sales = {}
        
        for order in self.orders.values():
            if order['payment_status'] == 'paid' and order['status'] not in ['cancelled', 'refunded']:
                for item in order['items']:
                    product_id = item['product_id']
                    
                    if product_id not in product_sales:
                        product_sales[product_id] = {
                            'product_id': product_id,
                            'product_name': item['product_name'],
                            'total_quantity': 0,
                            'total_revenue': 0.0
                        }
                    
                    product_sales[product_id]['total_quantity'] += item['quantity']
                    product_sales[product_id]['total_revenue'] += item['total']
        
        sorted_products = sorted(
            product_sales.values(),
            key=lambda x: x['total_quantity'],
            reverse=True
        )
        
        return sorted_products[:limit]
    
    def get_low_stock_products(self, threshold: int = 10) -> List[Dict]:
        """Récupère les produits avec un stock bas"""
        return [
            product for product in self.products.values()
            if product['stock'] <= threshold and product['is_active']
        ]
    
    def export_orders_to_json(self, filename: str, status: Optional[str] = None):
        """Exporte les commandes en JSON"""
        orders_to_export = self.orders.values()
        
        if status:
            orders_to_export = self.get_orders_by_status(status)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(list(orders_to_export), f, indent=2, ensure_ascii=False)
    
    def generate_order_report(self, order_id: str) -> str:
        """Génère un rapport détaillé pour une commande"""
        if order_id not in self.orders:
            raise ValueError(f"Commande {order_id} introuvable")
        
        order = self.orders[order_id]
        customer = self.customers[order['customer_email']]
        
        report = f"""
========================================
         RAPPORT DE COMMANDE
========================================

Commande: {order['id']}
Date: {order['created_at']}
Statut: {order['status']}
Paiement: {order['payment_status']}

CLIENT
------
Nom: {customer['name']}
Email: {customer['email']}
Tier: {customer['tier']}
Adresse: {order['shipping_address']}

ARTICLES
--------
"""
        
        for item in order['items']:
            report += f"{item['product_name']} x{item['quantity']} - {item['total']}€\n"
        
        report += f"""
MONTANTS
--------
Sous-total: {order['subtotal']}€
Réduction: -{order['discount']}€
Frais de port: {order['shipping_cost']}€
TVA ({self.tax_rate * 100}%): {order['tax_amount']}€
TOTAL: {order['total']}€

========================================
"""
        
        return report