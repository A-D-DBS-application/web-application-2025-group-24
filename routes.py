# routes.py
from flask import Blueprint, jsonify, request, render_template, session
from models import (
    supabase, 
    upload_property_image, 
    generate_unique_id, 
    generate_unique_property_id,
    estimate_property_price,
    PropertyType,
    Province,
    BELGIAN_CITIES,
    CITY_TO_PROVINCE
)

# Create blueprint for routes
routes = Blueprint('routes', __name__)


# Authentication helper functions
def is_logged_in():
    try:
        return 'user_id' in session and 'user_type' in session
    except Exception as e:
        print(f"Error checking login status: {e}")
        return False


def get_current_user():
    try:
        if is_logged_in():
            return {
                'user_id': session.get('user_id'),
                'user_type': session.get('user_type'),
                'user_data': session.get('user_data', {})
            }
        return None
    except Exception as e:
        print(f"Error getting current user: {e}")
        return None


# Page Routes
@routes.route('/')
def index():
    return render_template('index.html')


@routes.route('/developer')
def developer_page():
    return render_template('developer.html', provinces=Province)


@routes.route('/property-owner')
def property_owner_page():
    return render_template('property_owner.html', property_types=PropertyType, provinces=Province)


@routes.route('/property/<int:property_id>')
def property_detail(property_id):
    """Display detailed view of a specific property"""
    return render_template('property_detail.html', property_id=property_id)


