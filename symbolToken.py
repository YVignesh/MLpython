import pandas as pd

def symbolToken():
    json_file_path = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    df = pd.read_json(json_file_path)
    df = df[df.exch_seg == 'NSE']
    df = df[df['symbol'].str.contains('-EQ')]

    nifty = pd.read_csv('ind_nifty50list.csv')
    df = df[df['name'].isin(nifty['Symbol'])]
    df=pd.merge(df,nifty, left_on='name', right_on='Symbol')
    df = df.drop(['ISIN Code','Series','Symbol','expiry','strike','lotsize','instrumenttype'], axis=1)
    csv_file_path = 'symbolToken.csv'
    df.to_csv(csv_file_path, index=False)
    print("symbolToken CSV exported successfully")

symbolToken()
