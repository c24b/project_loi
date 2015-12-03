# moissonneur-republique-numerique

Harvest opinions from site https://www.republique-numerique.fr/ using its JSON API.

**Note:** [Another, more complete, harvester](http://a3nm.net/git/republique/tree/) has been developped by
Antoine Amarilli.

## Install

```bash
git clone https://git.framasoft.org/etalab/moissonneur-republique-numerique.git
cd moissonneur-republique-numerique
npm install
```

## Usage

### To harvest JSON files of opinions

```bash
node index.js path_of_download_directory
```

### To generate a CSV files of optinions, sorted by popularity

```bash
node extract-best-articles.js path_of_download_directory > path_of_csv_file.csv
```
