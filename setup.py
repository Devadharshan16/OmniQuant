#!/usr/bin/env python3
"""
OmniQuant Setup Script
Builds C++ engine and sets up Python environment
"""

import os
import sys
import subprocess
import platform

def print_header(msg):
    print("\n" + "=" * 60)
    print(msg)
    print("=" * 60 + "\n")

def check_cmake():
    """Check if CMake is installed"""
    try:
        result = subprocess.run(['cmake', '--version'], capture_output=True, text=True)
        print(f"✓ CMake found: {result.stdout.split()[2]}")
        return True
    except FileNotFoundError:
        print("✗ CMake not found! Please install CMake 3.15+")
        return False

def check_compiler():
    """Check if compiler is available"""
    if platform.system() == "Windows":
        # Check for MSVC
        try:
            result = subprocess.run(['cl'], capture_output=True, text=True)
            print("✓ MSVC compiler found")
            return True
        except FileNotFoundError:
            print("✗ MSVC not found! Please install Visual Studio Build Tools")
            return False
    else:
        # Check for GCC/Clang
        for compiler in ['g++', 'clang++']:
            try:
                result = subprocess.run([compiler, '--version'], capture_output=True, text=True)
                print(f"✓ {compiler} found")
                return True
            except FileNotFoundError:
                continue
        print("✗ No C++ compiler found!")
        return False

def install_python_deps():
    """Install Python dependencies"""
    print_header("Installing Python Dependencies")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def build_cpp_engine():
    """Build C++ engine"""
    print_header("Building C++ Engine")
    
    build_dir = 'build'
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    
    os.chdir(build_dir)
    
    # Configure
    print("Configuring with CMake...")
    subprocess.run(['cmake', '..'], check=True)
    
    # Build
    print("Building...")
    subprocess.run(['cmake', '--build', '.', '--config', 'Release'], check=True)
    
    os.chdir('..')
    print("✓ C++ engine built successfully!")

def setup_frontend():
    """Setup frontend"""
    print_header("Setting Up Frontend")
    
    os.chdir('frontend')
    
    print("Installing npm dependencies...")
    subprocess.run(['npm', 'install'], check=True)
    
    os.chdir('..')
    print("✓ Frontend setup complete!")

def create_env_file():
    """Create .env file"""
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("# OmniQuant Configuration\n")
            f.write("API_HOST=0.0.0.0\n")
            f.write("API_PORT=8000\n")
            f.write("FRONTEND_PORT=3000\n")
        print("✓ Created .env file")

def main():
    print_header("🚀 OmniQuant v2 Setup")
    
    print("⚠️  MANDATORY DISCLAIMER:")
    print("OmniQuant is a research and educational arbitrage detection simulator.")
    print("All opportunities shown are theoretical.")
    print("No trades are executed. Not financial advice.")
    print()
    
    # Check prerequisites
    print_header("Checking Prerequisites")
    
    cmake_ok = check_cmake()
    compiler_ok = check_compiler()
    
    if not (cmake_ok and compiler_ok):
        print("\n✗ Prerequisites not met. Please install missing components.")
        sys.exit(1)
    
    # Install Python dependencies
    install_python_deps()
    
    # Build C++ engine
    try:
        # First check if pybind11 submodule exists
        if not os.path.exists('external/pybind11'):
            print("\n⚠️  pybind11 not found. You may need to:")
            print("   git submodule init")
            print("   git submodule update")
            print("\nSkipping C++ build for now...")
        else:
            build_cpp_engine()
    except Exception as e:
        print(f"\n⚠️  C++ build failed: {e}")
        print("Continuing with Python fallback...")
    
    # Setup frontend
    try:
        setup_frontend()
    except Exception as e:
        print(f"\n⚠️  Frontend setup failed: {e}")
    
    # Create config files
    create_env_file()
    
    print_header("✓ Setup Complete!")
    print("\nTo start OmniQuant:")
    print("  1. Start backend:  python api/main.py")
    print("  2. Start frontend: cd frontend && npm start")
    print("\nAccess dashboard at: http://localhost:3000")
    print()

if __name__ == "__main__":
    main()
