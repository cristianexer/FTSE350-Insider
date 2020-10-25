import pandas_datareader.data as web


def pull_ticker(tick, start, end):
    d = web.DataReader(
        f'{tick}UK' if tick[-1] == '.' else f'{tick}.UK', 'stooq', start=start, end=end)
    d = d.reset_index()
    d.columns = d.columns.str.lower()
    d.columns = ['date'] + \
        [f'{tick.replace(".","")}_{x}' for x in d.columns if x != 'date']
    d.date = d.date.astype(str)
    return d
