import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

class ApplicationBuilder:
    def __init__(self):
        self.app_name = "CookieCleaner"
        self.version = "1.0.0"
        self.python_version = "3.11"

    def clean_build(self):
        """Clean previous builds"""
        for path in ['dist', 'build']:
            if os.path.exists(path):
                shutil.rmtree(path)
        if os.path.exists(f'{self.app_name}.spec'):
            os.remove(f'{self.app_name}.spec')

    def build_mac(self):
        """Build for macOS"""
        # Remove target-architecture for now to build for current architecture
        spec_options = [
            'pyinstaller',
            '--clean',
            '--windowed',
            '--noconfirm',
            '--name', self.app_name,
            '--osx-bundle-identifier', f'com.{self.app_name.lower()}.app',
            '--add-data', 'src:src',
            '--hidden-import', 'PyQt6.QtWidgets',
            '--hidden-import', 'PyQt6.QtCore',
            '--hidden-import', 'PyQt6.QtGui',
            'main.py'
        ]
        
        # Create DMG after build
        self._build_with_options(spec_options)
        self._create_dmg()

    def build_windows(self):
        """Build for Windows"""
        spec_options = [
            'pyinstaller',
            '--clean',
            '--windowed',
            '--noconfirm',
            '--name', self.app_name,
            '--add-data', 'src;src',
            '--hidden-import', 'PyQt6.QtWidgets',
            '--hidden-import', 'PyQt6.QtCore',
            '--hidden-import', 'PyQt6.QtGui',
            'main.py'
        ]
        self._build_with_options(spec_options)

    def build_linux(self):
        """Build for Linux"""
        spec_options = [
            'pyinstaller',
            '--clean',
            '--windowed',
            '--noconfirm',
            '--name', self.app_name,
            '--add-data', 'src:src',
            '--hidden-import', 'PyQt6.QtWidgets',
            '--hidden-import', 'PyQt6.QtCore',
            '--hidden-import', 'PyQt6.QtGui',
            'main.py'
        ]
        self._build_with_options(spec_options)

    def _build_with_options(self, options):
        """Common build process"""
        try:
            self.clean_build()
            print(f"Running PyInstaller with options: {' '.join(options)}")
            subprocess.run(options, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Build failed with error: {e}")
            raise

    def _create_dmg(self):
        """Create DMG for macOS"""
        try:
            if os.path.exists('dist'):
                print("Creating DMG file...")
                subprocess.run([
                    'hdiutil', 'create',
                    '-volname', self.app_name,
                    '-srcfolder', f'dist/{self.app_name}.app',
                    '-ov', '-format', 'UDZO',
                    f'dist/{self.app_name}.dmg'
                ], check=True)
                print("DMG creation successful")
        except subprocess.CalledProcessError as e:
            print(f"DMG creation failed with error: {e}")
            raise

def main():
    try:
        builder = ApplicationBuilder()
        system = platform.system().lower()
        
        print(f"Building for {system} platform...")
        print(f"Python version: {sys.version}")
        print(f"Platform details: {platform.platform()}")
        
        if system == 'darwin':
            builder.build_mac()
        elif system == 'windows':
            builder.build_windows()
        elif system == 'linux':
            builder.build_linux()
        else:
            print(f"Unsupported platform: {system}")
            
        print("Build completed successfully!")
            
    except Exception as e:
        print(f"Build failed with error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()