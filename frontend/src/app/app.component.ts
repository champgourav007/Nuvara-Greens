import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { environment } from '../environments/environment';

interface Product { id: string; name: string; description: string; tag: string; artwork: string; colour: string; unit_weight_g: number; price_inr: number; }
interface CartItem { product: Product; quantity: number; }

@Component({
  selector: 'app-root', standalone: true, imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html', styleUrl: './app.component.css'
})
export class AppComponent {
  private readonly http = inject(HttpClient);
  readonly apiUrl = environment.apiUrl;
  readonly products = signal<Product[]>([]);
  readonly cart = signal<CartItem[]>(this.restoreCart());
  readonly isCartOpen = signal(false);
  readonly isMenuOpen = signal(false);
  readonly loading = signal(true);
  readonly message = signal('');
  readonly cartCount = computed(() => this.cart().reduce((sum, item) => sum + item.quantity, 0));
  readonly total = computed(() => this.cart().reduce((sum, item) => sum + item.product.price_inr * item.quantity, 0));
  form = { name: '', phone: '', email: '', enquiry_type: 'Home order', message: '' };

  constructor() {
    this.http.get<Product[]>(`${this.apiUrl}/products`).subscribe({
      next: products => { this.products.set(products); this.loading.set(false); },
      error: () => { this.message.set('We could not load today’s harvest. Please try again shortly.'); this.loading.set(false); }
    });
  }

  add(product: Product) {
    this.cart.update(items => {
      const existing = items.find(item => item.product.id === product.id);
      const next = existing ? items.map(item => item.product.id === product.id ? {...item, quantity: item.quantity + 1} : item) : [...items, {product, quantity: 1}];
      this.saveCart(next); return next;
    });
    this.isCartOpen.set(true);
  }
  remove(productId: string) { this.cart.update(items => { const next = items.filter(item => item.product.id !== productId); this.saveCart(next); return next; }); }
  checkout() {
    if (!this.cart().length) return;
    this.http.post<{whatsapp_url: string | null}>(`${this.apiUrl}/orders`, {items: this.cart().map(item => ({product_id: item.product.id, quantity: item.quantity}))}).subscribe({
      next: result => {
        if (result.whatsapp_url) window.open(result.whatsapp_url, '_blank', 'noopener');
        else this.message.set('Your order enquiry was saved. Add WHATSAPP_NUMBER to backend/.env to enable WhatsApp checkout.');
      }, error: () => this.message.set('We could not send your order enquiry. Please try again.')
    });
  }
  submitEnquiry() {
    this.http.post(`${this.apiUrl}/enquiries`, this.form).subscribe({
      next: () => { this.message.set('Thank you — your enquiry has been received.'); this.form = {name: '', phone: '', email: '', enquiry_type: 'Home order', message: ''}; },
      error: () => this.message.set('We could not send your enquiry. Please check the form and try again.')
    });
  }
  private restoreCart(): CartItem[] { try { return JSON.parse(localStorage.getItem('nuvara-cart') ?? '[]'); } catch { return []; } }
  private saveCart(items: CartItem[]) { localStorage.setItem('nuvara-cart', JSON.stringify(items)); }
}