# API Routes
@routes.route('/api/submit-property', methods=['POST'])
def submit_property():
    """Handle property submission from landowners with image upload"""
    
    user = get_current_user()
    
    if not user or user['user_type'] != 'property_owner':
        return jsonify({"success": False, "error": "Must be logged in as property owner"}), 401
    
    if not supabase:
        return jsonify({"error": "Database not connected"}), 500
    
    try:
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = {
                'property_name': request.form.get('property_name'),
                'province': request.form.get('province'),
                'city': request.form.get('city'),
                'size': request.form.get('size'),
                'description': request.form.get('description'),
                'type': request.form.get('type'),
                'price_min': request.form.get('price_min'),
                'price_max': request.form.get('price_max')
            }
            image_count = int(request.form.get('image_count', 0))
        else:
            data = request.get_json()
            image_count = 0
        
        property_id = generate_unique_property_id()
        if property_id is None:
            return jsonify({"success": False, "error": "Could not generate unique property ID"}), 500
        
        image_urls = []
        for i in range(image_count):
            file_key = f'image_{i}'
            if file_key in request.files:
                file = request.files[file_key]
                if file and file.filename:
                    try:
                        image_url = upload_property_image(file, property_id, i)
                        if image_url:
                            image_urls.append(image_url)
                    except Exception as img_error:
                        print(f"Error uploading image {i}: {img_error}")
        
        allowed_types = {'land', 'building'}
        raw_type = (data.get('type') or '').strip().lower()
        property_type = raw_type if raw_type in allowed_types else 'land'

        allowed_provinces = [p.value for p in Province]
        province = (data.get('province') or '').strip()
        city = (data.get('city') or '').strip()
        if province and province not in allowed_provinces:
            return jsonify({"success": False, "error": "Invalid province"}), 400

        try:
            price_min = float(data.get('price_min') or 0)
            price_max = float(data.get('price_max') or 0)
            if price_min < 0 or price_max < 0:
                return jsonify({"success": False, "error": "Prices cannot be negative"}), 400
            if price_max < price_min:
                return jsonify({"success": False, "error": "Maximum price must be greater than minimum price"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid price format"}), 400

        property_data = {
            "property_id": property_id,
            "property_name": data.get("property_name", ""),
            "size": int(data.get("size")),
            "description": data.get("description", ""),
            "province": province,
            "city": city,
            "propertyOwner_id": user['user_id'],
            "image_urls": image_urls,
            "type": property_type,
            "price_min": price_min,
            "price_max": price_max
        }
        
        response = supabase.table('Property').insert(property_data).execute()
        
        return jsonify({
            "success": True,
            "message": "Property added successfully!",
            "property_id": property_id,
            "image_count": len(image_urls),
            "data": response.data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error saving property: {str(e)}"
        }), 500


@routes.route('/api/properties', methods=['GET'])
def get_properties():
    """Get all properties with optional filtering"""
    
    if not supabase:
        return jsonify({"success": False, "error": "Database not connected"}), 500
    
    try:
        province = request.args.get('province', '')
        city = request.args.get('city', '')
        min_size = request.args.get('min_size', '')
        max_price = request.args.get('max_price', '')
        prop_type = request.args.get('type', '')
        
        query = supabase.table('Property').select('*').eq('sold', False)
        
        if province:
            query = query.eq('province', province)
        if city:
            query = query.ilike('city', f'%{city}%')
        if min_size:
            try:
                query = query.gte('size', int(min_size))
            except ValueError:
                pass
        if prop_type:
            # Do a case-insensitive match so both 'Land' and 'land' stored values match
            query = query.ilike('type', prop_type)
        if max_price:
            try:
                query = query.lte('price_min', float(max_price))
            except ValueError:
                pass
        
        response = query.execute()
        
        return jsonify({
            "success": True,
            "properties": response.data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error fetching properties: {str(e)}"
        }), 500


@routes.route('/api/contact-owner', methods=['POST'])
def contact_owner():
    """Handle contact requests from developers to property owners"""
    if not supabase:
        return jsonify({"success": False, "error": "Database not connected"}), 500
    
    try:
        return jsonify({
            "success": True,
            "message": "Contact request submitted successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error processing contact: {str(e)}"
        }), 500


@routes.route('/api/register-developer', methods=['POST'])
def register_developer():
    """Handle developer registration"""
    
    if not supabase:
        return jsonify({"success": False, "error": "Database not connected"}), 500
    
    try:
        data = request.get_json()
        
        email = (data.get("email") or "").strip()
        phone = (data.get("phone_number") or "").strip()
        first_name = (data.get("first_name") or "").strip()
        last_name = (data.get("last_name") or "").strip()
        company_name = (data.get("company_name") or "").strip()
        vat_number = (data.get("vat_number") or "").strip()
        
        if not first_name:
            return jsonify({"success": False, "error": "First name is required"}), 400
        if not last_name:
            return jsonify({"success": False, "error": "Last name is required"}), 400
        if not email:
            return jsonify({"success": False, "error": "Email is required"}), 400
        if not phone:
            return jsonify({"success": False, "error": "Phone number is required"}), 400
        if not company_name:
            return jsonify({"success": False, "error": "Company name is required"}), 400
        if not vat_number:
            return jsonify({"success": False, "error": "VAT number is required"}), 400
        
        email_check = supabase.table('Developer').select('email').eq('email', email).execute()
        if email_check.data:
            return jsonify({"success": False, "error": "This email address is already registered"}), 400
        
        phone_check = supabase.table('Developer').select('phone_number').eq('phone_number', phone).execute()
        if phone_check.data:
            return jsonify({"success": False, "error": "This phone number is already registered"}), 400
        
        developer_id = generate_unique_id('Developer', 'developer_id')
        
        developer_data = {
            "developer_id": developer_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": phone,
            "company_name": company_name,
            "VAT_number": vat_number,
            "verified": False
        }
        
        response = supabase.table('Developer').insert(developer_data).execute()
        
        return jsonify({
            "success": True,
            "message": "Developer registration successful!",
            "developer_id": developer_id,
            "data": response.data
        })
        
    except Exception as e:
        error_msg = str(e).lower()
        if 'duplicate' in error_msg or 'unique' in error_msg:
            if 'email' in error_msg:
                return jsonify({"success": False, "error": "This email address is already registered"}), 400
            elif 'phone' in error_msg:
                return jsonify({"success": False, "error": "This phone number is already registered"}), 400
            else:
                return jsonify({"success": False, "error": "An account with these details already exists"}), 400
        return jsonify({
            "success": False,
            "error": "Registration failed. Please check your information and try again."
        }), 500


@routes.route('/api/register-property-owner', methods=['POST'])
def register_property_owner():
    """Handle property owner registration"""
    
    if not supabase:
        return jsonify({"success": False, "error": "Database not connected"}), 500
    
    try:
        data = request.get_json()
        
        email = (data.get("email") or "").strip()
        phone = (data.get("phone_number") or "").strip()
        first_name = (data.get("first_name") or "").strip()
        last_name = (data.get("last_name") or "").strip()
        
        if not first_name:
            return jsonify({"success": False, "error": "First name is required"}), 400
        if not last_name:
            return jsonify({"success": False, "error": "Last name is required"}), 400
        if not email:
            return jsonify({"success": False, "error": "Email is required"}), 400
        if not phone:
            return jsonify({"success": False, "error": "Phone number is required"}), 400
        
        email_check = supabase.table('Property owner').select('email').eq('email', email).execute()
        if email_check.data:
            return jsonify({"success": False, "error": "This email address is already registered"}), 400
        
        phone_check = supabase.table('Property owner').select('phone_number').eq('phone_number', phone).execute()
        if phone_check.data:
            return jsonify({"success": False, "error": "This phone number is already registered"}), 400
        
        property_owner_id = generate_unique_id('Property owner', 'propertyOwner_id')
        
        property_owner_data = {
            "propertyOwner_id": property_owner_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone_number": phone
        }
        
        response = supabase.table('Property owner').insert(property_owner_data).execute()
        
        return jsonify({
            "success": True,
            "message": "Property Owner registration successful!",
            "property_owner_id": property_owner_id,
            "data": response.data
        })
        
    except Exception as e:
        error_msg = str(e).lower()
        if 'duplicate' in error_msg or 'unique' in error_msg:
            if 'email' in error_msg:
                return jsonify({"success": False, "error": "This email address is already registered"}), 400
            elif 'phone' in error_msg:
                return jsonify({"success": False, "error": "This phone number is already registered"}), 400
            else:
                return jsonify({"success": False, "error": "An account with these details already exists"}), 400
        return jsonify({
            "success": False,
            "error": "Registration failed. Please check your information and try again."
        }), 500


@routes.route('/api/login', methods=['POST'])
def login():
    """Handle email-based login for developers and property owners"""
    print("Login request received")
    
    try:
        data = request.get_json()
        print(f"Login data received: {data}")
        
        email = data.get('email', '').strip()
        user_type = data.get('user_type', '').strip()
        
        print(f"Email: {email}, User type: {user_type}")
        
        if not email or not user_type:
            print("Missing email or user type")
            return jsonify({"success": False, "error": "Email and type are required"}), 400
        
        if user_type == 'developer':
            print("Checking developer table...")
            result = supabase.table('Developer').select('*').eq('email', email).execute()
            print(f"Developer query result: {result}")
            
            if not result.data:
                print("Developer email not found")
                return jsonify({"success": False, "error": "Developer email not found"}), 404
            user_data = result.data[0]
            
            if not user_data.get('verified', False):
                print("Developer account not verified")
                return jsonify({"success": False, "error": "Your account is pending verification. An admin is reviewing your registration and will approve it shortly."}), 403
            
        elif user_type == 'property_owner':
            print("Checking property owner table...")
            result = supabase.table('Property owner').select('*').eq('email', email).execute()
            print(f"Property owner query result: {result}")
            
            if not result.data:
                print("Property owner email not found")
                return jsonify({"success": False, "error": "Property Owner email not found"}), 404
            user_data = result.data[0]
            
        else:
            print("Invalid user type")
            return jsonify({"success": False, "error": "Invalid user type"}), 400
        
        print(f"User data found: {user_data}")
        
        session['user_id'] = user_data.get('developer_id') if user_type == 'developer' else user_data.get('propertyOwner_id')
        session['user_type'] = user_type
        session['user_data'] = user_data
        
        print(f"Session created for user ID: {session['user_id']}")
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user_type": user_type,
            "user_data": user_data
        })
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"success": False, "error": f"Login error: {str(e)}"}), 500


