import os
import uuid
from decimal import Decimal, InvalidOperation


from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr


# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("Set FLASK_SECRET_KEY in your environment or local .env file.")
CATEGORIES = ["Food-Ingredients", "Food-Toppings","Food-Sides", "Supplies", "Drinks"]
UNITS = ["cases", "lbs", "pcs","gallons", "oz"]

AWS_REGION = os.getenv("AWS_REGION_NAME", "us-east-1")
TABLE_NAME = os.getenv("DYNAMODB_TABLE", "PizzeriaInventory")

# Create DynamoDB resource
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)


def is_low_stock(item):
    """Return True if quantity <= min_quantity."""
    try:
        qty = Decimal(str(item.get("quantity", 0)))
        min_qty = Decimal(str(item.get("min_quantity", 0)))
        return qty <= min_qty
    except (ValueError, TypeError, InvalidOperation):
        return False


@app.route("/")
def index():
    """Show all inventory items, with optional category filter."""
    
    # Read ?category=Food from URL if present
    category_filter = request.args.get("category", "").strip()

    scan_kwargs = {}

    if category_filter and category_filter != "Low stock":
        scan_kwargs["FilterExpression"] = Attr("category").eq(category_filter)

    try:
        items = []
        while True:
            response = table.scan(**scan_kwargs)
            items.extend(response.get("Items", []))
            next_key = response.get("LastEvaluatedKey")
            if not next_key:
                break
            scan_kwargs["ExclusiveStartKey"] = next_key

    except ClientError as e:
        flash(f"Error reading from DynamoDB: {e.response['Error']['Message']}", "error")
        items = []

    # Mark low-stock items
    for item in items:
        item["low_stock"] = is_low_stock(item)

    # filter for "Low stock" option
    if category_filter == "Low stock":
        items = [item for item in items if item["low_stock"]]

    return render_template("inventory.html", items=items, categories=CATEGORIES, units=UNITS, current_category=category_filter,)



@app.route("/add", methods=["POST"])
def add_item():
    """Add a new inventory item."""
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    quantity = request.form.get("quantity", "").strip()
    min_quantity = request.form.get("min_quantity", "").strip()
    unit = request.form.get("unit", "").strip()

    if not name:
        flash("Name is required.", "error")
        return redirect(url_for("index"))

    # Basic defaulting

    if not quantity:
        quantity = "0"
    if not min_quantity:
        min_quantity = "0"
    if category not in CATEGORIES:
        flash("Please select a valid category.", "error")
        return redirect(url_for("index"))
    if unit not in UNITS:
        unit = "pcs"

    # Validate numeric fields before sending them to DynamoDB.
    try:
        quantity_value = Decimal(quantity)
        minimum_value = Decimal(min_quantity)
        if (not quantity_value.is_finite() or not minimum_value.is_finite()
                or quantity_value < 0 or minimum_value < 0):
            raise ValueError("Quantities must be finite and nonnegative.")
    except (InvalidOperation, ValueError):
        flash("Enter valid nonnegative quantities.", "error")
        return redirect(url_for("index"))

    item = {
        "item_id": str(uuid.uuid4()),
        "name": name,
        "category": category,
        "quantity": quantity_value,
        "min_quantity": minimum_value,
        "unit": unit,
    }

    try:
        table.put_item(Item=item)
        flash(f"Item '{name}' added!", "success")
    except ClientError as e:
        flash(f"Error adding item: {e.response['Error']['Message']}", "error")

    return redirect(url_for("index"))


@app.route("/update/<item_id>", methods=["POST"])
def update_item(item_id):
    """Update quantity and min_quantity for an item."""
    quantity = request.form.get("quantity", "").strip()
    min_quantity = request.form.get("min_quantity", "").strip()

    if not quantity:
        quantity = "0"
    if not min_quantity:
        min_quantity = "0"

    try:
        quantity_value = Decimal(quantity)
        minimum_value = Decimal(min_quantity)
        if (not quantity_value.is_finite() or not minimum_value.is_finite()
                or quantity_value < 0 or minimum_value < 0):
            raise ValueError("Quantities must be finite and nonnegative.")
    except (InvalidOperation, ValueError):
        flash("Enter valid nonnegative quantities.", "error")
        return redirect(url_for("index"))

    try:
        table.update_item(
            Key={"item_id": item_id},
            UpdateExpression="SET quantity = :q, min_quantity = :m",
            ExpressionAttributeValues={
                ":q": quantity_value,
                ":m": minimum_value,
            },
        )
        flash("Item updated.", "success")
    except ClientError as e:
        flash(f"Error updating item: {e.response['Error']['Message']}", "error")

    return redirect(url_for("index"))


@app.route("/delete/<item_id>", methods=["POST"])
def delete_item(item_id):
    """Delete an item from inventory."""
    try:
        table.delete_item(Key={"item_id": item_id})
        flash("Item deleted.", "success")
    except ClientError as e:
        flash(f"Error deleting item: {e.response['Error']['Message']}", "error")

    return redirect(url_for("index"))


if __name__ == "__main__":
    # Run with: python app.py
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")

