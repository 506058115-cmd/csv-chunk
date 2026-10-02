# csv-chunk

Split a large CSV table into smaller files while keeping each row intact and repeating the header. It streams through the input, so memory use does not grow with the file size.

## Use

Requires Python 3.8+; no packages to install.

```sh
python csv_chunk.py export.csv --rows-per-file 50000
python csv_chunk.py events.tsv --delimiter $'\t' --rows-per-file 20000 --output-dir event-parts
```

The output directory must not already exist. Each part is written there as `export-part-0001.csv`, `export-part-0002.csv`, and so on. The first input row is treated as the header. UTF-8 and UTF-8-with-BOM inputs are supported. Quoted commas, delimiters, and embedded newlines are handled by Python's CSV reader.

The tool reads only the selected input file, does not contact a network, and does not overwrite existing output directories.

## License

MIT
