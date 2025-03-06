import requests

def get_token(username, password):
    url = "http://localhost:8000/token"
    response = requests.post(url, data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json().get("access_token")
    print("Login failed.")
    return None

def fetch_employees(token):
    url = "http://localhost:8000/employees/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    print("Failed to fetch employees.")
    return []

def add_employee(token, name, role, salary):
    url = "http://localhost:8000/employees/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": name, "role": role, "salary": salary}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print("Employee added successfully.")
    else:
        print("Failed to add employee.")

def main():
    print("HR & Payroll Dashboard")
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    token = get_token(username, password)
    
    if not token:
        return
    
    while True:
        print("\nOptions:")
        print("1. View Employees")
        print("2. Add Employee")
        print("3. Exit")
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            employees = fetch_employees(token)
            if employees:
                for emp in employees:
                    print(f"ID: {emp.get('id')}, Name: {emp.get('name')}, Role: {emp.get('role')}, Salary: ${emp.get('salary', 0):,.2f}")
            else:
                print("No employees found.")
        elif choice == "2":
            name = input("Enter name: ").strip()
            role = input("Enter role: ").strip()
            try:
                salary = float(input("Enter salary: ").strip())
                add_employee(token, name, role, salary)
            except ValueError:
                print("Invalid salary input. Please enter a valid number.")
        elif choice == "3":
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
