## Get Lib reports

A simple way to obtain a report on the usage of open-source libraries.

### Validation

After running script #6 ```_python_csv_6_npm_geturl.py``` or script #5 ```_python_csv_5_nuget_geturl.py```, execute the following command to check for missing libraries and fix them manually. (Due to some issues outside the automation process, there are a few special cases out of scope).

```bash
python ./validate.py --file "updated_filtered_output_nuget.csv"
```

```bash
python ./validate.py --file "updated_filtered_output_npm.csv"
```