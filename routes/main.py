from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Product, Cart, Order, OrderItem, db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    products = Product.query.all()
    return render_template('main/index.html', products=products)

@main.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('main/product_detail.html', product=product)

@main.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart_item = Cart.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product_id)
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Added to cart')
    return redirect(url_for('main.index'))

@main.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    return render_template('main/cart.html', cart_items=cart_items)

@main.route('/cart/remove/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    Cart.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).delete()
    db.session.commit()
    flash('Removed from cart')
    return redirect(url_for('main.cart'))

@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        payment_method = request.form['payment_method']
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        
        if not cart_items:
            flash('Your cart is empty')
            return redirect(url_for('main.cart'))
            
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        
        order = Order(
            user_id=current_user.id,
            payment_method=payment_method,
            total_amount=total_amount
        )
        db.session.add(order)
        
        for item in cart_items:
            order_item = OrderItem(
                order=order,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price
            )
            db.session.add(order_item)
            
        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        flash('Order placed successfully')
        return redirect(url_for('main.index'))
        
    return render_template('main/checkout.html')

@main.route('/orders')
@login_required
def orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('main/orders.html', orders=orders)