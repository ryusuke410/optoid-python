## Optoid

A helper library named optoid.


## Install

```
pip install optoid
```


## Usage

```
from optoid import Commander

commander = Commander()

# You need to attach once.
commander.attach()
print("success to attach")

commander.send_command("lis;len;lis;lis;lis")
print("success to send command")
```


## Develop

```
pip install pywin32
pip install wheel
pip install twine
```

```
python setup.py sdist
python setup.py bdist_wheel
```

```
twine upload --repository pypitest dist/*
python -m pip install --index-url https://test.pypi.org/simple/ optoid
```

```
twine upload --repository pypi dist/*
```


## Develop (wine)

```
wine64 cmd
.venv\\Scripts\activate
python -m example.tryout
```
