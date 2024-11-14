from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from functools import wraps
from models import Product, Order, User, db

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/admin')
@login_required
@admin_required
def admin_panel():
    return render_template('admin/index.html')

@admin.route('/admin/products')
@login_required
@admin_required
def manage_products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@admin.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        product = Product(
            name=request.form['name'],
            description=request.form['description'],
            price=float(request.form['price']),
            stock=int(request.form['stock']),
            image_url=request.form['image_url']
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully')
        return redirect(url_for('admin.manage_products'))
    return render_template('admin/add_product.html')

@admin.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.stock = int(request.form['stock'])
        product.image_url = request.form['image_url']
        db.session.commit()
        flash('Product updated successfully')
        return redirect(url_for('admin.manage_products'))
    return render_template('admin/edit_product.html', product=product)

@admin.route('/admin/products/delete/<int:id>')
@login_required
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully')
    return redirect(url_for('admin.manage_products'))

@admin.route('/admin/orders')
@login_required
@admin_required
def manage_orders():
    orders = Order.query.all()
    return render_template('admin/orders.html', orders=orders)

@admin.route('/admin/orders/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def update_order_status(id):
    order = Order.query.get_or_404(id)
    order.status = request.form['status']
    db.session.commit()
    flash('Order status updated')
    return redirect(url_for('admin.manage_orders'))

@admin.route('/admin/manage_users')
@login_required
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/admin/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        if request.form['password']:
            user.set_password(request.form['password'])
        db.session.commit()
        return redirect(url_for('admin.manage_users'))
    return render_template('admin/edit_user.html', user=user)

@admin.route('/admin/toggle_admin/<int:id>', methods=['POST'])
@login_required
def toggle_admin(id):
    user = User.query.get_or_404(id)
    user.is_admin = not user.is_admin
    db.session.commit()
    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/delete_user/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.manage_users'))