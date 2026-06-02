import subprocess
import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))

DEPS_CORE = [
    'numpy', 'pandas', 'matplotlib', 'scipy', 'scikit-learn',
    'pulp', 'openpyxl', 'python-docx', 'pyyaml',
]

DEPS_OPTIONAL = [
    'xgboost', 'lightgbm', 'torch', 'statsmodels', 'pmdarima',
]

def main():
    print('Installing core dependencies...')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *DEPS_CORE])

    answer = input('Install optional packages (xgboost, lightgbm, torch, etc.)? [y/N]: ')
    if answer.lower() == 'y':
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *DEPS_OPTIONAL])

    for d in ['data/raw', 'data/processed', 'data/external',
              'logs', 'paper/figures']:
        os.makedirs(os.path.join(BASE, d), exist_ok=True)

    print('Done. Ready to start modeling.')

if __name__ == '__main__':
    main()
