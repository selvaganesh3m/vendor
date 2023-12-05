# Vendor Management System


1. Project Setup:
    - clone `git@github.com:selvaganesh3m/vendor.git` (using ssh)
    - create virtual env for project and activate
    -  if activated `pip install -r requirements.txt` type the command from base dir
    - check if all the package installed by using `pip freeze`
    - to run test cases (must run from BASE directory)
        - `python manage.py test apps/order/api`
        - `python manage.py test apps/vendor/api`
    - to run server `python manage.py runsererver`

1. Some changes:
    1. Problem:
        - In the PurchaseOrder table there is a fields `order_date`,`issue_date` and `vendor (not null)`
            - `order_date` - this timestamp records each time when the order creates
            - `issue_date` - this timestamp records each time when the order assigned to vendor
            - `vendor (not null)` - Not null field, then technically the order date and issue date takes same timestamp with some difference in microsecons
            - In the above case we can use the `order_date` has a issue date, if we use separate `issue date` which resembles the `order_date` causes duplication when we have millions of records
    
    1. Solution:
        - To use the `issue_date` effectively, I've used a diffrent flow,
        - Created Purchase order without vendor, when we assign the order to vendor, the `issue_date` timestamp records (also created api to assign vendor)

    1. Project Flow
        ### User
        1. Register User (register user)
            - url: POST `http://localhost:8000/api/register/`
            - payload
                ```json
                {
                    "email": "ram@gmail.com",
                    "password": "johndoe",
                    "confirm_password": "johndoe"
                }
                ```
        1. Get Token:
            - url: GET `http://localhost:8000/api-token-auth/`
            - payload
                ```json
                {
                    "username": "james@gmail.com",
                    "password": "samsam"
                }
                ```
          

        ### Vendor (in requirement)
        1. Get Vendors
           - url: GET `http://localhost:8000/api/vendors/`
        1. Get Vendor Detail
            - url: GET `http://localhost:8000/api/vendors/<str:vendor_code>/`
        1. Create Vendor
           - url: POST `http://localhost:8000/api/vendors/`
           - payload: 
                ```json
                {
                    "user_email": "kalpesh@gmail.com",
                    "name": "Kalpesh",
                    "contact_detail":"14, Tom Ashok Nagar, Delhi",
                    "address": "India"
                }
                ```
        1. Update Vendor
           - url: PUT `http://localhost:8000/api/vendors/<str:vendor_code>/`
           - payload: 
                ```json
                {
                    "name": "Rakesh Kumar",
                    "address": "14, James streen, Chennai, TN",
                }
                ```
        1. Delete Vendor
           - url: DELETE `http://localhost:8000/api/vendors/<str:vendor_code>/`

        

        ### Order (in requirement)
        1. Get Purchase Orders
            - url: GET `http://localhost:8000/api/purchase-orders/`
        1. Get Purchase Order Detail
            - url: GET `http://localhost:8000/api/purchase-orders/<str:po_number>/`
        1. Create Purchase Order
            - url: POST `http://localhost:8000/api/purchase-orders/`
            - payload:
                ```json
                {
                    "delivery_date": "2023-12-12T16:49:11.025411+05:30",
                    "items": [{"Monitor": 4}],
                    "quantity": 1
                }
                ```
        1. Update Puchase Order
            - url: PUT `http://localhost:8000/api/purchase-orders/<str:po_number>/`
            - payload:
                ```json
                {
                    "delivery_date": "2023-12-12T16:49:11.025411+05:30",
                    "items": [{"note": 3}],
                    "quantity": 2
                }
                ```
        1. Delete Purchase Order
             - url: DELETE `http://localhost:8000/api/purchase-orders/<str:po_number>/`

        ### Order Related API
        1. Assign order to vendor
            - url: PUT `http://localhost:8000/api/purchase-orders/<str:po_number>/assign/<str:vendor_code>/`
        1. Acknowledge (in requirement)
            - url: PUT `http://localhost:8000/api/purchase-orders/<str:po_number>/acknowledge/`
        1. Complete Order
            - url: PUT `http://localhost:8000/api/purchase-orders/<str:po_number>/complete/`
        1. Rate Order
            - url: PUT   
            - payload: `http://localhost:8000/api/purchase-orders/<str:po_number>/rate/`
                ```json
                {
                    "rating": 3
                }
                ```

        ### Vendor Related API (In requirement)
        1. Vendor Performance
             - url: GET `http://localhost:8000/api/vendors/<str:vendor_code>/performance`
