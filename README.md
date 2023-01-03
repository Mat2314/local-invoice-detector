# Invoice generator CLI
A command line tool to communicate with API shared by fakturownia.pl (invoiceocean.com).

The main requirement for this script is to generate invoices smoothly with one terminal command.

# How to run
First, create a `.env` file by copying `.env.example` in the root directory of the project. Then fill `.env` file with proper data that you use in fakturownia.pl (invoiceocean.com).

Create virtual environment and install packages from requirements.txt
```
python3 -m venv myvenv
source myvenv/bin/activate
```

Run the script with no arguments to see instructions or see 
```
# Create an invoice with 168 hours worked this month
python3 main.py 168 
```

```
# Create an invoice with automatically calculated hours for this month (all workdays)
python3 main.py --auto 
```

## pytest useful commands
Run the tests with one of the following commands:

- `pytest` - run the tests
- `pytest --cov [module_name]` - see the coverage in percentage
- `pytest --cov [module_name] --cov-report annotate` - generate the test coverage report
- `ptw` - watch changes in files and run tests on every file save