from flask import Blueprint, render_template, flash, send_from_directory, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .forms import ShopItemsForm, OrderForm
from .models import Product, Order, Customer
from . import db
import os

admin = Blueprint('admin', __name__)

def admin_required(func):
    @login_required
    def decorated_view(*args, **kwargs):
        if current_user.id != 1:
            return render_template('404.html'), 404
        return func(*args, **kwargs)
    return decorated_view

@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)

@admin.route('/add-shop-items', methods=['GET', 'POST'])
@admin_required
def add_shop_items():
    form = ShopItemsForm()
    if form.validate_on_submit():
        product_name = form.product_name.data
        current_price = form.current_price.data
        previous_price = form.previous_price.data
        in_stock = form.in_stock.data
        flash_sale = form.flash_sale.data
        file = form.product_picture.data
        if file:
            file_name = secure_filename(file.filename)
            file_path = os.path.join('./media', file_name)
            file.save(file_path)
        else:
            file_path = None

        new_shop_item = Product(
            product_name=product_name,
            current_price=current_price,
            previous_price=previous_price,
            in_stock=in_stock,
            flash_sale=flash_sale,
            product_picture=file_path
        )

        try:
            db.session.add(new_shop_item)
            db.session.commit()
            flash(f'{product_name} added successfully!', 'success')
            return redirect(url_for('admin.add_shop_items'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product: {str(e)}', 'danger')

    return render_template('add_shop_items.html', form=form)

@admin.route('/shop-items', methods=['GET', 'POST'])
@admin_required
def shop_items():
    items = Product.query.order_by(Product.date_added).all()
    return render_template('shop_items.html', items=items)

@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def update_item(item_id):
    item_to_update = Product.query.get_or_404(item_id)
    form = ShopItemsForm(obj=item_to_update)

    if form.validate_on_submit():
        product_name = form.product_name.data
        current_price = form.current_price.data
        previous_price = form.previous_price.data
        in_stock = form.in_stock.data
        flash_sale = form.flash_sale.data
        file = form.product_picture.data
        if file:
            file_name = secure_filename(file.filename)
            file_path = os.path.join('./media', file_name)
            file.save(file_path)
            item_to_update.product_picture = file_path

        item_to_update.product_name = product_name
        item_to_update.current_price = current_price
        item_to_update.previous_price = previous_price
        item_to_update.in_stock = in_stock
        item_to_update.flash_sale = flash_sale

        try:
            db.session.commit()
            flash(f'{product_name} updated successfully!', 'success')
            return redirect(url_for('admin.shop_items'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'danger')

    return render_template('update_item.html', form=form, item=item_to_update)

@admin.route('/delete-item/<int:item_id>', methods=['POST'])
@admin_required
def delete_item(item_id):
    item_to_delete = Product.query.get_or_404(item_id)
    try:
        db.session.delete(item_to_delete)
        db.session.commit()
        flash('Item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting item: {str(e)}', 'danger')
    return redirect(url_for('admin.shop_items'))

@admin.route('/view-orders')
@admin_required
def order_view():
    orders = Order.query.all()
    return render_template('view_orders.html', orders=orders)

@admin.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@admin_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    form = OrderForm(obj=order)

    if form.validate_on_submit():
        order.status = form.order_status.data
        try:
            db.session.commit()
            flash(f'Order {order_id} updated successfully!', 'success')
            return redirect(url_for('admin.order_view'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating order: {str(e)}', 'danger')

    return render_template('order_update.html', form=form, order=order)

@admin.route('/customers')
@admin_required
def display_customers():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@admin.route('/admin-page')
@admin_required
def admin_page():
    return render_template('admin.html')
