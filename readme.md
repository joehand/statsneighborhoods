
# Spatial Selection and the Statistics of Neighborhoods

[Working Paper](http://www.santafe.edu/media/workingpapers/15-06-020.pdf)

# Using this module


## Calculating DKLs

**Please see [example notebook](https://github.com/SFI-Cities/statistics-neighborhoods/blob/master/notebooks/US_DKL_Example.ipynb) with basic DKL calculations on US census data**

### Data Organization:

Data needs to be organized so that:

* Each row represents one *neighborhood*
* Each row has a unique ID.
* The data should be in a Pandas dataframe. The unique ID's should be the index (it is also sometimes helpful to keep the IDs as a column)
* A "City", or group, column should also be in the dataframe. Each city needs to have a unique identifier. You can check sizes of the cities by running: `df.groupby('CITY_COLUMN').size()`
* A set of "bin" columns. The bins should be counts of people/households in a bin subset.
* A column that contains the total population/household values for the row (this can be created by summing the bins)

### Setting Up the DataFrame

1. Create a regular expression to match all the bin column names. The easiest way to do this is to add `_bin` to all the bin columns. Check your regex by running: `df.filter(regex=bin_regex).columns`
2. Create the `CensusFrame`:

```
    cf = CensusFrame(
        data=df,
        bin_regex=bin_regex,
        group_col='CITY_COLUMN',
        tot_col='TOTAL_POP_COLUMN',
    )
```

### Getting Calcuations

3. You can run each calculation individually (see the functions in information.py). Or just run all of them (see notebook).
4. The calculations will create two new dataframes:
    * **A neighborhood dataframe**, accesseed at `cf.nhood_df`, this is a copy of the original dataframe with DKL and other values added
    * **A city dataframe** , accesseed at `cf.city_df`, this is a dataframe for all the group

