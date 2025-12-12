"""
Application Health Check Script
Validates all components before starting the server
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print(f"   ❌ Python {major}.{minor} detected. Python 3.8+ required!")
        return False
    print(f"   ✅ Python {major}.{minor} - Compatible")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    required_packages = [
        ('flask', 'Flask'),
        ('pymongo', 'PyMongo'),
        ('werkzeug', 'Werkzeug'),
        ('PIL', 'Pillow'),
        ('sklearn', 'scikit-learn'),
        ('dotenv', 'python-dotenv')
    ]
    
    all_installed = True
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} - Missing!")
            all_installed = False
    
    if not all_installed:
        print("\n   Install missing packages: pip install -r requirements.txt")
    
    return all_installed

def check_mongodb_connection():
    """Check MongoDB connection"""
    print("\n🍃 Checking MongoDB connection...")
    try:
        from pymongo import MongoClient
        from config import get_config
        
        config = get_config()
        client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        db_name = config.MONGO_DB_NAME
        print(f"   ✅ Connected to MongoDB database: {db_name}")
        return True
    except Exception as e:
        print(f"   ❌ MongoDB connection failed: {str(e)}")
        print("   Please check your MONGO_URI in config/settings.py")
        return False

def check_required_directories():
    """Check if required directories exist"""
    print("\n📁 Checking required directories...")
    required_dirs = ['uploads', 'logs', 'models', 'templates', 'static']
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), dir_name)
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ⚠️  {dir_name}/ - Creating...")
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"   ✅ {dir_name}/ created")
            except Exception as e:
                print(f"   ❌ Failed to create {dir_name}/: {e}")
                all_exist = False
    
    return all_exist

def check_configuration():
    """Check configuration settings"""
    print("\n⚙️  Checking configuration...")
    try:
        from config import get_config
        config = get_config()
        
        # Check critical settings
        checks = [
            ('SECRET_KEY', config.SECRET_KEY, config.SECRET_KEY != 'dev-secret-key-change-in-production'),
            ('MONGO_URI', config.MONGO_URI, True),
            ('MONGO_DB_NAME', config.MONGO_DB_NAME, True),
            ('UPLOAD_FOLDER', config.UPLOAD_FOLDER, True)
        ]
        
        all_good = True
        for setting_name, setting_value, is_valid in checks:
            if setting_value and is_valid:
                print(f"   ✅ {setting_name}")
            else:
                if setting_name == 'SECRET_KEY' and not is_valid:
                    print(f"   ⚠️  {setting_name} - Using default (change for production!)")
                else:
                    print(f"   ❌ {setting_name} - Not configured!")
                    all_good = False
        
        return all_good
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False

def check_routes():
    """Check if routes are properly registered"""
    print("\n🛣️  Checking routes...")
    try:
        from run import create_app
        app = create_app()
        
        critical_routes = ['/', '/login', '/register', '/report', '/admin']
        registered_routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        all_registered = True
        for route in critical_routes:
            if route in registered_routes:
                print(f"   ✅ {route}")
            else:
                print(f"   ❌ {route} - Not registered!")
                all_registered = False
        
        total_routes = len([r for r in registered_routes if not r.startswith('/static')])
        print(f"\n   📊 Total routes registered: {total_routes}")
        
        return all_registered
    except Exception as e:
        print(f"   ❌ Routes check failed: {e}")
        return False

def main():
    """Run all health checks"""
    print("=" * 60)
    print("   Urban Issue Reporter - Health Check")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("MongoDB Connection", check_mongodb_connection),
        ("Directories", check_required_directories),
        ("Configuration", check_configuration),
        ("Routes", check_routes)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"\n❌ {check_name} check crashed: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("   Health Check Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {check_name}")
    
    print(f"\n   Score: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Application is ready to run.")
        print("   Run: python run.py")
        return 0
    else:
        print(f"\n⚠️  {total - passed} check(s) failed. Please fix issues before running.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
