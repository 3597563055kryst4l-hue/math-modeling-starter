import subprocess
import sys
import os

REQUIREMENTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')

OPTIONAL_PACKAGES = [
    'xgboost', 'lightgbm', 'torch', 'statsmodels', 'pmdarima',
]

def main():
    print('Installing core dependencies...')
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', REQUIREMENTS])

    answer = input('Install optional packages (xgboost, lightgbm, torch, etc.)? [y/N]: ')
    if answer.lower() == 'y':
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *OPTIONAL_PACKAGES])

    BASE = os.path.dirname(os.path.abspath(__file__))
    for d in ['data/raw', 'data/processed', 'data/external',
              'logs', 'paper/figures']:
        os.makedirs(os.path.join(BASE, d), exist_ok=True)

    print('Done. Ready to start modeling.')

if __name__ == '__main__':
    main()
