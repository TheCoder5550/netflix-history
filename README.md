# netflix-history
Plot a timeline of your netflix viewing history

## Usage
1. Download your [viewing history](https://www.netflix.com/settings/viewing-history) as a `.csv` file from Netflix.
1. Run the `plot.py` script using Python 3 and pass the path of your viewing history to the `--file` flag:
    ```bash
    python plot.py --file ./NetflixViewingHistory.csv
    ```
1. A window will pop up with a timeline of every series you've watched.

### Flags
The following flags can be passed to the script:
* `--file`: Specify the path of your viewing history
* `--year`: Plot only a single year
* `--output`: Specify a path for the output csv file with formatted data. If `--year` is specified, the output will only include that year