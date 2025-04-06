# smart-coding-assistant

Program that translate text

## Testar program

```bash
cd src
python3 -m smart_coding_assistant.program
```

## Upload to PYPI

```bash
cd src
python setup.py sdist bdist_wheel
twine upload dist/*
```

## Install from PYPI

The homepage in pipy is https://pypi.org/project/smart-coding-assistant/

```bash
pip install --upgrade smart-coding-assistant
```

Using:

```bash
smart-coding-assistant
```

## Install from source
Installing `smart-coding-assistant` program

```bash
git clone https://github.com/trucomanx/SmartCodingAssistant.git
cd SmartCodingAssistant
pip install -r requirements.txt
cd src
python3 setup.py sdist
pip install dist/smart_coding_assistant-*.tar.gz
```
Using:

```bash
smart-coding-assistant
```

## Uninstall

```bash
pip uninstall smart_coding_assistant
```
