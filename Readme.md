Backend Run First
 cd backend
 pip install virtualenv
 python -m venv venv
 venv\Scripts\activate
 pip install -r requirements.txt
 python flask_api.py
 
 Frontend Run 
cd frontend
pip install virtualenv
 python -m venv venv
 venv\Scripts\activate
 cd expense_estimator
 pip install -r requirements.txt
 python manage.py makemigrati
 python manage.py migrate
 pip install django
 pip install pillow
 pip install requests
 python manage.py runserver