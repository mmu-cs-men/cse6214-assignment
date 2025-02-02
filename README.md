# CSE6214 Assignment
A second-hand book e-commerce site written in Django for this stupid assignment.

> [!IMPORTANT]  
> **Read and understand all instructions in this README before proceeding with development.**

## Getting Started
1. Fork the repo.

2. Clone your fork.

3. Launch PyCharm and open the project folder. It should prompt to create a virtual environment and install dependencies automatically. If it doesn't, you *somehow* fucked up already.

4. Open your PyCharm settings, and navigate to _"Tools > Actions on Save"_. From here, ensure _"Reformat code"_, _"Optimize imports"_, and _"Run Black"_ are checked.

## Coding Guidelines
1. Always make sure your code has been formatted with _Black_. A linter will run and check that you've formatted your code correctly when you send a pull request. If this linter fails, your code won't be merged.

2. If you're writing Model code, write tests. Not only is this good practice, but **we have to do this** as it's a grading criteria for Part III. Check out the Django official testing [tutorial](https://docs.djangoproject.com/en/5.1/topics/testing/overview/) for a great guide on testing.

3. A test runner will execute when you send a pull request. If there are any failing tests, your code won't be merged.

4. Every class and/or method should have a detailed docstring describing its use. Function docstrings must have parameter hints, if any. Your docstrings should follow _reStructuredText_ format. PyCharm can help you out with this.
