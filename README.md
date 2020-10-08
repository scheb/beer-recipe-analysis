beer-recipe-analysis 🍺
======================

**Analyzing the composition of beer brewing recipes** with Python and Pandas.

This project ended up becoming a website with more data and interactive analysis: https://www.beer-analytics.com/

The goal of this project was to use the power of data analysis to get a better idea how different styles of beer are
brewed. Among other things, I wanted to find out which ingredients are commonly used and how much in relation to each
other.

Requirements
------------

- Python 3
- tqdm
- pandas
- matplotlib
- seaborn

Usage
-----

1) Load the data:

```bash
./bin/load_data.sh
```

2) Start Jupyter Labs in the project root

3) Run the notebooks from the `notebooks` folder

Results
-------

Run the Jupyter notebooks to see the results. The notebooks have a variable to generate results for a different beer
style. Per default it's analyzing the `pale ale` beer style.

### [Malts used](notebooks/malts.ipynb)

![alt text](img/malts.png "Malts used")

### [Hops used](notebooks/hops.ipynb)

![alt text](img/hops.png "Hops used")

License
-------

This software is available under the [WTFPL License](LICENSE).