@routes.route('/api/logout', methods=['POST'])
def logout():
    """Handle logout"""
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})


@routes.route('/api/current-user', methods=['GET'])
def current_user():
    """Get current logged in user info"""
    user = get_current_user()
    if user:
        return jsonify({"success": True, "user": user})
    else:
        return jsonify({"success": False, "error": "Not logged in"}), 401


@routes.route('/api/mark-sold/<int:property_id>', methods=['POST'])
def mark_property_sold(property_id):
    """Mark a property as sold and set the final sale price"""
    user = get_current_user()
    if not user or user['user_type'] != 'property_owner':
        return jsonify({"success": False, "error": "Must be logged in as property owner"}), 401
    
    try:
        property_check = supabase.table('Property').select('propertyOwner_id').eq('property_id', property_id).execute()
        
        if not property_check.data:
            return jsonify({"success": False, "error": "Property not found"}), 404
        
        if property_check.data[0]['propertyOwner_id'] != user['user_id']:
            return jsonify({"success": False, "error": "You can only mark your own properties as sold"}), 403
        
        data = request.get_json()
        definite_price = data.get('definite_price')
        
        if definite_price is None:
            return jsonify({"success": False, "error": "Please enter the final sale price"}), 400
        
        try:
            definite_price = float(definite_price)
            if definite_price < 0:
                return jsonify({"success": False, "error": "Price cannot be negative"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid price format"}), 400
        
        response = supabase.table('Property').update({
            'sold': True,
            'final_price': definite_price
        }).eq('property_id', property_id).execute()
        
        return jsonify({
            "success": True,
            "message": "Property marked as sold successfully"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error marking property as sold: {str(e)}"}), 500


@routes.route('/api/validate-city', methods=['POST'])
def validate_city():
    """Check if a city exists in the Belgian cities database and matches the province"""
    try:
        data = request.get_json()
        city = (data.get('city') or '').strip().lower()
        province = (data.get('province') or '').strip()
        
        if not city:
            return jsonify({"success": False, "valid": False, "error": "City name is required"}), 400
        
        # Check if city exists in pre-cached Belgian cities (case-insensitive)
        if city not in BELGIAN_CITIES:
            return jsonify({
                "success": True, 
                "valid": False, 
                "error": f"'{data.get('city')}' is not a recognized Belgian city. Please check the spelling."
            })
        
        # Check if city is in the correct province
        if province and city in CITY_TO_PROVINCE:
            expected_province = CITY_TO_PROVINCE[city]
            if expected_province != province:
                return jsonify({
                    "success": True,
                    "valid": False,
                    "error": f"'{data.get('city').title()}' is not in {province}. This city is located in {expected_province}."
                })
        
        return jsonify({"success": True, "valid": True, "city": city})
            
    except Exception as e:
        return jsonify({"success": False, "error": f"Error validating city: {str(e)}"}), 500


@routes.route('/api/estimate-price', methods=['POST'])
def api_estimate_price():
    """API endpoint to estimate property price based on KNN algorithm"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        required_fields = ['province', 'city', 'size', 'type']
        missing_fields = [f for f in required_fields if not data.get(f)]
        
        if missing_fields:
            return jsonify({
                "success": False, 
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        result = estimate_property_price(data)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": f"Error estimating price: {str(e)}"}), 500


@routes.route('/api/my-properties', methods=['GET'])
def get_my_properties():
    """Get properties for the current logged-in property owner"""
    user = get_current_user()
    if not user or user['user_type'] != 'property_owner':
        return jsonify({"success": False, "error": "Must be logged in as property owner"}), 401
    
    try:
        response = supabase.table('Property').select('*').eq('propertyOwner_id', user['user_id']).execute()
        
        properties = response.data
        
        for property_data in properties:
            property_id = property_data['property_id']
            
            interests_response = supabase.table('Property_Interest').select('developer_id').eq('property_id', property_id).execute()
            print(f"Property {property_id} - Interests from DB: {interests_response.data}")
            
            interested_developers = []
            if interests_response.data:
                for interest in interests_response.data:
                    developer_id = interest['developer_id']
                    print(f"  Fetching developer {developer_id}")
                    developer_response = supabase.table('Developer').select('first_name, last_name, email, phone_number, company_name').eq('developer_id', developer_id).execute()
                    
                    if developer_response.data:
                        dev_data = developer_response.data[0]
                        interested_developers.append({
                            'first_name': dev_data['first_name'],
                            'last_name': dev_data['last_name'],
                            'email': dev_data['email'],
                            'phone_number': dev_data.get('phone_number'),
                            'company': dev_data.get('company_name')
                        })
            
            print(f"Property {property_id} - Total interested developers: {len(interested_developers)}")
            property_data['interested_developers'] = interested_developers
            property_data['interested_developer'] = interested_developers[0] if interested_developers else None
        
        return jsonify({
            "success": True,
            "properties": properties
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error fetching properties: {str(e)}"}), 500


@routes.route('/api/property/<int:property_id>', methods=['GET'])
def get_property_details(property_id):
    """Get detailed information for a specific property"""
    try:
        response = supabase.table('Property').select('*').eq('property_id', property_id).execute()
        
        if not response.data:
            return jsonify({"success": False, "error": "Property not found"}), 404
            
        property_data = response.data[0]
        
        return jsonify({
            "success": True,
            "property": property_data
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error fetching property: {str(e)}"}), 500


@routes.route('/api/show-contact', methods=['POST'])
def show_contact_info():
    """Show property owner contact info and register developer interest"""
    user = get_current_user()
    if not user or user['user_type'] != 'developer':
        return jsonify({"success": False, "error": "Must be logged in as developer"}), 401
    
    data = request.json
    property_id = data.get('property_id')
    developer_id = data.get('developer_id')
    
    if not property_id or not developer_id:
        return jsonify({"success": False, "error": "Missing property_id or developer_id"}), 400
    
    try:
        property_response = supabase.table('Property').select('*').eq('property_id', property_id).execute()
        
        if not property_response.data:
            return jsonify({"success": False, "error": "Property not found"}), 404
            
        property_data = property_response.data[0]
        property_owner_id = property_data['propertyOwner_id']
        
        existing_interest = supabase.table('Property_Interest').select('*').eq('property_id', property_id).eq('developer_id', developer_id).execute()
        print(f"Existing interest check for property {property_id}, developer {developer_id}: {existing_interest.data}")
        
        if not existing_interest.data:
            print(f"Inserting new interest for property {property_id}, developer {developer_id}")
            insert_result = supabase.table('Property_Interest').insert({
                'property_id': property_id,
                'developer_id': developer_id
            }).execute()
            print(f"Insert result: {insert_result.data}")
        else:
            print(f"Interest already exists, skipping insert")
        
        owner_response = supabase.table('Property owner').select('email, phone_number').eq('propertyOwner_id', property_owner_id).execute()
        
        if not owner_response.data:
            return jsonify({"success": False, "error": "Property owner contact not found"}), 404
            
        owner_contact = owner_response.data[0]
        
        return jsonify({
            "success": True,
            "contact": {
                "email": owner_contact['email'],
                "phone": owner_contact.get('phone_number', 'Not provided')
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error retrieving contact info: {str(e)}"}), 500


@routes.route('/api/delete-property/<int:property_id>', methods=['DELETE'])
def delete_property(property_id):
    """Delete a property and its images from storage"""
    user = get_current_user()
    if not user or user['user_type'] != 'property_owner':
        return jsonify({"success": False, "error": "Must be logged in as property owner"}), 401
    
    try:
        property_response = supabase.table('Property').select('*').eq('property_id', property_id).execute()
        
        if not property_response.data:
            return jsonify({"success": False, "error": "Property not found"}), 404
        
        property_data = property_response.data[0]
        
        if property_data['propertyOwner_id'] != user['user_id']:
            return jsonify({"success": False, "error": "You can only delete your own properties"}), 403
        
        try:
            supabase.table('Property_Interest').delete().eq('property_id', property_id).execute()
            print(f"Deleted developer interests for property {property_id}")
        except Exception as interest_error:
            print(f"Error deleting interests (may not exist): {interest_error}")
        
        image_urls = property_data.get('image_urls', []) or []
        bucket_name = 'property-images'
        
        for image_url in image_urls:
            try:
                filename = image_url.split('/')[-1]
                if filename:
                    supabase.storage.from_(bucket_name).remove([filename])
                    print(f"Deleted image: {filename}")
            except Exception as img_error:
                print(f"Error deleting image {image_url}: {img_error}")
        
        supabase.table('Property').delete().eq('property_id', property_id).execute()
        
        return jsonify({
            "success": True,
            "message": "Property and images deleted successfully"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Error deleting property: {str(e)}"}), 500


@routes.route('/api/update-property/<int:property_id>', methods=['PUT'])
def update_property(property_id):
    """Update an existing property"""
    user = get_current_user()
    if not user or user['user_type'] != 'property_owner':
        return jsonify({"success": False, "error": "Must be logged in as property owner"}), 401
    
    try:
        # Check if property exists and belongs to user
        property_response = supabase.table('Property').select('*').eq('property_id', property_id).execute()
        
        if not property_response.data:
            return jsonify({"success": False, "error": "Property not found"}), 404
        
        property_data = property_response.data[0]
        
        if property_data['propertyOwner_id'] != user['user_id']:
            return jsonify({"success": False, "error": "You can only edit your own properties"}), 403
        
        if property_data.get('sold'):
            return jsonify({"success": False, "error": "Cannot edit a sold property"}), 400
        
        # Get form data
        data = request.form
        
        # Validate required fields
        property_name = (data.get('property_name') or '').strip()
        property_type = (data.get('type') or 'land').strip().lower()
        province = (data.get('province') or '').strip()
        city = (data.get('city') or '').strip()
        size = data.get('size')
        description = (data.get('description') or '').strip()
        price_min = data.get('price_min')
        price_max = data.get('price_max')
        
        if not property_name or not city or not size:
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        # Validate prices
        try:
            price_min = float(price_min) if price_min else 0
            price_max = float(price_max) if price_max else 0
            size = int(size)
            
            if price_min < 0 or price_max < 0:
                return jsonify({"success": False, "error": "Prices cannot be negative"}), 400
            if price_max < price_min:
                return jsonify({"success": False, "error": "Maximum price must be greater than minimum price"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid price or size format"}), 400
        
        # Handle image deletions
        import json
        images_to_delete = json.loads(data.get('images_to_delete', '[]'))
        current_images = property_data.get('image_urls', []) or []
        bucket_name = 'property-images'
        
        # Delete marked images from storage
        for image_url in images_to_delete:
            try:
                filename = image_url.split('/')[-1]
                if filename:
                    supabase.storage.from_(bucket_name).remove([filename])
                    print(f"Deleted image: {filename}")
            except Exception as img_error:
                print(f"Error deleting image {image_url}: {img_error}")
        
        # Remove deleted images from the list
        updated_images = [url for url in current_images if url not in images_to_delete]
        
        # Handle new image uploads
        from models import upload_property_image
        for key in request.files:
            if key.startswith('new_image_'):
                file = request.files[key]
                if file and file.filename:
                    try:
                        image_url = upload_property_image(file, property_id, len(updated_images))
                        if image_url:
                            updated_images.append(image_url)
                    except Exception as img_error:
                        print(f"Error uploading new image: {img_error}")
        
        # Update property in database
        update_data = {
            "property_name": property_name,
            "type": property_type,
            "province": province,
            "city": city,
            "size": size,
            "description": description,
            "price_min": price_min,
            "price_max": price_max,
            "image_urls": updated_images
        }
        
        response = supabase.table('Property').update(update_data).eq('property_id', property_id).execute()
        
        return jsonify({
            "success": True,
            "message": "Property updated successfully",
            "data": response.data
        })
        
    except Exception as e:
        print(f"Error updating property: {e}")
        return jsonify({"success": False, "error": f"Error updating property: {str(e)}"}), 500
